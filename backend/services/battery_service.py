import math
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from backend.database.models import BatteryRecord
from backend.schemas.battery import BatteryStatusResponse, BatterySocPoint


class BatteryService:
    """Manages 100 kWh Lithium-ion Battery Energy Storage System (BESS) telemetry and state."""

    def __init__(self):
        self.capacity_kwh: float = 100.0
        self.current_soc: float = 68.0
        self.current_power_kw: float = 6.5  # Positive = discharging, negative = charging
        self.min_soc: float = 20.0
        self.max_soc: float = 95.0
        self.storm_reserve_percent: float = 50.0
        self.is_storm_mode: bool = False
        self.health_percent: float = 91.0
        self.cycle_count: int = 1247
        self.today_throughput_kwh: float = 82.4
        self.deep_discharge_events: int = 0

    def get_status(self, db: Optional[Session] = None) -> BatteryStatusResponse:
        # Check latest record from DB if available
        if db:
            latest = db.query(BatteryRecord).order_by(BatteryRecord.timestamp.desc()).first()
            if latest:
                self.current_soc = latest.soc_percent
                self.current_power_kw = latest.power_kw
                self.health_percent = latest.health_percent
                self.cycle_count = latest.cycle_count
                self.today_throughput_kwh = latest.today_throughput_kwh
                self.deep_discharge_events = latest.deep_discharge_events
                self.is_storm_mode = latest.is_storm_mode

        # Generate 24-hour SOC curve
        soc_history = []
        for i in range(24):
            soc_val = round(65.0 + math.sin(i / 3.0) * 20.0)
            soc_history.append(
                BatterySocPoint(
                    hour=f"{i:02d}:00",
                    soc=float(soc_val),
                    minLimit=self.min_soc,
                    stormLimit=self.storm_reserve_percent
                )
            )

        return BatteryStatusResponse(
            capacityKwh=self.capacity_kwh,
            currentSocPercent=self.current_soc,
            minSocPercent=self.min_soc,
            maxSocPercent=self.max_soc,
            stormReservePercent=self.storm_reserve_percent,
            isStormModeActive=self.is_storm_mode,
            healthPercent=self.health_percent,
            cycleCount=self.cycle_count,
            todayThroughputKwh=self.today_throughput_kwh,
            deepDischargeEvents=self.deep_discharge_events,
            socHistory=soc_history,
            capacity_kwh=self.capacity_kwh,
            current_soc_percent=self.current_soc,
            is_storm_mode=self.is_storm_mode
        )

    def set_storm_mode(self, active: bool, db: Optional[Session] = None) -> bool:
        self.is_storm_mode = active
        if db:
            record = BatteryRecord(
                timestamp=datetime.now(timezone.utc),
                soc_percent=self.current_soc,
                power_kw=self.current_power_kw,
                health_percent=self.health_percent,
                cycle_count=self.cycle_count,
                today_throughput_kwh=self.today_throughput_kwh,
                deep_discharge_events=self.deep_discharge_events,
                is_storm_mode=self.is_storm_mode
            )
            db.add(record)
            db.commit()
        return self.is_storm_mode


battery_service = BatteryService()
