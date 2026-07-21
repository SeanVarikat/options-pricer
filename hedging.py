import numpy as np
from pricing import black_scholes, delta, theta, gamma
import matplotlib.pyplot as plt

def simulate_path(S0, mu, sigma, T, steps):
    prices  = np.zeros(steps + 1)
    prices[0] = S0

    for i in range(1, steps + 1):
       prices[i] = prices[i-1] * np.exp((mu - (sigma**2/2))*T/steps + sigma*np.sqrt(T/steps)*np.random.standard_normal())
        
    return prices

def simulate_hedge(S0, K, T, r, sigma_implied, sigma_realised, steps):
    dt = T/steps
    cash = 0
    path = simulate_path(S0, 0.0, sigma_realised, T, steps)
    current_price = black_scholes(S0, K, T, r, sigma_implied)
    cash = cash + current_price
    current_delta = delta(S0, K, T, r, sigma_implied)
    cash = cash - (current_delta * S0)

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

def attribute_pnl(S0, K, T, r, sigma_implied, sigma_realised, steps):
    dt = T / steps
    path = simulate_path(S0, 0.0, sigma_realised, T, steps)
    theta_total = 0
    gamma_total = 0
    for i in range(1, steps):
        tau = T - (i *dt)
        theta_total = theta_total - theta(path[i], K, tau, r, sigma_implied)
        dS = path[i] - path[i-1]
        gamma_total = gamma_total - (0.5 * gamma(path[i], K, tau, r, sigma_implied) * dS**2)
    return theta_total, gamma_total




if __name__ == "__main__":
    pnls_15 = [simulate_hedge(100, 100, 1.0, 0.05, 0.2, 0.15, 252) for _ in range(1000)]
    pnls_20 = [simulate_hedge(100, 100, 1.0, 0.05, 0.2, 0.20, 252) for _ in range(1000)]
    pnls_25 = [simulate_hedge(100, 100, 1.0, 0.05, 0.2, 0.25, 252) for _ in range(1000)]

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
        th, ga = attribute_pnl(100, 100, 1.0, 0.05, 0.2, 0.2, 252)
        theta_totals.append(th)
        gamma_totals.append(ga)

    print("mean theta collected:", np.mean(theta_totals))
    print("mean gamma paid:", np.mean(gamma_totals))
    print("mean net:", np.mean(theta_totals) + np.mean(gamma_totals))