"""
Synthetic Wind Power Generation Model for Off-Grid Microgrids.
Models wind speed (m/s) and wind turbine kW output at 15-minute intervals.
"""

from datetime import datetime, timedelta, timezone
import math
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd


def wind_turbine_power_curve(
    wind_speed_ms: Union[float, np.ndarray],
    rated_capacity_kw: float = 30.0,
    cut_in_speed_ms: float = 3.0,
    rated_speed_ms: float = 11.5,
    cut_out_speed_ms: float = 25.0,
) -> Union[float, np.ndarray]:
    """
    Simplified, realistic wind turbine power curve:
    - v < cut_in: 0 kW
    - cut_in <= v < rated: cubic power interpolation: P = P_rated * ((v - v_in) / (v_rated - v_in))^3
    - rated <= v <= cut_out: P_rated kW
    - v > cut_out: 0 kW (safety shutdown)

    Args:
        wind_speed_ms: Wind speed in meters per second.
        rated_capacity_kw: Rated generator capacity in kW.
        cut_in_speed_ms: Minimum wind speed to start generating power.
        rated_speed_ms: Wind speed where turbine reaches full rated capacity.
        cut_out_speed_ms: Maximum wind speed before safety braking engages.

    Returns:
        Power output in kW (non-negative, clamped to [0, rated_capacity_kw]).
    """
    is_scalar = np.isscalar(wind_speed_ms)
    v = np.asarray([wind_speed_ms] if is_scalar else wind_speed_ms, dtype=float)

    power = np.zeros_like(v)

    # Region 2: between cut-in and rated (aerodynamic cubic power curve)
    mask_ramp = (v >= cut_in_speed_ms) & (v < rated_speed_ms)
    norm_v = (v[mask_ramp] - cut_in_speed_ms) / (rated_speed_ms - cut_in_speed_ms)
    power[mask_ramp] = rated_capacity_kw * (norm_v ** 3)

    # Region 3: between rated and cut-out
    mask_rated = (v >= rated_speed_ms) & (v <= cut_out_speed_ms)
    power[mask_rated] = rated_capacity_kw

    # Region 4: above cut-out (0 kW due to safety pitch/brake)
    # Already 0

    power = np.clip(power, 0.0, rated_capacity_kw)
    return float(power[0]) if is_scalar else power


def generate_wind_profile(
    start_time: Optional[Union[datetime, str]] = None,
    duration_hours: int = 24,
    rated_capacity_kw: float = 30.0,
    mean_wind_speed_ms: float = 7.5,
    gustiness: float = 1.8,
    seed: Optional[int] = 42,
) -> pd.DataFrame:
    """
    Generates synthetic wind speed (m/s) and wind power (kW) at 15-minute intervals.

    Wind behavior:
    - Diurnal breeze variation (often higher late afternoon or early morning in coastal/savannah settings).
    - Auto-correlated stochastic variability (Ornstein-Uhlenbeck style persistence).
    - Realistic bounds and turbine aerodynamic response.

    Args:
        start_time: Starting timestamp.
        duration_hours: Duration in hours (24 or 48).
        rated_capacity_kw: Turbine rated capacity in kW.
        mean_wind_speed_ms: Base average wind speed.
        gustiness: Standard deviation of wind variability.
        seed: Random seed for reproducibility.

    Returns:
        pd.DataFrame with columns:
        ['timestamp', 'interval', 'time_str', 'wind_speed_ms', 'wind_available_kw']
    """
    if start_time is None:
        now = datetime.now(timezone.utc)
        start_dt = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
    elif isinstance(start_time, str):
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    else:
        start_dt = start_time

    n_intervals = int(duration_hours * 4)
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    timestamps: List[datetime] = [start_dt + timedelta(minutes=15 * i) for i in range(n_intervals)]
    hours = np.array([ts.hour + ts.minute / 60.0 for ts in timestamps])

    # Diurnal cyclic pattern (e.g. thermal breeze peaking at 15:00 and secondary night breeze)
    diurnal_pattern = 1.8 * np.sin((hours % 24 - 8.0) * np.pi / 12.0) + 0.8 * np.cos((hours % 24) * np.pi / 6.0)

    # Autoregressive / persistent random walk noise
    wind_speeds = np.zeros(n_intervals, dtype=float)
    current_speed = mean_wind_speed_ms
    alpha = 0.85  # persistence factor for 15-min step

    for i in range(n_intervals):
        base_target = mean_wind_speed_ms + diurnal_pattern[i]
        shock = rng.normal(0, gustiness * np.sqrt(1 - alpha**2))
        current_speed = alpha * current_speed + (1 - alpha) * base_target + shock
        wind_speeds[i] = max(0.5, current_speed)

    wind_kw = wind_turbine_power_curve(wind_speeds, rated_capacity_kw=rated_capacity_kw)

    df = pd.DataFrame({
        "timestamp": [ts.isoformat() for ts in timestamps],
        "interval": np.arange(1, n_intervals + 1, dtype=int),
        "time_str": [f"{ts.hour:02d}:{ts.minute:02d}" for ts in timestamps],
        "wind_speed_ms": np.round(wind_speeds, 2),
        "wind_available_kw": np.round(wind_kw, 2),
    })

    return df


def generate_wind_dict(
    duration_hours: int = 24,
    rated_capacity_kw: float = 30.0,
    mean_wind_speed_ms: float = 7.5,
    seed: Optional[int] = 42,
) -> Dict[str, Union[List[str], List[float]]]:
    """Convenience helper returning dictionary of lists for JSON/MPC consumption."""
    df = generate_wind_profile(
        duration_hours=duration_hours,
        rated_capacity_kw=rated_capacity_kw,
        mean_wind_speed_ms=mean_wind_speed_ms,
        seed=seed,
    )
    return {
        "timestamps": df["timestamp"].tolist(),
        "time_strings": df["time_str"].tolist(),
        "wind_speed_ms": df["wind_speed_ms"].tolist(),
        "wind_available_kw": df["wind_available_kw"].tolist(),
    }
