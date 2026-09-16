from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, model_validator


class DispatchDetail(BaseModel):
    solarKw: float = 0.0
    windKw: float = 0.0
    batteryKw: float = 0.0
    dieselKw: float = 0.0


class MetricsDetail(BaseModel):
    totalGenerationKw: float = 0.0
    unmetDemandKw: float = 0.0
    renewablePercent: float = 0.0
    estimatedCostPerHour: float = 0.0
    fuelConsumptionLitersHour: float = 0.0
    co2EmissionsKgHour: float = 0.0
    reliabilityPercent: float = 100.0


class OptimizeRequest(BaseModel):
    demand_kw: float = Field(default=50.0, description="Community electrical load demand in kW")
    solar_available_kw: float = Field(default=30.0, description="Available solar generation in kW")
    wind_available_kw: float = Field(default=15.0, description="Available wind generation in kW")
    battery_soc: float = Field(default=70.0, ge=0, le=100, description="Current Battery State of Charge (%)")
    battery_capacity_kwh: float = Field(default=100.0, gt=0, description="Total battery capacity in kWh")
    diesel_available: bool = Field(default=True, description="Whether backup diesel generator is available")
    fuel_price: float = Field(default=95.0, description="Fuel cost per liter (or unit)")
    min_soc: float = Field(default=20.0, ge=0, le=100, description="Minimum reserve SOC (%)")
    max_soc: float = Field(default=95.0, ge=0, le=100, description="Maximum operational SOC (%)")
    fuel_remaining: Optional[float] = Field(default=360.0, description="Remaining diesel fuel in liters")
    optimization_mode: Optional[str] = Field(default="balanced", description="Optimization mode: cost_saver, balanced, green")

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        
        normalized: Dict[str, Any] = dict(data)
        
        # Support camelCase aliases sent by Member 1's frontend
        if "optimizationMode" in normalized and "optimization_mode" not in normalized:
            normalized["optimization_mode"] = str(normalized["optimizationMode"])
        if "mode" in normalized and "optimization_mode" not in normalized:
            normalized["optimization_mode"] = str(normalized["mode"])
        if "currentDemand" in normalized and "demand_kw" not in normalized:
            normalized["demand_kw"] = float(normalized["currentDemand"])
        if "solarAvailable" in normalized and "solar_available_kw" not in normalized:
            normalized["solar_available_kw"] = float(normalized["solarAvailable"])
        if "windAvailable" in normalized and "wind_available_kw" not in normalized:
            normalized["wind_available_kw"] = float(normalized["windAvailable"])
        if "batterySoc" in normalized and "battery_soc" not in normalized:
            normalized["battery_soc"] = float(normalized["batterySoc"])
        if "batteryCapacity" in normalized and "battery_capacity_kwh" not in normalized:
            normalized["battery_capacity_kwh"] = float(normalized["batteryCapacity"])
        if "dieselAvailable" in normalized and "diesel_available" not in normalized:
            val = normalized["dieselAvailable"]
            normalized["diesel_available"] = val is True or str(val).lower() == "true"
        if "dieselPrice" in normalized and "fuel_price" not in normalized:
            normalized["fuel_price"] = float(normalized["dieselPrice"])
        if "minSoc" in normalized and "min_soc" not in normalized:
            normalized["min_soc"] = float(normalized["minSoc"])
        if "maxSoc" in normalized and "max_soc" not in normalized:
            normalized["max_soc"] = float(normalized["maxSoc"])
        if "fuelRemaining" in normalized and "fuel_remaining" not in normalized:
            normalized["fuel_remaining"] = float(normalized["fuelRemaining"])

        return normalized


class OptimizeResponse(BaseModel):
    # Prompt specification top-level fields
    status: str = "optimal"
    solar_kw: float = 30.0
    wind_kw: float = 15.0
    battery_kw: float = 5.0
    diesel_kw: float = 0.0
    total_supply_kw: float = 50.0
    demand_kw: float = 50.0
    unmet_demand_kw: float = 0.0
    renewable_percentage: float = 90.0

    # Member 1 Frontend compatibility nested structures
    dispatch: DispatchDetail = Field(default_factory=DispatchDetail)
    metrics: MetricsDetail = Field(default_factory=MetricsDetail)
    grid_id: Optional[int] = 1
    solver_status: Optional[str] = "optimal"
    cost: Optional[float] = 3150.0
    dispatch_plan: Optional[list] = None
