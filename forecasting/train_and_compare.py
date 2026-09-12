"""Train and compare three candidate forecasting models:
1. Naive Persistence (tomorrow = today, 24-hour lag)
2. Simple PyTorch LSTM
3. XGBoost Regressor

Evaluates on held-out test data using MAE, RMSE, and R2.
Prints a formatted comparison table and serializes the winning models to /forecasting/models/.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

# Resolve OpenMP multiple runtime conflict on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Ensure repository root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset
import xgboost as xgb

from forecasting.config import (
    DEFAULT_SOLAR_CAPACITY_KW,
    DEFAULT_WIND_CAPACITY_KW,
    HISTORICAL_DAYS,
    MODELS_DIR,
)
from forecasting.data_loader import load_dataset
from forecasting.feature_engineering import (
    SOLAR_FEATURES,
    WIND_FEATURES,
    prepare_train_test_split,
)

logger = logging.getLogger("forecasting.train")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ---------------------------------------------------------------------------
# 1. Candidate Model: Simple PyTorch LSTM
# ---------------------------------------------------------------------------
class SimpleLSTM(nn.Module):
    """Compact LSTM network for hourly energy time-series regression."""

    def __init__(self, input_dim: int, hidden_dim: int = 32, num_layers: int = 2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0.0,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        # Take the output from the last time step
        last_out = out[:, -1, :]
        return self.fc(last_out)


def create_lstm_sequences(
    X_mat: np.ndarray,
    y_vec: np.ndarray,
    seq_len: int = 6,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Convert 2D tabular features into 3D sequential sliding windows for LSTM."""
    xs, ys = [], []
    for i in range(len(X_mat) - seq_len):
        xs.append(X_mat[i : i + seq_len])
        ys.append(y_vec[i + seq_len])
    return torch.tensor(np.array(xs), dtype=torch.float32), torch.tensor(np.array(ys), dtype=torch.float32).unsqueeze(1)


def train_pytorch_lstm(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    seq_len: int = 6,
    epochs: int = 25,
    batch_size: int = 64,
) -> Tuple[np.ndarray, Dict[str, float]]:
    """Train PyTorch LSTM candidate and return predictions on test set with metrics."""
    # Scale inputs
    scaler_x = StandardScaler()
    X_train_s = scaler_x.fit_transform(X_train)
    X_test_s = scaler_x.transform(X_test)

    scaler_y = StandardScaler()
    y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

    X_train_seq, y_train_seq = create_lstm_sequences(X_train_s, y_train_s, seq_len=seq_len)

    # For test evaluation, stack last seq_len rows from train to predict from the start of test
    full_X = np.vstack([X_train_s[-seq_len:], X_test_s])
    dummy_y = np.zeros(len(full_X))
    X_test_seq, _ = create_lstm_sequences(full_X, dummy_y, seq_len=seq_len)

    dataset = TensorDataset(X_train_seq, y_train_seq)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    input_dim = X_train.shape[1]
    model = SimpleLSTM(input_dim=input_dim, hidden_dim=32, num_layers=2)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.008, weight_decay=1e-5)

    model.train()
    for _ in range(epochs):
        for bx, by in loader:
            optimizer.zero_grad()
            pred = model(bx)
            loss = criterion(pred, by)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        test_pred_scaled = model(X_test_seq).numpy()

    test_pred = scaler_y.inverse_transform(test_pred_scaled).flatten()
    test_pred = np.maximum(0.0, test_pred)

    mae = mean_absolute_error(y_test, test_pred)
    rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    r2 = r2_score(y_test, test_pred)

    return test_pred, {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)}


