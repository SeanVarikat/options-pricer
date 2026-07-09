import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from scipy.optimize import brentq
import yfinance as yf
from datetime import datetime

def compute_d1_d2(S, K, T, r, sigma):
    d1 = (np.log(S/K) + ((r + 0.5*sigma**2)*T)) / (sigma*np.sqrt(T))
    d2 = d1 - (sigma*np.sqrt(T))
    
    return d1,d2

def black_scholes(S, K, T, r, sigma, option_type="call"):
    """S - Current Stock Price, K - Strike Price, T - time to expiry in years,
    r - risk-free interest rate, sigma - volatility,
    option type - defaults 'call' unless you specify 'put'"""

    d1, d2 = compute_d1_d2(S, K, T, r, sigma)

    if option_type == 'call':
        price = S * norm.cdf(d1) - (K*np.exp(-r*T)*norm.cdf(d2))
    elif option_type == 'put':
        price = K * np.exp(-r*T) * norm.cdf(-d2) - S*norm.cdf(-d1)

    return price



def delta(S, K, T, r, sigma, option_type="call"):

    d1, d2 = compute_d1_d2(S, K, T, r, sigma)

    if option_type == 'call':
        return norm.cdf(d1)
    elif option_type == 'put':
        return norm.cdf(d1) - 1
    

def gamma(S, K, T, r, sigma):
    
    d1, d2 = compute_d1_d2(S, K, T, r, sigma)

    return norm.pdf(d1)/(S*sigma*np.sqrt(T))

def theta(S, K, T, r, sigma, option_type="call"):

    d1, d2 = compute_d1_d2(S, K, T, r, sigma)

    if option_type == 'call':
        return ((-(S*norm.pdf(d1)*sigma)/(2*np.sqrt(T)))-r*K*np.exp(-r*T)*norm.cdf(d2))/365
    elif option_type == 'put':
        return ((-(S*norm.pdf(d1)*sigma)/(2*np.sqrt(T)))+r*K*np.exp(-r*T)*norm.cdf(-d2))/365
    

def vega(S, K, T, r, sigma):

    d1, d2 = compute_d1_d2(S, K, T, r, sigma)

    return (S*norm.pdf(d1)*np.sqrt(T))/100


def rho(S, K, T, r, sigma, option_type="call"):

    d1, d2 = compute_d1_d2(S, K, T, r, sigma)

    if option_type == 'call':
        return (K*T*np.exp(-r*T)*norm.cdf(d2))/100
    elif option_type == 'put':
        return (-K*T*np.exp(-r*T)*norm.cdf(-d2))/100
    
def implied_volatility(market_price, S, K, T, r, option_type='call'):

    def helper(sigma):
        return black_scholes(S, K, T, r, sigma, option_type) - market_price
    
    return brentq(helper, 0.001, 5.0)


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

    '''Time Calculation'''
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