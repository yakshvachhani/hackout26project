"""
Tests for Priority Loads & Hierarchical Shedding:
- Three tiers: P0 (Critical), P1 (Shiftable), P2 (Deferrable)
- TEST 7: Energy shortage (P2 curtailed before P1, P1 before P0, P0 protected)
- TEST 10: Diesel unavailable (Renewable + battery insufficient -> priorities activate)
"""

import pytest
from optimization.priority_loads import PriorityLoadSubsystem
from optimization.milp import optimize_dispatch
from optimization.models import OptimizationInput


def test_priority_demand_split():
    sub = PriorityLoadSubsystem()
    total_dem = [100.0] * 96
    p0, p1, p2 = sub.split_demand(total_dem)
    assert len(p0) == 96
    assert p0[0] == 30.0
    assert p1[0] == 40.0
    assert p2[0] == 30.0


def test_7_energy_shortage_hierarchical_shedding():
    """
    TEST 7: Energy shortage.
    Expected: P2 curtailed before P1, P1 curtailed before P0.
    Hospital/critical loads (P0) strictly preserved whenever sufficient total energy exists.
    """
    # Create severe deficit scenario:
    # Demand: P0 = 10 kW, P1 = 20 kW, P2 = 30 kW (Total = 60 kW)
    # Available power: Only 15 kW total generation capacity
    inp = OptimizationInput(
        demand_forecast=[60.0] * 96,
        solar_forecast=[15.0] * 96,
        wind_forecast=[0.0] * 96,
        p0_demand=[10.0] * 96,
        p1_demand=[20.0] * 96,
        p2_demand=[30.0] * 96,
        initial_battery_energy=20.0,  # Empty battery at floor
        battery_capacity=100.0,
        diesel_available=False,       # No diesel backup available
    )

    result = optimize_dispatch(inp)

    # 15 kW available against 60 kW demand:
    # 1. P0 (10 kW) must be 100% satisfied.
    # 2. Remaining 5 kW must go to P1 (5 kW served of 20 kW).
    # 3. P2 (30 kW) must be completely shed (0 kW served).
    for step in result.full_schedule:
        assert step["p0_served_kw"] == 10.0, f"P0 critical load compromised: {step['p0_served_kw']} < 10.0 kW"
        assert step["p1_served_kw"] == 5.0, f"P1 load allocation mismatch: {step['p1_served_kw']}"
        assert step["p2_served_kw"] == 0.0, f"P2 deferrable load should be fully curtailed: {step['p2_served_kw']}"


def test_10_diesel_unavailable_load_priorities():
    """
    TEST 10: Diesel unavailable.
    Expected: When diesel is unavailable and renewables/battery are constrained,
    load priorities activate to ensure critical P0 loads stay powered.
    """
    # Demand: P0 = 15 kW, P1 = 15 kW, P2 = 20 kW (Total = 50 kW)
    # Supply: Solar = 20 kW, Wind = 5 kW (Total = 25 kW), Battery at min SOC floor
    inp = OptimizationInput(
        demand_forecast=[50.0] * 96,
        solar_forecast=[20.0] * 96,
        wind_forecast=[5.0] * 96,
        p0_demand=[15.0] * 96,
        p1_demand=[15.0] * 96,
        p2_demand=[20.0] * 96,
        initial_battery_energy=20.0,
        battery_capacity=100.0,
        diesel_available=False,
    )

    result = optimize_dispatch(inp)

    # 25 kW total clean generation:
    # P0 (15 kW) fully served.
    # Remaining 10 kW goes to P1 (10 kW of 15 kW served).
    # P2 is completely shed (0 kW of 20 kW served).
    for step in result.full_schedule:
        assert step["p0_served_kw"] == 15.0, "Critical P0 must be 100% served"
        assert step["p1_served_kw"] == 10.0, "P1 should receive the remaining 10 kW"
        assert step["p2_served_kw"] == 0.0, "P2 should be completely shed"
        assert step["diesel_kw"] == 0.0, "Diesel must be 0 kW when unavailable"
