from pydantic import BaseModel, Field
from typing import List

class ForecastRecord(BaseModel):
    timestamp: str
    solar_kw: float
    wind_kw: float
    demand_kw: float
    weather_condition: str

class DispatchRecord(BaseModel):
    timestamp: str
    solar_used_kw: float
    wind_used_kw: float
    battery_kw: float
    diesel_kw: float
    battery_soc_percent: float
    unmet_demand_kw: float
    decision_reason: str

class SimulationRequest(BaseModel):
    solar_capacity_kw: float = Field(..., gt=0)
    wind_capacity_kw: float = Field(..., gt=0)
    battery_capacity_kwh: float = Field(..., gt=0)
    diesel_capacity_kw: float = Field(..., ge=0)
    demand_multiplier: float = Field(..., gt=0)
    weather_scenario: str = Field(..., pattern="^(normal|cloudy|storm)$")
