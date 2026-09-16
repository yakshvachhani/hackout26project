"""
OptiGrid-AI: Mathematical Constraints for PuLP MILP Formulation.
Defines power balance, physical generator bounds, battery dynamics, and priority limits.
"""

from typing import Dict, List, Any
import pulp

from optimization.battery import BatterySubsystem
from optimization.diesel import DieselSubsystem
from optimization.priority_loads import PriorityLoadSubsystem


def add_power_balance_constraints(
    model: pulp.LpProblem,
    timesteps: List[int],
    solar: Dict[int, pulp.LpVariable],
    wind: Dict[int, pulp.LpVariable],
    battery_discharge: Dict[int, pulp.LpVariable],
    diesel: Dict[int, pulp.LpVariable],
    p0_served: Dict[int, pulp.LpVariable],
    p1_served: Dict[int, pulp.LpVariable],
    p2_served: Dict[int, pulp.LpVariable],
    battery_charge: Dict[int, pulp.LpVariable],
    curtailment: Dict[int, pulp.LpVariable],
) -> None:
    """
    Hard power balance constraint at every timestep t:
    Generation + Storage Discharge = Load Served + Storage Charging + Curtailment
    """
    for t in timesteps:
        generation_supply = (
            solar[t]
            + wind[t]
            + battery_discharge[t]
            + diesel[t]
        )
        demand_and_sinks = (
            p0_served[t]
            + p1_served[t]
            + p2_served[t]
            + battery_charge[t]
            + curtailment[t]
        )
        model += (
            generation_supply == demand_and_sinks,
            f"PowerBalance_step_{t}",
        )


def add_renewable_constraints(
    model: pulp.LpProblem,
    timesteps: List[int],
    solar: Dict[int, pulp.LpVariable],
    wind: Dict[int, pulp.LpVariable],
    solar_available: List[float],
    wind_available: List[float],
) -> None:
    """Limits renewable dispatch to current environmental availability."""
    for t in timesteps:
        model += (solar[t] <= float(solar_available[t]), f"SolarUpper_step_{t}")
        model += (wind[t] <= float(wind_available[t]), f"WindUpper_step_{t}")


def add_battery_constraints(
    model: pulp.LpProblem,
    timesteps: List[int],
    battery_charge: Dict[int, pulp.LpVariable],
    battery_discharge: Dict[int, pulp.LpVariable],
    battery_energy: Dict[int, pulp.LpVariable],
    battery_subsystem: BatterySubsystem,
    initial_energy_kwh: float,
    dt_hours: float = 0.25,
) -> None:
    """
    Formulates battery storage energy transitions and physical boundaries:
    E[0] == initial_energy_kwh
    E[t+1] == E[t] + (eta_ch * P_ch[t] - P_dis[t] / eta_dis) * dt
    min_energy <= E[t] <= max_energy for all t in [0, T]
    """
    eta_ch = battery_subsystem.charge_eff
    eta_dis = battery_subsystem.discharge_eff
    min_e = battery_subsystem.min_energy_kwh
    max_e = battery_subsystem.max_energy_kwh

    # Initial energy anchor
    model += (battery_energy[0] == initial_energy_kwh, "BatteryEnergyInitial")

    # Dynamic transition over the horizon for all intervals
    for t in timesteps:
        delta_e = (eta_ch * battery_charge[t] - (1.0 / eta_dis) * battery_discharge[t]) * dt_hours
        model += (
            battery_energy[t + 1] == battery_energy[t] + delta_e,
            f"BatteryEnergyDynamic_step_{t}",
        )

    # Enforce operational limits on state of charge at all timesteps and terminal state
    for t in range(len(timesteps) + 1):
        model += (battery_energy[t] >= min_e, f"BatteryMinEnergy_point_{t}")
        model += (battery_energy[t] <= max_e, f"BatteryMaxEnergy_point_{t}")


def add_diesel_constraints(
    model: pulp.LpProblem,
    timesteps: List[int],
    diesel: Dict[int, pulp.LpVariable],
    diesel_on: Dict[int, pulp.LpVariable],
    diesel_subsystem: DieselSubsystem,
    fuel_remaining: float,
    dt_hours: float = 0.25,
) -> None:
    """
    Enforces minimum loading (30% rule) and binary commitment:
    diesel[t] >= min_output * diesel_on[t]
    diesel[t] <= max_output * diesel_on[t]
    """
    min_kw = diesel_subsystem.min_output_kw
    max_kw = diesel_subsystem.max_output_kw

    for t in timesteps:
        if not diesel_subsystem.is_available or max_kw <= 0:
            model += (diesel[t] == 0.0, f"DieselUnavailable_step_{t}")
            model += (diesel_on[t] == 0, f"DieselOnUnavailable_step_{t}")
        else:
            model += (diesel[t] >= min_kw * diesel_on[t], f"DieselMinLoading_step_{t}")
            model += (diesel[t] <= max_kw * diesel_on[t], f"DieselMaxCapacity_step_{t}")

    # Enforce fuel stock limitation over the 24h horizon if diesel is active
    if diesel_subsystem.is_available and fuel_remaining > 0:
        total_fuel_expr = pulp.lpSum(
            (
                diesel_on[t] * (diesel_subsystem.alpha_intercept * diesel_subsystem.rated_capacity_kw)
                + diesel[t] * diesel_subsystem.beta_slope
            )
            * dt_hours
            for t in timesteps
        )
        model += (total_fuel_expr <= fuel_remaining, "DieselFuelStockLimit")


def add_priority_load_constraints(
    model: pulp.LpProblem,
    timesteps: List[int],
    p0_served: Dict[int, pulp.LpVariable],
    p1_served: Dict[int, pulp.LpVariable],
    p2_served: Dict[int, pulp.LpVariable],
    p0_demand: List[float],
    p1_demand: List[float],
    p2_demand: List[float],
) -> None:
    """Limits served power in each priority tier to the actual requested demand."""
    for t in timesteps:
        model += (p0_served[t] <= float(p0_demand[t]), f"P0DemandLimit_step_{t}")
        model += (p1_served[t] <= float(p1_demand[t]), f"P1DemandLimit_step_{t}")
        model += (p2_served[t] <= float(p2_demand[t]), f"P2DemandLimit_step_{t}")
