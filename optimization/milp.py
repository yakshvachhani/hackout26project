"""
OptiGrid-AI: Core Mixed-Integer Linear Programming (MILP) Engine.
Formulates and solves the 96-timestep microgrid dispatch problem using PuLP.
Features deterministic fail-safe fallback and microsecond-accuracy execution profiling.
"""

import time
import logging
from typing import Dict, Any, Union, Optional, List
import pulp

from optimization.config import OptimizationConfig
from optimization.models import (
    OptimizationInput,
    OptimizationResult,
    DispatchStep,
)
from optimization.battery import BatterySubsystem
from optimization.diesel import DieselSubsystem
from optimization.priority_loads import PriorityLoadSubsystem
from optimization.constraints import (
    add_power_balance_constraints,
    add_renewable_constraints,
    add_battery_constraints,
    add_diesel_constraints,
    add_priority_load_constraints,
)
from optimization.objective import build_optimization_objective

logger = logging.getLogger(__name__)


def optimize_dispatch(
    input_data: Union[OptimizationInput, Dict[str, Any]],
    config: Optional[OptimizationConfig] = None,
) -> OptimizationResult:
    """
    Main entrypoint to solve 24-hour (96 timestep) optimal dispatch.
    
    Args:
        input_data: OptimizationInput instance or dictionary containing microgrid state and forecasts.
        config: Optional OptimizationConfig overrides.
        
    Returns:
        OptimizationResult with current dispatch (t=0), full 96-step schedule, and key KPIs.
    """
    cfg = config or OptimizationConfig()

    # 1. Normalize input model
    if isinstance(input_data, dict):
        inp = OptimizationInput(**input_data)
    else:
        inp = input_data

    # 2. Instantiate physical subsystems
    battery_sub = BatterySubsystem(
        config=cfg.battery,
        capacity_kwh=inp.battery_capacity,
        storm_mode=inp.storm_mode,
        min_soc_override=inp.min_soc,
        max_soc_override=inp.max_soc,
    )

    diesel_sub = DieselSubsystem(
        config=cfg.diesel,
        rated_capacity_kw=inp.diesel_capacity_kw,
        min_loading_ratio=inp.diesel_min_loading_ratio,
        fuel_price=inp.fuel_price,
        is_available=inp.diesel_available,
    )

    priority_sub = PriorityLoadSubsystem(config=cfg.loads)

    # Split demand across P0, P1, P2
    p0_demand, p1_demand, p2_demand = priority_sub.split_demand(
        inp.demand_forecast, inp.p0_demand, inp.p1_demand, inp.p2_demand
    )

    num_steps = cfg.horizon.num_timesteps
    timesteps = list(range(num_steps))
    dt = cfg.horizon.timestep_hours

    # 3. Setup PuLP MILP Model
    start_time = time.perf_counter()
    model = pulp.LpProblem("OptiGrid_Microgrid_MILP", pulp.LpMinimize)

    # Decision variables
    solar = {
        t: pulp.LpVariable(f"solar_{t}", lowBound=0.0, upBound=float(inp.solar_forecast[t]))
        for t in timesteps
    }
    wind = {
        t: pulp.LpVariable(f"wind_{t}", lowBound=0.0, upBound=float(inp.wind_forecast[t]))
        for t in timesteps
    }
    battery_charge = {
        t: pulp.LpVariable(f"bat_ch_{t}", lowBound=0.0, upBound=battery_sub.max_charge_kw)
        for t in timesteps
    }
    battery_discharge = {
        t: pulp.LpVariable(f"bat_dis_{t}", lowBound=0.0, upBound=battery_sub.max_discharge_kw)
        for t in timesteps
    }
    battery_energy = {
        t: pulp.LpVariable(
            f"bat_energy_{t}",
            lowBound=battery_sub.min_energy_kwh,
            upBound=battery_sub.max_energy_kwh,
        )
        for t in range(num_steps + 1)
    }
    diesel = {
        t: pulp.LpVariable(f"diesel_{t}", lowBound=0.0, upBound=diesel_sub.max_output_kw)
        for t in timesteps
    }
    diesel_on = {
        t: pulp.LpVariable(f"diesel_on_{t}", cat=pulp.LpBinary)
        for t in timesteps
    }
    p0_served = {
        t: pulp.LpVariable(f"p0_served_{t}", lowBound=0.0, upBound=float(p0_demand[t]))
        for t in timesteps
    }
    p1_served = {
        t: pulp.LpVariable(f"p1_served_{t}", lowBound=0.0, upBound=float(p1_demand[t]))
        for t in timesteps
    }
    p2_served = {
        t: pulp.LpVariable(f"p2_served_{t}", lowBound=0.0, upBound=float(p2_demand[t]))
        for t in timesteps
    }
    curtailment = {
        t: pulp.LpVariable(f"curtailment_{t}", lowBound=0.0)
        for t in timesteps
    }

    # Add constraints
    add_power_balance_constraints(
        model, timesteps, solar, wind, battery_discharge, diesel,
        p0_served, p1_served, p2_served, battery_charge, curtailment
    )
    add_renewable_constraints(
        model, timesteps, solar, wind, inp.solar_forecast, inp.wind_forecast
    )
    add_battery_constraints(
        model, timesteps, battery_charge, battery_discharge, battery_energy,
        battery_sub, inp.initial_battery_energy, dt
    )
    add_diesel_constraints(
        model, timesteps, diesel, diesel_on, diesel_sub, inp.fuel_remaining, dt
    )
    add_priority_load_constraints(
        model, timesteps, p0_served, p1_served, p2_served,
        p0_demand, p1_demand, p2_demand
    )

    # Set objective function
    model += build_optimization_objective(
        timesteps, diesel, diesel_on, battery_charge, battery_discharge,
        p0_served, p1_served, p2_served, curtailment,
        p0_demand, p1_demand, p2_demand,
        battery_sub, diesel_sub, priority_sub, inp.fuel_price, dt
    )

    # 4. Solve Problem
    try:
        solver = pulp.PULP_CBC_CMD(
            timeLimit=cfg.solver.time_limit_seconds,
            gapRel=cfg.solver.mip_gap,
            threads=cfg.solver.threads,
            msg=cfg.solver.log_solver,
        )
        status_code = model.solve(solver)
        solve_status_str = pulp.LpStatus.get(status_code, "Undefined")
    except Exception as e:
        logger.warning(f"PuLP solver threw exception: {e}; engaging deterministic fallback.")
        return run_deterministic_fallback(inp, cfg, reason=str(e))

    solve_duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    # Check for optimality
    if solve_status_str != "Optimal":
        logger.warning(f"MILP solve returned non-optimal status '{solve_status_str}'; engaging fallback.")
        return run_deterministic_fallback(inp, cfg, reason=f"Solver returned {solve_status_str}")

    # 5. Extract Solution and Build Schedule
    full_schedule: List[Dict[str, Any]] = []
    tot_fuel_liters = 0.0
    tot_curtailment_kwh = 0.0
    tot_p0_kwh = 0.0
    tot_p1_kwh = 0.0
    tot_p2_kwh = 0.0
    tot_unmet_kwh = 0.0
    tot_renewable_kwh = 0.0
    tot_generation_kwh = 0.0

    for t in timesteps:
        s_kw = max(0.0, round(float(solar[t].varValue or 0.0), 3))
        w_kw = max(0.0, round(float(wind[t].varValue or 0.0), 3))
        b_ch = max(0.0, round(float(battery_charge[t].varValue or 0.0), 3))
        b_dis = max(0.0, round(float(battery_discharge[t].varValue or 0.0), 3))
        b_e = max(0.0, round(float(battery_energy[t].varValue or 0.0), 3))
        d_kw = max(0.0, round(float(diesel[t].varValue or 0.0), 3))
        d_on = int(round(float(diesel_on[t].varValue or 0.0)))
        
        # Binary threshold safety check
        if d_kw < 0.01:
            d_kw = 0.0
            d_on = 0

        p0_s = max(0.0, round(float(p0_served[t].varValue or 0.0), 3))
        p1_s = max(0.0, round(float(p1_served[t].varValue or 0.0), 3))
        p2_s = max(0.0, round(float(p2_served[t].varValue or 0.0), 3))
        curt = max(0.0, round(float(curtailment[t].varValue or 0.0), 3))

        total_served = round(p0_s + p1_s + p2_s, 3)
        total_demand_t = round(p0_demand[t] + p1_demand[t] + p2_demand[t], 3)
        p0_unmet = max(0.0, round(p0_demand[t] - p0_s, 3))
        p1_unmet = max(0.0, round(p1_demand[t] - p1_s, 3))
        p2_unmet = max(0.0, round(p2_demand[t] - p2_s, 3))
        unmet_t = max(0.0, round(total_demand_t - total_served, 3))

        f_liters = diesel_sub.calculate_fuel_consumption_liters(d_kw, bool(d_on), dt)
        f_cost = diesel_sub.calculate_fuel_cost(f_liters, inp.fuel_price)

        step_data = DispatchStep(
            timestep=t,
            solar_kw=s_kw,
            wind_kw=w_kw,
            battery_charge_kw=b_ch,
            battery_discharge_kw=b_dis,
            battery_net_kw=round(b_dis - b_ch, 3),
            battery_energy_kwh=b_e,
            battery_soc_pct=battery_sub.get_soc_percent(b_e),
            diesel_kw=d_kw,
            diesel_on=d_on,
            p0_served_kw=p0_s,
            p1_served_kw=p1_s,
            p2_served_kw=p2_s,
            total_served_kw=total_served,
            p0_unmet_kw=p0_unmet,
            p1_unmet_kw=p1_unmet,
            p2_unmet_kw=p2_unmet,
            unmet_demand_kw=unmet_t,
            curtailment_kw=curt,
            fuel_consumed_liters=round(f_liters, 3),
            fuel_cost=round(f_cost, 2),
        ).model_dump()
        full_schedule.append(step_data)

        # Totals accumulation
        tot_fuel_liters += f_liters
        tot_curtailment_kwh += curt * dt
        tot_p0_kwh += p0_s * dt
        tot_p1_kwh += p1_s * dt
        tot_p2_kwh += p2_s * dt
        tot_unmet_kwh += unmet_t * dt
        tot_renewable_kwh += (s_kw + w_kw) * dt
        tot_generation_kwh += (s_kw + w_kw + b_dis + d_kw) * dt

    total_demand_kwh = sum(inp.demand_forecast) * dt
    reliability_pct = 100.0 if total_demand_kwh == 0 else round(
        max(0.0, (1.0 - tot_unmet_kwh / total_demand_kwh) * 100.0), 2
    )
    renewable_pct = 0.0 if tot_generation_kwh == 0 else round(
        (tot_renewable_kwh / tot_generation_kwh) * 100.0, 2
    )

    t0 = full_schedule[0]
    total_supply_t0 = round(t0["solar_kw"] + t0["wind_kw"] + t0["battery_discharge_kw"] + t0["diesel_kw"], 3)
    t0_demand = round(inp.demand_forecast[0], 3)
    t0_renewable_pct = 0.0 if total_supply_t0 <= 0 else round(((t0["solar_kw"] + t0["wind_kw"]) / total_supply_t0) * 100.0, 1)

    return OptimizationResult(
        solver_status="optimal",
        status="optimal",
        solve_time_ms=solve_duration_ms,
        objective_value=round(float(pulp.value(model.objective) or 0.0), 2),
        current_dispatch=t0,
        full_schedule=full_schedule,
        total_fuel_used_liters=round(tot_fuel_liters, 2),
        total_fuel_cost=round(tot_fuel_liters * inp.fuel_price, 2),
        renewable_percentage=t0_renewable_pct,
        total_curtailment_kwh=round(tot_curtailment_kwh, 2),
        total_p0_served_kwh=round(tot_p0_kwh, 2),
        total_p1_served_kwh=round(tot_p1_kwh, 2),
        total_p2_served_kwh=round(tot_p2_kwh, 2),
        total_unmet_kwh=round(tot_unmet_kwh, 2),
        reliability_pct=reliability_pct,
        final_battery_soc_pct=battery_sub.get_soc_percent(float(battery_energy[num_steps].varValue or 0.0)),
        solar_kw=t0["solar_kw"],
        wind_kw=t0["wind_kw"],
        battery_kw=t0["battery_net_kw"],
        diesel_kw=t0["diesel_kw"],
        total_supply_kw=total_supply_t0,
        demand_kw=t0_demand,
        unmet_demand_kw=t0["unmet_demand_kw"],
        battery_soc=t0["battery_soc_pct"],
        dispatch={
            "solarKw": t0["solar_kw"],
            "windKw": t0["wind_kw"],
            "batteryKw": t0["battery_net_kw"],
            "dieselKw": t0["diesel_kw"],
        },
        metrics={
            "totalGenerationKw": total_supply_t0,
            "unmetDemandKw": t0["unmet_demand_kw"],
            "renewablePercent": renewable_pct,
            "estimatedCostPerHour": round(t0["fuel_cost"] * 4.0, 2),
            "fuelConsumptionLitersHour": round(t0["fuel_consumed_liters"] * 4.0, 2),
            "co2EmissionsKgHour": round(t0["fuel_consumed_liters"] * 4.0 * 2.68, 2),
            "reliabilityPercent": reliability_pct,
        },
    )


