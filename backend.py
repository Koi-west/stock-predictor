"""FastAPI backend for Stock Predictor."""

import warnings
warnings.filterwarnings("ignore")

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from src.config import SYMBOLS, SYMBOL_NAMES, SYMBOL_CATEGORIES, MACRO_TICKERS, MODEL_DIR, DATA_DIR, FORWARD_DAYS, VAL_END
from src.data_fetcher import fetch_symbol

app = FastAPI(title="Oracle Stock Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

log = logging.getLogger("uvicorn")


@app.on_event("startup")
def refresh_data_on_startup():
    """Fetch latest market data for all symbols on server start."""
    all_tickers = SYMBOLS + list(MACRO_TICKERS.values())
    for ticker in all_tickers:
        try:
            fetch_symbol(ticker)
            log.info(f"Refreshed {ticker}")
        except Exception as e:
            log.warning(f"Failed to refresh {ticker}: {e}")


# ── Helpers ─────────────────────────────────────────────

def _model_path(symbol: str) -> Path:
    return Path(MODEL_DIR) / f"{symbol.replace('.', '_').replace('-', '_')}_models.pkl"


def _load_model(symbol: str) -> dict:
    path = _model_path(symbol)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No trained model for {symbol}. Train first via /api/train/{symbol}")
    return joblib.load(path)


def _load_prices(symbol: str) -> pd.DataFrame:
    csv_name = symbol.replace("^", "")
    path = Path(DATA_DIR) / f"{csv_name}.csv"
    if not path.exists():
        fetch_symbol(symbol)
    return pd.read_csv(path, index_col=0, parse_dates=True)


# ── Routes ──────────────────────────────────────────────

@app.get("/api/symbols")
def get_symbols():
    return {
        "categories": {
            cat: [{"symbol": sym, "name": name} for sym, name in items.items()]
            for cat, items in SYMBOL_CATEGORIES.items()
        }
    }


@app.get("/api/price/{symbol:path}")
def get_price(symbol: str, days: int = 120):
    df = _load_prices(symbol).tail(days)
    records = []
    for ts, row in df.iterrows():
        records.append({
            "time": ts.strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        })
    # Stats
    all_df = _load_prices(symbol)
    last_close = all_df["Close"].iloc[-1]
    prev_close = all_df["Close"].iloc[-2]
    change_pct = (last_close / prev_close - 1) * 100
    high_52w = all_df["Close"].tail(252).max()
    low_52w = all_df["Close"].tail(252).min()

    return {
        "data": records,
        "stats": {
            "last_close": round(last_close, 2),
            "change_pct": round(change_pct, 2),
            "high_52w": round(high_52w, 2),
            "low_52w": round(low_52w, 2),
        },
    }


@app.get("/api/model-status/{symbol:path}")
def get_model_status(symbol: str):
    """Check if a trained model exists for this symbol."""
    path = _model_path(symbol)
    return {"symbol": symbol, "trained": path.exists()}


@app.post("/api/train/{symbol:path}")
def train_symbol(symbol: str):
    """Train models for a symbol on demand."""
    from src.model import train_all_for_symbol
    try:
        result = train_all_for_symbol(symbol)
        # Save with sanitized filename
        path = _model_path(symbol)
        joblib.dump(result, path)
        return {"symbol": symbol, "status": "trained", "metrics": result["metrics"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predict/{symbol:path}")
def get_prediction(symbol: str, horizon: int = 10):
    result = _load_model(symbol)
    models = result["models"]
    weights = result["weights"]
    scaler = result["scaler"]

    from src.features import build_features
    X, _ = build_features(symbol)
    X_latest = X.iloc[[-1]]
    X_scaled = scaler.transform(X_latest)

    predictions = {}
    for name, model in models.items():
        predictions[name] = round(float(model.predict_proba(X_scaled)[:, 1][0]), 4)

    ensemble = round(sum(weights[n] * predictions[n] for n in models), 4)
    predictions["Ensemble"] = ensemble

    return {
        "symbol": symbol,
        "date": X_latest.index[0].strftime("%Y-%m-%d"),
        "direction": "bullish" if ensemble > 0.5 else "bearish",
        "ensemble": ensemble,
        "models": predictions,
        "horizon": horizon,
    }


@app.get("/api/metrics/{symbol:path}")
def get_metrics(symbol: str):
    result = _load_model(symbol)
    out = {}
    for name, m in result["metrics"].items():
        out[name] = {k: round(v, 4) for k, v in m.items()}
    return out


@app.get("/api/features/{symbol:path}")
def get_features(symbol: str, top_n: int = 12):
    result = _load_model(symbol)
    xgb = result["models"].get("XGBoost")
    if xgb is None or not hasattr(xgb, "feature_importances_"):
        return []
    fi = pd.Series(xgb.feature_importances_, index=result["feature_names"])
    fi = fi.nlargest(top_n)
    return [{"name": name, "importance": round(float(val), 4)} for name, val in fi.items()]


@app.get("/api/backtest/{symbol:path}")
def get_backtest(symbol: str):
    from src.backtest import run_backtest
    bt = run_backtest(symbol)
    if "error" in bt:
        return bt

    pf = bt["portfolio_values"]
    bh = bt["buy_hold_values"]

    # Normalized curves
    pf_norm = ((pf["value"] / pf["value"].iloc[0]) - 1) * 100
    bh_norm = ((bh["value"] / bh["value"].iloc[0]) - 1) * 100

    curve = []
    for (ts, pv), (_, bv) in zip(pf_norm.items(), bh_norm.items()):
        curve.append({
            "time": ts.strftime("%Y-%m-%d"),
            "strategy": round(pv, 2),
            "buyhold": round(bv, 2),
        })

    return {
        "total_return": round(bt["total_return"], 4),
        "bh_total_return": round(bt["bh_total_return"], 4),
        "max_drawdown": round(bt["max_drawdown"], 4),
        "sharpe": round(bt["sharpe"], 2),
        "n_trades": bt["n_trades"],
        "curve": curve,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
