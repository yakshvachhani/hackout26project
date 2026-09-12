"""Inference module providing production forecast() interface conforming to /backend/data_schema.md."""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Resolve OpenMP multiple runtime conflict on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Ensure repository root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import numpy as np
import pandas as pd
import requests

from forecasting.config import (
    DEFAULT_FORECAST_HORIZON_HOURS,
    DEFAULT_SOLAR_CAPACITY_KW,
    DEFAULT_WIND_CAPACITY_KW,
    LATITUDE,
    LONGITUDE,
    MODELS_DIR,
    OPEN_METEO_FORECAST_URL,
)
from forecasting.data_loader import (
    determine_weather_condition,
    generate_synthetic_weather,
)
from forecasting.demand_model import generate_demand_series
from forecasting.feature_engineering import SOLAR_FEATURES, WIND_FEATURES

logger = logging.getLogger("forecasting.predict")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Global in-memory model cache to avoid reloading on every call
_SOLAR_MODEL = None
_WIND_MODEL = None
_METADATA = None


def load_production_models() -> Tuple[Any, Any, Dict[str, Any]]:
    """Load serialized models and metadata from disk without retraining."""
    global _SOLAR_MODEL, _WIND_MODEL, _METADATA

    if _SOLAR_MODEL is not None and _WIND_MODEL is not None and _METADATA is not None:
        return _SOLAR_MODEL, _WIND_MODEL, _METADATA

    solar_path = MODELS_DIR / "solar_xgb.joblib"
    wind_path = MODELS_DIR / "wind_xgb.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"

    # If models do not exist yet, trigger training once
    if not solar_path.exists() or not wind_path.exists() or not meta_path.exists():
        logger.info("Pre-trained models not found in %s. Initiating initial training...", MODELS_DIR)
        from forecasting.train_and_compare import run_model_training_and_benchmarking
        run_model_training_and_benchmarking(days=90)

    logger.info("Loading pre-trained production models from %s...", MODELS_DIR)
    _SOLAR_MODEL = joblib.load(solar_path)
    _WIND_MODEL = joblib.load(wind_path)

    with open(meta_path, "r") as f:
        _METADATA = json.load(f)

    return _SOLAR_MODEL, _WIND_MODEL, _METADATA


def fetch_or_synthesize_forecast_weather(
    horizon_hours: int = DEFAULT_FORECAST_HORIZON_HOURS,
    latitude: float = LATITUDE,
    longitude: float = LONGITUDE,
    start_time: Optional[datetime] = None,
) -> Tuple[pd.DataFrame, str]:
    """Fetch forward weather forecast from Open-Meteo or synthesize physically plausible weather."""
    mode = "LIVE_OPEN_METEO"
    forecast_days = int(np.ceil(horizon_hours / 24.0)) + 1

    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "past_days": 1,  # 24 hours of history to initialize lag features
            "forecast_days": forecast_days,
            "hourly": "temperature_2m,relative_humidity_2m,cloud_cover,shortwave_radiation,wind_speed_10m,wind_speed_80m",
            "timezone": "auto",
        }
        res = requests.get(OPEN_METEO_FORECAST_URL, params=params, timeout=10)
        res.raise_for_status()
        hourly = res.json()["hourly"]

        times = [datetime.fromisoformat(t) for t in hourly["time"]]
        df = pd.DataFrame({
            "timestamp": [t.isoformat() for t in times],
            "time": times,
            "temperature_2m": hourly["temperature_2m"],
            "relative_humidity_2m": hourly["relative_humidity_2m"],
            "cloud_cover": hourly["cloud_cover"],
            "shortwave_radiation": hourly["shortwave_radiation"],
            "wind_speed_10m": hourly["wind_speed_10m"],
            "wind_speed_80m": hourly["wind_speed_80m"],
        }).ffill().bfill()

    except Exception as err:
        logger.warning("Could not fetch live Open-Meteo forward forecast (%s). Using synthetic forecast.", err)
        mode = "SYNTHETIC_FALLBACK"
        # Generate 1 day past + forecast horizon
        base_t = (start_time or datetime.now()).replace(minute=0, second=0, microsecond=0) - timedelta(hours=24)
        df = generate_synthetic_weather(days=int(np.ceil((horizon_hours + 24) / 24.0)), base_time=base_t)

    return df, mode


