"""Demand forecasting and simulation model.

NOTE FOR PRODUCTION DEPLOYMENT:
In a live commercial microgrid, this synthetic load generator would be replaced
by real-time smart meter telemetry (AMI / SCADA aggregators) or an ML demand
forecaster trained on historical building meter intervals.
"""

import math
import random
from datetime import datetime
from typing import List, Union

import numpy as np
import pandas as pd


def compute_hourly_demand(
    dt: datetime,
    base_demand_kw: float = 50.0,
    multiplier: float = 1.0,
    ambient_temp_c: float = 28.0,
) -> float:
    """Calculate synthetic load for a specific hour based on human activity patterns.

    Key characteristics:
    - Base nocturnal baseload (refrigeration, security, standby loads)
    - Morning peak (07:00 - 10:00) as breakfast, commercial startups occur
    - Afternoon plateau (11:00 - 16:00) with temperature-dependent AC cooling load
    - Evening peak (18:00 - 22:00) corresponding to peak residential cooking, lighting, HVAC
    - Weekend adjustments: delayed morning wake-up and lower commercial load
    - Stochastic noise: +/- 5% realistic fluctuation
    """
    hour = dt.hour + dt.minute / 60.0
    day_of_week = dt.weekday()  # 0=Monday, 6=Sunday
    is_weekend = day_of_week >= 5

    # 1. Base diurnal curve normalized to [0, 1]
    # Night trough (00:00 - 05:00): ~0.25 - 0.35
    if hour < 5.5:
        curve = 0.28 + 0.05 * math.sin((hour / 5.5) * math.pi)
    # Morning ramp (05:30 - 09:30)
    elif 5.5 <= hour < 10.0:
        # Weekend morning peak is delayed and softer
        peak_hour = 9.5 if is_weekend else 8.5
        curve = 0.70 * math.exp(-((hour - peak_hour) ** 2) / 3.2) + 0.35
    # Afternoon plateau (10:00 - 16:30)
    elif 10.0 <= hour < 16.5:
        curve = 0.55 if not is_weekend else 0.45
    # Evening peak (16:30 - 22:00)
    elif 16.5 <= hour < 22.0:
        peak_hour = 20.0
        curve = 0.95 * math.exp(-((hour - peak_hour) ** 2) / 4.5) + 0.30
    # Late night descent (22:00 - 24:00)
    else:
        curve = 0.35 - 0.10 * ((hour - 22.0) / 2.0)

    # 2. Weekend commercial discount factor
    if is_weekend:
        curve *= 0.88

    # 3. Cooling load sensitivity: higher load when ambient temperature exceeds 30 C
    cooling_bump = 0.0
    if ambient_temp_c > 30.0 and 11.0 <= hour <= 19.0:
        cooling_bump = 0.02 * (ambient_temp_c - 30.0)

    # 4. Realistic stochastic noise
    noise_factor = random.gauss(0.0, 0.035)

    load_ratio = max(0.20, curve + cooling_bump + noise_factor)
    demand_kw = base_demand_kw * load_ratio * multiplier

    return round(float(demand_kw), 2)


def generate_demand_series(
    timestamps: Union[List[str], List[datetime], pd.Series],
    base_demand_kw: float = 50.0,
    multiplier: float = 1.0,
    temperatures: Union[List[float], np.ndarray] = None,
) -> np.ndarray:
    """Generate hourly synthetic demand array corresponding to input timestamps.

    Production Note:
        Replace this function with:
        `fetch_smart_meter_readings(meter_ids, start_time, end_time)`
        in live SCADA / EMS microgrid environment.
    """
    demands = []
    
    for idx, item in enumerate(timestamps):
        if isinstance(item, str):
            dt = datetime.fromisoformat(item)
        elif isinstance(item, (datetime, pd.Timestamp)):
            dt = item.to_pydatetime() if hasattr(item, "to_pydatetime") else item
        else:
            dt = datetime.now()

        temp = 28.0
        if temperatures is not None and idx < len(temperatures):
            temp = float(temperatures[idx])

        val = compute_hourly_demand(
            dt=dt,
            base_demand_kw=base_demand_kw,
            multiplier=multiplier,
            ambient_temp_c=temp,
        )
        demands.append(val)

    return np.array(demands, dtype=float)


if __name__ == "__main__":
    from datetime import timedelta
    sample_times = [datetime.now() + timedelta(hours=i) for i in range(24)]
    sample_demands = generate_demand_series(sample_times)
    print("Sample 24-Hour Synthetic Demand Curve (kW):")
    for t, d in zip(sample_times[:12], sample_demands[:12]):
        print(f"  {t.strftime('%Y-%m-%d %H:%M')}: {d:.2f} kW")
