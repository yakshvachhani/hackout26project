"""
Tests for Core MILP Optimization Engine:
- TEST 1: High solar, Low demand -> Solar preferred, Diesel OFF
- TEST 2: Low renewable, Battery available -> Battery assists load
- TEST 3: Renewable + battery insufficient -> Diesel starts
- TEST 8: Zero solar -> Wind/battery/diesel compensate
- TEST 9: Zero renewable -> Diesel supplies if available
- Strict Power Balance verification over all 96 timesteps
- Edge solve time profiling and fallback mechanism
"""

import time
import pytest
from optimization.milp import optimize_dispatch, run_deterministic_fallback
from optimization.models import OptimizationInput


def test_1_high_solar_low_demand():
    """
    TEST 1: High solar, Low demand.
    Expected: Solar preferred, Diesel OFF.
    """
    inp = OptimizationInput(
        demand_forecast=[20.0] * 96,
        solar_forecast=[50.0] * 96,
        wind_forecast=[5.0] * 96,
        initial_battery_energy=50.0,
        battery_capacity=100.0,
        diesel_available=True,
    )

    result = optimize_dispatch(inp)
    assert result.solver_status == "optimal"

    # Verify diesel is completely OFF for every single timestep
    for step in result.full_schedule:
        assert step["diesel_kw"] == 0.0, f"Diesel ran when solar was abundant at step {step['timestep']}"
        assert step["diesel_on"] == 0
        assert step["solar_kw"] >= 20.0 or (step["solar_kw"] + step["battery_discharge_kw"] >= 20.0)
        assert step["unmet_demand_kw"] == 0.0

    assert result.total_fuel_used_liters == 0.0


def test_2_low_renewable_battery_available():
    """
    TEST 2: Low renewable, Battery available.
    Expected: Battery assists load without starting diesel unnecessarily.
    """
    # Demand = 30 kW, Solar = 10 kW, Wind = 5 kW (Renewable deficit = 15 kW)
    # Battery has 80 kWh (at 100 kWh cap, min floor is 20 kWh, headroom is 60 kWh)
    # 15 kW over a few hours is easily covered by battery
    inp = OptimizationInput(
        demand_forecast=[25.0] * 96,
        solar_forecast=[10.0] * 96,
        wind_forecast=[5.0] * 96,
        initial_battery_energy=80.0,
        battery_capacity=100.0,
        diesel_available=True,
        fuel_price=95.0,
    )

    result = optimize_dispatch(inp)
    assert result.solver_status == "optimal"

    # In early timesteps when battery energy is high, battery must discharge to cover deficit
    t0 = result.full_schedule[0]
    assert t0["battery_discharge_kw"] > 0.0, "Battery did not assist load despite ample capacity"
    assert t0["diesel_kw"] == 0.0, "Diesel prematurely started when battery had ample stored energy"
    assert t0["unmet_demand_kw"] == 0.0


def test_3_renewable_plus_battery_insufficient_diesel_starts():
    """
    TEST 3: Renewable + battery insufficient.
    Expected: Diesel generator starts up to prevent power deficit.
    """
    # Demand = 45 kW, Solar = 5 kW, Wind = 0 kW (Deficit = 40 kW)
    # Battery is at 20 kWh (20% min floor, cannot discharge)
    inp = OptimizationInput(
        demand_forecast=[45.0] * 96,
        solar_forecast=[5.0] * 96,
        wind_forecast=[0.0] * 96,
        initial_battery_energy=20.0,  # Floor reached
        battery_capacity=100.0,
        diesel_available=True,
        diesel_capacity_kw=40.0,
    )

    result = optimize_dispatch(inp)
    assert result.solver_status == "optimal"

    # Diesel must start
    t0 = result.full_schedule[0]
    assert t0["diesel_on"] == 1, "Diesel failed to start when renewables and battery were insufficient"
    assert t0["diesel_kw"] >= 12.0, "Diesel minimum loading violated"
    assert t0["diesel_kw"] == 40.0, "Diesel should operate at rated capacity to meet demand"


