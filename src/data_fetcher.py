"""Fetch stock and macro data from Yahoo Finance, cache to CSV."""

import os
from pathlib import Path

import pandas as pd
import yfinance as yf

from src.config import DATA_DIR, DATA_START, MACRO_TICKERS, SYMBOLS


def _csv_path(symbol: str) -> Path:
    return Path(DATA_DIR) / f"{symbol.replace('^', '')}.csv"


def fetch_symbol(symbol: str, start: str = DATA_START, force: bool = False) -> pd.DataFrame:
    """Download OHLCV for one symbol. Uses CSV cache unless force=True."""
    path = _csv_path(symbol)
    if path.exists() and not force:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        # Incremental update: fetch only new rows
        last_date = df.index[-1]
        new = yf.download(symbol, start=last_date + pd.Timedelta(days=1), progress=False, auto_adjust=True)
        if not new.empty:
            # Flatten multi-level columns if present
            if isinstance(new.columns, pd.MultiIndex):
                new.columns = new.columns.get_level_values(0)
            df = pd.concat([df, new]).loc[~pd.concat([df, new]).index.duplicated(keep="last")]
            df.to_csv(path)
        return df

    os.makedirs(DATA_DIR, exist_ok=True)
    df = yf.download(symbol, start=start, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.to_csv(path)
    return df


def fetch_all(force: bool = False) -> dict[str, pd.DataFrame]:
    """Fetch all target symbols + macro tickers."""
    data = {}
    all_tickers = {s: s for s in SYMBOLS} | MACRO_TICKERS
    for name, ticker in all_tickers.items():
        print(f"  Fetching {name} ({ticker})...")
        data[name] = fetch_symbol(ticker, force=force)
    return data


if __name__ == "__main__":
    print("Fetching all data...")
    result = fetch_all(force=True)
    for name, df in result.items():
        print(f"  {name}: {len(df)} rows, {df.index[0].date()} ~ {df.index[-1].date()}")
