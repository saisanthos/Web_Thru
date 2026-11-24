"""Nifty 50 next-day closing price dashboard.

Fetches live daily data from Yahoo Finance, trains a model on the spot,
backtests it walk-forward, and plots predicted vs actual closing prices.

Run:  streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import predictor as p

st.set_page_config(page_title="Nifty 50 Predictor", page_icon="📈", layout="wide")

ACTUAL = "#2a78d6"  # blue
PREDICTED = "#eb6834"  # orange
FALLBACK_CSV = Path(__file__).parent / "data" / "nifty50_history.csv"


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Yahoo ticker", "^NSEI", help="^NSEI is the Nifty 50 index.")
    period = st.selectbox("History to train on", ["5y", "10y", "15y", "max"], index=1)
    model_name = st.selectbox("Model", list(p.MODELS), index=1)
    test_days = st.slider("Backtest window (trading days)", 60, 500, 250, step=10)
    use_spx = st.toggle(
        "Use S&P 500 overnight move",
        value=True,
        help="The US market closes after NSE, so the S&P 500's last move is known "
        "before Nifty opens next. In backtests this cut the error by 2.5–4%.",
    )
    st.divider()
    uploaded = st.file_uploader(
        "Or upload your own CSV",
        type="csv",
        help="Yahoo format (Date,Open,High,Low,Close,Volume) or "
        "Investing.com format (Date,Price,Open,High,Low,Vol.,Change %).",
    )
    if st.button("🔄 Refresh live data", width="stretch"):
        st.cache_data.clear()
        st.rerun()


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner="Fetching live data from Yahoo Finance…")
def get_live(ticker: str, period: str) -> pd.DataFrame:
    return p.fetch_yahoo(ticker, period)


@st.cache_data(ttl=300, show_spinner="Fetching S&P 500 data…")
def get_spx(period: str) -> pd.DataFrame:
    return p.fetch_us_closed("^GSPC", period)


@st.cache_data(ttl=60, show_spinner=False)
def get_intraday(ticker: str) -> pd.DataFrame:
    return p.fetch_intraday(ticker)


@st.cache_data(show_spinner="Training model and running backtest…")
def get_result(df: pd.DataFrame, model_name: str, test_days: int, spx: pd.DataFrame | None) -> p.Result:
    extra = {"spx": spx} if spx is not None else None
    return p.run(df, model_name, test_days, extra)


source = ""
df = pd.DataFrame()
if uploaded is not None:
    df = p.load_csv(uploaded)
    source = f"Uploaded file **{uploaded.name}**"
else:
    fetch_error = "no rows returned"
    try:
        df = get_live(ticker, period)
        source = f"Live from Yahoo Finance (**{ticker}**), refreshed every 5 minutes"
    except Exception as e:  # network errors, rate limits
        fetch_error = str(e)
    if df.empty and FALLBACK_CSV.exists():
        st.warning(
            "Couldn't get live data from Yahoo Finance, so this is using the bundled "
            f"historical CSV instead. Predictions won't be current. ({fetch_error})"
        )
        df = p.load_csv(FALLBACK_CSV)
        source = "Bundled CSV (offline fallback)"
        use_spx = False  # no matching S&P 500 history offline

spx = None
if use_spx:
    try:
        spx = get_spx("max" if period == "max" else period)
    except Exception:
        spx = None
    if spx is None or spx.empty or spx.index[-1] < df.index[-1] - pd.Timedelta(days=5):
        st.info("S&P 500 data isn't available right now, so the model runs without it.")
        spx = None

if df.empty:
    st.error("No data available. Check the ticker or upload a CSV.")
    st.stop()


# --------------------------------------------------------------------------
# Header + live quote
# --------------------------------------------------------------------------
st.title("📈 Nifty 50 next-day closing price")
st.caption(f"Data: {source}. Last daily bar: {df.index[-1]:%d %b %Y}.")

try:
    result = get_result(df, model_name, test_days, spx)
except ValueError as e:
    st.error(str(e))
    st.stop()

m = result.metrics
change = result.next_close - result.last_close

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    f"Predicted close · {result.next_date:%a %d %b}",
    f"₹{result.next_close:,.2f}",
    f"{change:+,.2f} ({change / result.last_close:+.2%})",
)
c2.metric(f"Last close · {result.last_date:%a %d %b}", f"₹{result.last_close:,.2f}")
c3.metric(
    "Backtest MAE",
    f"₹{m['MAE']:,.1f}",
    f"{m['MAE'] - m['Naive MAE']:+,.1f} vs naive",
    delta_color="inverse",
    help="Mean absolute error over the backtest window. 'Naive' assumes tomorrow "
    "closes where today did; beating it is the real bar.",
)
c4.metric(
    "Direction accuracy",
    f"{m['Direction accuracy']:.1f}%",
    help=f"How often the predicted up/down move matched reality. "
    f"Up-days were {m['Up-day share']:.1f}% of the window.",
)


@st.fragment(run_every=60)
def live_quote():
    if uploaded is not None:
        return
    try:
        intra = get_intraday(ticker)
    except Exception:
        intra = pd.DataFrame()
    if intra.empty:
        return
    last = intra["Close"].iloc[-1]
    open_ = intra["Open"].iloc[0]
    with st.expander(
        f"Intraday · {intra.index[-1]:%d %b %H:%M} · ₹{last:,.2f} ({last / open_ - 1:+.2%} from open)",
        expanded=False,
    ):
        fig = go.Figure(
            go.Scatter(
                x=intra.index, y=intra["Close"], mode="lines",
                line=dict(color=ACTUAL, width=2), name="Price",
                hovertemplate="%{x|%H:%M}<br>₹%{y:,.2f}<extra></extra>",
            )
        )
        fig.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), hovermode="x unified")
        st.plotly_chart(fig, width="stretch")
        st.caption("Auto-refreshes every minute. Yahoo data may be delayed ~15 minutes.")


live_quote()


# --------------------------------------------------------------------------
# Predicted vs actual
# --------------------------------------------------------------------------
bt = result.backtest
st.subheader("Predicted vs actual closing price")
st.caption(
    f"Walk-forward backtest over the last {len(bt)} trading days. Each prediction was made "
    "by a model trained only on data before that day, so it never saw the answer."
)

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=bt["Date"], y=bt["Actual"], name="Actual", mode="lines",
        line=dict(color=ACTUAL, width=2),
        hovertemplate="₹%{y:,.2f}",
    )
)
fig.add_trace(
    go.Scatter(
        x=bt["Date"], y=bt["Predicted"], name="Predicted", mode="lines",
        line=dict(color=PREDICTED, width=2),
        hovertemplate="₹%{y:,.2f}",
    )
)
fig.add_trace(
    go.Scatter(
        x=[result.next_date], y=[result.next_close], name="Next-day forecast",
        mode="markers", marker=dict(color=PREDICTED, size=11, symbol="star",
                                    line=dict(width=2, color="white")),
        hovertemplate="Forecast ₹%{y:,.2f}<extra></extra>",
    )
)
fig.update_layout(
    height=460, hovermode="x unified", margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    yaxis=dict(title="Close (₹)", tickformat=",.0f"),
    xaxis=dict(rangeslider=dict(visible=True, thickness=0.06)),
)
st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)

with left:
    st.subheader("Prediction error by day")
    err = bt["Predicted"] - bt["Actual"]
    fig_err = go.Figure(
        go.Bar(
            x=bt["Date"], y=err, marker_color=PREDICTED,
            hovertemplate="%{x|%d %b %Y}<br>Error ₹%{y:+,.1f}<extra></extra>",
        )
    )
    fig_err.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=0), bargap=0.1,
        yaxis=dict(title="Predicted − actual (₹)", tickformat=",.0f", zeroline=True),
    )
    st.plotly_chart(fig_err, width="stretch")

with right:
    st.subheader("Predicted vs actual (scatter)")
    lo, hi = bt[["Actual", "Predicted"]].min().min(), bt[["Actual", "Predicted"]].max().max()
    fig_sc = go.Figure()
    fig_sc.add_trace(
        go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", name="Perfect",
                   line=dict(color="gray", width=1, dash="dot"), hoverinfo="skip")
    )
    fig_sc.add_trace(
        go.Scatter(
            x=bt["Actual"], y=bt["Predicted"], mode="markers", name="Days",
            marker=dict(color=ACTUAL, size=8, opacity=0.7, line=dict(width=1, color="white")),
            customdata=bt["Date"],
            hovertemplate="%{customdata|%d %b %Y}<br>Actual ₹%{x:,.0f}<br>Predicted ₹%{y:,.0f}<extra></extra>",
        )
    )
    fig_sc.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=0), showlegend=False,
        xaxis=dict(title="Actual (₹)", tickformat=",.0f"),
        yaxis=dict(title="Predicted (₹)", tickformat=",.0f"),
    )
    st.plotly_chart(fig_sc, width="stretch")


# --------------------------------------------------------------------------
# Details
# --------------------------------------------------------------------------
with st.expander("Backtest table"):
    table = bt[["Date", "Actual", "Predicted"]].copy()
    table["Error"] = table["Predicted"] - table["Actual"]
    table["Error %"] = table["Error"] / table["Actual"] * 100
    table = table.iloc[::-1].reset_index(drop=True)
    st.dataframe(
        table.style.format(
            {"Date": "{:%d %b %Y}", "Actual": "₹{:,.2f}", "Predicted": "₹{:,.2f}",
             "Error": "{:+,.2f}", "Error %": "{:+.2f}%"}
        ),
        width="stretch", height=360,
    )
    st.download_button("Download CSV", table.to_csv(index=False), "nifty_backtest.csv")

spx_note = (
    "Plus the S&P 500's latest 1-day and 5-day returns (US close on or before each Nifty date)."
    if spx is not None
    else "S&P 500 features are off."
)

with st.expander("Model details"):
    st.markdown(
        f"""
