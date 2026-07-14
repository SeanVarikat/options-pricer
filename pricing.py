import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq

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
