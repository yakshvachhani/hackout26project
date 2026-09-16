"""
Synthetic Diesel Fuel Logistics and Emissions Model for Off-Grid Microgrids.
Tracks fuel tank levels, daily burn rates, autonomy days, depletion dates, alert states, and CO2 footprint.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from enum import Enum


class FuelAlertLevel(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# Documented default emission factors:
# Standard EPA / IPCC diesel factor is ~2.68 - 2.70 kg CO2 per liter of diesel fuel.
# Clearly marked as an empirical engineering estimate.
DEFAULT_DIESEL_CO2_KG_PER_LITER: float = 2.68
DEFAULT_DIESEL_PRICE_PER_LITER: float = 1.45


def calculate_fuel_autonomy(
    fuel_remaining_l: float,
    daily_burn_l: float,
    as_of_time: Optional[datetime] = None,
    warning_threshold_days: float = 15.0,
    critical_threshold_days: float = 7.0,
) -> Dict[str, Any]:
    """
    Computes fuel autonomy metrics based on remaining liters and daily burn rate.

    Formulas:
    days_remaining = fuel_remaining_l / average_daily_consumption
    depletion_date = as_of_time + days_remaining

    Thresholds:
    > 15 days -> NORMAL
    7 - 15 days -> WARNING
    < 7 days -> CRITICAL
    """
    as_of = as_of_time or datetime.now(timezone.utc)

    if daily_burn_l <= 0.0:
        days_remaining = 999.9  # Generator not running
        depletion_date = None
        status = FuelAlertLevel.NORMAL
    else:
        days_remaining = round(fuel_remaining_l / daily_burn_l, 1)
        depletion_dt = as_of + timedelta(days=days_remaining)
        depletion_date = depletion_dt.strftime("%Y-%m-%d")

        if days_remaining < critical_threshold_days:
            status = FuelAlertLevel.CRITICAL
        elif days_remaining <= warning_threshold_days:
            status = FuelAlertLevel.WARNING
        else:
            status = FuelAlertLevel.NORMAL

    return {
        "fuel_remaining_l": round(fuel_remaining_l, 1),
        "daily_burn_l": round(daily_burn_l, 1),
        "days_remaining": days_remaining,
        "depletion_date": depletion_date,
        "status": status.value,
        "as_of": as_of.isoformat(),
    }


def estimate_generator_fuel_burn(
    power_kw: float,
    duration_hours: float = 0.25,
    genset_capacity_kw: float = 60.0,
    base_idle_burn_lph: float = 2.0,
    marginal_burn_l_per_kwh: float = 0.26,
) -> float:
    """
    Computes diesel fuel consumption (liters) for a given power level and duration.

    Industrial diesel genset model:
    - If power_kw <= 0: 0 L
    - If running: Idle standby fuel + load proportional consumption.
    - Typical 50-100kW diesel genset consumes ~0.26 - 0.30 L/kWh at nominal load.
    """
    if power_kw <= 0.0:
        return 0.0
    burn_rate_lph = base_idle_burn_lph + (marginal_burn_l_per_kwh * power_kw)
    return round(burn_rate_lph * duration_hours, 3)


def calculate_diesel_emissions_and_cost(
    diesel_liters: float,
    co2_kg_per_liter: float = DEFAULT_DIESEL_CO2_KG_PER_LITER,
    fuel_price_per_liter: float = DEFAULT_DIESEL_PRICE_PER_LITER,
) -> Dict[str, Any]:
    """
    Calculates CO2 emissions and economic fuel cost.

    Note: CO2 emission calculation is an empirical estimate based on
    standard EPA/IPCC stoichiometric diesel combustion factors (2.68 kg CO2/L).
    """
    co2_kg = round(diesel_liters * co2_kg_per_liter, 2)
    cost = round(diesel_liters * fuel_price_per_liter, 2)
    return {
        "diesel_liters": round(diesel_liters, 2),
        "co2_emissions_kg": co2_kg,
        "co2_emission_factor_kg_per_l": co2_kg_per_liter,
        "co2_estimate_note": "Engineering estimate based on IPCC/EPA stoichiometric standard (2.68 kg CO2/L)",
        "fuel_cost_dollars": cost,
        "fuel_price_per_l": fuel_price_per_liter,
    }
