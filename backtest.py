import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hedging import hedge_straddle

sp500 = yf.download("^GSPC", start="2005-01-01")
vix = yf.download("^VIX", start="2005-01-01")

sp500_close = sp500["Close"]
vix_close = vix["Close"]
returns = sp500_close.pct_change()
cost = 0.00001
realised_vol = returns.rolling(21).std() * np.sqrt(252) * 100
data = pd.concat([vix_close, realised_vol, sp500_close], axis=1)
data.columns = ["implied", "realised", "price"]
data = data.dropna()
data["daily_var"] = returns**2
data["gap"] = data["implied"] - data["realised"]
data["signal"] = data['gap'] > 0.50
data["daily_pnl"] = (((data["implied"]/100)**2)/252) - data["daily_var"]
data["strategy_pnl"] = data["daily_pnl"] * data["signal"] - (data["signal"] * cost)
data["cumulative"] = data["strategy_pnl"].cumsum()
data['running_peak'] = data["cumulative"].cummax()
data["drawdown"] = data["cumulative"] - data["running_peak"]


in_sample = data.loc[data.index < "2015-01-01"].copy()
out_sample = data.loc[data.index >= "2015-01-01"].copy()

for threshold in [0.5, 1.0, 1.5]:
    in_sample["signal"] = in_sample['gap'] > threshold
    in_sample["strategy_pnl"] = in_sample["daily_pnl"] * in_sample["signal"] - (in_sample["signal"] * cost)
    cumulative_return = in_sample["strategy_pnl"].cumsum()
    print(cumulative_return.iloc[-1])

out_sample["signal"] = out_sample["gap"] > 0.5
out_sample["strategy_pnl"] = out_sample["daily_pnl"] * out_sample["signal"] - (out_sample["signal"] * cost)
cumulative_return_out = out_sample["strategy_pnl"].cumsum()
print(cumulative_return_out.iloc[-1])

total_return = data["cumulative"].iloc[-1]
max_drawdown = data["drawdown"].min()

print("total return:", total_return)
print("max drawdown:,", max_drawdown)

data["cumulative"].plot()
plt.xlabel("Date")
plt.ylabel("Cumulative P&L (variance units)")
plt.title("Short-vol strategy: cumulative P&L")
plt.savefig("backtest_equity.png", dpi=150, bbox_inches="tight")
plt.show()

months = data.groupby(data.index.to_period("M"))

trade_pnls = []
for period, group in months:
    if group["signal"].iloc[0] == True and len(group) > 1:
        path = group["price"].values
        K = path[0]
        sigma_implied = (group["implied"].iloc[0]/100)
        T = (len(group)/252)
        trade_pnls.append(hedge_straddle(path, K, 0.05, sigma_implied, T))

print("number of trades:", len(trade_pnls))
print("total P&L:", sum(trade_pnls))
print("worst trade:", min(trade_pnls))
print("number of losing trades:", sum(1 for p in trade_pnls if p < 0))

sharpe = (np.mean(trade_pnls) / np.std(trade_pnls)) * np.sqrt(12)
print("Sharpe ratio =", sharpe)
equity = np.cumsum(trade_pnls)
plt.plot(equity)
plt.xlabel("Trade number")
plt.ylabel("Cumulative P&L (S&P index points)")
plt.title("Straddle-hedge backtest: cumulative P&L")
plt.savefig("backtest_integrated.png", dpi=150, bbox_inches="tight")
plt.show()
