# Nifty 50 next-day closing price predictor

A Streamlit dashboard that pulls live Nifty 50 data from Yahoo Finance (`^NSEI`),
trains a model on the spot, and forecasts the next trading day's close. It shows
predicted vs actual prices from a walk-forward backtest so you can see how well
the model really does.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What you get

- **Next-day forecast** next to the last close, plus backtest error and direction accuracy.
- **Predicted vs actual chart** over the backtest window (60 to 500 trading days), with
  the next-day forecast marked.
- **Error by day** and a **predicted vs actual scatter**.
- **Intraday live quote** (5-minute bars, refreshes every minute).
- A backtest table you can download as CSV, and feature importances.

Sidebar settings: ticker, training history (5y to max), model (Ridge, Random forest,
Gradient boosting), backtest window, and an optional CSV upload.

## How it works

- `predictor.py` holds data loading, features and training, with no Streamlit code.
- The model predicts the next day's **log return**; the price is today's close × e^return.
  Predicting the return rather than the raw price keeps tree models valid at index
  levels they never saw in training.
- The backtest retrains every 21 trading days using only past data, so it never sees
  the answer.
- The model also uses the **S&P 500's** latest 1-day and 5-day returns (toggle in the
  sidebar). The US market closes after NSE, so that move is already known before Nifty
  opens the next day. Today's S&P bar is ignored while the US session is still open.
- The **naive** baseline (tomorrow closes where today did) is shown next to the model's
  error, because it's hard to beat on daily index data.
- If Yahoo Finance can't be reached, the app falls back to `data/nifty50_history.csv`
  (Nifty 50 from 2000 to Apr 2025) and says so.

## Backtest results

500-day walk-forward backtests, mean absolute error of the next-day close.
"vs naive" compares with guessing that tomorrow closes where today did.

| Test period ending | Model | Nifty only | + S&P 500 |
|---|---|---|---|
| Nov 2019 | Random forest | 0.2% better than naive | 2.5% better |
| Nov 2019 | Gradient boosting | 0.1% better | 2.8% better |
| Nov 2015 | Random forest | 0.2% worse | 4.1% better |
| Nov 2015 | Gradient boosting | 0.4% worse | 4.0% better |

Direction accuracy rose from 51–56% to 56–61% with the S&P 500 features. Adding
Nifty Bank didn't help in any test, so it isn't used. India VIX, Nikkei and USD/INR
haven't been tested yet because they need live data to evaluate.

Educational use only, not investment advice.
