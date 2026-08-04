import numpy as np
from pricing import black_scholes, delta, theta, gamma, straddle_price
import matplotlib.pyplot as plt

def simulate_path(S0, mu, sigma, T, steps):
    prices  = np.zeros(steps + 1)
    prices[0] = S0

    for i in range(1, steps + 1):
       prices[i] = prices[i-1] * np.exp((mu - (sigma**2/2))*T/steps + sigma*np.sqrt(T/steps)*np.random.standard_normal())
        
    return prices

def simulate_paths(S0, mu, sigma, T, steps, n_paths):
    dt = T/steps
    Z = np.random.standard_normal((n_paths, steps))
    log_returns = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    yearsum = np.cumsum(log_returns, axis=1)
    St = S0 * np.exp(yearsum)
    start_column = np.full((n_paths, 1), S0)
    paths = np.hstack([start_column, St])
    return paths


def simulate_hedge(path, K, T, r, sigma_implied, steps):
    dt = T/steps
    cash = 0
    current_price = black_scholes(path[0], K, T, r, sigma_implied)
    cash = cash + current_price
    current_delta = delta(path[0], K, T, r, sigma_implied)
    cash = cash - (current_delta *path[0])

    for i in range(1, steps):
        tau = T - (i *dt)
        cash = cash * np.exp(r * dt)
        new_delta = delta(path[i], K, tau, r, sigma_implied)
        cash = cash - (new_delta - current_delta)*path[i]
        current_delta = new_delta

    cash = cash * np.exp(r * dt)
    cash = cash + (current_delta * path[-1])
    cash = cash - max(path[-1] - K, 0)

    return cash

def simulate_hedge_vec(paths, K, T, r, sigma_implied, steps):
    dt = T/steps
    current_price = black_scholes(paths[:,0], K, T, r, sigma_implied)
    cash = current_price
    current_delta = delta(paths[:,0], K, T, r, sigma_implied)
    cash = cash - (current_delta * paths[:,0])

    for i in range(1, steps):
        tau = T - (i*dt)
        cash = cash * np.exp(r * dt)
        new_delta = delta(paths[:,i], K, tau, r, sigma_implied)
        cash = cash - (new_delta - current_delta)*paths[:,i]
        current_delta = new_delta
    
    cash = cash * np.exp(r * dt)
    cash = cash + (current_delta * paths[:,-1])
    cash = cash - np.maximum(paths[:,-1] - K, 0)

    return cash

def attribute_pnl(path, K, T, r, sigma_implied, steps):
    dt = T / steps
    theta_total = 0
    gamma_total = 0
    for i in range(1, steps):
        tau = T - (i *dt)
        theta_total = theta_total - theta(path[i], K, tau, r, sigma_implied)
        dS = path[i] - path[i-1]
        gamma_total = gamma_total - (0.5 * gamma(path[i], K, tau, r, sigma_implied) * dS**2)
    return theta_total, gamma_total

def hedge_straddle(prices, K, r, sigma_implied, T):
    steps = len(prices)-1
    dt = T/steps
    cash = straddle_price(prices[0], K, T, r, sigma_implied)
    call_delta = delta(prices[0], K, T, r, sigma_implied, 'call')
    put_delta = delta(prices[0], K, T, r, sigma_implied, 'put')
    current_delta = call_delta + put_delta
    cash = cash - (current_delta * prices[0])

    for i in range(1, steps):
        tau = T - (i*dt)
        cash = cash * np.exp(r * dt)
        new_call_delta = delta(prices[i], K, tau, r, sigma_implied, 'call')
        new_put_delta = delta(prices[i], K, tau, r, sigma_implied, 'put')
        new_delta = new_put_delta + new_call_delta
        cash = cash - (new_delta - current_delta)*prices[i]
        current_delta = new_delta
    
    cash = cash * np.exp(r*dt)
    cash = cash + (current_delta * prices[-1])
    cash = cash - np.maximum(prices[-1] - K, 0) - np.maximum(K - prices[-1], 0)

    return cash






if __name__ == "__main__":

    pnls_15 = simulate_hedge_vec(simulate_paths(100, 0.0, 0.15, 1.0, 252, 1000), 100, 1.0, 0.05, 0.2, 252)
    pnls_20 = simulate_hedge_vec(simulate_paths(100, 0.0, 0.20, 1.0, 252, 1000), 100, 1.0, 0.05, 0.2, 252)
    pnls_25 = simulate_hedge_vec(simulate_paths(100, 0.0, 0.25, 1.0, 252, 1000), 100, 1.0, 0.05, 0.2, 252)

    plt.hist(pnls_15, bins=50, alpha=0.5, label="realised 0.15")
    plt.hist(pnls_20, bins=50, alpha=0.5, label="realised 0.20")
    plt.hist(pnls_25, bins=50, alpha=0.5, label="realised 0.25")
    
    plt.axvline(0, color="black", linestyle="--")
    plt.xlabel("P&L")
    plt.ylabel("frequency")
    plt.title("Hedged P&L: implied 0.20 vs realised vol")
    plt.legend()
    plt.savefig("pnl_histogram.png", dpi=150, bbox_inches="tight")
    plt.show()

    theta_totals = []
    gamma_totals = []
    for _ in range(1000):
        th, ga = attribute_pnl(simulate_path(100, 0.0, 0.20, 1.0, 252), 100, 1.0, 0.05, 0.2, 252)
        theta_totals.append(th)
        gamma_totals.append(ga)

    print("mean theta collected:", np.mean(theta_totals))
    print("mean gamma paid:", np.mean(gamma_totals))
    print("mean net:", np.mean(theta_totals) + np.mean(gamma_totals))