from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

from backend.database.models import DieselRecord
from backend.schemas.fuel import FuelStatusResponse, GeneratorStatus, FuelConsumptionPoint


class FuelService:
    """Manages diesel fuel storage, daily burn rates, logistics warnings, and generator metrics."""

    def __init__(self):
        self.tank_capacity: float = 500.0
        self.fuel_remaining: float = 360.0
        self.burn_rate_daily: float = 18.0  # liters per day
        self.generator_status: str = "STANDBY"
        self.current_output_kw: float = 0.0
        self.max_capacity_kw: float = 45.0
        self.runtime_today_hours: float = 1.5
        self.fuel_consumed_today: float = 12.4

    def get_status(self, db: Optional[Session] = None) -> FuelStatusResponse:
        if db:
            latest = db.query(DieselRecord).order_by(DieselRecord.timestamp.desc()).first()
            if latest:
                self.fuel_remaining = latest.fuel_level_liters
                self.generator_status = latest.status
                self.current_output_kw = latest.power_kw
                self.burn_rate_daily = latest.burn_rate_liters_day
                self.runtime_today_hours = latest.runtime_today_hours
                self.fuel_consumed_today = latest.fuel_consumed_today_liters

        tank_pct = round((self.fuel_remaining / self.tank_capacity) * 100.0, 1)
        days = int(self.fuel_remaining / max(1.0, self.burn_rate_daily))
        depletion_date = (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")

        system_status = "NORMAL"
        if tank_pct < 20.0:
            system_status = "CRITICAL"
        elif tank_pct < 40.0:
            system_status = "WARNING"

        consumption_history = [
            FuelConsumptionPoint(day="Mon", liters=14.0),
            FuelConsumptionPoint(day="Tue", liters=22.0),
            FuelConsumptionPoint(day="Wed", liters=18.0),
            FuelConsumptionPoint(day="Thu", liters=12.0),
            FuelConsumptionPoint(day="Fri", liters=16.0),
            FuelConsumptionPoint(day="Sat", liters=20.0),
            FuelConsumptionPoint(day="Sun", liters=18.0),
        ]

        generator = GeneratorStatus(
            status=self.generator_status,
            name="Caterpillar DE50 50kVA Generator",
            currentOutputKw=self.current_output_kw,
            maxCapacityKw=self.max_capacity_kw,
            runtimeTodayHours=self.runtime_today_hours,
            fuelConsumedTodayLiters=self.fuel_consumed_today,
            lastMaintenanceDate="2026-08-15"
        )

        return FuelStatusResponse(
            tankCapacityLiters=self.tank_capacity,
            fuelRemainingLiters=self.fuel_remaining,
            tankLevelPercent=tank_pct,
            currentBurnRateLitersPerDay=self.burn_rate_daily,
            daysRemaining=days,
            estimatedDepletionDate=depletion_date,
            status=system_status,
            generator=generator,
            consumptionHistory=consumption_history,
            tank_capacity_liters=self.tank_capacity,
            fuel_remaining_liters=self.fuel_remaining,
            tank_level_percent=tank_pct
        )


fuel_service = FuelService()
