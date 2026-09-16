from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.database.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
async def get_health(db: Session = Depends(get_db)):
    """Health check endpoint for OptiGrid-AI backend services and database."""
    db_status = "HEALTHY"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"UNHEALTHY: {str(e)}"

    return {
        "status": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "service": "OptiGrid-AI Backend",
        "version": "1.0.0"
    }
