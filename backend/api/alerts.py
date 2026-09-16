from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import AlertRecord
from backend.schemas.alerts import AlertItem
from backend.services.alert_service import alert_service
from backend.websocket.manager import ws_manager

router = APIRouter(tags=["Alerts & Notifications"])


@router.get("/alerts", response_model=List[AlertItem])
async def get_alerts(
    location_id: Optional[str] = Query(None, description="Active microgrid location ID"),
    mode: Optional[str] = Query("LIVE", description="Grid operational mode (LIVE or SIMULATION)"),
    scenario: Optional[str] = Query("nominal", description="Simulation scenario if applicable"),
    db: Session = Depends(get_db)
):
    """Returns dynamically evaluated microgrid telemetry, weather forecast, and dispatch alerts."""
    live_alerts = await alert_service.generate_live_alerts(
        db=db,
        location_id=location_id,
        mode=mode,
        scenario=scenario,
    )
    return live_alerts


@router.post("/alerts", response_model=AlertItem)
async def create_alert(alert: AlertItem, db: Session = Depends(get_db)):
    """Creates a new alert and broadcasts it to connected WebSocket clients."""
    now = datetime.now(timezone.utc)
    record = AlertRecord(
        timestamp=now,
        type=alert.type,
        title=alert.title,
        message=alert.message,
        read=alert.read,
        time_str=now.strftime("%I:%M %p")
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    created_alert = AlertItem(
        id=record.id,
        type=record.type,
        title=record.title,
        message=record.message,
        timestamp=record.time_str,
        read=record.read
    )

    await ws_manager.broadcast_alert_created(created_alert.model_dump())
    return created_alert
