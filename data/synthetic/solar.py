"""
Synthetic Solar PV Generation Model for Off-Grid Microgrids.
Models solar irradiance (GHI) and PV kW generation at 15-minute intervals.
"""

from datetime import datetime, timedelta, timezone
import math
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd


def generate_solar_profile(
    start_time: Optional[Union[datetime, str]] = None,
    duration_hours: int = 24,
    pv_capacity_kw: float = 60.0,
    system_efficiency: float = 0.85,
    cloud_factor: float = 1.0,
    seed: Optional[int] = 42,
    noise_std: float = 0.5,
) -> pd.DataFrame:
    """
    Generates solar generation profile (kW) at 15-minute resolution.

    Characteristics:
    - Zero at night (before ~06:00 and after ~18:30).
    - Increase after sunrise following diurnal solar zenith angle.
    - Peak at solar noon (~12:30 - 13:00) with typical GHI up to 950-1000 W/m².
    - Decrease toward sunset.
    - Cloud factor scales irradiance (1.0 = clear sky, 0.2 = heavy overcast/storm).
    - Hard bounded [0, pv_capacity_kw].

    Args:
        start_time: Starting timestamp (default: today 00:00:00 UTC).
        duration_hours: Horizon length in hours (default 24).
        pv_capacity_kw: Installed DC/AC solar PV nameplate capacity in kW.
        system_efficiency: Inverter, temperature, and soiling derating factor (typical 0.80 - 0.88).
        cloud_factor: Cloud attenuation multiplier (0.0 to 1.0).
        seed: Random seed for deterministic reproducibility.
        noise_std: High-frequency fluctuation std dev (kW).

    Returns:
        pd.DataFrame with columns:
        ['timestamp', 'interval', 'time_str', 'irradiance_wm2', 'solar_available_kw']
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

    irradiance_wm2 = np.zeros(n_intervals, dtype=float)
    solar_kw = np.zeros(n_intervals, dtype=float)

    # Sunrise around 06:15 (6.25h), sunset around 18:30 (18.5h)
    sunrise = 6.25
    sunset = 18.50
    daylight_hours = sunset - sunrise

    for i, h in enumerate(hours):
        hour_of_day = h % 24.0
        if sunrise <= hour_of_day <= sunset:
            # Normalized solar zenith sine bell
            solar_angle = (hour_of_day - sunrise) / daylight_hours * np.pi
            clear_sky_ghi = 980.0 * np.sin(solar_angle) ** 1.15
            
            # Apply cloud factor and micro-variability
            ghi = max(0.0, clear_sky_ghi * cloud_factor)
            
            # PV power = Capacity * (GHI / 1000 W/m^2) * system_efficiency
            kw = pv_capacity_kw * (ghi / 1000.0) * system_efficiency
            
            # Add stochastic cloud passing ripple
            ripple = rng.normal(0, noise_std) if kw > 1.0 else 0.0
            kw_final = max(0.0, min(pv_capacity_kw, kw + ripple))
            
            irradiance_wm2[i] = round(ghi, 1)
            solar_kw[i] = round(kw_final, 2)
        else:
            irradiance_wm2[i] = 0.0
            solar_kw[i] = 0.0

    df = pd.DataFrame({
        "timestamp": [ts.isoformat() for ts in timestamps],
        "interval": np.arange(1, n_intervals + 1, dtype=int),
        "time_str": [f"{ts.hour:02d}:{ts.minute:02d}" for ts in timestamps],
        "irradiance_wm2": irradiance_wm2,
        "solar_available_kw": solar_kw,
    })

    return df


def generate_solar_dict(
    duration_hours: int = 24,
    pv_capacity_kw: float = 60.0,
    cloud_factor: float = 1.0,
    seed: Optional[int] = 42,
) -> Dict[str, Union[List[str], List[float]]]:
    """Convenience helper returning dictionary of lists for JSON/MPC consumption."""
    df = generate_solar_profile(
        duration_hours=duration_hours,
        pv_capacity_kw=pv_capacity_kw,
        cloud_factor=cloud_factor,
        seed=seed,
    )
    return {
        "timestamps": df["timestamp"].tolist(),
        "time_strings": df["time_str"].tolist(),
        "irradiance_wm2": df["irradiance_wm2"].tolist(),
        "solar_available_kw": df["solar_available_kw"].tolist(),
    }
