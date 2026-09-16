"""
NASA POWER API Weather Service Abstraction.
Decoupled client fetching hourly solar irradiance and meteorological data, normalized to 15-min intervals.
Endpoint: https://power.larc.nasa.gov/api/temporal/hourly/point
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import Optional, List, Dict, Any
import httpx
import numpy as np
import pandas as pd

from data.weather.weather_models import (
    WeatherInterval,
    WeatherForecastSeries,
    WeatherSnapshot,
    WeatherSource,
)

logger = logging.getLogger(__name__)

NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"


class NasaPowerClient:
    """
    Client for NASA Prediction of Worldwide Energy Resources (POWER) API.
    Provides independent solar (ALLSKY_SFC_SW_DWN) and wind (WS10M) data.
    """

    def __init__(
        self,
        base_url: str = NASA_POWER_BASE_URL,
        timeout_seconds: float = 6.0,
        default_latitude: float = 18.15,
        default_longitude: float = 74.58,
    ):
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.default_latitude = default_latitude
        self.default_longitude = default_longitude

    def fetch_forecast_15min(
        self,
        duration_hours: int = 24,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        target_date: Optional[datetime] = None,
    ) -> WeatherForecastSeries:
        """
        Fetches hourly parameters from NASA POWER and interpolates to 15-min intervals.
        Parameters:
        - ALLSKY_SFC_SW_DWN: All Sky Surface Shortwave Downward Irradiance (Wh/m^2 or W/m^2)
        - T2M: Temperature at 2 Meters (C)
        - WS10M: Wind Speed at 10 Meters (m/s)
        """
        lat = latitude if latitude is not None else self.default_latitude
        lon = longitude if longitude is not None else self.default_longitude
        
        # NASA POWER data typically has a 1-2 day latency for historical hourly;
        # We query the target date range or recent baseline
        ref_dt = target_date or (datetime.now(timezone.utc) - timedelta(days=2))
        start_str = ref_dt.strftime("%Y%m%d")
        end_dt = ref_dt + timedelta(hours=duration_hours)
        end_str = end_dt.strftime("%Y%m%d")

        params = {
            "parameters": "ALLSKY_SFC_SW_DWN,T2M,WS10M",
            "community": "RE",
            "longitude": lon,
            "latitude": lat,
            "start": start_str,
            "end": end_str,
            "format": "JSON",
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            resp = client.get(self.base_url, params=params)
            resp.raise_for_status()
            data = resp.json()

        properties = data.get("properties", {}).get("parameter", {})
        ghi_dict = properties.get("ALLSKY_SFC_SW_DWN", {})
        temp_dict = properties.get("T2M", {})
        wind_dict = properties.get("WS10M", {})

        if not ghi_dict:
            raise ValueError("NASA POWER returned empty parameter dictionary.")

        # Build hourly dataframe
        sorted_keys = sorted(ghi_dict.keys())
        rows = []
        for k in sorted_keys:
            # key format: "YYYYMMDDHH"
            try:
                dt_k = datetime.strptime(k, "%Y%m%d%H").replace(tzinfo=timezone.utc)
                g = max(0.0, float(ghi_dict.get(k, 0.0)))
                t = float(temp_dict.get(k, 25.0))
                w = max(0.0, float(wind_dict.get(k, 5.0)))
                # Missing data in NASA is often -999.0
                if g < -500: g = 0.0
                if t < -500: t = 25.0
                if w < -500: w = 5.0
                rows.append({"time": dt_k, "irradiance": g, "temp": t, "wind": w})
            except Exception:
                continue

        if not rows:
            raise ValueError("No valid hourly records parsed from NASA POWER response.")

        df_hourly = pd.DataFrame(rows).set_index("time")
        
        # Resample to 15-minute and interpolate
        target_intervals = duration_hours * 4
        df_15 = df_hourly.resample("15min").interpolate(method="linear").ffill().bfill()
        df_15 = df_15.iloc[:target_intervals]

        # Shift timestamps forward to align with requested optimization horizon starting now
        now_start = datetime.now(timezone.utc)
        start_horizon = datetime(now_start.year, now_start.month, now_start.day, 0, 0, 0, tzinfo=timezone.utc)

        intervals: List[WeatherInterval] = []
        for i in range(min(target_intervals, len(df_15))):
            ts = start_horizon + timedelta(minutes=15 * i)
            row = df_15.iloc[i]
            rad = max(0.0, round(float(row["irradiance"]), 1))
            cond = "Sunny" if rad > 400 else ("Partly Cloudy" if rad > 50 else "Clear Night")
            intervals.append(
                WeatherInterval(
                    interval=i + 1,
                    timestamp=ts.isoformat(),
                    time_str=f"{ts.hour:02d}:{ts.minute:02d}",
                    solar_irradiance_wm2=rad,
                    wind_speed_ms=max(0.0, round(float(row["wind"]), 2)),
                    temperature_c=round(float(row["temp"]), 1),
                    cloud_cover_pct=25.0 if rad > 200 else 60.0,
                    weather_code=0 if rad > 200 else 1,
                    condition=cond,
                )
            )

        return WeatherForecastSeries(
            source=WeatherSource.LIVE,
            provider="NASA-POWER",
            created_at=datetime.now(timezone.utc).isoformat(),
            duration_hours=duration_hours,
            intervals=intervals,
        )
