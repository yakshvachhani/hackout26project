from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, Index
from backend.database.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    demand_kw = Column(Float, nullable=False, default=0.0)
    solar_kw = Column(Float, nullable=False, default=0.0)
    wind_kw = Column(Float, nullable=False, default=0.0)
    battery_kw = Column(Float, nullable=False, default=0.0)
    diesel_kw = Column(Float, nullable=False, default=0.0)
    renewable_percentage = Column(Float, nullable=False, default=0.0)
    reliability = Column(Float, nullable=False, default=100.0)

    __table_args__ = (
        Index("idx_energy_timestamp", "timestamp"),
    )


class BatteryRecord(Base):
    __tablename__ = "battery_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    soc_percent = Column(Float, nullable=False, default=68.0)
    power_kw = Column(Float, nullable=False, default=0.0)
    health_percent = Column(Float, nullable=False, default=91.0)
    cycle_count = Column(Integer, nullable=False, default=1247)
    today_throughput_kwh = Column(Float, nullable=False, default=82.4)
    deep_discharge_events = Column(Integer, nullable=False, default=0)
    is_storm_mode = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("idx_battery_timestamp", "timestamp"),
    )


class DieselRecord(Base):
    __tablename__ = "diesel_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    status = Column(String(32), nullable=False, default="OFF")  # OFF, STANDBY, RUNNING
    power_kw = Column(Float, nullable=False, default=0.0)
    fuel_level_liters = Column(Float, nullable=False, default=360.0)
    burn_rate_liters_day = Column(Float, nullable=False, default=18.0)
    runtime_today_hours = Column(Float, nullable=False, default=1.5)
    fuel_consumed_today_liters = Column(Float, nullable=False, default=12.4)

    __table_args__ = (
        Index("idx_diesel_timestamp", "timestamp"),
    )


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    condition = Column(String(64), nullable=False, default="Partly Cloudy")
    temperature_c = Column(Float, nullable=False, default=28.5)
    solar_irradiance_wm2 = Column(Float, nullable=False, default=820.0)
    wind_speed_ms = Column(Float, nullable=False, default=7.2)
    forecast_warning = Column(String(255), nullable=True)

    __table_args__ = (
        Index("idx_weather_timestamp", "timestamp"),
    )


class DispatchRecord(Base):
    __tablename__ = "dispatch_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    status = Column(String(32), nullable=False, default="optimal")
    solar_kw = Column(Float, nullable=False, default=0.0)
    wind_kw = Column(Float, nullable=False, default=0.0)
    battery_kw = Column(Float, nullable=False, default=0.0)
    diesel_kw = Column(Float, nullable=False, default=0.0)
    total_supply_kw = Column(Float, nullable=False, default=0.0)
    demand_kw = Column(Float, nullable=False, default=0.0)
    unmet_demand_kw = Column(Float, nullable=False, default=0.0)
    renewable_percentage = Column(Float, nullable=False, default=0.0)
    cost_per_hour = Column(Float, nullable=False, default=0.0)
    co2_avoided_kg = Column(Float, nullable=False, default=0.0)
    reliability_pct = Column(Float, nullable=False, default=100.0)

    __table_args__ = (
        Index("idx_dispatch_timestamp", "timestamp"),
    )


class LoadRecord(Base):
    __tablename__ = "load_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    total_demand_kw = Column(Float, nullable=False, default=48.2)
    p0_served_pct = Column(Float, nullable=False, default=100.0)
    p1_served_pct = Column(Float, nullable=False, default=92.0)
    p2_served_pct = Column(Float, nullable=False, default=61.0)
    details_json = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_load_timestamp", "timestamp"),
    )


class AlertRecord(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    type = Column(String(32), nullable=False, default="INFO")  # SUCCESS, INFO, WARNING, CRITICAL
    title = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, nullable=False, default=False)
    time_str = Column(String(32), nullable=True)

    __table_args__ = (
        Index("idx_alert_timestamp", "timestamp"),
    )


class SimulationRecord(Base):
    __tablename__ = "simulation_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    scenario = Column(String(64), nullable=False)
    severity = Column(Float, nullable=False, default=50.0)
    duration_hours = Column(Float, nullable=False, default=12.0)
    p0_reliability_pct = Column(Float, nullable=False, default=100.0)
    p1_served_pct = Column(Float, nullable=False, default=92.0)
    p2_served_pct = Column(Float, nullable=False, default=61.0)
    extra_diesel_liters = Column(Float, nullable=False, default=0.0)
    extra_co2_kg = Column(Float, nullable=False, default=0.0)
    cost_diff_dollars = Column(Float, nullable=False, default=0.0)
    details_json = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_simulation_timestamp", "timestamp"),
    )