- **Model:** {model_name}, trained on {len(df):,} daily bars.
- **Target:** next day's log return. The price is rebuilt as today's close × e^(predicted return),
  which keeps the model valid at price levels it never saw in training.
- **Features:** last 5 daily returns, distance from 5/10/20/50-day averages, 5- and 20-day
  volatility, daily range, candle body, RSI(14), volume z-score and day of week.
  {spx_note}
- **Accuracy:** RMSE ₹{m['RMSE']:,.1f}, MAPE {m['MAPE']:.2f}%. Naive (tomorrow = today) MAE is
  ₹{m['Naive MAE']:,.1f}.
- **Calendar:** the next trading day is the next weekday; NSE holidays aren't skipped.
"""
    )
    if result.feature_importance is not None:
        imp = result.feature_importance
        fig_imp = go.Figure(
            go.Bar(x=imp.values, y=imp.index, orientation="h", marker_color=ACTUAL,
                   hovertemplate="%{y}: %{x:.3f}<extra></extra>")
        )
        fig_imp.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0),
                              xaxis_title="Importance")
        st.plotly_chart(fig_imp, width="stretch")

st.caption(
    "Daily index moves are close to random, so a next-day forecast is usually within a "
    "fraction of a percent of today's close. Educational use only, not investment advice."
)
