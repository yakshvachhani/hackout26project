from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.schemas.battery import BatteryStatusResponse
from backend.services.battery_service import battery_service
from backend.websocket.manager import ws_manager

router = APIRouter(tags=["Battery Storage (BESS)"])


@router.get("/battery", response_model=BatteryStatusResponse)
async def get_battery_status(db: Session = Depends(get_db)):
    """Returns current telemetry, operational limits, health, and 24h SOC trajectory for BESS."""
    return battery_service.get_status(db=db)


@router.post("/battery/storm-mode")
async def toggle_storm_mode(active: bool = Body(..., embed=True), db: Session = Depends(get_db)):
    """Toggles storm reserve mode (keeps 50% SOC reserved for severe weather)."""
    new_state = battery_service.set_storm_mode(active, db=db)
    await ws_manager.broadcast_storm_mode(is_active=new_state, reserve_percent=50.0)
    return {"status": "success", "isStormModeActive": new_state}