def run_deterministic_fallback(
    inp: OptimizationInput,
    config: Optional[OptimizationConfig] = None,
    reason: str = "Fallback triggered",
) -> OptimizationResult:
    """
    Deterministic rule-based fallback dispatch when MILP fails or is infeasible.
    Priority order: Solar -> Wind -> Battery -> Diesel
    Loads served strictly: P0 first -> P1 second -> P2 last.
    Clearly marks solver_status = "fallback".
    """
    cfg = config or OptimizationConfig()
    start_time = time.perf_counter()

    battery_sub = BatterySubsystem(
        config=cfg.battery,
        capacity_kwh=inp.battery_capacity,
        storm_mode=inp.storm_mode,
        min_soc_override=inp.min_soc,
        max_soc_override=inp.max_soc,
    )
    diesel_sub = DieselSubsystem(
        config=cfg.diesel,
        rated_capacity_kw=inp.diesel_capacity_kw,
        min_loading_ratio=inp.diesel_min_loading_ratio,
        fuel_price=inp.fuel_price,
        is_available=inp.diesel_available,
    )
    priority_sub = PriorityLoadSubsystem(config=cfg.loads)

    p0_demand, p1_demand, p2_demand = priority_sub.split_demand(
        inp.demand_forecast, inp.p0_demand, inp.p1_demand, inp.p2_demand
    )

    num_steps = cfg.horizon.num_timesteps
    timesteps = list(range(num_steps))
    dt = cfg.horizon.timestep_hours

    current_battery_energy = inp.initial_battery_energy
    fuel_stock = inp.fuel_remaining

    full_schedule: List[Dict[str, Any]] = []
    tot_fuel_liters = 0.0
    tot_curtailment_kwh = 0.0
    tot_p0_kwh = 0.0
    tot_p1_kwh = 0.0
    tot_p2_kwh = 0.0
    tot_unmet_kwh = 0.0
    tot_renewable_kwh = 0.0
    tot_generation_kwh = 0.0

    for t in timesteps:
        dem_0 = p0_demand[t]
        dem_1 = p1_demand[t]
        dem_2 = p2_demand[t]
        total_dem = dem_0 + dem_1 + dem_2

        s_avail = float(inp.solar_forecast[t])
        w_avail = float(inp.wind_forecast[t])

        # Step 1: Dispatch Solar & Wind up to total demand
        renewable_disp = min(s_avail + w_avail, total_dem)
        # Allocate solar and wind proportionally
        if s_avail + w_avail > 0:
            s_disp = round(min(s_avail, renewable_disp * (s_avail / (s_avail + w_avail))), 3)
            w_disp = round(min(w_avail, renewable_disp - s_disp), 3)
        else:
            s_disp, w_disp = 0.0, 0.0

        net_demand = total_dem - (s_disp + w_disp)
        excess_renewable = (s_avail - s_disp) + (w_avail - w_disp)

        b_ch = 0.0
        b_dis = 0.0

        # Charge battery with excess renewable if any
        if excess_renewable > 0:
            max_ch = battery_sub.max_available_charge_power(current_battery_energy, dt)
            b_ch = round(min(excess_renewable, max_ch), 3)
            excess_renewable -= b_ch

        # Curtail unused excess
        curt = round(max(0.0, excess_renewable), 3)

        # Step 2: Battery discharge if deficit remains
        if net_demand > 0:
            max_dis = battery_sub.max_available_discharge_power(current_battery_energy, dt)
            b_dis = round(min(net_demand, max_dis), 3)
            net_demand -= b_dis

        # Step 3: Diesel generator if deficit remains and generator available
        d_disp = 0.0
        d_on = 0
        if net_demand > 0 and diesel_sub.is_available and fuel_stock > 0:
            # Must satisfy minimum loading (30%)
            min_output = diesel_sub.min_output_kw
            max_output = diesel_sub.max_output_kw

            required_diesel = net_demand
            if required_diesel <= max_output:
                d_disp = max(min_output, required_diesel)
            else:
                d_disp = max_output

            d_on = 1
            # If diesel output exceeds net demand due to minimum loading, charge battery if possible
            extra_diesel = d_disp - net_demand
            if extra_diesel > 0:
                headroom_ch = battery_sub.max_available_charge_power(current_battery_energy, dt) - b_ch
                possible_extra_ch = min(extra_diesel, max(0.0, headroom_ch))
                b_ch += possible_extra_ch
                extra_diesel -= possible_extra_ch
                curt += extra_diesel
                net_demand = 0.0
            else:
                net_demand = 0.0

        # Step 4: Total supplied power and hierarchical allocation to loads
        total_power_for_load = s_disp + w_disp + b_dis + (d_disp - (d_disp - min(d_disp, total_dem - (s_disp + w_disp + b_dis))))
        p0_s, p1_s, p2_s, _ = priority_sub.allocate_available_power_hierarchical(
            total_power_for_load, dem_0, dem_1, dem_2
        )

        p0_s = round(p0_s, 3)
        p1_s = round(p1_s, 3)
        p2_s = round(p2_s, 3)
        total_served = round(p0_s + p1_s + p2_s, 3)
        unmet_t = max(0.0, round(total_dem - total_served, 3))

        # Battery energy evolution
        next_e = battery_sub.next_energy_state(current_battery_energy, b_ch, b_dis, dt)
        current_battery_energy = next_e

        # Fuel consumption
        f_liters = diesel_sub.calculate_fuel_consumption_liters(d_disp, bool(d_on), dt)
        fuel_stock = max(0.0, fuel_stock - f_liters)
        f_cost = diesel_sub.calculate_fuel_cost(f_liters, inp.fuel_price)

        step_data = DispatchStep(
            timestep=t,
            solar_kw=s_disp,
            wind_kw=w_disp,
            battery_charge_kw=b_ch,
            battery_discharge_kw=b_dis,
            battery_net_kw=round(b_dis - b_ch, 3),
            battery_energy_kwh=round(current_battery_energy, 3),
            battery_soc_pct=battery_sub.get_soc_percent(current_battery_energy),
            diesel_kw=round(d_disp, 3),
            diesel_on=d_on,
            p0_served_kw=p0_s,
            p1_served_kw=p1_s,
            p2_served_kw=p2_s,
            total_served_kw=total_served,
            p0_unmet_kw=round(dem_0 - p0_s, 3),
            p1_unmet_kw=round(dem_1 - p1_s, 3),
            p2_unmet_kw=round(dem_2 - p2_s, 3),
            unmet_demand_kw=unmet_t,
            curtailment_kw=curt,
            fuel_consumed_liters=round(f_liters, 3),
            fuel_cost=round(f_cost, 2),
        ).model_dump()
        full_schedule.append(step_data)

        tot_fuel_liters += f_liters
        tot_curtailment_kwh += curt * dt
        tot_p0_kwh += p0_s * dt
        tot_p1_kwh += p1_s * dt
        tot_p2_kwh += p2_s * dt
        tot_unmet_kwh += unmet_t * dt
        tot_renewable_kwh += (s_disp + w_disp) * dt
        tot_generation_kwh += (s_disp + w_disp + b_dis + d_disp) * dt

    total_demand_kwh = sum(inp.demand_forecast) * dt
    reliability_pct = 100.0 if total_demand_kwh == 0 else round(
        max(0.0, (1.0 - tot_unmet_kwh / total_demand_kwh) * 100.0), 2
    )
    renewable_pct = 0.0 if tot_generation_kwh == 0 else round(
        (tot_renewable_kwh / tot_generation_kwh) * 100.0, 2
    )

    solve_duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    t0 = full_schedule[0]
    total_supply_t0 = round(t0["solar_kw"] + t0["wind_kw"] + t0["battery_discharge_kw"] + t0["diesel_kw"], 3)
    t0_demand = round(inp.demand_forecast[0], 3)

    return OptimizationResult(
        solver_status="fallback",
        status="fallback",
        solve_time_ms=solve_duration_ms,
        objective_value=0.0,
        current_dispatch=t0,
        full_schedule=full_schedule,
        total_fuel_used_liters=round(tot_fuel_liters, 2),
        total_fuel_cost=round(tot_fuel_liters * inp.fuel_price, 2),
        renewable_percentage=renewable_pct,
        total_curtailment_kwh=round(tot_curtailment_kwh, 2),
        total_p0_served_kwh=round(tot_p0_kwh, 2),
        total_p1_served_kwh=round(tot_p1_kwh, 2),
        total_p2_served_kwh=round(tot_p2_kwh, 2),
        total_unmet_kwh=round(tot_unmet_kwh, 2),
        reliability_pct=reliability_pct,
        final_battery_soc_pct=full_schedule[-1]["battery_soc_pct"],
        solar_kw=t0["solar_kw"],
        wind_kw=t0["wind_kw"],
        battery_kw=t0["battery_net_kw"],
        diesel_kw=t0["diesel_kw"],
        total_supply_kw=total_supply_t0,
        demand_kw=t0_demand,
        unmet_demand_kw=t0["unmet_demand_kw"],
        battery_soc=t0["battery_soc_pct"],
        dispatch={
            "solarKw": t0["solar_kw"],
            "windKw": t0["wind_kw"],
            "batteryKw": t0["battery_net_kw"],
            "dieselKw": t0["diesel_kw"],
        },
        metrics={
            "totalGenerationKw": total_supply_t0,
            "unmetDemandKw": t0["unmet_demand_kw"],
            "renewablePercent": renewable_pct,
            "estimatedCostPerHour": round(t0["fuel_cost"] * 4.0, 2),
            "fuelConsumptionLitersHour": round(t0["fuel_consumed_liters"] * 4.0, 2),
            "co2EmissionsKgHour": round(t0["fuel_consumed_liters"] * 4.0 * 2.68, 2),
            "reliabilityPercent": reliability_pct,
        },
    )


# Backward and cross-module compatibility for Member 2
def optimize(input_data: Union[OptimizationInput, Dict[str, Any]]) -> Dict[str, Any]:
    """Compatibility alias directly called by Member 2's optimizer_service.py."""
    res = optimize_dispatch(input_data)
    return res.to_dict()


def run_milp_optimization(input_data: Union[OptimizationInput, Dict[str, Any]]) -> Dict[str, Any]:
    """Compatibility alias directly called by Member 2's optimizer_service.py."""
    res = optimize_dispatch(input_data)
    return res.to_dict()
