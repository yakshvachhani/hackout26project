from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import ForecastRecord, DispatchRecord, SimulationRequest
from mock_data import generate_forecast, generate_dispatch

app = FastAPI(title="Microgrid Dispatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_hours(hours: int):
    if hours <= 0:
        raise HTTPException(status_code=400, detail="Hours must be a positive integer.")
    if hours > 168: # Max 1 week
        raise HTTPException(status_code=400, detail="Max 168 hours allowed.")
    return hours

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/forecast", response_model=List[ForecastRecord])
def get_forecast(hours: int = Query(48, description="Number of hours to forecast")):
    valid_hours = validate_hours(hours)
    return generate_forecast(hours=valid_hours)

@app.get("/optimize", response_model=List[DispatchRecord])
def get_optimize(hours: int = Query(48, description="Number of hours to optimize")):
    valid_hours = validate_hours(hours)
    # Default capacities for the basic endpoint
    forecast = generate_forecast(hours=valid_hours)
    # 200kWh battery, 50kW diesel
    return generate_dispatch(forecast, battery_capacity_kwh=200.0, diesel_capacity_kw=50.0)

@app.get("/dispatch-history", response_model=List[DispatchRecord])
def get_dispatch_history(hours: int = Query(24, description="Number of past hours")):
    valid_hours = validate_hours(hours)
    # Generate past forecast data
    forecast = generate_forecast(hours=valid_hours)
    # Simulate history with random deviations
    return generate_dispatch(forecast, battery_capacity_kwh=200.0, diesel_capacity_kw=50.0, is_history=True)

@app.post("/simulate", response_model=List[DispatchRecord])
def simulate_dispatch(request: SimulationRequest):
    forecast = generate_forecast(
        hours=48, # Simulate next 48 hours based on parameters
        weather_scenario=request.weather_scenario,
        demand_multiplier=request.demand_multiplier,
        solar_capacity_kw=request.solar_capacity_kw,
        wind_capacity_kw=request.wind_capacity_kw
    )
    return generate_dispatch(
        forecast, 
        battery_capacity_kwh=request.battery_capacity_kwh, 
        diesel_capacity_kw=request.diesel_capacity_kw
    )
