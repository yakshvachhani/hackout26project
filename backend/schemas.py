from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AssetBase(BaseModel):
    asset_type: str
    name: str
    capacity_kw: float
    capacity_kwh: Optional[float] = None
    current_status: str
    efficiency: float

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    microgrid_id: int

    class Config:
        orm_mode = True

class MicrogridBase(BaseModel):
    name: str
    location: str
    latitude: float
    longitude: float
    population: int
    connected_households: int
    operating_mode: str

class MicrogridCreate(MicrogridBase):
    pass

class Microgrid(MicrogridBase):
    id: int
    last_updated: datetime
    assets: List[Asset] = []

    class Config:
        orm_mode = True
