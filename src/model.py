"""Model training, evaluation, ensemble, and prediction."""

import os
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report,
)
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from src.config import TRAIN_END, VAL_END, MODEL_DIR, N_SEARCH_ITER, SYMBOLS
from src.features import build_features

warnings.filterwarnings("ignore", category=UserWarning)


# --- Hyperparameter search spaces ---
RF_PARAMS = {
    "n_estimators": [100, 200, 300, 500],
    "max_depth": [5, 8, 10, 15, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2", 0.3, 0.5],
}

XGB_PARAMS = {
    "n_estimators": [100, 200, 300, 500],
    "max_depth": [3, 5, 7, 9],
    "learning_rate": [0.01, 0.05, 0.1, 0.2],
    "subsample": [0.6, 0.7, 0.8, 0.9],
    "colsample_bytree": [0.5, 0.6, 0.7, 0.8],
    "reg_alpha": [0, 0.1, 1],
    "reg_lambda": [1, 2, 5],
}

LGBM_PARAMS = {
    "n_estimators": [100, 200, 300, 500],
    "max_depth": [3, 5, 7, 9, -1],
    "learning_rate": [0.01, 0.05, 0.1, 0.2],
    "num_leaves": [15, 31, 63, 127],
    "subsample": [0.6, 0.7, 0.8, 0.9],
    "colsample_bytree": [0.5, 0.6, 0.7, 0.8],
    "reg_alpha": [0, 0.1, 1],
    "reg_lambda": [1, 2, 5],
}


def split_data(X: pd.DataFrame, y: pd.Series):
    """Time-based train/val/test split. Returns (X_train, y_train, X_val, y_val, X_test, y_test)."""
    train_mask = X.index <= TRAIN_END
    val_mask = (X.index > TRAIN_END) & (X.index <= VAL_END)
    test_mask = X.index > VAL_END

    return (
        X[train_mask], y[train_mask],
        X[val_mask], y[val_mask],
        X[test_mask], y[test_mask],
    )


def train_model(name: str, base_model, param_grid: dict,
                X_train: pd.DataFrame, y_train: pd.Series,
                scaler: StandardScaler) -> tuple:
    """Train one model with RandomizedSearchCV + time series CV, return (model, best_params)."""
    X_scaled = scaler.transform(X_train)
    tscv = TimeSeriesSplit(n_splits=5)

    search = RandomizedSearchCV(
        base_model, param_grid, n_iter=min(N_SEARCH_ITER, 30),
        cv=tscv, scoring="roc_auc", n_jobs=-1, random_state=42, verbose=0,
    )
    search.fit(X_scaled, y_train)
    print(f"  {name}: best AUC={search.best_score_:.4f}")
    return search.best_estimator_, search.best_params_


def evaluate(model, X: pd.DataFrame, y: pd.Series, scaler: StandardScaler, label: str) -> dict:
    """Evaluate model on a dataset, return metrics dict."""
    X_scaled = scaler.transform(X)
    y_pred = model.predict(X_scaled)
    y_proba = model.predict_proba(X_scaled)[:, 1]
    metrics = {
        "accuracy": accuracy_score(y, y_pred),
        "precision": precision_score(y, y_pred, zero_division=0),
        "recall": recall_score(y, y_pred, zero_division=0),
        "f1": f1_score(y, y_pred, zero_division=0),
        "auc": roc_auc_score(y, y_proba) if len(set(y)) > 1 else 0.5,
    }
    print(f"  [{label}] Acc={metrics['accuracy']:.3f} AUC={metrics['auc']:.3f} "
          f"F1={metrics['f1']:.3f} Prec={metrics['precision']:.3f} Rec={metrics['recall']:.3f}")
    return metrics


def train_all_for_symbol(symbol: str) -> dict:
    """Train RF + XGB + LGBM for one symbol. Returns dict with models, scaler, metrics, feature_names."""
    print(f"\n{'='*60}")
    print(f"Training models for {symbol}")
    print(f"{'='*60}")

    X, y = build_features(symbol)
    X_train, y_train, X_val, y_val, X_test, y_test = split_data(X, y)

    print(f"  Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    print(f"  Train target ratio: {y_train.mean():.2%} bullish")

    # Fit scaler on train only
    scaler = StandardScaler()
    scaler.fit(X_train)

    # Train 3 models
    models_config = [
        ("RandomForest", RandomForestClassifier(random_state=42, n_jobs=-1), RF_PARAMS),
        ("XGBoost", XGBClassifier(random_state=42, eval_metric="logloss", verbosity=0), XGB_PARAMS),
        ("LightGBM", LGBMClassifier(random_state=42, verbose=-1), LGBM_PARAMS),
    ]

    trained = {}
    all_metrics = {}
    val_aucs = {}

    for name, base, params in models_config:
        model, best_params = train_model(name, base, params, X_train, y_train, scaler)

        # Refit on train+val combined for final model
        X_full = pd.concat([X_train, X_val])
        y_full = pd.concat([y_train, y_val])

        # Evaluate on val set first (for ensemble weighting)
        val_metrics = evaluate(model, X_val, y_val, scaler, f"{name} val")
        val_auc = val_metrics["auc"]

        # Evaluate on test set
        print(f"  {name} test performance:")
        metrics = evaluate(model, X_test, y_test, scaler, "test")

        trained[name] = model
        all_metrics[name] = metrics
        val_aucs[name] = val_auc

    # --- Ensemble (weighted by validation AUC) ---
    total_auc = sum(val_aucs.values())
    if total_auc == 0:
        weights = {name: 1.0 / len(val_aucs) for name in val_aucs}
    else:
        weights = {name: auc / total_auc for name, auc in val_aucs.items()}
    print(f"\n  Ensemble weights: {', '.join(f'{k}={v:.3f}' for k, v in weights.items())}")

    # Ensemble test evaluation
    X_test_scaled = scaler.transform(X_test)
    ensemble_proba = sum(
        w * model.predict_proba(X_test_scaled)[:, 1]
        for (name, model), w in zip(trained.items(), weights.values())
    )
    ensemble_pred = (ensemble_proba > 0.5).astype(int)
    ens_metrics = {
        "accuracy": accuracy_score(y_test, ensemble_pred),
        "precision": precision_score(y_test, ensemble_pred, zero_division=0),
        "recall": recall_score(y_test, ensemble_pred, zero_division=0),
        "f1": f1_score(y_test, ensemble_pred, zero_division=0),
        "auc": roc_auc_score(y_test, ensemble_proba) if len(set(y_test)) > 1 else 0.5,
    }
    all_metrics["Ensemble"] = ens_metrics
    print(f"  Ensemble test: Acc={ens_metrics['accuracy']:.3f} AUC={ens_metrics['auc']:.3f} "
          f"F1={ens_metrics['f1']:.3f}")

    # Save everything
    os.makedirs(MODEL_DIR, exist_ok=True)
    result = {
        "models": trained,
        "weights": weights,
        "scaler": scaler,
        "metrics": all_metrics,
        "feature_names": list(X.columns),
        "X_test": X_test,
        "y_test": y_test,
        "ensemble_proba_test": ensemble_proba,
    }
    safe_name = symbol.replace(".", "_").replace("-", "_")
    joblib.dump(result, Path(MODEL_DIR) / f"{safe_name}_models.pkl")
    print(f"  Saved to {MODEL_DIR}/{symbol}_models.pkl")

    return result


def predict_latest(symbol: str) -> dict:
    """Load trained models and predict on the latest available data point."""
    model_path = Path(MODEL_DIR) / f"{symbol}_models.pkl"
    result = joblib.load(model_path)

    X, _ = build_features(symbol)
    # Use the last row (most recent complete data)
    X_latest = X.iloc[[-1]]
    X_scaled = result["scaler"].transform(X_latest)

    predictions = {}
    for name, model in result["models"].items():
        proba = model.predict_proba(X_scaled)[:, 1][0]
        predictions[name] = proba

    # Ensemble
    weights = result["weights"]
    ensemble_proba = sum(
        weights[name] * proba for name, proba in predictions.items()
    )
    predictions["Ensemble"] = ensemble_proba

    direction = "BULLISH" if ensemble_proba > 0.5 else "BEARISH"

    return {
        "symbol": symbol,
        "date": X_latest.index[0].strftime("%Y-%m-%d"),
        "predictions": predictions,
        "ensemble_probability": ensemble_proba,
        "direction": direction,
    }


if __name__ == "__main__":
    for sym in SYMBOLS:
        train_all_for_symbol(sym)

    print("\n" + "=" * 60)
    print("PREDICTIONS (next ~2 weeks)")
    print("=" * 60)
    for sym in SYMBOLS:
        pred = predict_latest(sym)
        print(f"\n  {pred['symbol']} (as of {pred['date']}):")
        print(f"    Direction: {pred['direction']}")
        print(f"    Ensemble probability: {pred['ensemble_probability']:.1%}")
        for name, p in pred['predictions'].items():
            if name != "Ensemble":
                print(f"    {name}: {p:.1%}")
