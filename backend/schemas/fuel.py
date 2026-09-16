from typing import List, Optional
from pydantic import BaseModel, Field


class FuelConsumptionPoint(BaseModel):
    day: str
    liters: float


class GeneratorStatus(BaseModel):
    status: str = "STANDBY"  # STANDBY, RUNNING, OFFLINE
    name: str = "Caterpillar DE50 50kVA Generator"
    currentOutputKw: float = 0.0
    maxCapacityKw: float = 45.0
    runtimeTodayHours: float = 1.5
    fuelConsumedTodayLiters: float = 12.4
    lastMaintenanceDate: str = "2026-08-15"


class FuelStatusResponse(BaseModel):
    tankCapacityLiters: float = 500.0
    fuelRemainingLiters: float = 360.0
    tankLevelPercent: float = 72.0
    currentBurnRateLitersPerDay: float = 18.0
    daysRemaining: int = 20
    estimatedDepletionDate: str = "2026-10-02"
    status: str = "NORMAL"  # NORMAL, WARNING, CRITICAL
    generator: GeneratorStatus = Field(default_factory=GeneratorStatus)
    consumptionHistory: List[FuelConsumptionPoint] = Field(default_factory=list)

    # Snake_case aliases
    tank_capacity_liters: float = 500.0
    fuel_remaining_liters: float = 360.0
    tank_level_percent: float = 72.0
