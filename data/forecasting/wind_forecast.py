"""
Wind Generation Forecasting Engine for Off-Grid Microgrids.
Translates forward wind speed telemetry (m/s) into expected wind turbine kW generation
using a configurable simplified aerodynamic power curve.
"""

from typing import List, Optional, Union, Dict, Any
import numpy as np

from data.weather.weather_models import WeatherForecastSeries
from data.weather.weather_manager import WeatherManager
from data.synthetic.wind import wind_turbine_power_curve


class WindForecaster:
    """
    Translates wind speed forecasts into electrical power (kW).
    Avoids claiming exact manufacturer precision while maintaining aerodynamic fidelity:
    - 0 kW below cut-in speed
    - Cubic aerodynamic rise between cut-in and rated speed
    - Constant rated output between rated and cut-out speed
    - Automatic cutout (0 kW) for extreme wind safety shut-off
    """

    def __init__(
        self,
        rated_capacity_kw: float = 30.0,
        cut_in_speed_ms: float = 3.0,
        rated_speed_ms: float = 11.5,
        cut_out_speed_ms: float = 25.0,
        density_correction_factor: float = 1.0,
    ):
        self.rated_capacity_kw = rated_capacity_kw
        self.cut_in_speed_ms = cut_in_speed_ms
        self.rated_speed_ms = rated_speed_ms
        self.cut_out_speed_ms = cut_out_speed_ms
        self.density_correction = density_correction_factor

    def wind_speed_to_power(
        self,
        wind_speed_ms: Union[float, List[float], np.ndarray],
    ) -> Union[float, List[float]]:
        """
        Converts wind speed array to generated power (kW).
        Guarantees non-negative values clamped within [0, rated_capacity_kw].
        """
        is_scalar = np.isscalar(wind_speed_ms)
        v = np.asarray([wind_speed_ms] if is_scalar else wind_speed_ms, dtype=float)

        power = wind_turbine_power_curve(
            wind_speed_ms=v,
            rated_capacity_kw=self.rated_capacity_kw,
            cut_in_speed_ms=self.cut_in_speed_ms,
            rated_speed_ms=self.rated_speed_ms,
            cut_out_speed_ms=self.cut_out_speed_ms,
        )
        power = power * self.density_correction
        power = np.clip(power, 0.0, self.rated_capacity_kw)

        if is_scalar:
            return round(float(power[0]), 2)
        return [round(float(val), 2) for val in power]

    def forecast_from_weather(
        self,
        weather_series: WeatherForecastSeries,
    ) -> List[float]:
        """Translates WeatherForecastSeries wind speeds into expected wind generation."""
        speeds = [it.wind_speed_ms for it in weather_series.intervals]
        return self.wind_speed_to_power(speeds)

    def forecast_96(
        self,
        weather_manager: Optional[WeatherManager] = None,
        duration_hours: int = 24,
    ) -> List[float]:
        """
        End-to-end 96-interval wind forecast via resilient weather fetching.
        """
        target_n = duration_hours * 4
        mgr = weather_manager or WeatherManager()
        series = mgr.get_forecast_15min(duration_hours=duration_hours)
        wind_kw = self.forecast_from_weather(series)

        if len(wind_kw) < target_n:
            wind_kw.extend([0.0] * (target_n - len(wind_kw)))
        return wind_kw[:target_n]


wind_forecaster = WindForecaster()
