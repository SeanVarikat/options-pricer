import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from black_scholes import black_scholes, delta, gamma, theta, vega, rho, implied_volatility

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