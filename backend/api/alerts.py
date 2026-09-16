from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import AlertRecord
from backend.schemas.alerts import AlertItem
from backend.websocket.manager import ws_manager

router = APIRouter(tags=["Alerts & Notifications"])


@router.get("/alerts", response_model=List[AlertItem])
async def get_alerts(db: Session = Depends(get_db)):
    """Returns all active microgrid telemetry and dispatch alerts."""
    records = db.query(AlertRecord).order_by(AlertRecord.timestamp.desc()).all()
    if not records:
        return [
            AlertItem(
                id=1,
                type="SUCCESS",
                title="Optimization Run Complete",
                message="System operating normally with 86.5% renewable penetration.",
                timestamp="10:45 AM",
                read=False
            ),
            AlertItem(
                id=2,
                type="INFO",
                title="Solar Peak Window",
                message="Solar irradiance peak reaching 820 W/m². Battery charging active.",
                timestamp="10:30 AM",
                read=False
            ),
            AlertItem(
                id=3,
                type="WARNING",
                title="Storm Advisory",
                message="High wind and storm predicted in 18 hours. Consider Storm Reserve mode.",
                timestamp="09:15 AM",
                read=False
            )
        ]

    return [
        AlertItem(
            id=r.id,
            type=r.type,
            title=r.title,
            message=r.message,
            timestamp=r.time_str or r.timestamp.strftime("%I:%M %p"),
            read=r.read
        )
        for r in records
    ]


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
