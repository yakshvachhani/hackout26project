"""
Weather package for OptiGrid-AI.
Exports weather models, Open-Meteo, NASA POWER, and resilient WeatherManager.
"""

from data.weather.weather_models import (
    WeatherSource,
    WeatherSnapshot,
    WeatherForecastSeries,
    WeatherInterval,
)
from data.weather.open_meteo import OpenMeteoClient
from data.weather.nasa_power import NasaPowerClient
from data.weather.weather_manager import WeatherManager

__all__ = [
    "WeatherSource",
    "WeatherSnapshot",
    "WeatherForecastSeries",
    "WeatherInterval",
    "OpenMeteoClient",
    "NasaPowerClient",
    "WeatherManager",
]
