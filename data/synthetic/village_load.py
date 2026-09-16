"""
Synthetic Village Load Profile Generator for Off-Grid Microgrids.
Generates realistic multi-tier load profiles at 15-minute resolution (96 intervals per 24 hours).
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd


def generate_village_load(
    start_time: Optional[Union[datetime, str]] = None,
    duration_hours: int = 24,
    base_demand_kw: float = 22.0,
    peak_demand_kw: float = 68.0,
    seed: Optional[int] = 42,
    noise_std: float = 1.8,
) -> pd.DataFrame:
    """
    Generates realistic 15-minute resolution electrical load for an off-grid village.
    
    Load characteristics:
    - Night baseload (00:00 - 05:00): Low consumption (refrigeration, security lights).
    - Morning rise (06:00 - 09:00): Breakfast preparation, water pumping, domestic chores.
    - Daytime plateau (09:00 - 17:00): Health clinic, grain mills, small retail, schools.
    - Evening peak (17:30 - 21:30): Domestic lighting, cooking, TV/entertainment, community hub.
    - Night drop (22:00 - 24:00): Gradual decline to baseload.

    Load Priority Breakdown:
    - P0 (Critical): Healthcare clinic vaccine fridge, water borehole pumps, emergency comms (~28%).
    - P1 (Essential): Food storage, school lighting, core commerce, street lighting (~44%).
    - P2 (Flexible / Deferrable): Water heating, heavy milling, EV/tool charging (~28%).

    Args:
        start_time: Starting timestamp. Defaults to today at 00:00:00 UTC.
        duration_hours: Duration in hours (e.g. 24 or 48).
        base_demand_kw: Baseline low-load kW.
        peak_demand_kw: Maximum typical peak load kW.
        seed: Random seed for deterministic reproducibility.
        noise_std: Standard deviation of white noise in kW.

    Returns:
        pd.DataFrame with columns:
        ['timestamp', 'interval', 'hour_of_day', 'minute_of_hour', 'demand_kw', 'p0_kw', 'p1_kw', 'p2_kw']
    """
    if start_time is None:
        now = datetime.now(timezone.utc)
        start_dt = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
    elif isinstance(start_time, str):
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    else:
        start_dt = start_time

    n_intervals = int(duration_hours * 4)  # 4 intervals per hour
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    timestamps: List[datetime] = [start_dt + timedelta(minutes=15 * i) for i in range(n_intervals)]
    hours = np.array([ts.hour + ts.minute / 60.0 for ts in timestamps])

    # Diurnal components:
    # 1. Base constant
    # 2. Morning peak centered at 7.5h with width sigma=1.3h
    morning_peak = 18.0 * np.exp(-0.5 * ((hours % 24 - 7.5) / 1.3) ** 2)
    
    # 3. Daytime commercial/clinic activity (10:00 to 16:30)
    daytime_plateau = 12.0 * np.exp(-0.5 * ((hours % 24 - 13.0) / 3.0) ** 2)
    
    # 4. Evening major residential peak centered at 19.5h with width sigma=1.6h
    evening_peak = (peak_demand_kw - base_demand_kw - 8.0) * np.exp(-0.5 * ((hours % 24 - 19.5) / 1.6) ** 2)
    
    # 5. Night dip modulation
    night_modulation = np.sin((hours % 24 - 14.0) * np.pi / 12.0) * 4.0

    raw_demand = base_demand_kw + morning_peak + daytime_plateau + evening_peak + night_modulation
    
    # Add random noise
    noise = rng.normal(0, noise_std, n_intervals)
    demand = np.maximum(base_demand_kw * 0.75, raw_demand + noise)

    # Breakdown into P0, P1, P2 priorities
    p0_fraction = 0.28
    p1_fraction = 0.44

    p0_kw = np.round(demand * p0_fraction, 2)
    p1_kw = np.round(demand * p1_fraction, 2)
    p2_kw = np.round(demand - p0_kw - p1_kw, 2)
    p2_kw = np.maximum(0.0, p2_kw)

    df = pd.DataFrame({
        "timestamp": [ts.isoformat() for ts in timestamps],
        "interval": np.arange(1, n_intervals + 1, dtype=int),
        "hour_of_day": np.array([ts.hour for ts in timestamps], dtype=int),
        "minute_of_hour": np.array([ts.minute for ts in timestamps], dtype=int),
        "time_str": [f"{ts.hour:02d}:{ts.minute:02d}" for ts in timestamps],
        "demand_kw": np.round(demand, 2),
        "p0_kw": p0_kw,
        "p1_kw": p1_kw,
        "p2_kw": p2_kw,
    })

    return df


def generate_village_load_dict(
    duration_hours: int = 24,
    start_time: Optional[Union[datetime, str]] = None,
    seed: Optional[int] = 42,
) -> Dict[str, Union[List[str], List[float]]]:
    """Convenience helper returning dictionary of lists for JSON/MPC consumption."""
    df = generate_village_load(start_time=start_time, duration_hours=duration_hours, seed=seed)
    return {
        "timestamps": df["timestamp"].tolist(),
        "time_strings": df["time_str"].tolist(),
        "demand_kw": df["demand_kw"].tolist(),
        "p0_kw": df["p0_kw"].tolist(),
        "p1_kw": df["p1_kw"].tolist(),
        "p2_kw": df["p2_kw"].tolist(),
    }
