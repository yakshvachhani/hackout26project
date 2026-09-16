"""
Synthetic telemetry generation package for OptiGrid-AI.
Generates realistic village load, solar PV, wind turbine, battery storage, and fuel logistics profiles.
"""

from data.synthetic.village_load import generate_village_load, generate_village_load_dict
from data.synthetic.solar import generate_solar_profile, generate_solar_dict
from data.synthetic.wind import generate_wind_profile, generate_wind_dict, wind_turbine_power_curve
from data.synthetic.battery import BatteryStorage, BatteryConfig
from data.synthetic.fuel import (
    calculate_fuel_autonomy,
    estimate_generator_fuel_burn,
    calculate_diesel_emissions_and_cost,
    FuelAlertLevel,
    DEFAULT_DIESEL_CO2_KG_PER_LITER,
    DEFAULT_DIESEL_PRICE_PER_LITER,
)

__all__ = [
    "generate_village_load",
    "generate_village_load_dict",
    "generate_solar_profile",
    "generate_solar_dict",
    "generate_wind_profile",
    "generate_wind_dict",
    "wind_turbine_power_curve",
    "BatteryStorage",
    "BatteryConfig",
    "calculate_fuel_autonomy",
    "estimate_generator_fuel_burn",
    "calculate_diesel_emissions_and_cost",
    "FuelAlertLevel",
    "DEFAULT_DIESEL_CO2_KG_PER_LITER",
    "DEFAULT_DIESEL_PRICE_PER_LITER",
]
