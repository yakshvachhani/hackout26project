"""
OptiGrid-AI: Microgrid Optimization Data Models.
Pydantic schemas and dataclasses defining inputs, outputs, and status containers.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator


class OptimizationInput(BaseModel):
    """
    Standardized typed input for 96-timestep (24h) MILP / MPC optimization.
    Tolerates scalar inputs (auto-broadcasting to 96 steps) and camelCase aliases.
    """
    # Forecast profiles (length 96 or broadcastable scalar)
    demand_forecast: List[float] = Field(default_factory=lambda: [50.0] * 96)
    solar_forecast: List[float] = Field(default_factory=lambda: [30.0] * 96)
    wind_forecast: List[float] = Field(default_factory=lambda: [15.0] * 96)

    # Priority load breakdown (optional; split by config ratios if absent)
    p0_demand: Optional[List[float]] = None
    p1_demand: Optional[List[float]] = None
    p2_demand: Optional[List[float]] = None

    # Battery state
    initial_battery_energy: Optional[float] = None
    initial_battery_soc: Optional[float] = 70.0  # Percentage (0 - 100)
    battery_capacity: float = 100.0              # kWh

    # Diesel parameters
    diesel_available: bool = True
    diesel_capacity_kw: float = 40.0
    diesel_min_loading_ratio: float = 0.30
    fuel_remaining: float = 500.0                # Liters
    fuel_price: float = 95.0                     # Currency per Liter

    # Operating flags
    storm_mode: bool = False                     # If True, enforces 50% min SOC reserve
    min_soc: Optional[float] = None              # Explicit min SOC override (%)
    max_soc: Optional[float] = 95.0              # Max SOC operational limit (%)

    @model_validator(mode="before")
    @classmethod
    def normalize_and_validate(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        normalized = dict(data)

        # 1. Alias handling from Member 1 / Member 2 (camelCase and single-point dispatch)
        if "demand_kw" in normalized and "demand_forecast" not in normalized:
            val = float(normalized["demand_kw"])
            normalized["demand_forecast"] = [val] * 96
        elif "currentDemand" in normalized and "demand_forecast" not in normalized:
            val = float(normalized["currentDemand"])
            normalized["demand_forecast"] = [val] * 96

        if "solar_available_kw" in normalized and "solar_forecast" not in normalized:
            val = float(normalized["solar_available_kw"])
            normalized["solar_forecast"] = [val] * 96
        elif "solarAvailable" in normalized and "solar_forecast" not in normalized:
            val = float(normalized["solarAvailable"])
            normalized["solar_forecast"] = [val] * 96

        if "wind_available_kw" in normalized and "wind_forecast" not in normalized:
            val = float(normalized["wind_available_kw"])
            normalized["wind_forecast"] = [val] * 96
        elif "windAvailable" in normalized and "wind_forecast" not in normalized:
            val = float(normalized["windAvailable"])
            normalized["wind_forecast"] = [val] * 96

        if "battery_soc" in normalized and "initial_battery_soc" not in normalized:
            normalized["initial_battery_soc"] = float(normalized["battery_soc"])
        elif "batterySoc" in normalized and "initial_battery_soc" not in normalized:
            normalized["initial_battery_soc"] = float(normalized["batterySoc"])

        if "battery_capacity_kwh" in normalized and "battery_capacity" not in normalized:
            normalized["battery_capacity"] = float(normalized["battery_capacity_kwh"])
        elif "batteryCapacity" in normalized and "battery_capacity" not in normalized:
            normalized["battery_capacity"] = float(normalized["batteryCapacity"])

        if "dieselAvailable" in normalized and "diesel_available" not in normalized:
            v = normalized["dieselAvailable"]
            normalized["diesel_available"] = v is True or str(v).lower() == "true"

        if "dieselPrice" in normalized and "fuel_price" not in normalized:
            normalized["fuel_price"] = float(normalized["dieselPrice"])

        if "min_soc" in normalized and normalized["min_soc"] is not None:
            normalized["min_soc"] = float(normalized["min_soc"])
        elif "minSoc" in normalized:
            normalized["min_soc"] = float(normalized["minSoc"])

        if "max_soc" in normalized and normalized["max_soc"] is not None:
            normalized["max_soc"] = float(normalized["max_soc"])
        elif "maxSoc" in normalized:
            normalized["max_soc"] = float(normalized["maxSoc"])

        if "fuelRemaining" in normalized and "fuel_remaining" not in normalized:
            normalized["fuel_remaining"] = float(normalized["fuelRemaining"])

        # 2. Member 4 Data Module Structured Dictionary Support
        if "p0_forecast" in normalized and "p0_demand" not in normalized:
            normalized["p0_demand"] = normalized["p0_forecast"]
        if "p1_forecast" in normalized and "p1_demand" not in normalized:
            normalized["p1_demand"] = normalized["p1_forecast"]
        if "p2_forecast" in normalized and "p2_demand" not in normalized:
            normalized["p2_demand"] = normalized["p2_forecast"]

        if "battery" in normalized and isinstance(normalized["battery"], dict):
            b_dict = normalized["battery"]
            if "capacity_kwh" in b_dict and "battery_capacity" not in normalized:
                normalized["battery_capacity"] = float(b_dict["capacity_kwh"])
            if "current_soc_pct" in b_dict and "initial_battery_soc" not in normalized:
                normalized["initial_battery_soc"] = float(b_dict["current_soc_pct"])
            elif "soc_pct" in b_dict and "initial_battery_soc" not in normalized:
                normalized["initial_battery_soc"] = float(b_dict["soc_pct"])
            if "min_soc_pct" in b_dict and "min_soc" not in normalized:
                normalized["min_soc"] = float(b_dict["min_soc_pct"])
            if "max_soc_pct" in b_dict and "max_soc" not in normalized:
                normalized["max_soc"] = float(b_dict["max_soc_pct"])

        if "diesel" in normalized and isinstance(normalized["diesel"], dict):
            d_dict = normalized["diesel"]
            if "rated_capacity_kw" in d_dict and "diesel_capacity_kw" not in normalized:
                normalized["diesel_capacity_kw"] = float(d_dict["rated_capacity_kw"])
            if "fuel_remaining_l" in d_dict and "fuel_remaining" not in normalized:
                normalized["fuel_remaining"] = float(d_dict["fuel_remaining_l"])
            if "fuel_price_per_l" in d_dict and "fuel_price" not in normalized:
                normalized["fuel_price"] = float(d_dict["fuel_price_per_l"])
            if "is_available" in d_dict and "diesel_available" not in normalized:
                normalized["diesel_available"] = bool(d_dict["is_available"])

        if "grid_flags" in normalized and isinstance(normalized["grid_flags"], dict):
            g_dict = normalized["grid_flags"]
            if "storm_mode" in g_dict and "storm_mode" not in normalized:
                normalized["storm_mode"] = bool(g_dict["storm_mode"])

        # Broadcast scalar lists to 96 steps if needed
        for key in ["demand_forecast", "solar_forecast", "wind_forecast", "p0_demand", "p1_demand", "p2_demand"]:
            if key in normalized and normalized[key] is not None:
                val = normalized[key]
                if isinstance(val, (int, float)):
                    normalized[key] = [float(val)] * 96
                elif isinstance(val, list):
                    if len(val) == 1:
                        normalized[key] = val * 96
                    elif 1 < len(val) < 96:
                        # Pad with last value
                        normalized[key] = val + [val[-1]] * (96 - len(val))
                    elif len(val) > 96:
                        normalized[key] = val[:96]

        # Initial battery energy computation if not explicitly given
        cap = float(normalized.get("battery_capacity", 100.0))
        if normalized.get("initial_battery_energy") is None:
            soc = float(normalized.get("initial_battery_soc", 70.0))
            normalized["initial_battery_energy"] = (soc / 100.0) * cap

        return normalized


class DispatchStep(BaseModel):
    """Dispatch status and power variables for a single 15-minute timestep."""
    timestep: int
    solar_kw: float
    wind_kw: float
    battery_charge_kw: float
    battery_discharge_kw: float
    battery_net_kw: float               # Positive = discharging to load, Negative = charging
    battery_energy_kwh: float
    battery_soc_pct: float
    diesel_kw: float
    diesel_on: int                      # 0 or 1
    p0_served_kw: float
    p1_served_kw: float
    p2_served_kw: float
    total_served_kw: float
    p0_unmet_kw: float
    p1_unmet_kw: float
    p2_unmet_kw: float
    unmet_demand_kw: float
    curtailment_kw: float
    fuel_consumed_liters: float
    fuel_cost: float


class OptimizationResult(BaseModel):
    """
    Standard optimization output containing current decision, full 96-step schedule,
    and microgrid performance metrics. Fully compatible with Member 2's backend.
    """
    solver_status: str                  # "optimal", "suboptimal", "infeasible", "fallback"
    status: str                         # "optimal", "suboptimal", "fallback"
    solve_time_ms: float
    objective_value: float

    # Timestep 0 decision (for immediate dispatch execution)
    current_dispatch: Dict[str, Any]

    # Full 96-step optimal schedule
    full_schedule: List[Dict[str, Any]]

    # Aggregate 24h metrics
    total_fuel_used_liters: float
    total_fuel_cost: float
    renewable_percentage: float
    total_curtailment_kwh: float
    total_p0_served_kwh: float
    total_p1_served_kwh: float
    total_p2_served_kwh: float
    total_unmet_kwh: float
    reliability_pct: float
    final_battery_soc_pct: float

    # Member 2 backend root convenience fields (based on timestep 0 dispatch)
    solar_kw: float = 0.0
    wind_kw: float = 0.0
    battery_kw: float = 0.0
    diesel_kw: float = 0.0
    total_supply_kw: float = 0.0
    demand_kw: float = 0.0
    unmet_demand_kw: float = 0.0
    battery_soc: float = 0.0

    # Nested frontend compatibility structures
    dispatch: Dict[str, float] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
