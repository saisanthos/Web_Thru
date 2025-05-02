import streamlit as st
import yfinance as yf
import pandas as pd
import joblib
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.title("🔮 NIFTY 50 Next-Day Closing Price Predictor")

@st.cache_resource
def load_model():
    return joblib.load("Web_Thru_Predictor.pkl")

model = load_model()

@st.cache_data
def get_latest_data():
    end = datetime.today()
    start = end - timedelta(days=35)
    df = yf.download("^NSEI", start=start, end=end)
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date  # Force date conversion
    return df.dropna()

latest_df = get_latest_data()

if latest_df.empty:
    st.warning("No recent NIFTY 50 data found. Please try again later.")
    st.stop()

# Feature engineering
def calculate_features(df):
    df = df.copy()
    df['Change %'] = ((df['Close'] - df['Open']) / df['Open']) * 100
    df['Daily_Range'] = df['High'] - df['Low']
    df['Rolling_Mean_5'] = df['Close'].rolling(5).mean()
    df['Rolling_Std_5'] = df['Close'].rolling(5).std()
    df['Price_Change'] = df['Close'].diff()
    df['Year'] = pd.to_datetime(df['Date']).dt.year
    df['Month'] = pd.to_datetime(df['Date']).dt.month
    df['Day'] = pd.to_datetime(df['Date']).dt.day
    df['DayOfWeek'] = pd.to_datetime(df['Date']).dt.weekday
    return df.dropna()

latest_df = calculate_features(latest_df)



# Current Prediction
st.subheader("📈 Latest Market Data")
st.dataframe(latest_df[['Date', 'Open', 'High', 'Low', 'Close']].tail(1))

current = latest_df.iloc[-1]

features = pd.DataFrame({
    'Open': [current['Open']],
    'High': [current['High']],
    'Low': [current['Low']],
    'Vol.': [current['Volume']],
    'Change %': [current['Change %']],
    'Daily_Range': [current['Daily_Range']],
    'Price_Change': [current['Price_Change']],
    'Rolling_Mean_5': [current['Rolling_Mean_5']],
    'Rolling_Std_5': [current['Rolling_Std_5']],
    'Year': [current['Year']],
    'Month': [current['Month']],
    'Day': [current['Day']],
    'DayOfWeek': [current['DayOfWeek']]
})

try:
    prediction = model.predict(features)[0]
    st.subheader("📊 Next-Day Prediction")
    st.success(f"₹ {prediction:.2f}")
except Exception as e:
    st.error(f"Prediction failed: {str(e)}")

# Historical Predictions
st.subheader("📊 Last 5 Trading Days Performance")

predictions = []
actuals = []
dates = []

for i in range(len(latest_df)-1):
    try:
        current = latest_df.iloc[i]
        next_day = latest_df.iloc[i+1]
        
        features = pd.DataFrame({
            'Open': [current['Open']],
            'High': [current['High']],
            'Low': [current['Low']],
            'Vol.': [current['Volume']],
            'Change %': [current['Change %']],
            'Daily_Range': [current['Daily_Range']],
            'Price_Change': [current['Price_Change']],
            'Rolling_Mean_5': [current['Rolling_Mean_5']],
            'Rolling_Std_5': [current['Rolling_Std_5']],
            'Year': [current['Year']],
            'Month': [current['Month']],
            'Day': [current['Day']],
            'DayOfWeek': [current['DayOfWeek']]
        })
        
        pred = model.predict(features)[0]
        
        # Safe date handling
        date_str = str(next_day['Date'])  # Already converted to date object
        actual = next_day['Close']
        
        predictions.append(pred)
        actuals.append(actual)
        dates.append(date_str)
        
    except Exception as e:
        # Robust error reporting
        try:
            err_date = str(current['Date'])
        except:
            err_date = "unknown date"
        st.error(f"Error processing {err_date}: {str(e)}")
        continue

# Visualization
if len(dates) >= 1:
    comparison_df = pd.DataFrame({
        'Date': dates[-5:],
        'Actual': actuals[-5:],
        'Predicted': predictions[-5:]
    })
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(comparison_df['Date'], comparison_df['Actual'], label='Actual', marker='o')
    ax.plot(comparison_df['Date'], comparison_df['Predicted'], label='Predicted', marker='x')
    plt.xticks(rotation=45)
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("Could not generate historical comparison")






# Tabular Display of Predictions vs Actuals
st.subheader("📋 Prediction vs Actual - Last 5 Trading Days")
comparison_df['Actual'] = comparison_df['Actual'].astype(float)
comparison_df['Predicted'] = comparison_df['Predicted'].astype(float)



st.dataframe(comparison_df.style.format({'Actual': '₹{:.2f}', 'Predicted': '₹{:.2f}'}))
