"""Unit tests for the renewable generation and demand forecasting pipeline."""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest

from forecasting.data_loader import (
    calculate_solar_generation,
    calculate_wind_generation,
    determine_weather_condition,
    generate_synthetic_weather,
    load_dataset,
)
from forecasting.demand_model import compute_hourly_demand, generate_demand_series
from forecasting.feature_engineering import create_features, prepare_train_test_split
from forecasting.predict import forecast


def test_synthetic_weather_generation():
    """Verify synthetic weather generator produces physically plausible columns and bounds."""
    df = generate_synthetic_weather(days=3)
    assert len(df) == 72
    assert "temperature_2m" in df.columns
    assert "shortwave_radiation" in df.columns
    assert "wind_speed_80m" in df.columns
    assert "cloud_cover" in df.columns

    # Non-negative radiation and wind speeds
    assert (df["shortwave_radiation"] >= 0.0).all()
    assert (df["wind_speed_80m"] >= 0.0).all()
    assert (df["cloud_cover"] >= 0.0).all() and (df["cloud_cover"] <= 100.0).all()


def test_physical_power_models():
    """Verify physical power conversion curves adhere to physics constraints."""
    # Night solar (0 radiation) must be 0 kW
    rad_night = np.array([0.0, 0.0])
    temp = np.array([25.0, 30.0])
    solar_out = calculate_solar_generation(rad_night, temp, capacity_kw=100.0)
    assert np.all(solar_out == 0.0)

    # Full sun with NOCT cell temperature heating
    rad_noon = np.array([1000.0])
    solar_noon = calculate_solar_generation(rad_noon, np.array([25.0]), capacity_kw=100.0)
    assert 80.0 <= solar_noon[0] <= 100.0

    # Wind: below cut-in (3 m/s) must be 0
    wind_calm = np.array([2.0, 1.5])
    wind_out = calculate_wind_generation(wind_calm, capacity_kw=100.0)
    assert np.all(wind_out == 0.0)

    # Wind: rated speed (12 m/s) should reach capacity
    wind_rated = np.array([13.0])
    wind_rated_out = calculate_wind_generation(wind_rated, capacity_kw=100.0)
    assert wind_rated_out[0] == 100.0


def test_weather_condition_logic():
    """Test weather condition classification matches expected states."""
    assert determine_weather_condition(cloud_cover=10.0, wind_speed_10m=12.0, solar_kw=50.0, hour=12) == "clear"
    assert determine_weather_condition(cloud_cover=50.0, wind_speed_10m=12.0, solar_kw=30.0, hour=12) == "partly cloudy"
    assert determine_weather_condition(cloud_cover=90.0, wind_speed_10m=12.0, solar_kw=10.0, hour=12) == "cloudy"
    assert determine_weather_condition(cloud_cover=10.0, wind_speed_10m=55.0, solar_kw=20.0, hour=12) == "storm"
    assert determine_weather_condition(cloud_cover=10.0, wind_speed_10m=10.0, solar_kw=0.0, hour=2) == "night"


def test_demand_model_curve():
    """Test diurnal demand curve peaks and baseload."""
    # Morning peak test (08:30 weekday) vs midnight baseload (03:00)
    dt_morning = datetime(2026, 9, 14, 8, 30)  # Monday
    dt_night = datetime(2026, 9, 14, 3, 0)
    dt_evening = datetime(2026, 9, 14, 20, 0)

    demand_morning = compute_hourly_demand(dt_morning, base_demand_kw=50.0)
    demand_night = compute_hourly_demand(dt_night, base_demand_kw=50.0)
    demand_evening = compute_hourly_demand(dt_evening, base_demand_kw=50.0)

    assert demand_night < demand_morning
    assert demand_night < demand_evening
    assert demand_evening > demand_morning * 0.8  # Evening peak is prominent


def test_feature_engineering_lags():
    """Verify lag features are constructed and empty rows cleanly dropped."""
    raw_df = generate_synthetic_weather(days=5)
    raw_df["solar_kw"] = 50.0
    raw_df["wind_kw"] = 50.0
    feats = create_features(raw_df)

    assert "solar_lag_1" in feats.columns
    assert "solar_lag_2" in feats.columns
    assert "solar_lag_3" in feats.columns
    assert "wind_lag_1" in feats.columns
    assert "sin_hour" in feats.columns
    assert not feats.isna().any().any()


def test_forecast_output_contract():
    """Verify forecast() return value matches /backend/data_schema.md exactly."""
    horizon = 48
    records = forecast(horizon_hours=horizon)

    assert len(records) == horizon
    required_keys = {
        "timestamp",
        "solar_kw",
        "wind_kw",
        "demand_kw",
        "solar_confidence",
        "wind_confidence",
        "weather_condition",
    }

    for idx, rec in enumerate(records):
        assert required_keys.issubset(rec.keys()), f"Row {idx} missing keys: {required_keys - set(rec.keys())}"
        assert isinstance(rec["timestamp"], str)
        assert isinstance(rec["solar_kw"], (float, int))
        assert isinstance(rec["wind_kw"], (float, int))
        assert isinstance(rec["demand_kw"], (float, int))
        assert isinstance(rec["solar_confidence"], (float, int))
        assert isinstance(rec["wind_confidence"], (float, int))
        assert isinstance(rec["weather_condition"], str)

        # Non-negativity
        assert rec["solar_kw"] >= 0.0
        assert rec["wind_kw"] >= 0.0
        assert rec["demand_kw"] >= 0.0

        # Confidence bounds [0, 1]
        assert 0.0 <= rec["solar_confidence"] <= 1.0
        assert 0.0 <= rec["wind_confidence"] <= 1.0


if __name__ == "__main__":
    test_synthetic_weather_generation()
    test_physical_power_models()
    test_weather_condition_logic()
    test_demand_model_curve()
    test_feature_engineering_lags()
    test_forecast_output_contract()
    print("\n[ALL UNIT TESTS PASSED SUCCESSFULLY!]")
