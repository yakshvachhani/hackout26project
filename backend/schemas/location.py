"""
Location schemas and Indian rural microgrid presets for OptiGrid-AI.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class LocationInfo(BaseModel):
    id: str
    name: str
    district: str
    state: str
    country: str = "India"
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    climate: str = "Semi-Arid"
    community: str = "Rural Microgrid"

    @field_validator("latitude")
    @classmethod
    def validate_latitude_india(cls, v: float) -> float:
        if v < -90.0 or v > 90.0:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if v < 6.0 or v > 38.0:
            raise ValueError("Please select a rural location within India (Latitude 6.0° - 38.0° N).")
        return round(v, 4)

    @field_validator("longitude")
    @classmethod
    def validate_longitude_india(cls, v: float) -> float:
        if v < -180.0 or v > 180.0:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        if v < 68.0 or v > 98.0:
            raise ValueError("Please select a rural location within India (Longitude 68.0° - 98.0° E).")
        return round(v, 4)


class LocationUpdateRequest(BaseModel):
    id: Optional[str] = None
    name: str = "Custom Location"
    district: Optional[str] = "Rural District"
    state: Optional[str] = "India"
    country: str = "India"
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    climate: Optional[str] = "Rural Climate"
    community: Optional[str] = "Off-Grid Community"

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if v < 6.0 or v > 38.0:
            raise ValueError("Please select a rural location within India.")
        return round(v, 4)

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if v < 68.0 or v > 98.0:
            raise ValueError("Please select a rural location within India.")
        return round(v, 4)


PRESET_LOCATIONS: List[LocationInfo] = [
    LocationInfo(
        id="baramati",
        name="Baramati Rural",
        district="Pune District",
        state="Maharashtra",
        country="India",
        latitude=18.15,
        longitude=74.58,
        climate="Semi-Arid Agro Basin",
        community="Farming & Agro-Processing Microgrid",
    ),
    LocationInfo(
        id="dhordo",
        name="Dhordo, Kutch",
        district="Kutch District",
        state="Gujarat",
        country="India",
        latitude=23.83,
        longitude=69.57,
        climate="Arid Salt Marsh & High Solar Desert",
        community="Remote Border Crafts & Tourism Microgrid",
    ),
    LocationInfo(
        id="rameshwaram",
        name="Rameshwaram Coastal",
        district="Ramanathapuram District",
        state="Tamil Nadu",
        country="India",
        latitude=9.28,
        longitude=79.31,
        climate="Tropical Maritime & High Wind Corridor",
        community="Coastal Fishing & Desalination Microgrid",
    ),
    LocationInfo(
        id="hampi",
        name="Hampi Rural",
        district="Vijayanagara District",
        state="Karnataka",
        country="India",
        latitude=15.33,
        longitude=76.46,
        climate="Hot Semi-Arid Plateau",
        community="Heritage Tourism & Agrarian Cluster",
    ),
    LocationInfo(
        id="pokhran",
        name="Pokhran Thar Microgrid",
        district="Jaisalmer District",
        state="Rajasthan",
        country="India",
        latitude=26.92,
        longitude=71.91,
        climate="Extreme Arid Thar Desert",
        community="Off-Grid Pastoral Desert Settlement",
    ),
]
