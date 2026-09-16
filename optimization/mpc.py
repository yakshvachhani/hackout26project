"""
OptiGrid-AI: Model Predictive Control (MPC) Engine.
Implements rolling-horizon dispatch optimization:
  1. Receives current state telemetry + 24h lookahead forecast (96 timesteps @ 15 min).
  2. Formulates and solves MILP over the full lookahead horizon.
  3. Executes only the FIRST timestep (t=0) decision to the microgrid physical plant.
  4. Evolves state and allows receding-horizon multi-step simulation.
"""

from typing import Dict, Any, Union, Optional, List
import time

from optimization.config import OptimizationConfig
from optimization.models import OptimizationInput, OptimizationResult
from optimization.milp import optimize_dispatch
from optimization.battery import BatterySubsystem
from optimization.diesel import DieselSubsystem


def run_mpc(
    input_data: Union[OptimizationInput, Dict[str, Any]],
    config: Optional[OptimizationConfig] = None,
) -> OptimizationResult:
    """
    Core MPC function called by Member 2 and microgrid telemetry controller.
    Runs 96-timestep lookahead MILP, extracts immediate dispatch control action,
    and returns full forecast trajectory alongside KPIs.
    """
    # Solve 96-step lookahead MILP
    result = optimize_dispatch(input_data, config=config)
    return result


class MPCRollingController:
    """
    Simulation harness for receding-horizon MPC over multiple consecutive timesteps.
    Tracks state evolution across consecutive 96-step optimization runs.
    """

    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.battery_sub = BatterySubsystem(config=self.config.battery)
        self.diesel_sub = DieselSubsystem(config=self.config.diesel)

    def step(
        self,
        current_battery_energy: float,
        current_fuel_liters: float,
        demand_forecast_96: List[float],
        solar_forecast_96: List[float],
        wind_forecast_96: List[float],
        diesel_available: bool = True,
        storm_mode: bool = False,
        fuel_price: float = 95.0,
    ) -> Dict[str, Any]:
        """
        Executes a single MPC rolling step:
        - Solves 96-step lookahead
        - Extracts step 0 control action
        - Simulates state progression to step 1
        - Returns action + next state
        """
        inp = OptimizationInput(
            demand_forecast=demand_forecast_96,
            solar_forecast=solar_forecast_96,
            wind_forecast=wind_forecast_96,
            initial_battery_energy=current_battery_energy,
            battery_capacity=self.battery_sub.capacity_kwh,
            diesel_available=diesel_available,
            fuel_remaining=current_fuel_liters,
            fuel_price=fuel_price,
            storm_mode=storm_mode,
        )

        opt_result = run_mpc(inp, self.config)
        action = opt_result.current_dispatch

        # State transition for next horizon step
        dt = self.config.horizon.timestep_hours
        next_battery_energy = self.battery_sub.next_energy_state(
            current_energy_kwh=current_battery_energy,
            charge_kw=action["battery_charge_kw"],
            discharge_kw=action["battery_discharge_kw"],
            dt_hours=dt,
        )
        fuel_used_step = action["fuel_consumed_liters"]
        next_fuel_liters = max(0.0, current_fuel_liters - fuel_used_step)

        return {
            "executed_action": action,
            "next_battery_energy": round(next_battery_energy, 3),
            "next_battery_soc": self.battery_sub.get_soc_percent(next_battery_energy),
            "next_fuel_liters": round(next_fuel_liters, 2),
            "optimization_result": opt_result,
        }
