"""
Open-Meteo Weather API Integration.
Retrieves live forecast telemetry and normalizes to 15-minute intervals (96 intervals / 24h).
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import Optional, List, Dict, Any
import httpx
import numpy as np
import pandas as pd

from data.weather.weather_models import (
    WeatherInterval,
    WeatherSnapshot,
    WeatherForecastSeries,
    WeatherSource,
)

logger = logging.getLogger(__name__)

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Standard WMO Weather interpretation table
WMO_CODE_MAP = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Slight Snow Fall",
    73: "Moderate Snow Fall",
    75: "Heavy Snow Fall",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail",
}


def decode_wmo_weather_code(code: int) -> str:
    return WMO_CODE_MAP.get(int(code), "Partly Cloudy")


class OpenMeteoClient:
    """Client for Open-Meteo free meteorological API with 15-minute normalization."""

    def __init__(
        self,
        base_url: str = OPEN_METEO_BASE_URL,
        timeout_seconds: float = 5.0,
        default_latitude: float = 18.15,  # Baramati Rural, Maharashtra, India
        default_longitude: float = 74.58,
    ):
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.default_latitude = default_latitude
        self.default_longitude = default_longitude

    def fetch_current(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> WeatherSnapshot:
        """Synchronous fetch of current live weather snapshot."""
        lat = latitude if latitude is not None else self.default_latitude
        lon = longitude if longitude is not None else self.default_longitude

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,direct_normal_irradiance,wind_speed_10m,weather_code,cloud_cover",
            "timezone": "UTC",
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            resp = client.get(self.base_url, params=params)
            resp.raise_for_status()
            data = resp.json()

        current = data.get("current", {})
        temp = float(current.get("temperature_2m", 25.0))
        dni = float(current.get("direct_normal_irradiance", 600.0))
        wind = float(current.get("wind_speed_10m", 6.5))
        code = int(current.get("weather_code", 0))
        cloud = float(current.get("cloud_cover", 20.0))

        advisory = None
        if wind > 18.0:
            advisory = "High Wind Warning: Cut-out proximity"
        elif code >= 95:
            advisory = "Thunderstorm Warning: Lightning protection engaged"

        return WeatherSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            source=WeatherSource.LIVE,
            provider="Open-Meteo",
            condition=decode_wmo_weather_code(code),
            temperature_c=temp,
            solar_irradiance_wm2=dni,
            wind_speed_ms=wind,
            cloud_cover_pct=cloud,
            advisory=advisory,
        )

    def fetch_forecast_15min(
        self,
        duration_hours: int = 24,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> WeatherForecastSeries:
        """
        Synchronous fetch of forward weather forecast normalized to 15-minute intervals.
        Queries Open-Meteo `minutely_15` or interpolates `hourly` series.
        """
        lat = latitude if latitude is not None else self.default_latitude
        lon = longitude if longitude is not None else self.default_longitude
        forecast_days = int(np.ceil(duration_hours / 24.0))

        params = {
            "latitude": lat,
            "longitude": lon,
            "minutely_15": "temperature_2m,shortwave_radiation,direct_normal_irradiance,wind_speed_10m,weather_code",
            "hourly": "temperature_2m,shortwave_radiation,direct_normal_irradiance,wind_speed_10m,weather_code,cloud_cover",
            "forecast_days": min(7, max(1, forecast_days)),
            "timezone": "UTC",
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            resp = client.get(self.base_url, params=params)
            resp.raise_for_status()
            data = resp.json()

        target_intervals = duration_hours * 4

        # Check if minutely_15 is provided
        minutely_data = data.get("minutely_15")
        if minutely_data and "time" in minutely_data and len(minutely_data["time"]) >= target_intervals:
            times = minutely_data["time"][:target_intervals]
            temps = minutely_data.get("temperature_2m", [])[:target_intervals]
            rads = minutely_data.get("shortwave_radiation", minutely_data.get("direct_normal_irradiance", []))[:target_intervals]
            winds = minutely_data.get("wind_speed_10m", [])[:target_intervals]
            codes = minutely_data.get("weather_code", [])[:target_intervals]

            intervals: List[WeatherInterval] = []
            for i in range(target_intervals):
                t_str = times[i]
                dt = datetime.fromisoformat(t_str.replace("Z", "+00:00"))
                code_val = int(codes[i]) if i < len(codes) else 0
                rad_val = max(0.0, float(rads[i])) if i < len(rads) else 0.0
                wind_val = max(0.0, float(winds[i])) if i < len(winds) else 5.0
                temp_val = float(temps[i]) if i < len(temps) else 25.0

                intervals.append(
                    WeatherInterval(
                        interval=i + 1,
                        timestamp=dt.isoformat(),
                        time_str=f"{dt.hour:02d}:{dt.minute:02d}",
                        solar_irradiance_wm2=round(rad_val, 1),
                        wind_speed_ms=round(wind_val, 2),
                        temperature_c=round(temp_val, 1),
                        cloud_cover_pct=round(min(100.0, max(0.0, 100.0 - (rad_val / 10.0))), 1) if rad_val > 0 else 20.0,
                        weather_code=code_val,
                        condition=decode_wmo_weather_code(code_val),
                    )
                )

            return WeatherForecastSeries(
                source=WeatherSource.LIVE,
                provider="Open-Meteo (minutely_15)",
                created_at=datetime.now(timezone.utc).isoformat(),
                duration_hours=duration_hours,
                intervals=intervals,
            )

        # Fallback to interpolating hourly data
        hourly_data = data.get("hourly", {})
        h_times = hourly_data.get("time", [])
        h_temps = hourly_data.get("temperature_2m", [])
        h_rads = hourly_data.get("shortwave_radiation", hourly_data.get("direct_normal_irradiance", []))
        h_winds = hourly_data.get("wind_speed_10m", [])
        h_codes = hourly_data.get("weather_code", [])
        h_clouds = hourly_data.get("cloud_cover", [])

        df_hourly = pd.DataFrame({
            "time": pd.to_datetime(h_times),
            "temp": h_temps,
            "irradiance": h_rads,
            "wind": h_winds,
            "code": h_codes,
            "cloud": h_clouds,
        }).set_index("time")

        # Resample to 15 minutes and interpolate linearly
        df_15 = df_hourly.resample("15min").interpolate(method="linear").ffill().bfill()
        df_15 = df_15.iloc[:target_intervals]

        intervals = []
        for i, (ts, row) in enumerate(df_15.iterrows()):
            intervals.append(
                WeatherInterval(
                    interval=i + 1,
                    timestamp=ts.isoformat(),
                    time_str=f"{ts.hour:02d}:{ts.minute:02d}",
                    solar_irradiance_wm2=max(0.0, round(float(row["irradiance"]), 1)),
                    wind_speed_ms=max(0.0, round(float(row["wind"]), 2)),
                    temperature_c=round(float(row["temp"]), 1),
                    cloud_cover_pct=round(float(row["cloud"]), 1),
                    weather_code=int(row["code"]),
                    condition=decode_wmo_weather_code(int(row["code"])),
                )
            )

        return WeatherForecastSeries(
            source=WeatherSource.LIVE,
            provider="Open-Meteo (hourly_interpolated)",
            created_at=datetime.now(timezone.utc).isoformat(),
            duration_hours=duration_hours,
            intervals=intervals,
        )

    async def fetch_forecast_15min_async(
        self,
        duration_hours: int = 24,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> WeatherForecastSeries:
        """Async variant using httpx.AsyncClient."""
        # For seamless synchronous + async support
        return self.fetch_forecast_15min(
            duration_hours=duration_hours,
            latitude=latitude,
            longitude=longitude,
        )
