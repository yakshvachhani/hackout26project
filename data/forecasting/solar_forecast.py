"""
Solar Generation Forecasting Engine for Off-Grid Microgrids.
Converts solar irradiance (GHI/DNI) and temperature into expected PV kW output.
Formula:
  P_pv = PV_capacity * (GHI / 1000) * efficiency * [1 - temp_coeff * (T_cell - 25°C)]
"""

from typing import List, Optional, Union, Dict, Any
import numpy as np

from data.weather.weather_models import WeatherForecastSeries
from data.weather.weather_manager import WeatherManager
from data.synthetic.solar import generate_solar_profile


class SolarForecaster:
    """
    Translates weather forecast irradiance and temperature into AC electrical power output.
    """

    def __init__(
        self,
        pv_capacity_kw: float = 60.0,
        panel_efficiency: float = 0.90,  # Combined inverter + cable + soiling efficiency
        temp_coefficient: float = 0.004,  # -0.4% per degree C above STC (25C)
        stc_irradiance: float = 1000.0,  # Standard Test Conditions W/m^2
    ):
        self.pv_capacity_kw = pv_capacity_kw
        self.panel_efficiency = panel_efficiency
        self.temp_coefficient = temp_coefficient
        self.stc_irradiance = stc_irradiance

    def irradiance_to_power(
        self,
        irradiance_wm2: Union[float, List[float], np.ndarray],
        temperature_c: Optional[Union[float, List[float], np.ndarray]] = None,
    ) -> Union[float, List[float]]:
        """
        Calculates expected solar kW generation from irradiance and temperature.
        Guarantees:
        - 0 kW at night / zero irradiance
        - Strict upper clamp to installed PV capacity
        - Strict lower clamp to 0.0 kW (no negative generation)
        """
        is_scalar = np.isscalar(irradiance_wm2)
        irr_arr = np.asarray([irradiance_wm2] if is_scalar else irradiance_wm2, dtype=float)
        
        if temperature_c is None:
            temp_arr = np.full_like(irr_arr, 25.0)
        else:
            temp_arr = np.asarray([temperature_c] if np.isscalar(temperature_c) else temperature_c, dtype=float)

        # Standard cell temperature approximation: T_cell = T_ambient + (NOCT - 20) * (GHI / 800)
        # Assuming NOCT = 45C:
        t_cell = temp_arr + (25.0 * (irr_arr / 800.0))
        temp_derate = 1.0 - self.temp_coefficient * (t_cell - 25.0)
        temp_derate = np.clip(temp_derate, 0.70, 1.05)

        # Base power
        raw_power = self.pv_capacity_kw * (irr_arr / self.stc_irradiance) * self.panel_efficiency * temp_derate
        
        # Zero out tiny irradiance (< 5 W/m^2) to prevent ghost night generation
        raw_power[irr_arr < 5.0] = 0.0

        clamped_power = np.clip(raw_power, 0.0, self.pv_capacity_kw)

        if is_scalar:
            return round(float(clamped_power[0]), 2)
        return [round(float(val), 2) for val in clamped_power]

    def forecast_from_weather(
        self,
        weather_series: WeatherForecastSeries,
    ) -> List[float]:
        """Converts a WeatherForecastSeries directly to expected solar kW."""
        irradiances = [it.solar_irradiance_wm2 for it in weather_series.intervals]
        temperatures = [it.temperature_c for it in weather_series.intervals]
        return self.irradiance_to_power(irradiances, temperatures)

    def forecast_96(
        self,
        weather_manager: Optional[WeatherManager] = None,
        duration_hours: int = 24,
    ) -> List[float]:
        """
        End-to-end 96-interval solar forecast.
        Fetches resilient weather (LIVE -> CACHED -> FALLBACK) and converts to PV generation.
        """
        target_n = duration_hours * 4
        mgr = weather_manager or WeatherManager()
        series = mgr.get_forecast_15min(duration_hours=duration_hours)
        solar_kw = self.forecast_from_weather(series)

        # Ensure exact length
        if len(solar_kw) < target_n:
            # Pad with zero night generation or fallback
            solar_kw.extend([0.0] * (target_n - len(solar_kw)))
        return solar_kw[:target_n]


solar_forecaster = SolarForecaster()
