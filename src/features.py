"""Feature engineering: technical indicators + macro factors."""

import pandas as pd
import numpy as np
import ta

from src.config import (
    SMA_WINDOWS, EMA_WINDOWS, RSI_WINDOW, ATR_WINDOW, BB_WINDOW,
    VOLUME_MA_WINDOW, FORWARD_DAYS, MACRO_TICKERS,
)
from src.data_fetcher import fetch_symbol


def add_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicator features to a price DataFrame."""
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # --- Trend ---
    for w in SMA_WINDOWS:
        df[f"SMA_{w}"] = ta.trend.sma_indicator(close, window=w)
        df[f"Close_SMA_{w}_ratio"] = close / df[f"SMA_{w}"]

    for w in EMA_WINDOWS:
        df[f"EMA_{w}"] = ta.trend.ema_indicator(close, window=w)

    macd = ta.trend.MACD(close)
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    df["MACD_hist"] = macd.macd_diff()

    # --- Momentum ---
    df["RSI"] = ta.momentum.rsi(close, window=RSI_WINDOW)

    stoch = ta.momentum.StochasticOscillator(high, low, close)
    df["Stoch_K"] = stoch.stoch()
    df["Stoch_D"] = stoch.stoch_signal()

    df["ROC_5"] = ta.momentum.roc(close, window=5)
    df["ROC_10"] = ta.momentum.roc(close, window=10)
    df["Williams_R"] = ta.momentum.williams_r(high, low, close)

    # Daily and 5-day returns
    df["Return_1d"] = close.pct_change()
    df["Return_5d"] = close.pct_change(5)

    # --- Volatility ---
    bb = ta.volatility.BollingerBands(close, window=BB_WINDOW)
    df["BB_high"] = bb.bollinger_hband()
    df["BB_low"] = bb.bollinger_lband()
    df["BB_pct"] = bb.bollinger_pband()

    df["ATR"] = ta.volatility.average_true_range(high, low, close, window=ATR_WINDOW)
    df["Volatility_20d"] = close.pct_change().rolling(20).std()

    # --- Volume ---
    df["OBV"] = ta.volume.on_balance_volume(close, volume)
    df["Volume_ratio"] = volume / volume.rolling(VOLUME_MA_WINDOW).mean()

    # --- Time features ---
    df["DayOfWeek"] = df.index.dayofweek
    df["Month"] = df.index.month

    return df


def add_macro_features(df: pd.DataFrame) -> pd.DataFrame:
    """Merge macro/cross-asset factors into the feature DataFrame."""
    for name, ticker in MACRO_TICKERS.items():
        macro_df = fetch_symbol(ticker)
        prefix = name.replace("^", "")

        # Use Close price, rename to avoid collision
        macro_series = macro_df["Close"].rename(f"{prefix}_Close")
        df = df.join(macro_series, how="left")
        df[f"{prefix}_Close"] = df[f"{prefix}_Close"].ffill()

        # Rate of change
        df[f"{prefix}_ROC_5"] = df[f"{prefix}_Close"].pct_change(5)

    # Cross-asset: QQQ relative strength vs SPY
    if "SPY_Close" in df.columns:
        qqq_close = fetch_symbol("QQQ")["Close"]
        qqq_aligned = qqq_close.reindex(df.index).ffill()
        df["QQQ_SPY_ratio"] = qqq_aligned / df["SPY_Close"]

    return df


def build_features(symbol: str) -> tuple[pd.DataFrame, pd.Series]:
    """Build full feature matrix X and target y for a symbol.

    Target: 1 if cumulative return over next FORWARD_DAYS > 0, else 0.
    """
    df = fetch_symbol(symbol).copy()

    # Add features
    df = add_technical_features(df)
    df = add_macro_features(df)

    # Target variable (forward-looking — no leakage because we shift)
    forward_return = df["Close"].pct_change(FORWARD_DAYS).shift(-FORWARD_DAYS)
    df["Target"] = (forward_return > 0).astype(int)

    # Drop rows where target is NaN (last FORWARD_DAYS rows)
    df = df.dropna(subset=["Target"])

    # Drop raw OHLCV + intermediate columns (keep only features)
    drop_cols = ["Open", "High", "Low", "Close", "Volume"]
    # Also drop raw SMA/EMA values (keep ratios)
    drop_cols += [f"SMA_{w}" for w in SMA_WINDOWS]
    drop_cols += [f"EMA_{w}" for w in EMA_WINDOWS]
    drop_cols += ["BB_high", "BB_low", "OBV"]  # Keep BB_pct instead

    feature_cols = [c for c in df.columns if c not in drop_cols + ["Target"]]

    X = df[feature_cols].copy()
    y = df["Target"].copy()

    # Drop any remaining NaN rows (from indicator warm-up period)
    mask = X.notna().all(axis=1)
    X = X[mask]
    y = y[mask]

    return X, y


if __name__ == "__main__":
    for sym in ["QQQ", "GOOGL", "PLTR"]:
        X, y = build_features(sym)
        print(f"{sym}: {X.shape[0]} samples, {X.shape[1]} features, "
              f"target ratio={y.mean():.2%} bullish")
