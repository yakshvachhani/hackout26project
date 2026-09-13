from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import pytz

from database import engine, Base, get_db
import models
import schemas
from services.weather_service import WeatherService
from services.simulation_service import SimulationService
from services.optimizer_service import OptimizationEngine










































































# Ensure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microgrid Energy Intelligence API",
    description="Backend services for the Microgrid operations platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

weather_service = WeatherService()
simulation_service = SimulationService()
optimizer = OptimizationEngine(horizon_hours=24)

@app.get("/")
def read_root():
    return {"status": "online", "mode": "LIVE", "server_time": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()}

@app.get("/api/microgrids")
def get_microgrids(db: Session = Depends(get_db)):
    return db.query(models.Microgrid).all()

@app.get("/api/microgrids/{grid_id}/status")
def get_microgrid_status(grid_id: int, db: Session = Depends(get_db)):
    grid = db.query(models.Microgrid).filter(models.Microgrid.id == grid_id).first()
    if not grid:
        raise HTTPException(status_code=404, detail="Microgrid not found")
        
    assets = db.query(models.Asset).filter(models.Asset.microgrid_id == grid_id).all()
    
    # In a real app we'd fetch live SCADA telemetry.
    # For HackOut, we generate current timestep data via SimulationService
    
    # 1. Fetch current weather for this location
    weather_res = weather_service.get_forecast(grid.latitude, grid.longitude, horizon_days=1)
    
    current_temp = 25
    current_rad = 800
    current_wind = 12
    
    if weather_res["status"] == "success":
        # Extract just the first hour or current hour
        data = weather_res["data"]
        current_temp = data["temperature"][0]
        current_rad = data["solar_radiation"][0]
        current_wind = data["wind_speed"][0]
        
    # Generate live simulated load
    hour_of_day = datetime.now(pytz.timezone('Asia/Kolkata')).hour
    demand_curve = simulation_service.generate_demand_forecast(grid.connected_households, 4, 10, horizon_hours=24)
    current_demand = demand_curve[hour_of_day]
    
    # Asset generation based on weather
    live_assets = []
    total_generation = 0
    solar_gen = 0
    wind_gen = 0
    
    for a in assets:
        gen = 0
        if a.asset_type == "SOLAR":
            gen = simulation_service.simulate_solar_generation([current_rad], a.capacity_kw, a.efficiency, [current_temp])[0]
            solar_gen = gen
        elif a.asset_type == "WIND":
            gen = simulation_service.simulate_wind_generation([current_wind], a.capacity_kw)[0]
            wind_gen = gen
            
        total_generation += gen
        live_assets.append({
            "id": a.id,
            "type": a.asset_type,
            "name": a.name,
            "status": a.current_status,
            "generation_kw": gen,
            "capacity_kw": a.capacity_kw,
            "soc": 68.0 if a.asset_type == "BATTERY" else None # hardcoded for now, real optimizer sets this
        })
        
    return {
        "grid_id": grid.id,
        "mode": grid.operating_mode,
        "demand_kw": current_demand,
        "renewable_gen_kw": solar_gen + wind_gen,
        "assets": live_assets,
        "weather": {
            "temperature": current_temp,
            "solar_radiation": current_rad,
            "wind_speed": current_wind
        }
    }

@app.post("/api/optimize")
def run_optimization(grid_id: int, db: Session = Depends(get_db)):
    # Runs the SciPy optimization engine based on the forecast
    grid = db.query(models.Microgrid).filter(models.Microgrid.id == grid_id).first()
    if not grid:
        raise HTTPException(status_code=404, detail="Microgrid not found")
        
    assets = db.query(models.Asset).filter(models.Asset.microgrid_id == grid_id).all()
    
    # Get capacities
    solar_cap, wind_cap, batt_cap, batt_kw, diesel_cap = 0, 0, 0, 0, 0
    for a in assets:
        if a.asset_type == "SOLAR": solar_cap = a.capacity_kw
        elif a.asset_type == "WIND": wind_cap = a.capacity_kw
        elif a.asset_type == "BATTERY": 
            batt_cap = a.capacity_kwh
            batt_kw = a.capacity_kw
        elif a.asset_type == "DIESEL": diesel_cap = a.capacity_kw
        
    # Get weather
    weather = weather_service.get_forecast(grid.latitude, grid.longitude, horizon_days=1)
    if weather["status"] != "success":
        raise HTTPException(status_code=500, detail="Failed to fetch weather forecast")
        
    # Get simulation forecasts
    demand = simulation_service.generate_demand_forecast(grid.connected_households, 4, 10, horizon_hours=24)
    solar_forecast = simulation_service.simulate_solar_generation(weather["data"]["solar_radiation"], solar_cap, temp_c=weather["data"]["temperature"])
    wind_forecast = simulation_service.simulate_wind_generation(weather["data"]["wind_speed"], wind_cap)
    
    # Run optimizer
    res = optimizer.optimize_dispatch(
        demand=demand,
        solar_forecast=solar_forecast,
        wind_forecast=wind_forecast,
        solar_cap=solar_cap,
        wind_cap=wind_cap,
        batt_cap_kwh=batt_cap,
        batt_max_kw=batt_kw,
        batt_min_soc=0.2,
        batt_max_soc=0.9,
        batt_init_soc=0.5,
        diesel_cap=diesel_cap,
        diesel_price=90.0, # Rs per liter
        carbon_price=1000.0 # Rs per ton
    )
    
    return {
        "grid_id": grid.id,
        "solver_status": res["status"],
        "cost": res.get("cost"),
        "dispatch_plan": res.get("results")
    }

