"""Feature engineering for renewable generation time-series modeling."""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure repository root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from forecasting.config import LAG_HOURS


# Explicit feature columns per modeling target
SOLAR_FEATURES = [
    "hour_of_day",
    "day_of_week",
    "sin_hour",
    "cos_hour",
    "sin_day",
    "cos_day",
    "cloud_cover",
    "shortwave_radiation",
    "temperature_2m",
    "solar_lag_1",
    "solar_lag_2",
    "solar_lag_3",
    "radiation_lag_1",
    "radiation_lag_2",
    "radiation_lag_3",
    "cloud_cover_lag_1",
    "solar_rolling_mean_3h",
]

WIND_FEATURES = [
    "hour_of_day",
    "day_of_week",
    "sin_hour",
    "cos_hour",
    "sin_day",
    "cos_day",
    "wind_speed_10m",
    "wind_speed_80m",
    "wind_lag_1",
    "wind_lag_2",
    "wind_lag_3",
    "wind_speed_80m_lag_1",
    "wind_speed_80m_lag_2",
    "wind_speed_80m_lag_3",
    "wind_rolling_mean_3h",
]


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer temporal, cyclical, meteorological, and autoregressive lag features."""
    data = df.copy()

    # 1. Parse timestamps
    if not pd.api.types.is_datetime64_any_dtype(data["time"]):
        data["time"] = pd.to_datetime(data["time"])

    # 2. Temporal & cyclical features
    data["hour_of_day"] = data["time"].dt.hour
    data["day_of_week"] = data["time"].dt.dayofweek
    data["is_weekend"] = (data["day_of_week"] >= 5).astype(int)

    data["sin_hour"] = np.sin(2.0 * np.pi * data["hour_of_day"] / 24.0)
    data["cos_hour"] = np.cos(2.0 * np.pi * data["hour_of_day"] / 24.0)
    data["sin_day"] = np.sin(2.0 * np.pi * data["day_of_week"] / 7.0)
    data["cos_day"] = np.cos(2.0 * np.pi * data["day_of_week"] / 7.0)

    # 3. Lagged features (1 to 3 hours prior)
    for lag in LAG_HOURS:
        data[f"solar_lag_{lag}"] = data["solar_kw"].shift(lag)
        data[f"wind_lag_{lag}"] = data["wind_kw"].shift(lag)
        data[f"radiation_lag_{lag}"] = data["shortwave_radiation"].shift(lag)
        data[f"wind_speed_80m_lag_{lag}"] = data["wind_speed_80m"].shift(lag)
        data[f"cloud_cover_lag_{lag}"] = data["cloud_cover"].shift(lag)

    # 4. Rolling statistics
    data["solar_rolling_mean_3h"] = data["solar_kw"].shift(1).rolling(window=3, min_periods=1).mean()
    data["wind_rolling_mean_3h"] = data["wind_kw"].shift(1).rolling(window=3, min_periods=1).mean()

    # Drop the initial rows with NaNs resulting from lags
    data = data.dropna().reset_index(drop=True)

    return data


def prepare_train_test_split(
    df: pd.DataFrame,
    test_ratio: float = 0.20,
) -> Dict[str, pd.DataFrame]:
    """Perform chronological train-test split avoiding data leakage."""
    features_df = create_features(df)
    n_rows = len(features_df)
    split_idx = int(n_rows * (1.0 - test_ratio))

    train_df = features_df.iloc[:split_idx].copy().reset_index(drop=True)
    test_df = features_df.iloc[split_idx:].copy().reset_index(drop=True)

    return {
        "full": features_df,
        "train": train_df,
        "test": test_df,
        "X_train_solar": train_df[SOLAR_FEATURES],
        "y_train_solar": train_df["solar_kw"].values,
        "X_test_solar": test_df[SOLAR_FEATURES],
        "y_test_solar": test_df["solar_kw"].values,
        "X_train_wind": train_df[WIND_FEATURES],
        "y_train_wind": train_df["wind_kw"].values,
        "X_test_wind": test_df[WIND_FEATURES],
        "y_test_wind": test_df["wind_kw"].values,
    }


if __name__ == "__main__":
    from forecasting.data_loader import load_dataset
    raw_df, mode = load_dataset(days=14)
    splits = prepare_train_test_split(raw_df)
    print(f"Data Mode: {mode}")
    print(f"Total engineered records: {len(splits['full'])}")
    print(f"Train records: {len(splits['train'])}, Test records: {len(splits['test'])}")
    print(f"Solar features count: {len(SOLAR_FEATURES)}, Wind features count: {len(WIND_FEATURES)}")
    print("\nFirst row solar features:")
    print(splits["X_train_solar"].iloc[0].to_dict())