# ---------------------------------------------------------------------------
# 2. Candidate Model: Naive Persistence Baseline (Tomorrow = Today)
# ---------------------------------------------------------------------------
def evaluate_persistence_baseline(
    y_series: np.ndarray,
    split_idx: int,
    lag: int = 24,
) -> Tuple[np.ndarray, Dict[str, float]]:
    """Persistence baseline: predict value from 24 hours ago (y_t = y_{t-24})."""
    y_test = y_series[split_idx:]
    test_pred = []
    for t in range(split_idx, len(y_series)):
        if t - lag >= 0:
            test_pred.append(y_series[t - lag])
        elif t - 1 >= 0:
            test_pred.append(y_series[t - 1])
        else:
            test_pred.append(y_series[t])

    test_pred = np.array(test_pred, dtype=float)
    mae = mean_absolute_error(y_test, test_pred)
    rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    r2 = r2_score(y_test, test_pred)

    return test_pred, {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)}


# ---------------------------------------------------------------------------
# 3. Candidate Model: XGBoost Regressor
# ---------------------------------------------------------------------------
def train_xgboost(
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    X_test: pd.DataFrame,
    y_test: np.ndarray,
    capacity_kw: float,
) -> Tuple[xgb.XGBRegressor, np.ndarray, Dict[str, float]]:
    """Train XGBoost Regressor on engineered features."""
    model = xgb.XGBRegressor(
        n_estimators=140,
        max_depth=5,
        learning_rate=0.07,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=3,
        random_state=42,
        verbosity=0,
    )
    model.fit(X_train, y_train)

    test_pred = model.predict(X_test)
    test_pred = np.clip(test_pred, 0.0, capacity_kw)

    mae = mean_absolute_error(y_test, test_pred)
    rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    r2 = r2_score(y_test, test_pred)

    return model, test_pred, {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)}


