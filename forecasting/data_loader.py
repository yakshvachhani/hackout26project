"""Data loader for weather data ingestion from Open-Meteo API with synthetic fallback."""

import logging
import math
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

# Ensure repository root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import requests

from forecasting.config import (
    DEFAULT_SOLAR_CAPACITY_KW,
    DEFAULT_WIND_CAPACITY_KW,
    HISTORICAL_DAYS,
    LATITUDE,
    LONGITUDE,
    OPEN_METEO_ARCHIVE_URL,
    OPEN_METEO_FORECAST_URL,
)

logger = logging.getLogger("forecasting.data_loader")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def calculate_solar_generation(
    shortwave_radiation: np.ndarray,
    temperature_2m: np.ndarray,
    capacity_kw: float = DEFAULT_SOLAR_CAPACITY_KW,
) -> np.ndarray:
    """Calculate solar output (kW) using standard PV cell temperature and irradiance model.
    
    P = Capacity * (G / 1000) * (1 - gamma * (T_cell - 25)) * eta_inverter
    """
    g = np.maximum(0.0, np.asarray(shortwave_radiation, dtype=float))
    t_amb = np.asarray(temperature_2m, dtype=float)
    
    # Nominal operating cell temperature NOCT ~ 45 C
    t_cell = t_amb + (45.0 - 20.0) / 800.0 * g
    # Temperature derating coeff ~ -0.4% per C above 25 C
    gamma = 0.004
    temp_factor = np.maximum(0.70, 1.0 - gamma * np.maximum(0.0, t_cell - 25.0))
    inverter_eff = 0.96
    
    raw_power = capacity_kw * (g / 1000.0) * temp_factor * inverter_eff
    # Clip at rated capacity
    return np.clip(np.round(raw_power, 2), 0.0, capacity_kw)


def calculate_wind_generation(
    wind_speed_80m: np.ndarray,
    capacity_kw: float = DEFAULT_WIND_CAPACITY_KW,
) -> np.ndarray:
    """Calculate wind generation (kW) using standard turbine power curve.
    
    Cut-in: 3.0 m/s (~10.8 km/h)
    Rated: 12.0 m/s (~43.2 km/h)
    Cut-out: 25.0 m/s (~90.0 km/h)
    """
    speeds = np.maximum(0.0, np.asarray(wind_speed_80m, dtype=float))
    
    # If speed values are likely in km/h (> 35 for typical mean), convert to m/s
    if np.nanmedian(speeds) > 20.0:
        speeds_ms = speeds / 3.6
    else:
        speeds_ms = speeds
        
    v_in = 3.0
    v_rated = 12.0
    v_out = 25.0
    
    power = np.zeros_like(speeds_ms)
    
    # Between cut-in and rated: cubic scaling
    cubic_mask = (speeds_ms >= v_in) & (speeds_ms < v_rated)
    power[cubic_mask] = capacity_kw * ((speeds_ms[cubic_mask] ** 3 - v_in ** 3) / (v_rated ** 3 - v_in ** 3))
    
    # Between rated and cut-out: rated capacity
    rated_mask = (speeds_ms >= v_rated) & (speeds_ms <= v_out)
    power[rated_mask] = capacity_kw
    
    # Above cut-out or below cut-in: 0.0 kW
    return np.clip(np.round(power, 2), 0.0, capacity_kw)


def determine_weather_condition(cloud_cover: float, wind_speed_10m: float, solar_kw: float, hour: int) -> str:
    """Determine descriptive weather condition string matching backend data schema."""
    if wind_speed_10m > 40.0:
        return "storm"
    if 20 <= hour or hour <= 5 or solar_kw <= 0.05:
        return "night"
    if cloud_cover < 25.0:
        return "clear"
    elif cloud_cover < 75.0:
        return "partly cloudy"
    else:
        return "cloudy"