@app.get('/api/weather')
def get_weather_forecast(lat: float = 23.7337, lon: float = 69.8597, days: int = 2):
    res = weather_service.get_forecast(lat, lon, horizon_days=days)
    if res['status'] == 'success':
        return res['data']
    raise HTTPException(status_code=500, detail='Failed to fetch weather')

@app.get('/api/demand')
def get_demand():
    demand_curve = simulation_service.generate_demand_forecast(250, 4, 10, horizon_hours=24)
    res = []
    for i, d in enumerate(demand_curve):
        res.append({
            'time': f"{str(i).zfill(2)}:00",
            'household': round(d * 0.6, 1),
            'business': round(d * 0.3, 1),
            'critical': round(d * 0.1, 1),
            'total': d
        })
    return res

@app.get('/api/battery')
def get_battery():
    res = []
    import math
    for i in range(24):
        soc = 40 + math.sin(i * math.pi / 12) * 30
        res.append({'time': f"{str(i).zfill(2)}:00", 'soc': round(soc, 1)})
    return res

@app.get('/api/dispatch')
def get_dispatch():
    res = []
    import math, random
    for i in range(24):
        is_day = 6 < i < 18
        solar = round(math.sin((i - 6) * math.pi / 12) * 180) if is_day else 0
        wind = round(20 + random.random() * 30)
        demand = 80 + (80 if i in [8, 19] else 0) + random.random() * 20
        batt_chg = min(solar + wind - demand, 50) if solar + wind > demand else 0
        batt_dis = min(demand - (solar + wind), 40) if demand > solar + wind and i < 18 else 0
        diesel = demand - (solar + wind + batt_dis) if demand > solar + wind else 0
        
        res.append({
            'time': f"{str(i).zfill(2)}:00",
            'solar': max(0, solar),
            'wind': max(0, wind),
            'batteryDischarge': max(0, batt_dis),
            'batteryCharge': -max(0, batt_chg),
            'diesel': max(0, diesel),
            'demand': round(demand)
        })
    return res

@app.get('/api/cost')
def get_cost():
    return [
        {'day': 'Mon', 'dieselOnlyCost': 5200, 'optimizedCost': 3100, 'savedCO2': 120},
        {'day': 'Tue', 'dieselOnlyCost': 4800, 'optimizedCost': 2800, 'savedCO2': 145},
        {'day': 'Wed', 'dieselOnlyCost': 5100, 'optimizedCost': 2400, 'savedCO2': 180},
        {'day': 'Thu', 'dieselOnlyCost': 4900, 'optimizedCost': 3200, 'savedCO2': 115},
        {'day': 'Fri', 'dieselOnlyCost': 5400, 'optimizedCost': 2900, 'savedCO2': 155},
        {'day': 'Sat', 'dieselOnlyCost': 4600, 'optimizedCost': 2100, 'savedCO2': 190},
        {'day': 'Sun', 'dieselOnlyCost': 4500, 'optimizedCost': 2200, 'savedCO2': 185},
    ]

@app.get('/api/analytics')
def get_analytics_db(days: int = 30, db: Session = Depends(get_db)):
    from models import DailyLog
    logs = db.query(DailyLog).order_by(DailyLog.date.asc()).limit(days).all()
    res = []
    for i, log in enumerate(logs):
        res.append({
            'day': f"Day {i+1}",
            'uptime': log.uptime_percentage,
            'renewablePenetration': log.renewable_share,
            'dieselDependency': log.diesel_dependency
        })
    return res

@app.get('/api/cost')
def get_cost_db(db: Session = Depends(get_db)):
    from models import DailyLog
    logs = db.query(DailyLog).order_by(DailyLog.date.desc()).limit(7).all()
    logs.reverse() # chronologically
    res = []
    for log in logs:
        from datetime import datetime
        day_str = datetime.strptime(log.date, '%Y-%m-%d').strftime('%a')
        res.append({
            'day': day_str,
            'dieselOnlyCost': log.diesel_only_cost,
            'optimizedCost': log.optimized_cost,
            'savedCO2': log.saved_co2_kg
        })
    return res