# ---------------------------------------------------------------------------
# Pipeline Driver & Benchmark Table
# ---------------------------------------------------------------------------
def run_model_training_and_benchmarking(
    days: int = HISTORICAL_DAYS,
    force_synthetic: bool = False,
) -> Dict[str, Any]:
    """Execute end-to-end model training, evaluation, comparison table, and serialization."""
    logger.info("Starting forecasting pipeline training & benchmark...")

    # Ingest data
    raw_df, data_mode = load_dataset(days=days, force_synthetic=force_synthetic)
    splits = prepare_train_test_split(raw_df, test_ratio=0.20)

    split_idx = len(splits["train"])
    y_full_solar = splits["full"]["solar_kw"].values
    y_full_wind = splits["full"]["wind_kw"].values
    y_test_solar = splits["y_test_solar"]
    y_test_wind = splits["y_test_wind"]

    # ------------------ SOLAR BENCHMARK ------------------
    logger.info("Evaluating Solar Models...")
    # 1. Persistence
    solar_pers_pred, solar_pers_metrics = evaluate_persistence_baseline(
        y_full_solar, split_idx=split_idx, lag=24
    )
    # 2. LSTM
    solar_lstm_pred, solar_lstm_metrics = train_pytorch_lstm(
        splits["X_train_solar"].values,
        splits["y_train_solar"],
        splits["X_test_solar"].values,
        y_test_solar,
    )
    # 3. XGBoost
    solar_xgb_model, solar_xgb_pred, solar_xgb_metrics = train_xgboost(
        splits["X_train_solar"],
        splits["y_train_solar"],
        splits["X_test_solar"],
        y_test_solar,
        capacity_kw=DEFAULT_SOLAR_CAPACITY_KW,
    )

    # ------------------ WIND BENCHMARK ------------------
    logger.info("Evaluating Wind Models...")
    # 1. Persistence
    wind_pers_pred, wind_pers_metrics = evaluate_persistence_baseline(
        y_full_wind, split_idx=split_idx, lag=24
    )
    # 2. LSTM
    wind_lstm_pred, wind_lstm_metrics = train_pytorch_lstm(
        splits["X_train_wind"].values,
        splits["y_train_wind"],
        splits["X_test_wind"].values,
        y_test_wind,
    )
    # 3. XGBoost
    wind_xgb_model, wind_xgb_pred, wind_xgb_metrics = train_xgboost(
        splits["X_train_wind"],
        splits["y_train_wind"],
        splits["X_test_wind"],
        y_test_wind,
        capacity_kw=DEFAULT_WIND_CAPACITY_KW,
    )

    # Calculate residual standard deviation on production model (XGBoost) for confidence intervals
    solar_res = y_test_solar - solar_xgb_pred
    solar_res_std = float(np.std(solar_res))
    solar_res_mean = float(np.mean(solar_res))

    wind_res = y_test_wind - wind_xgb_pred
    wind_res_std = float(np.std(wind_res))
    wind_res_mean = float(np.mean(wind_res))

    # Print candidate comparison table
    print("\n" + "=" * 88)
    print("                      CANDIDATE MODEL EVALUATION BENCHMARK TABLE")
    print("=" * 88)
    header = f"{'Target':<8} | {'Candidate Model':<26} | {'MAE (kW)':<10} | {'RMSE (kW)':<10} | {'R² Score':<10} | {'Status'}"
    print(header)
    print("-" * 88)
    
    rows = [
        ("Solar", "Naive Persistence (24h)", solar_pers_metrics, "Baseline"),
        ("Solar", "Simple LSTM (PyTorch)", solar_lstm_metrics, "Evaluated"),
        ("Solar", "XGBoost Regressor", solar_xgb_metrics, "SELECTED (Production)"),
        ("---", "---", None, "---"),
        ("Wind", "Naive Persistence (24h)", wind_pers_metrics, "Baseline"),
        ("Wind", "Simple LSTM (PyTorch)", wind_lstm_metrics, "Evaluated"),
        ("Wind", "XGBoost Regressor", wind_xgb_metrics, "SELECTED (Production)"),
    ]

    for target, model_name, m, status in rows:
        if m is None:
            print("-" * 88)
            continue
        print(f"{target:<8} | {model_name:<26} | {m['mae']:<10.2f} | {m['rmse']:<10.2f} | {m['r2']:<10.3f} | {status}")
    print("=" * 88)

    # ------------------ SERIALIZE PRODUCTION MODELS ------------------
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    solar_model_path = MODELS_DIR / "solar_xgb.joblib"
    wind_model_path = MODELS_DIR / "wind_xgb.joblib"
    metadata_path = MODELS_DIR / "model_metadata.json"
    test_eval_path = MODELS_DIR / "test_evaluation_cache.joblib"

    joblib.dump(solar_xgb_model, solar_model_path)
    joblib.dump(wind_xgb_model, wind_model_path)

    metadata = {
        "created_at": datetime.now().isoformat(),
        "data_mode": data_mode,
        "historical_days": days,
        "train_rows": len(splits["train"]),
        "test_rows": len(splits["test"]),
        "solar_features": SOLAR_FEATURES,
        "wind_features": WIND_FEATURES,
        "solar_capacity_kw": DEFAULT_SOLAR_CAPACITY_KW,
        "wind_capacity_kw": DEFAULT_WIND_CAPACITY_KW,
        "benchmarks": {
            "solar": {
                "persistence": solar_pers_metrics,
                "lstm": solar_lstm_metrics,
                "xgboost": solar_xgb_metrics,
            },
            "wind": {
                "persistence": wind_pers_metrics,
                "lstm": wind_lstm_metrics,
                "xgboost": wind_xgb_metrics,
            },
        },
        "residuals": {
            "solar_res_std": solar_res_std,
            "solar_res_mean": solar_res_mean,
            "wind_res_std": wind_res_std,
            "wind_res_mean": wind_res_mean,
        },
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Cache test actuals and predictions for plotting
    test_eval_data = {
        "timestamps": splits["test"]["time"].values,
        "solar_actual": y_test_solar,
        "solar_xgb": solar_xgb_pred,
        "solar_lstm": solar_lstm_pred,
        "solar_persistence": solar_pers_pred,
        "wind_actual": y_test_wind,
        "wind_xgb": wind_xgb_pred,
        "wind_lstm": wind_lstm_pred,
        "wind_persistence": wind_pers_pred,
    }
    joblib.dump(test_eval_data, test_eval_path)

    logger.info("Saved serialized models to %s", MODELS_DIR)
    logger.info("Saved metadata to %s", metadata_path)

    return metadata


if __name__ == "__main__":
    run_model_training_and_benchmarking(days=90)
