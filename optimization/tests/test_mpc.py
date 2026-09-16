"""
Tests for Model Predictive Control (MPC) and Receding-Horizon Framework:
- run_mpc() API contract and returned fields
- MPC 1st-timestep execution principle
- Receding horizon rolling simulation & state progression
- Interoperability with Member 2 backend interfaces
"""

import pytest
from optimization.mpc import run_mpc, MPCRollingController
from optimization.models import OptimizationInput
from optimization.milp import optimize, run_milp_optimization


def test_run_mpc_api_contract():
    """
    Verifies all required fields from prompt are present in MPC output:
    - current_dispatch
    - full_schedule
    - objective_value
    - fuel_used
    - renewable_percentage
    - battery_soc
    - p0_served
    - p1_served
    - p2_served
    - curtailment
    - unmet_demand
    - solver_status
    - solve_time_ms
    """
    inp = OptimizationInput(
        demand_forecast=[45.0] * 96,
        solar_forecast=[25.0] * 96,
        wind_forecast=[10.0] * 96,
        initial_battery_energy=60.0,
        battery_capacity=100.0,
        diesel_available=True,
    )

    res = run_mpc(inp)

    # Core required fields
    assert hasattr(res, "current_dispatch")
    assert hasattr(res, "full_schedule")
    assert hasattr(res, "objective_value")
    assert hasattr(res, "total_fuel_used_liters")
    assert hasattr(res, "renewable_percentage")
    assert hasattr(res, "battery_soc")
    assert hasattr(res, "total_p0_served_kwh")
    assert hasattr(res, "total_p1_served_kwh")
    assert hasattr(res, "total_p2_served_kwh")
    assert hasattr(res, "total_curtailment_kwh")
    assert hasattr(res, "unmet_demand_kw")
    assert hasattr(res, "solver_status")
    assert hasattr(res, "solve_time_ms")

    # Check 96 timesteps present in schedule
    assert len(res.full_schedule) == 96
    # Timestep 0 execution
    assert res.current_dispatch["timestep"] == 0


def test_mpc_receding_horizon_simulation():
    """
    Simulates rolling MPC across 3 sequential timesteps.
    Verifies that only step 0 is applied to the physical plant,
    and state variables (battery energy, fuel) evolve accurately.
    """
    controller = MPCRollingController()

    current_battery_e = 70.0
    current_fuel = 300.0

    for step_num in range(3):
        # Generate 96-step forecast starting from step_num
        demand_96 = [40.0 + step_num * 2.0] * 96
        solar_96 = [30.0] * 96
        wind_96 = [10.0] * 96

        step_output = controller.step(
            current_battery_energy=current_battery_e,
            current_fuel_liters=current_fuel,
            demand_forecast_96=demand_96,
            solar_forecast_96=solar_96,
            wind_forecast_96=wind_96,
        )

        action = step_output["executed_action"]
        next_e = step_output["next_battery_energy"]
        next_fuel = step_output["next_fuel_liters"]

        assert action["timestep"] == 0
        assert 20.0 <= next_e <= 95.0
        assert next_fuel <= current_fuel

        # Advance state
        current_battery_e = next_e
        current_fuel = next_fuel


def test_member_2_backend_compatibility():
    """
    Tests direct dictionary input and output compatibility with Member 2's
    optimizer_service.py (_solve_merit_order / optimize / run_milp_optimization).
    """
    req_payload = {
        "demand_kw": 50.0,
        "solar_available_kw": 30.0,
        "wind_available_kw": 15.0,
        "battery_soc": 70.0,
        "battery_capacity_kwh": 100.0,
        "diesel_available": True,
        "fuel_price": 95.0,
        "min_soc": 20.0,
        "max_soc": 95.0,
        "fuel_remaining": 360.0,
    }

    # Test optimize()
    res1 = optimize(req_payload)
    assert isinstance(res1, dict)
    assert "status" in res1
    assert "solar_kw" in res1
    assert "wind_kw" in res1
    assert "battery_kw" in res1
    assert "diesel_kw" in res1
    assert "total_supply_kw" in res1
    assert "demand_kw" in res1
    assert "unmet_demand_kw" in res1
    assert "renewable_percentage" in res1
    assert "dispatch" in res1
    assert "metrics" in res1

    # Test run_milp_optimization()
    res2 = run_milp_optimization(req_payload)
    assert isinstance(res2, dict)
    assert res2["status"] in ["optimal", "suboptimal", "fallback"]
    assert res2["metrics"]["reliabilityPercent"] >= 99.0
