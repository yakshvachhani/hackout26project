"""
Deterministic Baseline Demand Forecasting for Off-Grid Microgrids.
Generates 96 fifteen-minute interval load forecasts based on historical profile matching,
diurnal decomposition, day-type adjustment, and continuity blending.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union, Dict, Any
import numpy as np
import pandas as pd

from data.synthetic.village_load import generate_village_load


class DemandForecaster:
    """
    Robust deterministic baseline forecaster:
    - Avoids false ML claims: uses physics-informed diurnal profile matching + exponential smoothing.
    - Blends recent observed demand to guarantee smooth continuity at forecast horizon origin (t=0).
    - Supports day-type scaling (weekday vs weekend / market day).
    - Always outputs strictly non-negative demand values.
    """

    def __init__(
        self,
        base_demand_kw: float = 22.0,
        peak_demand_kw: float = 68.0,
        default_horizon_intervals: int = 96,
    ):
        self.base_demand_kw = base_demand_kw
        self.peak_demand_kw = peak_demand_kw
        self.default_horizon_intervals = default_horizon_intervals

    def forecast_96(
        self,
        historical_demand: Optional[List[float]] = None,
        recent_observed_demand_kw: Optional[float] = None,
        start_time: Optional[Union[datetime, str]] = None,
        day_type: str = "weekday",
        temperature_forecast_c: Optional[List[float]] = None,
    ) -> List[float]:
        """
        Produces 96 15-minute demand forecast values (kW).

        Args:
            historical_demand: Optional list of historical load values. If provided (e.g. >=96 intervals),
                               the forecaster extracts the diurnal empirical profile.
            recent_observed_demand_kw: The immediate prior telemetry reading for smooth transition.
            start_time: Forecast start time.
            day_type: 'weekday', 'weekend', or 'market_day'.
            temperature_forecast_c: Optional temperature series to model cooling/fans load sensitivity.

        Returns:
            List of 96 demand values in kW.
        """
        n_intervals = self.default_horizon_intervals
        if start_time is None:
            now = datetime.now(timezone.utc)
            start_dt = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
        elif isinstance(start_time, str):
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        else:
            start_dt = start_time

        # Step 1: Base Diurnal Curve
        if historical_demand is not None and len(historical_demand) >= 96:
            # Use empirical historical diurnal average
            hist_arr = np.array(historical_demand, dtype=float)
            # Reshape into daily cycles of 96 intervals and take median/mean
            complete_days = len(hist_arr) // 96
            reshaped = hist_arr[: complete_days * 96].reshape((complete_days, 96))
            baseline_curve = np.mean(reshaped, axis=0)
        else:
            # Generate deterministic synthetic baseline profile
            df_base = generate_village_load(
                start_time=start_dt,
                duration_hours=24,
                base_demand_kw=self.base_demand_kw,
                peak_demand_kw=self.peak_demand_kw,
                seed=42,
                noise_std=0.0,  # Pure deterministic template
            )
            baseline_curve = df_base["demand_kw"].to_numpy()

        # Step 2: Day Type Adjustments
        # Weekend: morning shift later, lower clinic/school commercial load (-10%), higher evening home use (+10%)
        # Market day: heavy midday activity (+25% between 10:00 and 16:00)
        curve = baseline_curve.copy()
        if day_type.lower() == "weekend":
            for i in range(n_intervals):
                hour = i * 0.25
                if 8.0 <= hour <= 16.0:
                    curve[i] *= 0.90
                elif 18.0 <= hour <= 22.0:
                    curve[i] *= 1.08
        elif day_type.lower() == "market_day":
            for i in range(n_intervals):
                hour = i * 0.25
                if 9.0 <= hour <= 16.0:
                    curve[i] *= 1.25

        # Step 3: Temperature Sensitivity (cooling / fans in tropical off-grid mini-grids)
        if temperature_forecast_c is not None and len(temperature_forecast_c) >= n_intervals:
            temp_arr = np.array(temperature_forecast_c[:n_intervals], dtype=float)
            # Increase demand by ~1.2% per degree above 26C
            cooling_factors = 1.0 + np.maximum(0.0, (temp_arr - 26.0) * 0.012)
            curve *= cooling_factors

        # Step 4: Continuity Blending with recent observation
        if recent_observed_demand_kw is not None and recent_observed_demand_kw > 0:
            offset = recent_observed_demand_kw - curve[0]
            # Exponential decay of offset over 8 intervals (2 hours)
            decay = np.exp(-np.arange(n_intervals) / 8.0)
            curve += offset * decay

        # Step 5: Enforce non-negativity and minimum baseload
        curve = np.maximum(self.base_demand_kw * 0.7, curve)
        return [round(float(val), 2) for val in curve]

    def forecast_detailed(
        self,
        start_time: Optional[Union[datetime, str]] = None,
        duration_hours: int = 24,
        recent_observed_demand_kw: Optional[float] = None,
        day_type: str = "weekday",
    ) -> Dict[str, Any]:
        """Returns structured forecast with timestamps and load priority breakdown."""
        n_intervals = duration_hours * 4
        if start_time is None:
            now = datetime.now(timezone.utc)
            start_dt = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
        elif isinstance(start_time, str):
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        else:
            start_dt = start_time

        values = self.forecast_96(
            recent_observed_demand_kw=recent_observed_demand_kw,
            start_time=start_dt,
            day_type=day_type,
        )

        timestamps = [(start_dt + timedelta(minutes=15 * i)).isoformat() for i in range(n_intervals)]
        time_strings = [(start_dt + timedelta(minutes=15 * i)).strftime("%H:%M") for i in range(n_intervals)]

        p0 = [round(v * 0.28, 2) for v in values]
        p1 = [round(v * 0.44, 2) for v in values]
        p2 = [round(max(0.0, values[i] - p0[i] - p1[i]), 2) for i in range(n_intervals)]

        return {
            "timestamps": timestamps,
            "time_strings": time_strings,
            "demand_kw": values,
            "p0_kw": p0,
            "p1_kw": p1,
            "p2_kw": p2,
            "day_type": day_type,
            "method": "deterministic_diurnal_decomposition",
        }


demand_forecaster = DemandForecaster()