def compute_forecast_confidence(
    residual_std: float,
    mean_prediction: float,
    horizon_step: int,
    total_horizon: int,
    is_solar_zero: bool = False,
) -> float:
    """Compute confidence metric in [0.0, 1.0] based on model residual standard deviation.
    
    Uncertainty scales with residual variance and increases with forecast horizon.
    """
    if is_solar_zero:
        # At night solar generation is 0 with near 100% certainty
        return 0.98

    # Uncertainty penalty grows slightly with lookahead horizon
    horizon_decay = 1.0 + 0.15 * (horizon_step / max(1, total_horizon))
    scale_denominator = max(15.0, mean_prediction + 20.0)
    
    # Normalized error ratio
    relative_uncertainty = (residual_std * horizon_decay) / scale_denominator
    confidence = 1.0 - relative_uncertainty

    # Clamp confidence to realistic operational bounds [0.65, 0.98]
    clamped_conf = max(0.65, min(0.98, confidence))
    return round(float(clamped_conf), 3)


def forecast(
    horizon_hours: int = DEFAULT_FORECAST_HORIZON_HOURS,
    start_time: Optional[datetime] = None,
    demand_multiplier: float = 1.0,
    solar_capacity_kw: float = DEFAULT_SOLAR_CAPACITY_KW,
    wind_capacity_kw: float = DEFAULT_WIND_CAPACITY_KW,
) -> List[Dict[str, Any]]:
    """Generate solar, wind, and demand forecasts matching /backend/data_schema.md.

    Args:
        horizon_hours: Number of forward hours to predict (default 48).
        start_time: Starting datetime (defaults to current hour).
        demand_multiplier: Demand scale multiplier (default 1.0).
        solar_capacity_kw: Installed solar capacity in kW (default 100.0).
        wind_capacity_kw: Installed wind capacity in kW (default 100.0).

    Returns:
        List of dicts containing:
        - timestamp: ISO-8601 string
        - solar_kw: float
        - wind_kw: float
        - demand_kw: float
        - solar_confidence: float
        - wind_confidence: float
        - weather_condition: str
    """
    solar_model, wind_model, metadata = load_production_models()

    solar_res_std = metadata.get("residuals", {}).get("solar_res_std", 0.96)
    wind_res_std = metadata.get("residuals", {}).get("wind_res_std", 2.50)

    weather_df, data_mode = fetch_or_synthesize_forecast_weather(
        horizon_hours=horizon_hours,
        start_time=start_time,
    )

    if start_time is None:
        start_time = datetime.now().replace(minute=0, second=0, microsecond=0)

    # Locate the starting index for forward prediction
    weather_df["time"] = pd.to_datetime(weather_df["time"])
    future_mask = weather_df["time"] >= start_time
    if not future_mask.any():
        start_idx = max(0, len(weather_df) - horizon_hours)
    else:
        start_idx = weather_df[future_mask].index[0]

    # Ensure we have at least 3 historical rows prior to start_idx for lag features
    if start_idx < 3:
        # Prepend synthetic historical rows if needed
        extra_hist = generate_synthetic_weather(days=1, base_time=weather_df["time"].iloc[0] - timedelta(hours=24))
        weather_df = pd.concat([extra_hist, weather_df], ignore_index=True)
        start_idx += len(extra_hist)

    # Calculate initial historical generation for the lookback window
    from forecasting.data_loader import (
        calculate_solar_generation,
        calculate_wind_generation,
    )

    weather_df["solar_kw"] = calculate_solar_generation(
        weather_df["shortwave_radiation"].values,
        weather_df["temperature_2m"].values,
        capacity_kw=solar_capacity_kw,
    )
    weather_df["wind_kw"] = calculate_wind_generation(
        weather_df["wind_speed_80m"].values,
        capacity_kw=wind_capacity_kw,
    )

    forecast_records = []
    solar_predictions = []
    wind_predictions = []

    # Iterative forward step prediction
    for h in range(horizon_hours):
        curr_idx = start_idx + h
        if curr_idx >= len(weather_df):
            break

        row = weather_df.iloc[curr_idx]
        dt = row["time"]
        hour = dt.hour
        day = dt.dayofweek

        # Get lags: prior predictions or historical values
        def get_lag_val(series_name: str, lag_k: int, pred_list: List[float]):
            if h - lag_k >= 0:
                return pred_list[h - lag_k]
            else:
                return float(weather_df.iloc[curr_idx - lag_k][series_name])

        solar_lag_1 = get_lag_val("solar_kw", 1, solar_predictions)
        solar_lag_2 = get_lag_val("solar_kw", 2, solar_predictions)
        solar_lag_3 = get_lag_val("solar_kw", 3, solar_predictions)

        wind_lag_1 = get_lag_val("wind_kw", 1, wind_predictions)
        wind_lag_2 = get_lag_val("wind_kw", 2, wind_predictions)
        wind_lag_3 = get_lag_val("wind_kw", 3, wind_predictions)

        rad_lag_1 = float(weather_df.iloc[curr_idx - 1]["shortwave_radiation"])
        rad_lag_2 = float(weather_df.iloc[curr_idx - 2]["shortwave_radiation"])
        rad_lag_3 = float(weather_df.iloc[curr_idx - 3]["shortwave_radiation"])

        w80_lag_1 = float(weather_df.iloc[curr_idx - 1]["wind_speed_80m"])
        w80_lag_2 = float(weather_df.iloc[curr_idx - 2]["wind_speed_80m"])
        w80_lag_3 = float(weather_df.iloc[curr_idx - 3]["wind_speed_80m"])

        cloud_lag_1 = float(weather_df.iloc[curr_idx - 1]["cloud_cover"])

        # Construct feature dictionaries
        solar_feats = pd.DataFrame([{
            "hour_of_day": hour,
            "day_of_week": day,
            "sin_hour": np.sin(2.0 * np.pi * hour / 24.0),
            "cos_hour": np.cos(2.0 * np.pi * hour / 24.0),
            "sin_day": np.sin(2.0 * np.pi * day / 7.0),
            "cos_day": np.cos(2.0 * np.pi * day / 7.0),
            "cloud_cover": float(row["cloud_cover"]),
            "shortwave_radiation": float(row["shortwave_radiation"]),
            "temperature_2m": float(row["temperature_2m"]),
            "solar_lag_1": solar_lag_1,
            "solar_lag_2": solar_lag_2,
            "solar_lag_3": solar_lag_3,
            "radiation_lag_1": rad_lag_1,
            "radiation_lag_2": rad_lag_2,
            "radiation_lag_3": rad_lag_3,
            "cloud_cover_lag_1": cloud_lag_1,
            "solar_rolling_mean_3h": np.mean([solar_lag_1, solar_lag_2, solar_lag_3]),
        }])[SOLAR_FEATURES]

        wind_feats = pd.DataFrame([{
            "hour_of_day": hour,
            "day_of_week": day,
            "sin_hour": np.sin(2.0 * np.pi * hour / 24.0),
            "cos_hour": np.cos(2.0 * np.pi * hour / 24.0),
            "sin_day": np.sin(2.0 * np.pi * day / 7.0),
            "cos_day": np.cos(2.0 * np.pi * day / 7.0),
            "wind_speed_10m": float(row["wind_speed_10m"]),
            "wind_speed_80m": float(row["wind_speed_80m"]),
            "wind_lag_1": wind_lag_1,
            "wind_lag_2": wind_lag_2,
            "wind_lag_3": wind_lag_3,
            "wind_speed_80m_lag_1": w80_lag_1,
            "wind_speed_80m_lag_2": w80_lag_2,
            "wind_speed_80m_lag_3": w80_lag_3,
            "wind_rolling_mean_3h": np.mean([wind_lag_1, wind_lag_2, wind_lag_3]),
        }])[WIND_FEATURES]

        # Model predictions
        pred_solar = float(solar_model.predict(solar_feats)[0])
        # Solar is strictly zero when sun is down or radiation is 0
        if row["shortwave_radiation"] <= 1.0 or hour < 6 or hour > 19:
            pred_solar = 0.0
        pred_solar = max(0.0, min(solar_capacity_kw, pred_solar))
        # Scale if capacity requested differs from default
        if solar_capacity_kw != DEFAULT_SOLAR_CAPACITY_KW:
            pred_solar = pred_solar * (solar_capacity_kw / DEFAULT_SOLAR_CAPACITY_KW)

        pred_wind = float(wind_model.predict(wind_feats)[0])
        pred_wind = max(0.0, min(wind_capacity_kw, pred_wind))
        if wind_capacity_kw != DEFAULT_WIND_CAPACITY_KW:
            pred_wind = pred_wind * (wind_capacity_kw / DEFAULT_WIND_CAPACITY_KW)

        solar_predictions.append(pred_solar)
        wind_predictions.append(pred_wind)

        # Confidence scores
        solar_conf = compute_forecast_confidence(
            residual_std=solar_res_std,
            mean_prediction=pred_solar,
            horizon_step=h,
            total_horizon=horizon_hours,
            is_solar_zero=(pred_solar == 0.0),
        )
        wind_conf = compute_forecast_confidence(
            residual_std=wind_res_std,
            mean_prediction=pred_wind,
            horizon_step=h,
            total_horizon=horizon_hours,
            is_solar_zero=False,
        )

        weather_cond = determine_weather_condition(
            cloud_cover=float(row["cloud_cover"]),
            wind_speed_10m=float(row["wind_speed_10m"]),
            solar_kw=pred_solar,
            hour=hour,
        )

        forecast_records.append({
            "timestamp": dt.isoformat(),
            "solar_kw": round(pred_solar, 2),
            "wind_kw": round(pred_wind, 2),
            "solar_confidence": solar_conf,
            "wind_confidence": wind_conf,
            "weather_condition": weather_cond,
            "temp_c": float(row["temperature_2m"]),
        })

    # Generate synthetic load demand using demand_model
    timestamps = [r["timestamp"] for r in forecast_records]
    temps = [r.pop("temp_c") for r in forecast_records]
    demands = generate_demand_series(
        timestamps=timestamps,
        base_demand_kw=50.0,
        multiplier=demand_multiplier,
        temperatures=temps,
    )

    for record, d in zip(forecast_records, demands):
        record["demand_kw"] = round(float(d), 2)

    return forecast_records


if __name__ == "__main__":
    print("\n--- STANDALONE FORECAST TEST (48 Hours) ---")
    results = forecast(horizon_hours=48)
    print(f"Total forecast records returned: {len(results)}\n")
    print(f"{'Hour':<4} | {'Timestamp':<20} | {'Solar(kW)':<10} | {'Wind(kW)':<10} | {'Demand(kW)':<10} | {'Solar Conf':<10} | {'Wind Conf':<10} | {'Weather'}")
    print("-" * 105)
    for i, r in enumerate(results):
        print(f"{i+1:<4} | {r['timestamp'][:19]:<20} | {r['solar_kw']:<10.2f} | {r['wind_kw']:<10.2f} | {r['demand_kw']:<10.2f} | {r['solar_confidence']:<10.3f} | {r['wind_confidence']:<10.3f} | {r['weather_condition']}")
