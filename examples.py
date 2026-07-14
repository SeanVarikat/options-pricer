import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime
from pricing import black_scholes, delta, theta, vega, implied_volatility


if __name__ == "__main__":
    stock_prices = np.linspace(50, 150, 100)
    call_prices = black_scholes(stock_prices, 100, 1, 0.05, 0.2)
    plt.plot(stock_prices, call_prices)
    plt.xlabel('Stock Price')
    plt.ylabel('Option Price')
    plt.title('Call Option Price vs Stock Price')
    plt.show()

    plt.plot(stock_prices, delta(stock_prices, 100, 1, 0.05, 0.2))
    plt.xlabel('Stock Price')
    plt.ylabel('Delta')
    plt.title('Delta vs Stock Price')
    plt.show()

    time_values = np.linspace(0.01, 1, 100)
    plt.plot(time_values, theta(100, 100, time_values, 0.05, 0.2))
    plt.xlabel('Time')
    plt.ylabel('Theta')
    plt.title('Theta vs Time')
    plt.show()

    sigma_values = np.linspace(0.05, 0.6, 100)
    plt.plot(sigma_values, vega(100, 100, 1, 0.05, sigma_values))
    plt.xlabel('Volatility')
    plt.ylabel('Vega')
    plt.title('Vega vs Volatility')
    plt.show()

    ticker = yf.Ticker('AAPL')
    S = ticker.history(period='1d')['Close'].iloc[-1]
    expiry_date = ticker.options[5]
    chain = ticker.option_chain(expiry_date)

    #Time Calculation
    dates = datetime.strptime(expiry_date, '%Y-%m-%d')
    current_date = datetime.now()
    T = (dates - current_date).days/365

    strikes, ivs = [], []
    r = 0.05
    for i in range(len(chain.calls)):
        K = chain.calls['strike'].iloc[i]
        market_price = (chain.calls['bid'].iloc[i] + chain.calls['ask'].iloc[i]) / 2
        if market_price == 0:
            continue
        try:
            iv = implied_volatility(market_price, S, K, T, r, option_type='call')
            strikes.append(K)
            ivs.append(iv)
        except:
            continue

    plt.plot(strikes, ivs)
    plt.xlabel('Strike')
    plt.ylabel('Implied Volatility')
    plt.title('Strike vs Implied Vol')
    plt.show()