"""
Tests for Diesel Generator Subsystem:
- Minimum loading rule (30% rated capacity when committed)
- Binary commitment state (diesel_on in {0, 1})
- Zero output when OFF
- Fuel consumption curve and cost calculations
- TEST 4: Diesel ON output >= 30% rated capacity
"""

import pytest
from optimization.diesel import DieselSubsystem
from optimization.milp import optimize_dispatch
from optimization.models import OptimizationInput


def test_diesel_subsystem_calculations():
    diesel = DieselSubsystem(rated_capacity_kw=40.0, min_loading_ratio=0.30, fuel_price=95.0)
    assert diesel.min_output_kw == 12.0
    assert diesel.max_output_kw == 40.0

    dt = 0.25
    # 20 kW output when ON:
    # F = [ 1 * (0.08 * 40) + 0.22 * 20 ] * 0.25 = [3.2 + 4.4] * 0.25 = 7.6 * 0.25 = 1.9 Liters
    liters = diesel.calculate_fuel_consumption_liters(power_kw=20.0, is_on=True, dt_hours=dt)
    assert round(liters, 3) == 1.900

    # When OFF, fuel should be exactly 0
    liters_off = diesel.calculate_fuel_consumption_liters(power_kw=0.0, is_on=False, dt_hours=dt)
    assert liters_off == 0.0

    cost = diesel.calculate_fuel_cost(liters)
    assert round(cost, 2) == round(1.9 * 95.0, 2)


def test_4_diesel_minimum_loading_when_on():
    """
    TEST 4: Diesel ON.
    Expected: Whenever diesel_on == 1, diesel output must be >= 30% rated capacity (>= 12 kW for 40 kW generator).
    When diesel_on == 0, output must be exactly 0.
    """
    inp = OptimizationInput(
        # Small demand of 15 kW that renewables cannot satisfy, forcing diesel on
        demand_forecast=[15.0] * 96,
        solar_forecast=[0.0] * 96,
        wind_forecast=[0.0] * 96,
        initial_battery_energy=20.0,  # Battery at 20% min floor, cannot discharge
        battery_capacity=100.0,
        diesel_available=True,
        diesel_capacity_kw=40.0,
        diesel_min_loading_ratio=0.30,
        storm_mode=False,
    )

    result = optimize_dispatch(inp)
    assert result.solver_status == "optimal"

    min_rated_kw = 40.0 * 0.30  # 12.0 kW

    for step in result.full_schedule:
        d_kw = step["diesel_kw"]
        d_on = step["diesel_on"]

        if d_on == 1:
            assert d_kw >= min_rated_kw - 0.01, (
                f"Timestep {step['timestep']}: Diesel ON with {d_kw} kW, "
                f"violating 30% min loading threshold of {min_rated_kw} kW"
            )
        else:
            assert d_kw == 0.0, (
                f"Timestep {step['timestep']}: Diesel OFF but generating {d_kw} kW"
            )


def test_diesel_unavailable():
    """When diesel is disabled, diesel generation must be zero across all timesteps."""
    inp = OptimizationInput(
        demand_forecast=[25.0] * 96,
        solar_forecast=[10.0] * 96,
        wind_forecast=[5.0] * 96,
        initial_battery_energy=50.0,
        battery_capacity=100.0,
        diesel_available=False,  # Generator broken or out of fuel
    )

    result = optimize_dispatch(inp)
    # Ensure zero diesel output throughout
    for step in result.full_schedule:
        assert step["diesel_kw"] == 0.0
        assert step["diesel_on"] == 0
