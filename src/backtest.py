"""Backtesting engine: simulate trading based on model predictions."""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from src.config import MODEL_DIR, FORWARD_DAYS, VAL_END
from src.data_fetcher import fetch_symbol


def run_backtest(symbol: str) -> dict:
    """Run backtest on test period using saved model predictions.

    Strategy:
        - Ensemble probability > 0.6 → full position
        - 0.5 < probability <= 0.6 → half position
        - probability <= 0.5 → no position (cash)

    Rebalance every FORWARD_DAYS trading days.
    """
    model_path = Path(MODEL_DIR) / f"{symbol}_models.pkl"
    result = joblib.load(model_path)

    models = result["models"]
    weights = result["weights"]
    scaler = result["scaler"]
    feature_names = result["feature_names"]

    # Get full feature matrix and price data
    from src.features import build_features
    X, y = build_features(symbol)
    price_df = fetch_symbol(symbol)

    # Test period only
    test_mask = X.index > VAL_END
    X_test = X[test_mask]

    if len(X_test) == 0:
        return {"error": "No test data available"}

    # Generate predictions for each test date
    X_scaled = scaler.transform(X_test)
    ensemble_proba = np.zeros(len(X_test))
    for name, model in models.items():
        ensemble_proba += weights[name] * model.predict_proba(X_scaled)[:, 1]

    # Align prices with test dates
    test_dates = X_test.index
    prices = price_df["Close"].reindex(test_dates).ffill()

    # Simulate trading
    cash = 10000.0
    position = 0.0  # number of shares
    portfolio_values = []
    buy_hold_values = []
    trade_log = []

    initial_price = prices.iloc[0]
    buy_hold_shares = cash / initial_price

    rebalance_counter = 0

    for i, (date, prob) in enumerate(zip(test_dates, ensemble_proba)):
        price = prices.iloc[i]
        current_value = cash + position * price
        portfolio_values.append({"date": date, "value": current_value})
        buy_hold_values.append({"date": date, "value": buy_hold_shares * price})

        # Rebalance every FORWARD_DAYS
        rebalance_counter += 1
        if rebalance_counter >= FORWARD_DAYS or i == 0:
            rebalance_counter = 0

            if prob > 0.6:
                target_pct = 1.0
            elif prob > 0.5:
                target_pct = 0.5
            else:
                target_pct = 0.0

            target_value = current_value * target_pct
            target_shares = target_value / price if price > 0 else 0
            delta_shares = target_shares - position

            if abs(delta_shares) > 0.01:
                # Apply simple transaction cost (0.1%)
                cost = abs(delta_shares * price) * 0.001
                cash -= delta_shares * price + cost
                position = target_shares
                trade_log.append({
                    "date": date,
                    "action": "BUY" if delta_shares > 0 else "SELL",
                    "shares": abs(delta_shares),
                    "price": price,
                    "prob": prob,
                    "target_pct": target_pct,
                })

    # Calculate metrics
    pf = pd.DataFrame(portfolio_values).set_index("date")
    bh = pd.DataFrame(buy_hold_values).set_index("date")

    strategy_returns = pf["value"].pct_change().dropna()
    bh_returns = bh["value"].pct_change().dropna()

    total_return = (pf["value"].iloc[-1] / pf["value"].iloc[0]) - 1
    bh_total_return = (bh["value"].iloc[-1] / bh["value"].iloc[0]) - 1

    # Annualize (approximate)
    n_days = len(pf)
    annual_factor = 252 / max(n_days, 1)
    annual_return = (1 + total_return) ** annual_factor - 1
    bh_annual_return = (1 + bh_total_return) ** annual_factor - 1

    # Sharpe ratio (annualized, risk-free = 0.05)
    if strategy_returns.std() > 0:
        sharpe = (strategy_returns.mean() * 252 - 0.05) / (strategy_returns.std() * np.sqrt(252))
    else:
        sharpe = 0.0

    # Max drawdown
    cummax = pf["value"].cummax()
    drawdown = (pf["value"] - cummax) / cummax
    max_drawdown = drawdown.min()

    # Win rate (of trades)
    wins = sum(1 for t in trade_log if t["action"] == "BUY")
    total_trades = len(trade_log)

    return {
        "symbol": symbol,
        "total_return": total_return,
        "annual_return": annual_return,
        "max_drawdown": max_drawdown,
        "sharpe": sharpe,
        "n_trades": total_trades,
        "bh_total_return": bh_total_return,
        "bh_annual_return": bh_annual_return,
        "portfolio_values": pf,
        "buy_hold_values": bh,
        "trade_log": trade_log,
    }


if __name__ == "__main__":
    from src.config import SYMBOLS

    for sym in SYMBOLS:
        bt = run_backtest(sym)
        if "error" in bt:
            print(f"{sym}: {bt['error']}")
            continue
        print(f"\n{sym} Backtest Results:")
        print(f"  Strategy return: {bt['total_return']:.2%}")
        print(f"  Buy & Hold return: {bt['bh_total_return']:.2%}")
        print(f"  Annualized return: {bt['annual_return']:.2%}")
        print(f"  Max drawdown: {bt['max_drawdown']:.2%}")
        print(f"  Sharpe ratio: {bt['sharpe']:.2f}")
        print(f"  Number of trades: {bt['n_trades']}")
