from pricing import black_scholes, delta, gamma, theta, vega, rho, implied_volatility, straddle_price
import numpy as np

def test_call_price():
    price = black_scholes(100, 100, 1, 0.05, 0.2, 'call')
    assert abs(price - 10.4506) < 0.001

def test_put_price():
    price = black_scholes(100, 100, 1, 0.05, 0.2, 'put')
    assert abs(price - 5.5735) < 0.001

def test_put_call_parity():
    S, K, T, r, sigma = 110, 100, 1, 0.05, 0.2
    call = black_scholes(S, K, T, r, sigma, 'call')
    put = black_scholes(S, K, T, r, sigma, 'put')
    assert abs((call - put) - (S-K*np.exp(-r*T))) < 1e-10

def test_delta_call():
    S, K, T, r, sigma = 110, 100, 1, 0.05, 0.2
    h = 0.01
    analytical = delta(S, K, T, r, sigma, 'call')
    numerical = (black_scholes(S+h,K, T, r, sigma, 'call')-black_scholes(S-h,K, T, r, sigma, 'call'))/(2*h)
    assert abs(analytical - numerical) < 1e-4

def test_delta_put():
    S, K, T, r, sigma = 110, 100, 1, 0.05, 0.2
    h = 0.01
    analytical = delta(S, K, T, r, sigma, 'put')
    numerical = (black_scholes(S+h,K, T, r, sigma, 'put')-black_scholes(S-h,K, T, r, sigma, 'put'))/(2*h)
    assert abs(analytical - numerical) < 1e-4    

def test_gamma():
    S, K, T, r, sigma = 110, 100, 1, 0.05, 0.2
    h = 0.01
    analytical = gamma(S, K, T, r, sigma)
    numerical = ((delta(S+h, K, T, r, sigma, 'call') - delta(S-h, K, T, r, sigma, 'call'))/(2*h))
    assert abs (analytical - numerical) < 1e-4

def test_theta_call():
    S, K, T, r, sigma = 110, 100, 1, 0.05, 0.2
    h = 0.01
    analytical = theta(S, K, T, r, sigma, "call")
    numerical = -(black_scholes(S,K, T+h, r, sigma, 'call')-black_scholes(S,K, T-h, r, sigma, 'call'))/(2*h)
    assert abs(analytical - (numerical/365)) < 1e-3

def test_theta_put():
    S, K, T, r, sigma = 110, 100, 1, 0.05, 0.2
    h = 0.01
    analytical = theta(S, K, T, r, sigma, "put")
    numerical = -(black_scholes(S,K, T+h, r, sigma, 'put')-black_scholes(S,K, T-h, r, sigma, 'put'))/(2*h)
    assert abs(analytical - (numerical/365)) < 1e-3

def test_vega():
    S, K, T, r, sigma = 110, 100, 1, 0.05, 0.2
    h = 0.01
    analytical = vega(S, K, T, r, sigma)
    numerical = (black_scholes(S,K, T, r, sigma+h, 'call')-black_scholes(S,K, T, r, sigma-h, 'call'))/(2*h)
    assert abs(analytical - numerical/100) < 1e-3

def test_rho_call():
    S, K, T, r, sigma = 110, 100, 1, 0.05, 0.2
    h = 0.01
    analytical = rho(S, K, T, r, sigma, 'call')
    numerical = (black_scholes(S,K, T, r+h, sigma, 'call')-black_scholes(S,K, T, r-h, sigma, 'call'))/(2*h)
    assert abs(analytical - numerical/100) < 1e-3

def test_rho_put():
    S, K, T, r, sigma = 110, 100, 1, 0.05, 0.2
    h = 0.01
    analytical = rho(S, K, T, r, sigma, 'put')
    numerical = (black_scholes(S,K, T, r+h, sigma, 'put')-black_scholes(S,K, T, r-h, sigma, 'put'))/(2*h)
    assert abs(analytical - numerical/100) < 1e-3

def test_implied_volatility_roundtrip():
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    price = black_scholes(S, K, T, r, sigma, 'call')
    iv = implied_volatility(price, S, K, T, r, 'call')
    assert abs(iv - sigma) < 1e-6

def test_straddle_price():
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    expected = black_scholes(S, K, T, r, sigma, 'call') + black_scholes(S, K, T, r, sigma, 'put')
    assert abs(straddle_price(S, K, T, r, sigma) - expected) < 1e-10