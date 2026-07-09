# Options Pricer

A Python options pricing tool implementing the Black-Scholes model, built from scratch to develop a practical understanding of derivatives pricing and risk sensitivities.

## Features

- European call and put pricing using the Black-Scholes model
- All five Greeks: delta, gamma, theta, vega, rho
- Implied volatility extraction from market prices using a Brent root-finder
- Live volatility smile construction from real option chain data (yfinance)
- Interactive Streamlit dashboard with real-time pricing and Greeks

## How to run

pip install -r requirements.txt
streamlit run app.py

## Built with

Python, NumPy, SciPy, Matplotlib, yfinance, Streamlit

## What I learned

Building this from first principles gave me a working understanding of how option prices respond to their inputs, why the Greeks matter for risk management, and how implied volatility is extracted from market prices in practice. Plotting the volatility smile from live market data made clear where the Black-Scholes assumptions break down in real markets.