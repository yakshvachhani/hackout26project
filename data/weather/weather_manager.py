"""
Weather Manager with Multi-Tier Fallback Hierarchy.
Ensures zero-downtime resilient weather telemetry:
  1. Primary: Live Open-Meteo API (LIVE)
  2. Secondary: Live NASA POWER API (LIVE)
  3. Tertiary: Local Cached Forecast (CACHED)
  4. Quaternary: Physics-informed Synthetic Default (FALLBACK)
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Tuple

from data.weather.weather_models import (
    WeatherSource,
    WeatherSnapshot,
    WeatherForecastSeries,
    WeatherInterval,
)
from data.weather.open_meteo import OpenMeteoClient
from data.weather.nasa_power import NasaPowerClient
from data.synthetic.solar import generate_solar_profile
from data.synthetic.wind import generate_wind_profile

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent.parent / "datasets" / "cache"


class WeatherManager:
    """
    Manages live API queries, cache invalidation, and deterministic fallback.
    """

    def __init__(
        self,
        open_meteo_client: Optional[OpenMeteoClient] = None,
        nasa_client: Optional[NasaPowerClient] = None,
        cache_dir: Path = CACHE_DIR,
        cache_ttl_hours: float = 6.0,
    ):
        self.open_meteo = open_meteo_client or OpenMeteoClient()
        self.nasa_power = nasa_client or NasaPowerClient()
        self.cache_dir = cache_dir
        self.cache_ttl_hours = cache_ttl_hours
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.forecast_cache_file = self.cache_dir / "last_forecast_cache.json"
        self.current_cache_file = self.cache_dir / "last_current_cache.json"

    def get_forecast_15min(
        self,
        duration_hours: int = 24,
        force_refresh: bool = False,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> WeatherForecastSeries:
        """
        Executes fallback chain to retrieve 15-minute weather forecast.
        Returns WeatherForecastSeries with source explicitly marked as LIVE, CACHED, or FALLBACK.
        """
        # Step 1: Attempt Live Open-Meteo
        try:
            logger.info("Attempting primary weather forecast: Open-Meteo")
            series = self.open_meteo.fetch_forecast_15min(
                duration_hours=duration_hours,
                latitude=latitude,
                longitude=longitude,
            )
            self._save_forecast_cache(series, latitude=latitude, longitude=longitude)
            return series
        except Exception as e:
            logger.warning(f"Open-Meteo forecast failed: {e}")

        # Step 2: Attempt Live NASA POWER
        try:
            logger.info("Attempting secondary weather forecast: NASA POWER")
            series = self.nasa_power.fetch_forecast_15min(
                duration_hours=duration_hours,
                latitude=latitude,
                longitude=longitude,
            )
            self._save_forecast_cache(series, latitude=latitude, longitude=longitude)
            return series
        except Exception as e:
            logger.warning(f"NASA POWER forecast failed: {e}")

        # Step 3: Attempt Cached Forecast
        cached_series = self._load_forecast_cache(duration_hours, latitude=latitude, longitude=longitude)
        if cached_series is not None:
            logger.info("Using cached weather forecast matching requested coordinates.")
            return cached_series

        # Step 4: Synthetic Default Fallback
        logger.warning("All live and cached weather services unavailable; deploying synthetic physics fallback.")
        return self._generate_synthetic_fallback_forecast(duration_hours=duration_hours)

    def get_current_weather(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> WeatherSnapshot:
        """
        Retrieves current weather snapshot through fallback chain.
        """
        try:
            snap = self.open_meteo.fetch_current(latitude=latitude, longitude=longitude)
            self._save_current_cache(snap, latitude=latitude, longitude=longitude)
            return snap
        except Exception as e:
            logger.warning(f"Live current weather fetch failed: {e}")

        # Check cache with coordinate matching
        cached_snap = self._load_current_cache(latitude=latitude, longitude=longitude)
        if cached_snap is not None:
            return cached_snap

        # Fallback snapshot
        return self._generate_synthetic_current_fallback()

    def _save_forecast_cache(
        self,
        series: WeatherForecastSeries,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ):
        try:
            data = series.to_dict()
            if latitude is not None:
                data["latitude"] = float(latitude)
            if longitude is not None:
                data["longitude"] = float(longitude)
            with open(self.forecast_cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to persist weather cache: {e}")

    def _load_forecast_cache(
        self,
        duration_hours: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Optional[WeatherForecastSeries]:
        if not self.forecast_cache_file.exists():
            return None
        try:
            with open(self.forecast_cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Coordinate comparison with strict 0.01 tolerance
            cached_lat = data.get("latitude")
            cached_lon = data.get("longitude")
            if latitude is not None:
                if cached_lat is None or abs(float(cached_lat) - float(latitude)) > 0.01:
                    logger.info(f"Cached forecast lat ({cached_lat}) != requested ({latitude}) > 0.01°. Rejecting stale cache.")
                    return None
            if longitude is not None:
                if cached_lon is None or abs(float(cached_lon) - float(longitude)) > 0.01:
                    logger.info(f"Cached forecast lon ({cached_lon}) != requested ({longitude}) > 0.01°. Rejecting stale cache.")
                    return None

            created_at = datetime.fromisoformat(data.get("created_at", "").replace("Z", "+00:00"))
            age_hours = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600.0
            if age_hours > self.cache_ttl_hours:
                logger.info(f"Cached weather expired ({age_hours:.1f}h > {self.cache_ttl_hours}h).")
            
            intervals = []
            target_n = duration_hours * 4
            raw_intervals = data.get("timestamps", [])
            limit = min(target_n, len(raw_intervals))

            for i in range(limit):
                intervals.append(
                    WeatherInterval(
                        interval=i + 1,
                        timestamp=data["timestamps"][i],
                        time_str=data["time_strings"][i],
                        solar_irradiance_wm2=float(data["solar_irradiance_wm2"][i]),
                        wind_speed_ms=float(data["wind_speed_ms"][i]),
                        temperature_c=float(data["temperature_c"][i]),
                        cloud_cover_pct=float(data["cloud_cover_pct"][i]),
                        condition=data["conditions"][i],
                    )
                )

            return WeatherForecastSeries(
                source=WeatherSource.CACHED,
                provider=f"Cached({data.get('provider', 'Historic')})",
                created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
                duration_hours=duration_hours,
                intervals=intervals,
            )
        except Exception as e:
            logger.warning(f"Failed to parse cached weather: {e}")
            return None

    def _save_current_cache(
        self,
        snap: WeatherSnapshot,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ):
        try:
            d = snap.to_dict()
            if latitude is not None:
                d["latitude"] = float(latitude)
            if longitude is not None:
                d["longitude"] = float(longitude)
            with open(self.current_cache_file, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to write current weather cache: {e}")

    def _load_current_cache(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Optional[WeatherSnapshot]:
        if not self.current_cache_file.exists():
            return None
        try:
            with open(self.current_cache_file, "r", encoding="utf-8") as f:
                d = json.load(f)

            # Coordinate tolerance 0.01 deg
            cached_lat = d.get("latitude")
            cached_lon = d.get("longitude")
            if latitude is not None:
                if cached_lat is None or abs(float(cached_lat) - float(latitude)) > 0.01:
                    logger.info(f"Cached current weather lat ({cached_lat}) != requested ({latitude}) > 0.01°. Rejecting stale cache.")
                    return None
            if longitude is not None:
                if cached_lon is None or abs(float(cached_lon) - float(longitude)) > 0.01:
                    logger.info(f"Cached current weather lon ({cached_lon}) != requested ({longitude}) > 0.01°. Rejecting stale cache.")
                    return None

            return WeatherSnapshot(
                timestamp=d["timestamp"],
                source=WeatherSource.CACHED,
                provider="LocalCache",
                condition=d["condition"],
                temperature_c=d["temperature_c"],
                solar_irradiance_wm2=d["solar_irradiance_wm2"],
                wind_speed_ms=d["wind_speed_ms"],
                cloud_cover_pct=d["cloud_cover_pct"],
                advisory="Using cached telemetry",
            )
        except Exception:
            return None

    def _generate_synthetic_fallback_forecast(self, duration_hours: int = 24) -> WeatherForecastSeries:
        """Generates physics-informed deterministic weather forecast when all networks fail."""
        target_intervals = duration_hours * 4
        solar_df = generate_solar_profile(duration_hours=duration_hours, pv_capacity_kw=60.0, seed=101)
        wind_df = generate_wind_profile(duration_hours=duration_hours, rated_capacity_kw=30.0, seed=101)

        intervals: List[WeatherInterval] = []
        for i in range(target_intervals):
            irr = float(solar_df["irradiance_wm2"].iloc[i])
            w_spd = float(wind_df["wind_speed_ms"].iloc[i])
            hour = i * 0.25 % 24
            temp = round(22.0 + 8.0 * max(0.0, 1.0 - abs(hour - 14.0) / 7.0), 1)
            cond = "Sunny" if irr > 500 else ("Partly Cloudy" if irr > 50 else "Clear Night")

            intervals.append(
                WeatherInterval(
                    interval=i + 1,
                    timestamp=solar_df["timestamp"].iloc[i],
                    time_str=solar_df["time_str"].iloc[i],
                    solar_irradiance_wm2=irr,
                    wind_speed_ms=w_spd,
                    temperature_c=temp,
                    cloud_cover_pct=15.0 if irr > 300 else 40.0,
                    weather_code=0,
                    condition=cond,
                )
            )

        return WeatherForecastSeries(
            source=WeatherSource.FALLBACK,
            provider="DeterministicFallbackModel",
            created_at=datetime.now(timezone.utc).isoformat(),
            duration_hours=duration_hours,
            intervals=intervals,
        )

    def _generate_synthetic_current_fallback(self) -> WeatherSnapshot:
        now = datetime.now(timezone.utc)
        hour = now.hour
        is_day = 6 <= hour <= 18
        irr = 650.0 if is_day else 0.0
        return WeatherSnapshot(
            timestamp=now.isoformat(),
            source=WeatherSource.FALLBACK,
            provider="DeterministicFallbackModel",
            condition="Sunny" if is_day else "Clear Night",
            temperature_c=27.5 if is_day else 21.0,
            solar_irradiance_wm2=irr,
            wind_speed_ms=7.2,
            cloud_cover_pct=10.0,
            advisory="Offline Fallback Telemetry Active",
        )
