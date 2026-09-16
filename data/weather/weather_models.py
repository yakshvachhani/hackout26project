"""
Standardized Weather Telemetry and Forecast Data Models.
Provides typed definitions for Open-Meteo, NASA POWER, and Fallback services.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class WeatherSource(str, Enum):
    LIVE = "LIVE"
    CACHED = "CACHED"
    FALLBACK = "FALLBACK"


@dataclass
class WeatherInterval:
    interval: int
    timestamp: str
    time_str: str
    solar_irradiance_wm2: float
    wind_speed_ms: float
    temperature_c: float
    cloud_cover_pct: float
    weather_code: int = 0
    condition: str = "Clear"


@dataclass
class WeatherSnapshot:
    timestamp: str
    source: WeatherSource
    provider: str  # e.g. "Open-Meteo", "NASA-POWER", "FallbackEngine"
    condition: str
    temperature_c: float
    solar_irradiance_wm2: float
    wind_speed_ms: float
    cloud_cover_pct: float
    advisory: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "source": self.source.value,
            "provider": self.provider,
            "condition": self.condition,
            "temperature_c": round(self.temperature_c, 1),
            "solar_irradiance_wm2": round(self.solar_irradiance_wm2, 1),
            "wind_speed_ms": round(self.wind_speed_ms, 1),
            "cloud_cover_pct": round(self.cloud_cover_pct, 1),
            "advisory": self.advisory,
        }


@dataclass
class WeatherForecastSeries:
    source: WeatherSource
    provider: str
    created_at: str
    duration_hours: int
    intervals: List[WeatherInterval] = field(default_factory=list)

    @property
    def total_intervals(self) -> int:
        return len(self.intervals)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source.value,
            "provider": self.provider,
            "created_at": self.created_at,
            "duration_hours": self.duration_hours,
            "total_intervals": len(self.intervals),
            "timestamps": [it.timestamp for it in self.intervals],
            "time_strings": [it.time_str for it in self.intervals],
            "solar_irradiance_wm2": [it.solar_irradiance_wm2 for it in self.intervals],
            "wind_speed_ms": [it.wind_speed_ms for it in self.intervals],
            "temperature_c": [it.temperature_c for it in self.intervals],
            "cloud_cover_pct": [it.cloud_cover_pct for it in self.intervals],
            "conditions": [it.condition for it in self.intervals],
        }
