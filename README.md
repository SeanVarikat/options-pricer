# Options Pricer

![tests](https://github.com/SeanVarikat/options-pricer/actions/workflows/tests.yml/badge.svg)

A Python options pricing tool implementing the Black-Scholes model, built from scratch to develop a practical understanding of derivatives pricing and risk sensitivities.

## Features

- European call and put pricing using the Black-Scholes model
- All five Greeks: delta, gamma, theta, vega, rho
- Implied volatility extraction from market prices using a Brent root-finder
- Live volatility smile construction from real option chain data (yfinance)
- Interactive Streamlit dashboard with real-time pricing and Greeks
- Pytest suite validating all Greeks against finite-difference approximations (100% coverage)
- Continuous integration via GitHub Actions

## How to run

pip install -r requirements.txt
streamlit run app.py

## Built with

Python, NumPy, SciPy, Matplotlib, yfinance, Streamlit

## What I learned

Building this from first principles gave me a working understanding of how option prices respond to their inputs, why the Greeks matter for risk management, and how implied volatility is extracted from market prices in practice. Plotting the volatility smile from live market data made clear where the Black-Scholes assumptions break down in real markets.

## Delta-Hedging Simulator

A Monte Carlo simulation of the classic short-volatility trade: sell an
option, hedge away its directional risk, and profit (or lose) purely on the
gap between the volatility you sold at and the volatility the market actually
delivers.

### What it does

`hedging.py` simulates a market maker who sells a call option and hedges it
daily. The option is *priced* at an assumed **implied volatility**, while the
underlying stock path is *generated* at a separate **realised volatility** —
letting us ask the central question of options market-making: what happens
when the world moves more, or less, than the price implied?

- **`simulate_path`** — generates a stock price path using geometric Brownian
  motion.
- **`simulate_hedge`** — sells one call, buys the delta hedge, then rebalances
  the hedge every day as the price and time-to-expiry change, tracking cash
  (including interest) through to expiry. Returns the final P&L.
- **`attribute_pnl`** — decomposes the P&L into its two opposing drivers:
  theta (time-decay income) and gamma (the cost of rehedging).

### Key result

Running 1,000 simulated paths for each scenario, with implied volatility
fixed at 20%:

| Realised vol | Mean P&L | Interpretation                          |
|--------------|----------|-----------------------------------------|
| 15%          | +1.97    | Sold vol high, market stayed calm → win |
| 20%          | ~0.00    | Fairly priced → break-even              |
| 25%          | −1.99    | Sold vol low, market was wild → loss    |

![P&L distributions](pnl_histogram.png)

The three distributions sit cleanly left, on, and right of zero. The P&L is
approximately **vega × (implied − realised)**, which the simulation
reproduces from first principles. The loss distribution is wider and more
negatively skewed than the win distribution — the signature risk profile of
short-volatility strategies: frequent small gains, occasional large losses.

### Why direction doesn't matter

Because the position is delta-hedged, the *direction* of each move is cancelled
out — only the *size* of moves matters. This is why P&L depends on realised
**volatility**, not realised return: a stock that swings wildly but ends flat
still generates large hedging costs. The gamma term makes this explicit — the
cost of each move scales with the square of the price change, stripping out its
sign.

### P&L attribution

For the break-even case (realised = implied = 20%), the simulator confirms the
P&L is the near-cancellation of two large forces:

- Theta collected: **+4.39** (time-decay income banked for being short)
- Gamma paid:      **−3.82** (buy-high/sell-low cost of rehedging)

The small residual reflects higher-order terms and interest not captured by the
first-order attribution.