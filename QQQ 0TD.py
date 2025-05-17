
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime

def fetch_intraday_data(symbol='QQQ', interval='1m', period='1d'):
    df = yf.download(tickers=symbol, interval=interval, period=period, progress=False)
    df.dropna(inplace=True)
    return df

def add_indicators(df):
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    df['EMA_9'] = ta.trend.EMAIndicator(close=df['Close'], window=9).ema_indicator()
    df['EMA_21'] = ta.trend.EMAIndicator(close=df['Close'], window=21).ema_indicator()
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low']) / 2).cumsum() / df['Volume'].cumsum()
    return df

def generate_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if last['RSI'] > 70 and last['Close'] < last['EMA_9'] and last['Close'] < last['VWAP']:
        return \"🔻 PUT Entry Signal (Overbought + Breakdown)\"
    elif last['RSI'] < 30 and last['Close'] > last['EMA_9'] and last['Close'] > last['VWAP']:
        return \"🔺 CALL Entry Signal (Oversold + Reversal)\"
    elif prev['RSI'] < 30 and last['RSI'] > 30:
        return \"⏫ Momentum Buy Signal — RSI Bullish Crossover\"
    elif prev['RSI'] > 70 and last['RSI'] < 70:
        return \"⏬ Momentum Fade Signal — RSI Bearish Crossover\"
    else:
        return \"⏸️ No High-Probability Entry Detected\"

st.set_page_config(page_title=\"QQQ 0DTE Trade Signal\", layout=\"centered\")
st.title(\"📈 QQQ 0DTE Trade Signal Dashboard\")
st.markdown(\"Live trade signal analysis using RSI, EMA, and VWAP\")

with st.spinner(\"Fetching latest QQQ data...\"):
    df = fetch_intraday_data()
    df = add_indicators(df)
    signal = generate_signal(df)
    now = datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")

st.metric(label=\"Last Updated\", value=now)
st.subheader(\"Current Trade Signal\")
st.success(signal)

st.line_chart(df[['Close', 'EMA_9', 'EMA_21', 'VWAP']].dropna().tail(100))
st.caption(\"Data: Yahoo Finance (1-minute interval)\")

