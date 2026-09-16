"""
Tests for Battery Energy Storage Subsystem & Dynamics:
- SOC state transitions
- Minimum/Maximum SOC limits
- TEST 5: Battery near minimum SOC (cannot breach 20% floor)
- TEST 6: Storm mode reserve (50% minimum SOC strictly enforced)
"""

import pytest
from optimization.battery import BatterySubsystem
from optimization.config import BatteryConfig
from optimization.milp import optimize_dispatch
from optimization.models import OptimizationInput


def test_battery_soc_conversion():
    battery = BatterySubsystem(capacity_kwh=100.0)
    assert battery.get_soc_percent(50.0) == 50.0
    assert battery.get_soc_percent(20.0) == 20.0
    assert battery.get_soc_percent(100.0) == 100.0


def test_battery_state_transition():
    battery = BatterySubsystem(capacity_kwh=100.0)
    dt = 0.25  # 15 minutes

    # Charge 20 kW for 15 min: E[t+1] = 50 + (0.92 * 20 * 0.25) = 50 + 4.6 = 54.6 kWh
    next_e = battery.next_energy_state(
        current_energy_kwh=50.0,
        charge_kw=20.0,
        discharge_kw=0.0,
        dt_hours=dt,
    )
    assert round(next_e, 2) == 54.60

    # Discharge 20 kW for 15 min: E[t+1] = 54.6 - (20 / 0.92 * 0.25) = 54.6 - 5.435 = 49.165 kWh
    next_e2 = battery.next_energy_state(
        current_energy_kwh=next_e,
        charge_kw=0.0,
        discharge_kw=20.0,
        dt_hours=dt,
    )
    assert round(next_e2, 2) == 49.17


def test_5_battery_near_minimum_soc():
    """
    TEST 5: Battery near minimum SOC.
    Expected: Battery cannot violate minimum SOC (normal mode floor = 20%).
    """
    cap = 100.0
    # Start at 20.5% SOC (20.5 kWh, min floor is 20.0 kWh)
    init_e = 20.5
    inp = OptimizationInput(
        demand_forecast=[30.0] * 96,
        solar_forecast=[0.0] * 96,
        wind_forecast=[0.0] * 96,
        initial_battery_energy=init_e,
        battery_capacity=cap,
        diesel_available=True,
        diesel_capacity_kw=40.0,
        storm_mode=False,
    )

    result = optimize_dispatch(inp)
    assert result.solver_status == "optimal"

    # Verify battery energy never drops below 20.0 kWh (20% SOC) in any of the 96 timesteps
    min_energy_observed = min(step["battery_energy_kwh"] for step in result.full_schedule)
    min_soc_observed = min(step["battery_soc_pct"] for step in result.full_schedule)

    assert min_energy_observed >= 19.99, f"Battery violated minimum energy floor: {min_energy_observed} kWh"
    assert min_soc_observed >= 19.99, f"Battery violated minimum SOC: {min_soc_observed}%"


def test_6_storm_mode_reserve():
    """
    TEST 6: Storm mode.
    Expected: Minimum SOC = 50% strictly enforced across entire horizon.
    """
    cap = 100.0
    # Start at 80% SOC (80 kWh)
    init_e = 80.0
    inp = OptimizationInput(
        demand_forecast=[40.0] * 96,
        solar_forecast=[5.0] * 96,
        wind_forecast=[5.0] * 96,
        initial_battery_energy=init_e,
        battery_capacity=cap,
        diesel_available=True,
        diesel_capacity_kw=40.0,
        storm_mode=True,  # Storm reserve mode active
    )

    result = optimize_dispatch(inp)
    assert result.solver_status == "optimal"

    # In storm mode, minimum allowed energy is 50 kWh (50% SOC)
    min_energy_observed = min(step["battery_energy_kwh"] for step in result.full_schedule)
    min_soc_observed = min(step["battery_soc_pct"] for step in result.full_schedule)

    assert min_energy_observed >= 49.99, f"Storm mode 50% energy floor breached: {min_energy_observed} kWh"
    assert min_soc_observed >= 49.99, f"Storm mode 50% SOC floor breached: {min_soc_observed}%"


def test_battery_degradation_cost_proxy():
    battery = BatterySubsystem()
    dt = 0.25
    # 20 kW charge + 10 kW discharge throughput
    cost = battery.calculate_degradation_cost(charge_kw=20.0, discharge_kw=10.0, dt_hours=dt)
    expected = (30.0 * 0.25) * battery.degradation_cost_per_kwh
    assert round(cost, 4) == round(expected, 4)
