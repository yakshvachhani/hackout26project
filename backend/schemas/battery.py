from typing import List
from pydantic import BaseModel, Field


class BatterySocPoint(BaseModel):
    hour: str
    soc: float
    minLimit: float = 20.0
    stormLimit: float = 50.0


class BatteryStatusResponse(BaseModel):
    # CamelCase (Frontend compatibility)
    capacityKwh: float = 100.0
    currentSocPercent: float = 68.0
    minSocPercent: float = 20.0
    maxSocPercent: float = 95.0
    stormReservePercent: float = 50.0
    isStormModeActive: bool = False
    healthPercent: float = 91.0
    cycleCount: int = 1247
    todayThroughputKwh: float = 82.4
    deepDischargeEvents: int = 0
    socHistory: List[BatterySocPoint] = Field(default_factory=list)

    # Snake_case aliases
    capacity_kwh: float = 100.0
    current_soc_percent: float = 68.0
    is_storm_mode: bool = False
