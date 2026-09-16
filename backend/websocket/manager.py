import json
import logging
from typing import List, Any, Dict
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts real-time microgrid events."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Any):
        """Broadcasts a structured event payload to all connected clients."""
        if not self.active_connections:
            return

        payload = {
            "type": event_type,
            "data": data
        }
        message_str = json.dumps(payload, default=str)

        disconnected = []
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.warning(f"Error sending message to websocket client: {e}")
                disconnected.append(connection)

        for dead_conn in disconnected:
            self.disconnect(dead_conn)

    # Convenience broadcast methods for the required events:
    async def broadcast_system_status(self, data: Dict[str, Any]):
        await self.broadcast("SYSTEM_STATUS_UPDATED", data)

    async def broadcast_solar_changed(self, solar_kw: float):
        await self.broadcast("SOLAR_CHANGED", {"solarGenKw": solar_kw, "solar_kw": solar_kw})

    async def broadcast_wind_changed(self, wind_kw: float):
        await self.broadcast("WIND_CHANGED", {"windGenKw": wind_kw, "wind_kw": wind_kw})

    async def broadcast_battery_changed(self, soc_percent: float, power_kw: float):
        await self.broadcast("BATTERY_CHANGED", {
            "batterySocPercent": soc_percent,
            "batteryPowerKw": power_kw,
            "battery_soc": soc_percent,
            "battery_kw": power_kw
        })

    async def broadcast_diesel_started(self, power_kw: float = 15.0):
        await self.broadcast("DIESEL_STARTED", {
            "dieselStatus": "RUNNING",
            "dieselPowerKw": power_kw,
            "message": "Diesel generator started to cover microgrid deficit"
        })

    async def broadcast_diesel_stopped(self):
        await self.broadcast("DIESEL_STOPPED", {
            "dieselStatus": "OFF",
            "dieselPowerKw": 0.0,
            "message": "Diesel generator shut down; renewable generation sufficient"
        })

    async def broadcast_new_optimization(self, dispatch_result: Dict[str, Any]):
        await self.broadcast("NEW_OPTIMIZATION", dispatch_result)

    async def broadcast_load_shed(self, tier: str, curtailed_kw: float, reason: str):
        await self.broadcast("LOAD_SHED", {
            "tier": tier,
            "curtailedKw": curtailed_kw,
            "reason": reason
        })

    async def broadcast_storm_mode(self, is_active: bool, reserve_percent: float = 50.0):
        await self.broadcast("STORM_MODE", {
            "isStormModeActive": is_active,
            "stormReservePercent": reserve_percent
        })

    async def broadcast_fuel_warning(self, fuel_remaining_liters: float, days_remaining: int):
        await self.broadcast("FUEL_WARNING", {
            "fuelRemainingLiters": fuel_remaining_liters,
            "daysRemaining": days_remaining,
            "severity": "WARNING"
        })

    async def broadcast_alert_created(self, alert: Dict[str, Any]):
        await self.broadcast("ALERT_CREATED", alert)

    async def broadcast_location_changed(self, location_data: Dict[str, Any]):
        await self.broadcast("LOCATION_CHANGED", location_data)


ws_manager = ConnectionManager()
