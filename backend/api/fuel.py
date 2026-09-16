from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.schemas.fuel import FuelStatusResponse
from backend.services.fuel_service import fuel_service

router = APIRouter(tags=["Fuel Intelligence & Logistics"])


@router.get("/fuel", response_model=FuelStatusResponse)
async def get_fuel_status(db: Session = Depends(get_db)):
    """Returns diesel tank levels, autonomy days, fuel burn rate, and generator status."""
    return fuel_service.get_status(db=db)


@router.get("/cost")
async def get_cost_comparison():
    """Returns cost comparison between diesel-only and optimized microgrid dispatch."""
    return [
        {'day': 'Mon', 'dieselOnlyCost': 5200, 'optimizedCost': 3100, 'savedCO2': 120},
        {'day': 'Tue', 'dieselOnlyCost': 4800, 'optimizedCost': 2800, 'savedCO2': 145},
        {'day': 'Wed', 'dieselOnlyCost': 5100, 'optimizedCost': 2400, 'savedCO2': 180},
        {'day': 'Thu', 'dieselOnlyCost': 4900, 'optimizedCost': 3200, 'savedCO2': 115},
        {'day': 'Fri', 'dieselOnlyCost': 5400, 'optimizedCost': 2900, 'savedCO2': 155},
        {'day': 'Sat', 'dieselOnlyCost': 4600, 'optimizedCost': 2100, 'savedCO2': 190},
        {'day': 'Sun', 'dieselOnlyCost': 4500, 'optimizedCost': 2200, 'savedCO2': 185},
    ]
