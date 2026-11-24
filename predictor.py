"""Data loading, feature engineering and model training for the Nifty 50
next-day closing price predictor. Kept free of Streamlit so it can be tested
on its own."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

OHLCV = ["Open", "High", "Low", "Close", "Volume"]

MODELS = {
    "Ridge regression": lambda: make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
    "Random forest": lambda: RandomForestRegressor(
        n_estimators=300, max_depth=6, min_samples_leaf=5, n_jobs=-1, random_state=42
    ),
    "Gradient boosting": lambda: GradientBoostingRegressor(
        n_estimators=300, max_depth=3, learning_rate=0.03, subsample=0.8, random_state=42
    ),
}


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
def fetch_yahoo(ticker: str = "^NSEI", period: str = "10y") -> pd.DataFrame:
    """Daily OHLCV from Yahoo Finance, indexed by date."""
    import yfinance as yf

    df = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=False)
    return _clean(df)


def fetch_us_closed(ticker: str = "^GSPC", period: str = "10y") -> pd.DataFrame:
    """Daily bars for a US index, without today's bar while the US session is
    still open (a half-finished day isn't what the model was trained on)."""
    df = fetch_yahoo(ticker, period)
    if df.empty:
        return df
    now_ny = pd.Timestamp.now(tz="America/New_York")
    if df.index[-1] == now_ny.normalize().tz_localize(None) and now_ny.hour * 60 + now_ny.minute < 16 * 60 + 15:
        df = df.iloc[:-1]
    return df


def fetch_intraday(ticker: str = "^NSEI") -> pd.DataFrame:
    """Today's (or the last session's) 5-minute bars, for the live quote."""
    import yfinance as yf

    df = yf.Ticker(ticker).history(period="5d", interval="5m", auto_adjust=False)
    if df.empty:
        return df
    last_day = df.index[-1].date()
    return df[df.index.date == last_day][OHLCV]


def load_csv(path_or_buffer) -> pd.DataFrame:
    """Read a CSV in either Yahoo format (Date,Open,High,Low,Close,Volume) or
    Investing.com format (Date,Price,Open,High,Low,Vol.,Change %)."""
    raw = pd.read_csv(path_or_buffer)
    raw.columns = [c.strip() for c in raw.columns]
    if "Price" in raw.columns and "Close" not in raw.columns:
        raw = raw.rename(columns={"Price": "Close"})
    if "Vol." in raw.columns:
        raw["Volume"] = raw["Vol."].map(_parse_volume)
    raw["Date"] = pd.to_datetime(raw["Date"], errors="coerce")
    raw = raw.set_index("Date")
    for col in ["Open", "High", "Low", "Close"]:
        raw[col] = pd.to_numeric(raw[col].astype(str).str.replace(",", ""), errors="coerce")
    if "Volume" not in raw.columns:
        raw["Volume"] = np.nan
    return _clean(raw)


def _parse_volume(v) -> float:
    if pd.isna(v):
        return np.nan
    s = str(v).replace(",", "").strip()
    mult = {"K": 1e3, "M": 1e6, "B": 1e9}.get(s[-1:].upper(), 1)
    try:
        return float(s.rstrip("KMBkmb")) * mult
    except ValueError:
        return np.nan


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    df.index = df.index.normalize()
    df.index.name = "Date"
    df = df[OHLCV].sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df.dropna(subset=["Open", "High", "Low", "Close"])


# --------------------------------------------------------------------------
# Features
# --------------------------------------------------------------------------
def build_features(df: pd.DataFrame, extra: dict | None = None) -> pd.DataFrame:
    """Features use only information available at that day's close.
    Target is the next day's log return; the price is rebuilt from it.

    extra maps a short name to another market's daily OHLCV. Each one adds its
    latest 1-day and 5-day returns as of that date (see _extra_features)."""
    out = pd.DataFrame(index=df.index)
    close = df["Close"]
    ret = np.log(close).diff()

    for lag in range(1, 6):
        out[f"ret_lag{lag}"] = ret.shift(lag - 1)
    for w in (5, 10, 20, 50):
        out[f"close_vs_ma{w}"] = close / close.rolling(w).mean() - 1
    out["vol_5"] = ret.rolling(5).std()
    out["vol_20"] = ret.rolling(20).std()
    out["range_pct"] = (df["High"] - df["Low"]) / close
    out["body_pct"] = (close - df["Open"]) / df["Open"]
    out["rsi_14"] = _rsi(close, 14) / 100
    vol = df["Volume"].replace(0, np.nan)
    if vol.notna().mean() > 0.8:
        out["volume_z20"] = (vol - vol.rolling(20).mean()) / vol.rolling(20).std()
    out["dow"] = df.index.dayofweek

    for name, other in (extra or {}).items():
        out = out.join(_extra_features(name, other, df.index))

    out["target"] = ret.shift(-1)
    out["Close"] = close
    return out


def _extra_features(name: str, other: pd.DataFrame, index: pd.DatetimeIndex) -> pd.DataFrame:
    """Returns of another market, aligned to each Nifty date by taking that
    market's last close on or before the same calendar date. US markets close
    after NSE, so the US close dated t is known before NSE opens on t+1."""
    c = other["Close"].dropna()
    r = np.log(c).diff()
    f = pd.DataFrame({f"{name}_ret1": r, f"{name}_ret5": np.log(c).diff(5)})
    aligned = f.reindex(f.index.union(index)).ffill().reindex(index)
    # Don't carry a stale value across a long gap (e.g. data that ends early).
    last_seen = pd.Series(c.index, index=c.index).reindex(c.index.union(index)).ffill().reindex(index)
    stale = (index.to_series() - last_seen).dt.days > 5
    aligned[stale.values] = np.nan
    return aligned


def _rsi(close: pd.Series, n: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def feature_columns(feats: pd.DataFrame) -> list[str]:
    return [c for c in feats.columns if c not in ("target", "Close")]


# --------------------------------------------------------------------------
# Training / evaluation
# --------------------------------------------------------------------------
@dataclass
class Result:
    backtest: pd.DataFrame  # Date, Actual, Predicted, Naive, PrevClose
    metrics: dict
    next_date: pd.Timestamp
    next_close: float
    last_close: float
    last_date: pd.Timestamp
    feature_importance: pd.Series | None


def run(df: pd.DataFrame, model_name: str, test_days: int, extra: dict | None = None) -> Result:
    feats = build_features(df, extra)
    cols = feature_columns(feats)
    feats = feats.replace([np.inf, -np.inf], np.nan)

    labelled = feats.dropna(subset=cols + ["target"])
    if len(labelled) < test_days + 200:
        raise ValueError(
            f"Need at least {test_days + 200} usable days of history, got {len(labelled)}."
        )

    # Walk-forward in monthly-ish blocks: each block is predicted by a model
    # trained only on data before it, so the backtest never sees the future.
    test = labelled.iloc[-test_days:]
    block = 21
    preds = []
    for start in range(0, len(test), block):
        chunk = test.iloc[start : start + block]
        train = labelled.loc[: chunk.index[0]].iloc[:-1]
        model = MODELS[model_name]()
        model.fit(train[cols], train["target"])
        preds.append(pd.Series(model.predict(chunk[cols]), index=chunk.index))
    pred_ret = pd.concat(preds)

    prev_close = test["Close"]
    next_dates = _shifted_index(feats, test.index)
    actual = prev_close * np.exp(test["target"])
    predicted = prev_close * np.exp(pred_ret)

    backtest = pd.DataFrame(
        {
            "Date": next_dates,
            "PrevClose": prev_close.values,
            "Actual": actual.values,
            "Predicted": predicted.values,
            "Naive": prev_close.values,
            "Open": df["Open"].reindex(next_dates).values,
        }
    )

    err = backtest["Predicted"] - backtest["Actual"]
    naive_err = backtest["Naive"] - backtest["Actual"]
    true_dir = np.sign(backtest["Actual"] - backtest["PrevClose"])
    pred_dir = np.sign(backtest["Predicted"] - backtest["PrevClose"])
    metrics = {
        "MAE": float(err.abs().mean()),
        "RMSE": float(np.sqrt((err**2).mean())),
        "MAPE": float((err.abs() / backtest["Actual"]).mean() * 100),
        "Naive MAE": float(naive_err.abs().mean()),
        "Direction accuracy": float((true_dir == pred_dir).mean() * 100),
        "Up-day share": float((true_dir > 0).mean() * 100),
    }

    # Final model on all labelled history, predicting the day after the last close.
    final = MODELS[model_name]()
    final.fit(labelled[cols], labelled["target"])
    last = feats.dropna(subset=cols).iloc[[-1]]
    next_ret = float(final.predict(last[cols])[0])
    last_close = float(last["Close"].iloc[0])
    last_date = last.index[0]

    importance = None
    if hasattr(final, "feature_importances_"):
        importance = pd.Series(final.feature_importances_, index=cols).sort_values()
    elif hasattr(final, "named_steps"):
        coef = final.named_steps["ridge"].coef_
        importance = pd.Series(np.abs(coef), index=cols).sort_values()

    return Result(
        backtest=backtest,
        metrics=metrics,
        next_date=next_business_day(last_date),
        next_close=last_close * np.exp(next_ret),
        last_close=last_close,
        last_date=last_date,
        feature_importance=importance,
    )


def _shifted_index(feats: pd.DataFrame, idx: pd.Index) -> list[pd.Timestamp]:
    """Date of the trading day after each date in idx."""
    all_idx = feats.index
    pos = all_idx.get_indexer(idx)
    return [all_idx[p + 1] if p + 1 < len(all_idx) else next_business_day(all_idx[p]) for p in pos]


def next_business_day(d: pd.Timestamp) -> pd.Timestamp:
    """Next weekday. NSE holidays are not modelled."""
    return (pd.Timestamp(d) + pd.offsets.BDay(1)).normalize()


# --------------------------------------------------------------------------
# Strategy backtest
# --------------------------------------------------------------------------
def strategy(
    bt: pd.DataFrame,
    mode: str = "long_flat",
    entry: str = "close",
    threshold_pct: float = 0.0,
    cost_pct: float = 0.03,
) -> tuple[pd.DataFrame, dict]:
    """Trade the backtest's predictions one day at a time.

    mode: "long_flat" (long on predicted up days, else cash) or
          "long_short" (long on predicted up days, short on predicted down days).
    entry: "close" trades from the previous close to the next close, which is only
           possible when every feature is known at NSE's close (no S&P 500).
           "open" enters at the next open and exits at that day's close, and
           compares the prediction with the open price.
    threshold_pct: skip days where the predicted move is smaller than this.
    cost_pct: cost per buy or sell, as % of the position (brokerage, taxes, slippage).
    """
    d = bt.set_index("Date")
    if entry == "open":
        start = d["Open"]
    else:
        start = d["PrevClose"]
    day_ret = np.log(d["Actual"] / start)
    pred_move = d["Predicted"] / start - 1

    pos = np.sign(pred_move).where(pred_move.abs() * 100 >= threshold_pct, 0.0)
    if mode == "long_flat":
        pos = pos.clip(lower=0)
    pos = pos.fillna(0.0)

    if entry == "open":
        # Every trading day is a round trip: in at the open, out at the close.
        trades = pos.abs() * 2
    else:
        trades = pos.diff().abs().fillna(pos.abs())
    strat = pos * day_ret - trades * cost_pct / 100
    hold = np.log(d["Actual"] / d["PrevClose"])

    out = pd.DataFrame(
        {
            "Position": pos,
            "Strategy": np.exp(strat.cumsum()),
            "Buy & hold": np.exp(hold.cumsum()),
        }
    )
    stats = {"Strategy": _perf(strat, pos, trades), "Buy & hold": _perf(hold, pd.Series(1.0, index=hold.index), None)}
    return out, stats


def _perf(r: pd.Series, pos: pd.Series, trades: pd.Series | None) -> dict:
    r = r.fillna(0.0)
    equity = np.exp(r.cumsum())
    years = len(r) / 252
    vol = r.std() * np.sqrt(252)
    active = r[pos != 0]
    return {
        "Total return %": (equity.iloc[-1] - 1) * 100,
        "Return per year %": (equity.iloc[-1] ** (1 / years) - 1) * 100 if years else np.nan,
        "Sharpe": r.mean() * 252 / vol if vol else np.nan,
        "Worst drop %": ((equity / equity.cummax()) - 1).min() * 100,
        "Winning days %": (active > 0).mean() * 100 if len(active) else np.nan,
        "Days in market %": (pos != 0).mean() * 100,
        "Trades": int(trades.sum()) if trades is not None else 1,
    }
