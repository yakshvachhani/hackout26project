"""
OptiGrid-AI: Objective Function Formulation.
Builds the multi-objective weighted cost function:
  Fuel Cost + Battery Degradation + Priority Load Shedding Penalties + Renewable Curtailment.
"""

from typing import Dict, List
import pulp

from optimization.battery import BatterySubsystem
from optimization.diesel import DieselSubsystem
from optimization.priority_loads import PriorityLoadSubsystem


def build_optimization_objective(
    timesteps: List[int],
    diesel: Dict[int, pulp.LpVariable],
    diesel_on: Dict[int, pulp.LpVariable],
    battery_charge: Dict[int, pulp.LpVariable],
    battery_discharge: Dict[int, pulp.LpVariable],
    p0_served: Dict[int, pulp.LpVariable],
    p1_served: Dict[int, pulp.LpVariable],
    p2_served: Dict[int, pulp.LpVariable],
    curtailment: Dict[int, pulp.LpVariable],
    p0_demand: List[float],
    p1_demand: List[float],
    p2_demand: List[float],
    battery_subsystem: BatterySubsystem,
    diesel_subsystem: DieselSubsystem,
    priority_subsystem: PriorityLoadSubsystem,
    fuel_price: float,
    dt_hours: float = 0.25,
) -> pulp.LpAffineExpression:
    """
    Constructs the weighted economic & reliability objective to minimize over the horizon.
    Costs and penalties are strictly calibrated according to the priority hierarchy:
      p0_penalty >> p1_penalty >> p2_penalty > fuel_cost > degradation_cost > curtailment_penalty
    """
    cost_terms = []

    alpha = diesel_subsystem.alpha_intercept
    p_rated = diesel_subsystem.rated_capacity_kw
    beta = diesel_subsystem.beta_slope
    c_deg = battery_subsystem.degradation_cost_per_kwh
    w0 = priority_subsystem.p0_penalty
    w1 = priority_subsystem.p1_penalty
    w2 = priority_subsystem.p2_penalty
    w_curt = priority_subsystem.curtailment_penalty

    for t in timesteps:
        # 1. Diesel Fuel Cost ($)
        fuel_consumption_expr = (diesel_on[t] * (alpha * p_rated) + diesel[t] * beta) * dt_hours
        fuel_cost_expr = fuel_price * fuel_consumption_expr
        cost_terms.append(fuel_cost_expr)

        # 2. Battery Throughput Degradation Proxy Cost ($)
        battery_throughput_expr = (battery_charge[t] + battery_discharge[t]) * dt_hours
        degradation_cost_expr = c_deg * battery_throughput_expr
        cost_terms.append(degradation_cost_expr)

        # 3. Unserved Load Penalties ($)
        # unserved = (demand - served) * dt_hours
        p0_unserved = (p0_demand[t] - p0_served[t]) * dt_hours
        p1_unserved = (p1_demand[t] - p1_served[t]) * dt_hours
        p2_unserved = (p2_demand[t] - p2_served[t]) * dt_hours

        cost_terms.append(w0 * p0_unserved)
        cost_terms.append(w1 * p1_unserved)
        cost_terms.append(w2 * p2_unserved)

        # 4. Renewable Curtailment Penalty ($)
        cost_terms.append(w_curt * curtailment[t] * dt_hours)

    return pulp.lpSum(cost_terms)
