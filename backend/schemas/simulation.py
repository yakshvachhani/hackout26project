from typing import Dict, Any, Union, Optional, List
from pydantic import BaseModel, Field, model_validator


class SimulationImpact(BaseModel):
    p0ReliabilityPercent: float = 100.0
    p1ServedPercent: float = 92.0
    p2ServedPercent: float = 61.0
    additionalDieselLiters: Union[float, str] = 0.0
    additionalCo2Kg: Union[float, str] = 0.0
    costDifferenceDollars: Union[float, str] = 0.0


class SimulationRequest(BaseModel):
    scenario: str = "SOLAR_FAILURE"
    severity: float = Field(default=80.0, ge=0, le=100)
    durationHours: float = Field(default=12.0, ge=1, le=168)
    solar_capacity_kw: float = Field(default=100.0, ge=0)
    battery_capacity_kwh: float = Field(default=200.0, ge=0)
    demand_kw: float = Field(default=80.0, gt=0)
    rain_probability: float = Field(default=70.0, ge=0, le=100)
    grid_price_per_kwh: float = Field(default=8.0, ge=0)
    optimization_mode: str = "balanced"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        if "duration_hours" in normalized and "durationHours" not in normalized:
            normalized["durationHours"] = normalized["duration_hours"]
        if "solarCapacityKw" in normalized and "solar_capacity_kw" not in normalized:
            normalized["solar_capacity_kw"] = normalized["solarCapacityKw"]
        if "batteryCapacityKwh" in normalized and "battery_capacity_kwh" not in normalized:
            normalized["battery_capacity_kwh"] = normalized["batteryCapacityKwh"]
        if "demandKw" in normalized and "demand_kw" not in normalized:
            normalized["demand_kw"] = normalized["demandKw"]
        if "rainProbability" in normalized and "rain_probability" not in normalized:
            normalized["rain_probability"] = normalized["rainProbability"]
        if "gridPricePerKwh" in normalized and "grid_price_per_kwh" not in normalized:
            normalized["grid_price_per_kwh"] = normalized["gridPricePerKwh"]
        if "optimizationMode" in normalized and "optimization_mode" not in normalized:
            normalized["optimization_mode"] = normalized["optimizationMode"]
        return normalized


class SimulationResponse(BaseModel):
    scenario: str
    severity: float
    durationHours: float
    before: Dict[str, float]
    after: Dict[str, float]
    impact: SimulationImpact
    withoutOptimization: Optional[Dict[str, Any]] = None
    withOptigrid: Optional[Dict[str, Any]] = None
    comparison: Optional[Dict[str, Any]] = None
    aiExplanation: Optional[str] = None
    chartData: Optional[List[Dict[str, Any]]] = None

