"""
Location API endpoints for OptiGrid-AI.
Enables dynamic rural Indian microgrid switching with immediate data cascade.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.location import LocationInfo, LocationUpdateRequest
from backend.services.location_service import location_service
from backend.services.weather_service import weather_service
from backend.services.forecast_service import forecast_service
from backend.websocket.manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Location & Rural Sites"])


@router.get("/location")
async def get_location_info() -> Dict[str, Any]:
    """Returns the currently active microgrid location and available Indian presets."""
    return {
        "activeLocation": location_service.get_active_location().model_dump(),
        "presets": [loc.model_dump() for loc in location_service.get_presets()],
    }


@router.post("/location")
async def set_location(
    update: LocationUpdateRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Updates the active rural microgrid location.
    Triggers immediate cache-busting, fresh weather telemetry, 
    forecast updates, and broadcasts the change across WebSockets.
    """
    try:
        new_loc = location_service.set_active_location(update)
        logger.info(
            f"Active location changed to: {new_loc.name} "
            f"({new_loc.latitude}° N, {new_loc.longitude}° E)"
        )

        # 1. Fetch fresh weather for new coordinates (force_refresh=True to bypass old cache)
        weather = await weather_service.get_current_weather(
            db=db,
            force_refresh=True,
            latitude=new_loc.latitude,
            longitude=new_loc.longitude,
        )

        # 2. Generate updated 24h / 96-interval forecast for new coordinates
        forecast = forecast_service.generate_24h_forecast(
            latitude=new_loc.latitude,
            longitude=new_loc.longitude,
        )

        # 3. Broadcast real-time WebSocket event
        loc_dict = new_loc.model_dump()
        await ws_manager.broadcast_location_changed(loc_dict)

        return {
            "status": "success",
            "activeLocation": loc_dict,
            "weather": weather.model_dump(),
            "weatherSource": weather.source,
            "forecast": [f.model_dump() for f in forecast],
        }
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as e:
        logger.error(f"Failed to update location: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update location: {str(e)}")
