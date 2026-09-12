"""Configuration and constants for the renewable and demand forecasting pipeline."""

from pathlib import Path

# Geographical microgrid site location (Ahmedabad, Gujarat, India)
LATITUDE = 23.0225
LONGITUDE = 72.5714
CITY_NAME = "Ahmedabad, Gujarat, India"
TIMEZONE = "Asia/Kolkata"

# Default rated capacities (kW) matching microgrid simulation baseline
DEFAULT_SOLAR_CAPACITY_KW = 100.0
DEFAULT_WIND_CAPACITY_KW = 100.0

# Data window
HISTORICAL_DAYS = 90
DEFAULT_FORECAST_HORIZON_HOURS = 48

# Open-Meteo Archive API URL
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Meteorological features pulled from Open-Meteo
WEATHER_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "cloud_cover",
    "shortwave_radiation",
    "wind_speed_10m",
    "wind_speed_80m",
]

# Lag parameters (in hours)
LAG_HOURS = [1, 2, 3]

# File system paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
PLOT_PATH = BASE_DIR / "predicted_vs_actual.png"