def generate_synthetic_weather(
    days: int = HISTORICAL_DAYS,
    base_time: datetime = None,
) -> pd.DataFrame:
    """Generate physically plausible hourly weather dataset with diurnal curves and noise."""
    if base_time is None:
        base_time = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(days=days)

    total_hours = days * 24
    records = []
    
    # Ambient weather states modeled with persistent transitions
    cloud_state = 25.0
    wind_state = 12.0

    for i in range(total_hours):
        current_time = base_time + timedelta(hours=i)
        hour = current_time.hour
        day_of_year = current_time.timetuple().tm_yday

        # Diurnal solar cycle
        # Ahmedabad approx: sunrise ~06:00, noon ~12:30, sunset ~19:00
        solar_elevation = 0.0
        if 6 <= hour <= 19:
            # Solar peak at 12:45
            solar_elevation = math.sin((hour - 6) * math.pi / 13.5)
            solar_elevation = max(0.0, solar_elevation)
            
        # Cloud cover with Markovian drift
        cloud_delta = random.uniform(-15.0, 15.0)
        cloud_state = max(0.0, min(100.0, cloud_state + cloud_delta))
        
        # Occasional cloudy front
        if random.random() < 0.05:
            cloud_state = random.uniform(70.0, 100.0)
            
        # Solar radiation: Clear-sky max ~950 W/m2 attenuated by clouds
        clear_sky_rad = 950.0 * (solar_elevation ** 1.1)
        cloud_transmission = (1.0 - 0.75 * ((cloud_state / 100.0) ** 2.5))
        radiation = max(0.0, clear_sky_rad * cloud_transmission * random.uniform(0.92, 1.04))
        if solar_elevation <= 0:
            radiation = 0.0

        # Temperature: Diurnal swing with min at 05:00, max at 15:00, mean ~30 C in Ahmedabad
        base_temp = 31.0 + 3.0 * math.sin((day_of_year - 80) * 2 * math.pi / 365)
        diurnal_temp = 5.5 * math.sin((hour - 8) * math.pi / 12)
        temp_2m = round(base_temp + diurnal_temp - 0.05 * cloud_state + random.gauss(0, 0.8), 2)
        humidity = max(15.0, min(95.0, 65.0 - 1.2 * diurnal_temp + 0.3 * cloud_state + random.gauss(0, 3)))

        # Wind speed (10m and 80m hub height)
        # Higher in afternoon due to thermal mixing
        thermal_wind = 4.0 * max(0.0, math.sin((hour - 10) * math.pi / 10))
        wind_delta = random.gauss(0, 1.5)
        wind_state = max(4.0, min(38.0, wind_state + 0.2 * (10.0 - wind_state) + wind_delta))
        speed_10m = round(wind_state + thermal_wind, 2)
        # Power law wind shear alpha ~ 0.18
        speed_80m = round(speed_10m * ((80.0 / 10.0) ** 0.18) + random.gauss(0, 0.5), 2)

        records.append({
            "timestamp": current_time.isoformat(),
            "time": current_time,
            "temperature_2m": temp_2m,
            "relative_humidity_2m": round(humidity, 1),
            "cloud_cover": round(cloud_state, 1),
            "shortwave_radiation": round(radiation, 2),
            "wind_speed_10m": speed_10m,
            "wind_speed_80m": speed_80m,
        })

    df = pd.DataFrame(records)
    return df


def fetch_open_meteo_history(
    days: int = HISTORICAL_DAYS,
    latitude: float = LATITUDE,
    longitude: float = LONGITUDE,
) -> pd.DataFrame:
    """Pull historical hourly weather data from Open-Meteo API."""
    # We use the forecast endpoint with past_days for reliable, zero-latency recent historical data
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "past_days": days,
        "forecast_days": 2,
        "hourly": "temperature_2m,relative_humidity_2m,cloud_cover,shortwave_radiation,wind_speed_10m,wind_speed_80m",
        "timezone": "auto",
    }
    
    response = requests.get(OPEN_METEO_FORECAST_URL, params=params, timeout=12)
    response.raise_for_status()
    payload = response.json()
    
    hourly = payload["hourly"]
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
    })
    
    # Fill any null values if present
    df = df.ffill().bfill()
    return df


def load_dataset(
    days: int = HISTORICAL_DAYS,
    force_synthetic: bool = False,
    solar_capacity_kw: float = DEFAULT_SOLAR_CAPACITY_KW,
    wind_capacity_kw: float = DEFAULT_WIND_CAPACITY_KW,
) -> Tuple[pd.DataFrame, str]:
    """Load weather dataset either from Open-Meteo or synthetic fallback, with generation metrics."""
    mode = "LIVE_OPEN_METEO"
    df = None
    
    if not force_synthetic:
        try:
            logger.info("Connecting to Open-Meteo API for historical data (%d days)...", days)
            df = fetch_open_meteo_history(days=days)
            logger.info("[DATA MODE] LIVE_OPEN_METEO - Successfully fetched %d hourly records.", len(df))
            mode = "LIVE_OPEN_METEO"
        except Exception as err:
            logger.warning("[DATA MODE] LIVE_OPEN_METEO pull failed (%s). Activating SYNTHETIC_FALLBACK.", err)
            df = generate_synthetic_weather(days=days)
            mode = "SYNTHETIC_FALLBACK"
            logger.info("[DATA MODE] SYNTHETIC_FALLBACK - Generated %d hourly synthetic records.", len(df))
    else:
        df = generate_synthetic_weather(days=days)
        mode = "SYNTHETIC_FALLBACK"
        logger.info("[DATA MODE] SYNTHETIC_FALLBACK - Force synthetic enabled (%d records).", len(df))

    # Compute physical generation targets
    df["solar_kw"] = calculate_solar_generation(
        df["shortwave_radiation"].values,
        df["temperature_2m"].values,
        capacity_kw=solar_capacity_kw,
    )
    df["wind_kw"] = calculate_wind_generation(
        df["wind_speed_80m"].values,
        capacity_kw=wind_capacity_kw,
    )
    
    # Compute weather condition labels
    hours = df["time"].apply(lambda t: t.hour)
    df["weather_condition"] = [
        determine_weather_condition(c, w, s, h)
        for c, w, s, h in zip(df["cloud_cover"], df["wind_speed_10m"], df["solar_kw"], hours)
    ]
    
    return df, mode


if __name__ == "__main__":
    test_df, active_mode = load_dataset(days=14)
    print(f"\nActive Data Mode: {active_mode}")
    print(f"Total Rows: {len(test_df)}")
    print("\nSample Records:")
    print(test_df[["timestamp", "temperature_2m", "shortwave_radiation", "wind_speed_80m", "solar_kw", "wind_kw", "weather_condition"]].head())
