"""
Simulation Metrics Calculation Module.
Calculates energy totals, fuel burn, configurable CO2 footprint, prioritized load reliability, and costs.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np

from data.synthetic.fuel import (
    DEFAULT_DIESEL_CO2_KG_PER_LITER,
    DEFAULT_DIESEL_PRICE_PER_LITER,
    calculate_diesel_emissions_and_cost,
)


@dataclass
class SimulationMetrics:
    total_demand_kwh: float
    total_served_kwh: float
    unmet_demand_kwh: float
    renewable_energy_kwh: float
    renewable_fraction_pct: float
    diesel_generation_kwh: float
    diesel_fuel_liters: float
    fuel_cost_dollars: float
    co2_emissions_kg: float
    co2_emission_factor_kg_per_l: float
    battery_throughput_kwh: float
    p0_served_pct: float
    p1_served_pct: float
    p2_served_pct: float
    overall_reliability_pct: float
    co2_estimate_disclaimer: str = (
        "CO2 emissions represent an empirical engineering estimate based on standard "
        "IPCC/EPA diesel fuel combustion factors (2.68 kg CO2/L)."
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_demand_kwh": round(self.total_demand_kwh, 2),
            "total_served_kwh": round(self.total_served_kwh, 2),
            "unmet_demand_kwh": round(self.unmet_demand_kwh, 2),
            "renewable_energy_kwh": round(self.renewable_energy_kwh, 2),
            "renewable_fraction_pct": round(self.renewable_fraction_pct, 1),
            "diesel_generation_kwh": round(self.diesel_generation_kwh, 2),
            "diesel_fuel_liters": round(self.diesel_fuel_liters, 2),
            "fuel_cost_dollars": round(self.fuel_cost_dollars, 2),
            "co2_emissions_kg": round(self.co2_emissions_kg, 2),
            "co2_emission_factor_kg_per_l": self.co2_emission_factor_kg_per_l,
            "co2_estimate_disclaimer": self.co2_estimate_disclaimer,
            "battery_throughput_kwh": round(self.battery_throughput_kwh, 2),
            "p0_served_pct": round(self.p0_served_pct, 1),
            "p1_served_pct": round(self.p1_served_pct, 1),
            "p2_served_pct": round(self.p2_served_pct, 1),
            "overall_reliability_pct": round(self.overall_reliability_pct, 1),
        }


def compute_metrics(
    demand_kw: List[float],
    solar_served_kw: List[float],
    wind_served_kw: List[float],
    battery_discharged_kw: List[float],
    diesel_kw: List[float],
    p0_demand_kw: List[float],
    p1_demand_kw: List[float],
    p2_demand_kw: List[float],
    p0_served_kw: List[float],
    p1_served_kw: List[float],
    p2_served_kw: List[float],
    diesel_liters_total: float,
    battery_throughput_kwh: float,
    co2_kg_per_liter: float = DEFAULT_DIESEL_CO2_KG_PER_LITER,
    fuel_price_per_l: float = DEFAULT_DIESEL_PRICE_PER_LITER,
    dt_hours: float = 0.25,
) -> SimulationMetrics:
    """Computes all microgrid simulation operational metrics."""
    tot_demand_kwh = sum(demand_kw) * dt_hours
    tot_solar_kwh = sum(solar_served_kw) * dt_hours
    tot_wind_kwh = sum(wind_served_kw) * dt_hours
    renewable_kwh = tot_solar_kwh + tot_wind_kwh
    diesel_kwh = sum(diesel_kw) * dt_hours
    
    tot_p0_demand = sum(p0_demand_kw) * dt_hours
    tot_p1_demand = sum(p1_demand_kw) * dt_hours
    tot_p2_demand = sum(p2_demand_kw) * dt_hours

    tot_p0_served = sum(p0_served_kw) * dt_hours
    tot_p1_served = sum(p1_served_kw) * dt_hours
    tot_p2_served = sum(p2_served_kw) * dt_hours

    tot_served_kwh = tot_p0_served + tot_p1_served + tot_p2_served
    unmet_kwh = max(0.0, tot_demand_kwh - tot_served_kwh)

    p0_pct = (tot_p0_served / max(0.001, tot_p0_demand)) * 100.0
    p1_pct = (tot_p1_served / max(0.001, tot_p1_demand)) * 100.0
    p2_pct = (tot_p2_served / max(0.001, tot_p2_demand)) * 100.0
    reliability_pct = (tot_served_kwh / max(0.001, tot_demand_kwh)) * 100.0
    renew_pct = (renewable_kwh / max(0.001, tot_served_kwh)) * 100.0

    eco = calculate_diesel_emissions_and_cost(
        diesel_liters=diesel_liters_total,
        co2_kg_per_liter=co2_kg_per_liter,
        fuel_price_per_liter=fuel_price_per_l,
    )

    return SimulationMetrics(
        total_demand_kwh=tot_demand_kwh,
        total_served_kwh=tot_served_kwh,
        unmet_demand_kwh=unmet_kwh,
        renewable_energy_kwh=renewable_kwh,
        renewable_fraction_pct=min(100.0, renew_pct),
        diesel_generation_kwh=diesel_kwh,
        diesel_fuel_liters=diesel_liters_total,
        fuel_cost_dollars=eco["fuel_cost_dollars"],
        co2_emissions_kg=eco["co2_emissions_kg"],
        co2_emission_factor_kg_per_l=co2_kg_per_liter,
        battery_throughput_kwh=battery_throughput_kwh,
        p0_served_pct=min(100.0, p0_pct),
        p1_served_pct=min(100.0, p1_pct),
        p2_served_pct=min(100.0, p2_pct),
        overall_reliability_pct=min(100.0, reliability_pct),
    )