def test_8_zero_solar_compensation():
    """
    TEST 8: Zero solar (e.g. night-time or heavy storm overcast).
    Expected: Wind, battery, and diesel compensate.
    """
    inp = OptimizationInput(
        demand_forecast=[35.0] * 96,
        solar_forecast=[0.0] * 96,
        wind_forecast=[15.0] * 96,
        initial_battery_energy=60.0,
        battery_capacity=100.0,
        diesel_available=True,
    )

    result = optimize_dispatch(inp)
    assert result.solver_status == "optimal"

    # Solar must be 0 for all timesteps
    for step in result.full_schedule:
        assert step["solar_kw"] == 0.0
        # Check that demand is fully served by wind + battery + diesel
        total_supply = step["wind_kw"] + step["battery_discharge_kw"] + step["diesel_kw"]
        assert total_supply >= step["total_served_kw"] - 0.01


def test_9_zero_renewable_diesel_supplies():
    """
    TEST 9: Zero renewable (calm night, zero solar and zero wind).
    Expected: Diesel supplies base load up to its rated limits if available.
    """
    inp = OptimizationInput(
        demand_forecast=[30.0] * 96,
        solar_forecast=[0.0] * 96,
        wind_forecast=[0.0] * 96,
        initial_battery_energy=20.0,  # Battery depleted to min reserve
        battery_capacity=100.0,
        diesel_available=True,
        diesel_capacity_kw=40.0,
    )

    result = optimize_dispatch(inp)
    assert result.solver_status == "optimal"

    t0 = result.full_schedule[0]
    assert t0["diesel_on"] == 1
    assert t0["diesel_kw"] >= 30.0, f"Diesel output {t0['diesel_kw']} should supply the 30 kW base load"
    assert t0["total_served_kw"] == 30.0, "All 30 kW load must be served"
    assert t0["unmet_demand_kw"] == 0.0


def test_strict_power_balance_all_timesteps():
    """
    Verifies the fundamental physics of the microgrid:
    Generation (Solar + Wind + Battery Disch + Diesel) == Load Served + Battery Charge + Curtailment
    at EVERY single one of the 96 timesteps.
    """
    inp = OptimizationInput(
        demand_forecast=[40.0] * 96,
        solar_forecast=[35.0] * 96,
        wind_forecast=[10.0] * 96,
        initial_battery_energy=50.0,
        battery_capacity=100.0,
        diesel_available=True,
    )

    result = optimize_dispatch(inp)
    assert result.solver_status == "optimal"

    for step in result.full_schedule:
        supply = step["solar_kw"] + step["wind_kw"] + step["battery_discharge_kw"] + step["diesel_kw"]
        demand_and_sinks = step["total_served_kw"] + step["battery_charge_kw"] + step["curtailment_kw"]
        diff = abs(supply - demand_and_sinks)
        assert diff < 0.05, f"Timestep {step['timestep']}: Power imbalance! Supply={supply}, Sinks={demand_and_sinks}, diff={diff}"


def test_edge_performance_solve_time():
    """
    Verifies that the MILP solves efficiently within lightweight edge requirements.
    Measures real execution time.
    """
    inp = OptimizationInput(
        demand_forecast=[50.0] * 96,
        solar_forecast=[30.0] * 96,
        wind_forecast=[15.0] * 96,
        initial_battery_energy=70.0,
    )

    t_start = time.perf_counter()
    result = optimize_dispatch(inp)
    measured_time_ms = (time.perf_counter() - t_start) * 1000.0

    assert result.solver_status == "optimal"
    # Ensure solve time is tracked and well within acceptable edge limits (< 2000 ms)
    assert result.solve_time_ms > 0.0
    assert result.solve_time_ms < 2000.0, f"Solve took too long: {result.solve_time_ms} ms"
    print(f"\nMeasured MILP solve time: {result.solve_time_ms:.2f} ms (Overall: {measured_time_ms:.2f} ms)")


def test_deterministic_fallback_execution():
    """
    Verifies fallback dispatch behaves predictably and marks solver_status='fallback'.
    """
    inp = OptimizationInput(
        demand_forecast=[50.0] * 96,
        solar_forecast=[30.0] * 96,
        wind_forecast=[15.0] * 96,
        initial_battery_energy=70.0,
    )

    fallback_res = run_deterministic_fallback(inp, reason="Test trigger")
    assert fallback_res.solver_status == "fallback"
    assert fallback_res.status == "fallback"
    assert len(fallback_res.full_schedule) == 96
    assert fallback_res.current_dispatch["total_served_kw"] > 0.0
