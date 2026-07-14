import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from pricing import black_scholes, delta, gamma, theta, vega, rho, implied_volatility
import yfinance as yf
from datetime import datetime

st.title("Options Pricer")
S = st.sidebar.slider("S", 50,150,100)
K = st.sidebar.slider("K", 50,150,100)
T = st.sidebar.slider("T", 0.01,2.0,1.0)
r = st.sidebar.slider("r", 0.0,0.1,0.05)
sigma = st.sidebar.slider("sigma", 0.05,1.0,0.2)
st.write("Call price:", black_scholes(S, K, T, r, sigma, 'call'))
st.write("Put price:", black_scholes(S, K, T, r, sigma, 'put'))

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Delta", round(delta(S, K, T, r, sigma, 'call'), 4))
col2.metric("Gamma", round(gamma(S, K, T, r, sigma), 4))
col3.metric("Theta", round(theta(S, K, T, r, sigma, 'call'), 4))
col4.metric("Vega", round(vega(S, K, T, r, sigma), 4))
col5.metric("Rho", round(rho(S, K, T, r, sigma, 'call'), 4))

stock_range = np.linspace(50, 150, 100)
fig, ax = plt.subplots()
ax.plot(stock_range, black_scholes(stock_range, K, T, r, sigma, 'call'))
ax.set_xlabel('Stock Price')
ax.set_ylabel('Call Price')
st.pyplot(fig)

ticker_symbol = st.text_input("Ticker", "AAPL")

@st.cache_data
def get_smile_data(symbol):
    ticker = yf.Ticker(symbol)
    S = ticker.history(period='1d')['Close'].iloc[-1]
    expiry_date = ticker.options[5]
    chain = ticker.option_chain(expiry_date)

    #Time Calculation
    dates = datetime.strptime(expiry_date, '%Y-%m-%d')
    current_date = datetime.now()
    T = (dates - current_date).days/365
    return S, chain.calls, T

S, calls, T_smile = get_smile_data(ticker_symbol)
strikes, ivs = [], []
r = 0.05
for i in range(len(calls)):
    K = calls['strike'].iloc[i]
    bid = calls['bid'].iloc[i]
    ask = calls['ask'].iloc[i]
    if bid > 0 and ask > 0:
        market_price = (bid + ask) / 2
    else:
        market_price = calls['lastPrice'].iloc[i]
    if market_price == 0 or market_price != market_price:
        continue
    try:
        iv = implied_volatility(market_price, S, K, T_smile, r, option_type='call')
        strikes.append(K)
        ivs.append(iv)
    except:
        continue

fig, ax = plt.subplots()
ax.plot(strikes, ivs)
ax.set_xlabel('Strike Price')
ax.set_ylabel('Implied Volatility')
st.pyplot(fig)

