"""
OptiGrid-AI: Microgrid Energy Mix Optimizer
Configuration and default system parameters.
"""

from dataclasses import dataclass, field


@dataclass
class TimeHorizonConfig:
    horizon_hours: float = 24.0
    timestep_minutes: int = 15
    
    @property
    def timestep_hours(self) -> float:
        return self.timestep_minutes / 60.0

    @property
    def num_timesteps(self) -> int:
        return int(self.horizon_hours * 60 / self.timestep_minutes)


@dataclass
class BatteryConfig:
    capacity_kwh: float = 100.0
    normal_min_soc: float = 0.20       # 20% normal operational floor
    storm_min_soc: float = 0.50        # 50% storm reserve floor
    max_soc: float = 0.95              # 95% upper limit to prolong lifetime
    max_charge_kw: float = 25.0        # Max charge rate (C-rate 0.25C)
    max_discharge_kw: float = 30.0     # Max discharge rate (C-rate 0.30C)
    charge_efficiency: float = 0.92    # Round-trip sqrt ~ 92%
    discharge_efficiency: float = 0.92
    degradation_cost_per_kwh: float = 0.04  # $/kWh throughput cycling cost proxy


@dataclass
class DieselConfig:
    rated_capacity_kw: float = 40.0
    min_loading_ratio: float = 0.30    # 30% minimum loading rule when generator is ON (12 kW)
    fuel_curve_intercept: float = 0.08 # L/hr per kW rated capacity when running
    fuel_curve_slope: float = 0.22     # L/kWh of active output
    default_fuel_price: float = 95.0   # Currency units per liter
    default_fuel_stock: float = 500.0  # Available diesel stock in Liters

    @property
    def min_output_kw(self) -> float:
        return self.rated_capacity_kw * self.min_loading_ratio


@dataclass
class PriorityLoadConfig:
    # Default fraction of total community demand if individual profiles not provided
    default_p0_ratio: float = 0.30     # Critical (hospital, vaccines, emergency)
    default_p1_ratio: float = 0.40     # Shiftable (water pumps, grain mills)
    default_p2_ratio: float = 0.30     # Deferrable (domestic appliances, HVAC)

    # Cost of unserved energy ($/kWh)
    p0_penalty: float = 10000.0        # Extremely high priority protection
    p1_penalty: float = 500.0          # Medium-high penalty
    p2_penalty: float = 50.0           # Lower penalty (curtailed first)

    # Curtailment penalty ($/kWh) to encourage maximum clean renewable utilization
    curtailment_penalty: float = 0.50


@dataclass
class SolverConfig:
    solver_name: str = "PULP_CBC_CMD"
    time_limit_seconds: int = 10
    mip_gap: float = 0.01              # 1% optimality tolerance for fast edge solve
    threads: int = 1
    log_solver: bool = False


@dataclass
class OptimizationConfig:
    horizon: TimeHorizonConfig = field(default_factory=TimeHorizonConfig)
    battery: BatteryConfig = field(default_factory=BatteryConfig)
    diesel: DieselConfig = field(default_factory=DieselConfig)
    loads: PriorityLoadConfig = field(default_factory=PriorityLoadConfig)
    solver: SolverConfig = field(default_factory=SolverConfig)
