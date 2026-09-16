import asyncio
import logging
import random
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config.settings import settings
from backend.database.database import engine, Base, SessionLocal
from backend.database.models import (
    EnergyReading,
    BatteryRecord,
    DieselRecord,
    WeatherRecord,
    DispatchRecord,
    LoadRecord,
    AlertRecord
)
from backend.websocket.manager import ws_manager

# API Routers
from backend.api.status import router as status_router
from backend.api.forecast import router as forecast_router
from backend.api.battery import router as battery_router
from backend.api.fuel import router as fuel_router
from backend.api.loads import router as loads_router
from backend.api.optimizer import router as optimizer_router
from backend.api.simulation import router as simulation_router
from backend.api.alerts import router as alerts_router
from backend.api.health import router as health_router
from backend.api.location import router as location_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("optigrid")


def seed_database_if_empty():
    """Initializes tables and populates default microgrid baseline data if empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(EnergyReading).first() is None:
            logger.info("Database empty. Seeding initial OptiGrid-AI telemetry and baseline records...")

            # 1. Energy reading
            energy = EnergyReading(
                timestamp=datetime.now(timezone.utc),
                demand_kw=48.2,
                solar_kw=26.4,
                wind_kw=15.3,
                battery_kw=6.5,
                diesel_kw=0.0,
                renewable_percentage=86.5,
                reliability=100.0
            )
            db.add(energy)

            # 2. Battery record
            battery = BatteryRecord(
                timestamp=datetime.now(timezone.utc),
                soc_percent=68.0,
                power_kw=6.5,
                health_percent=91.0,
                cycle_count=1247,
                today_throughput_kwh=82.4,
                deep_discharge_events=0,
                is_storm_mode=False
            )
            db.add(battery)

            # 3. Diesel record
            diesel = DieselRecord(
                timestamp=datetime.now(timezone.utc),
                status="OFF",
                power_kw=0.0,
                fuel_level_liters=360.0,
                burn_rate_liters_day=18.0,
                runtime_today_hours=1.5,
                fuel_consumed_today_liters=12.4
            )
            db.add(diesel)

            # 4. Weather record
            weather = WeatherRecord(
                timestamp=datetime.now(timezone.utc),
                condition="Partly Cloudy",
                temperature_c=28.5,
                solar_irradiance_wm2=820.0,
                wind_speed_ms=7.2,
                forecast_warning=None
            )
            db.add(weather)

            # 5. Dispatch record
            dispatch = DispatchRecord(
                timestamp=datetime.now(timezone.utc),
                status="optimal",
                solar_kw=26.4,
                wind_kw=15.3,
                battery_kw=6.5,
                diesel_kw=0.0,
                total_supply_kw=48.2,
                demand_kw=48.2,
                unmet_demand_kw=0.0,
                renewable_percentage=86.5,
                cost_per_hour=4.25,
                co2_avoided_kg=142.8,
                reliability_pct=100.0
            )
            db.add(dispatch)

            # 6. Load record
            load = LoadRecord(
                timestamp=datetime.now(timezone.utc),
                total_demand_kw=48.2,
                p0_served_pct=100.0,
                p1_served_pct=92.0,
                p2_served_pct=61.0,
                details_json="{}"
            )
            db.add(load)

            # 7. Initial alerts
            alerts = [
                AlertRecord(
                    timestamp=datetime.now(timezone.utc),
                    type="SUCCESS",
                    title="Optimization Run Complete",
                    message="System operating normally with 86.5% renewable penetration.",
                    read=False,
                    time_str="10:45 AM"
                ),
                AlertRecord(
                    timestamp=datetime.now(timezone.utc),
                    type="INFO",
                    title="Solar Peak Window",
                    message="Solar irradiance peak reaching 820 W/m². Battery charging active.",
                    read=False,
                    time_str="10:30 AM"
                ),
                AlertRecord(
                    timestamp=datetime.now(timezone.utc),
                    type="WARNING",
                    title="Storm Advisory",
                    message="High wind and storm predicted in 18 hours. Consider Storm Reserve mode.",
                    read=False,
                    time_str="09:15 AM"
                ),
            ]
            db.add_all(alerts)

            db.commit()
            logger.info("Database baseline seed complete.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


async def telemetry_broadcaster():
    """Background task that broadcasts realistic microgrid bus telemetry fluctuations."""
    logger.info("Telemetry background broadcaster started.")
    try:
        while True:
            await asyncio.sleep(settings.TELEMETRY_INTERVAL_SECONDS)
            if not ws_manager.active_connections:
                continue

            solar = round(26.4 + random.uniform(-1.5, 1.5), 1)
            wind = round(15.3 + random.uniform(-1.0, 1.0), 1)
            total_ren = round(solar + wind, 1)
            demand = round(48.2 + random.uniform(-0.8, 0.8), 1)
            battery = round(demand - total_ren, 1)
            ren_pct = round((total_ren / demand) * 100.0, 1)

            # Emit WebSocket events
            await ws_manager.broadcast_system_status({
                "metrics": {
                    "currentDemandKw": demand,
                    "renewableGenKw": total_ren,
                    "solarGenKw": solar,
                    "windGenKw": wind,
                    "batteryPowerKw": battery,
                    "renewablePercent": ren_pct,
                }
            })
            await ws_manager.broadcast_solar_changed(solar)
            await ws_manager.broadcast_wind_changed(wind)
    except asyncio.CancelledError:
        logger.info("Telemetry broadcaster background task cancelled.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("OptiGrid-AI Backend initializing...")
    seed_database_if_empty()
    broadcaster_task = asyncio.create_task(telemetry_broadcaster())
    yield
    # Shutdown
    logger.info("Shutting down OptiGrid-AI Backend...")
    broadcaster_task.cancel()
    try:
        await broadcaster_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Microgrid Energy Mix Optimizer & Telemetry Platform for Off-Grid Communities (Hackathon)",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler (Never expose stack traces to client)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal microgrid service error occurred. Please try again later."}
    )


# Mount WebSocket Telemetry Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep receiving client heartbeat or messages
            data = await websocket.receive_text()
            logger.debug(f"Received from client: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


# Mount API Routers
app.include_router(status_router, prefix="/api")
app.include_router(forecast_router, prefix="/api")
app.include_router(battery_router, prefix="/api")
app.include_router(fuel_router, prefix="/api")
app.include_router(loads_router, prefix="/api")
app.include_router(optimizer_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(location_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "system": "OptiGrid-AI Microgrid Optimizer",
        "role": "Member 2 Backend API",
        "docs": "/docs",
        "status": "ONLINE"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
