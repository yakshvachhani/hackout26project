"""
OptiGrid-AI Active Location Management Service.
Maintains the central active microgrid location for backend services.
"""

from typing import List, Optional
from backend.schemas.location import LocationInfo, LocationUpdateRequest, PRESET_LOCATIONS


class LocationService:
    def __init__(self):
        # Default active location: Baramati Rural, Maharashtra, India
        self._active_location: LocationInfo = PRESET_LOCATIONS[0]
        self._presets: List[LocationInfo] = list(PRESET_LOCATIONS)

    def get_active_location(self) -> LocationInfo:
        return self._active_location

    def get_presets(self) -> List[LocationInfo]:
        return self._presets

    def set_active_location(self, update: LocationUpdateRequest) -> LocationInfo:
        loc_id = update.id or update.name.lower().replace(" ", "_").replace(",", "")
        new_loc = LocationInfo(
            id=loc_id,
            name=update.name,
            district=update.district or "Rural District",
            state=update.state or "India",
            country=update.country or "India",
            latitude=update.latitude,
            longitude=update.longitude,
            climate=update.climate or "Rural Climate",
            community=update.community or "Off-Grid Community",
        )
        self._active_location = new_loc
        return self._active_location


location_service = LocationService()
