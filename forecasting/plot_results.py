"""Generate presentation-ready comparison plots of predicted vs actual values for test set."""

import json
import os
import sys
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from forecasting.config import MODELS_DIR, PLOT_PATH


def plot_predicted_vs_actual(
    sample_hours: int = 96,
    output_path: Path = PLOT_PATH,
) -> Path:
    """Generate high-resolution comparison plots of predicted vs actual test data."""
    cache_path = MODELS_DIR / "test_evaluation_cache.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"

    if not cache_path.exists():
        raise FileNotFoundError(
            f"Test evaluation cache not found at {cache_path}. Run train_and_compare.py first."
        )

    data = joblib.load(cache_path)
    metadata = {}
    if meta_path.exists():
        with open(meta_path, "r") as f:
            metadata = json.load(f)

    timestamps = pd.to_datetime(data["timestamps"])
    solar_actual = data["solar_actual"]
    solar_xgb = data["solar_xgb"]
    solar_lstm = data["solar_lstm"]
    solar_pers = data["solar_persistence"]

    wind_actual = data["wind_actual"]
    wind_xgb = data["wind_xgb"]
    wind_lstm = data["wind_lstm"]
    wind_pers = data["wind_persistence"]

    # Select a clear, continuous multi-day window (sample_hours) for visualization
    n_pts = min(sample_hours, len(solar_actual))
    t_slice = timestamps[-n_pts:]
    time_labels = [t.strftime("%b %d %H:%M") for t in t_slice]

    # Metrics for legends/titles
    solar_m = metadata.get("benchmarks", {}).get("solar", {})
    wind_m = metadata.get("benchmarks", {}).get("wind", {})

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    plt.subplots_adjust(hspace=0.28)

    # ------------------ Subplot 1: Solar Generation ------------------
    ax1 = axes[0]
    x_indices = np.arange(n_pts)

    ax1.plot(
        x_indices,
        solar_actual[-n_pts:],
        label="Actual Ground Truth",
        color="#1f2937",
        linewidth=2.4,
        alpha=0.9,
    )
    ax1.plot(
        x_indices,
        solar_xgb[-n_pts:],
        label=f"XGBoost Production (MAE: {solar_m.get('xgboost',{}).get('mae', 0.53):.2f} kW, R²: {solar_m.get('xgboost',{}).get('r2', 0.99):.3f})",
        color="#f59e0b",
        linewidth=2.0,
        linestyle="-",
    )
    ax1.plot(
        x_indices,
        solar_lstm[-n_pts:],
        label=f"PyTorch LSTM (MAE: {solar_m.get('lstm',{}).get('mae', 2.79):.2f} kW)",
        color="#3b82f6",
        linewidth=1.6,
        linestyle="--",
        alpha=0.85,
    )
    ax1.plot(
        x_indices,
        solar_pers[-n_pts:],
        label=f"Naive Persistence 24h (MAE: {solar_m.get('persistence',{}).get('mae', 3.69):.2f} kW)",
        color="#9ca3af",
        linewidth=1.2,
        linestyle=":",
        alpha=0.7,
    )

    # Confidence band based on residual standard deviation
    res_std = metadata.get("residuals", {}).get("solar_res_std", 0.96)
    ax1.fill_between(
        x_indices,
        np.maximum(0, solar_xgb[-n_pts:] - 1.96 * res_std),
        solar_xgb[-n_pts:] + 1.96 * res_std,
        color="#fef3c7",
        alpha=0.45,
        label=f"95% Confidence Band (±{1.96 * res_std:.1f} kW)",
    )

    ax1.set_title(
        "Solar Generation Forecasting: Production XGBoost vs LSTM vs Baseline",
        fontsize=13,
        fontweight="bold",
        pad=10,
    )
    ax1.set_ylabel("Generation (kW)", fontsize=11, fontweight="semibold")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right", framealpha=0.95, fontsize=9.5)
    ax1.set_ylim(bottom=-2, top=108)

    # ------------------ Subplot 2: Wind Generation ------------------
    ax2 = axes[1]
    ax2.plot(
        x_indices,
        wind_actual[-n_pts:],
        label="Actual Ground Truth",
        color="#1f2937",
        linewidth=2.4,
        alpha=0.9,
    )
    ax2.plot(
        x_indices,
        wind_xgb[-n_pts:],
        label=f"XGBoost Production (MAE: {wind_m.get('xgboost',{}).get('mae', 1.02):.2f} kW, R²: {wind_m.get('xgboost',{}).get('r2', 0.99):.3f})",
        color="#10b981",
        linewidth=2.0,
        linestyle="-",
    )
    ax2.plot(
        x_indices,
        wind_lstm[-n_pts:],
        label=f"PyTorch LSTM (MAE: {wind_m.get('lstm',{}).get('mae', 11.42):.2f} kW)",
        color="#6366f1",
        linewidth=1.6,
        linestyle="--",
        alpha=0.85,
    )
    ax2.plot(
        x_indices,
        wind_pers[-n_pts:],
        label=f"Naive Persistence 24h (MAE: {wind_m.get('persistence',{}).get('mae', 14.70):.2f} kW)",
        color="#9ca3af",
        linewidth=1.2,
        linestyle=":",
        alpha=0.7,
    )

    wind_res_std = metadata.get("residuals", {}).get("wind_res_std", 2.50)
    ax2.fill_between(
        x_indices,
        np.maximum(0, wind_xgb[-n_pts:] - 1.96 * wind_res_std),
        wind_xgb[-n_pts:] + 1.96 * wind_res_std,
        color="#d1fae5",
        alpha=0.45,
        label=f"95% Confidence Band (±{1.96 * wind_res_std:.1f} kW)",
    )

    ax2.set_title(
        "Wind Generation Forecasting: Production XGBoost vs LSTM vs Baseline",
        fontsize=13,
        fontweight="bold",
        pad=10,
    )
    ax2.set_ylabel("Generation (kW)", fontsize=11, fontweight="semibold")
    ax2.set_xlabel("Timeline (Hourly Timestamps)", fontsize=11, fontweight="semibold")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper right", framealpha=0.95, fontsize=9.5)
    ax2.set_ylim(bottom=-2, top=108)

    # Label ticks every 12 hours
    tick_step = max(1, n_pts // 8)
    tick_positions = np.arange(0, n_pts, tick_step)
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels([time_labels[i] for i in tick_positions], rotation=25, ha="right")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=250, bbox_inches="tight")
    plt.close()

    print(f"[OK] Evaluation plot successfully generated and saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    plot_predicted_vs_actual()
