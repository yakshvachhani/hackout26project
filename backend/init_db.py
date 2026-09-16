from database import engine, Base, SessionLocal
from models import Microgrid, Asset, DailyLog
import random
from datetime import datetime, timedelta

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()





















































































































    
    if not db.query(Microgrid).first():
        print("Seeding Demo Microgrid...")
        demo_grid = Microgrid(
            name="Kutch Rural Community Microgrid",
            location="Kutch, Gujarat",
            latitude=23.7337,
            longitude=69.8597,
            population=1200,
            connected_households=250,
            operating_mode="SIMULATION"
        )
        db.add(demo_grid)
        db.commit()
        db.refresh(demo_grid)
        
        assets = [
            Asset(microgrid_id=demo_grid.id, asset_type="SOLAR", name="Solar Farm 1", capacity_kw=250.0, current_status="Producing", efficiency=0.18),
            Asset(microgrid_id=demo_grid.id, asset_type="WIND", name="Wind Turbine 1", capacity_kw=100.0, current_status="Producing", efficiency=0.35),
            Asset(microgrid_id=demo_grid.id, asset_type="BATTERY", name="Main Battery Storage", capacity_kw=100.0, capacity_kwh=500.0, current_status="Charging", efficiency=0.92),
            Asset(microgrid_id=demo_grid.id, asset_type="DIESEL", name="Backup Generator 1", capacity_kw=150.0, current_status="Standby", efficiency=0.3)
        ]
        db.bulk_save_objects(assets)
        
        # Seed 30 days of DailyLogs
        logs = []
        base_date = datetime.now() - timedelta(days=30)
        for i in range(30):
            d_date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            logs.append(DailyLog(
                microgrid_id=demo_grid.id,
                date=d_date,
                uptime_percentage=round(98 + random.random() * 2, 1),
                renewable_share=round(60 + random.random() * 30, 1),
                diesel_dependency=round(10 + random.random() * 15, 1),
                diesel_only_cost=round(4500 + random.random() * 1000, 1),
                optimized_cost=round(2000 + random.random() * 1200, 1),
                saved_co2_kg=round(100 + random.random() * 90, 1)
            ))
        db.bulk_save_objects(logs)
        db.commit()
        print("Demo Microgrid seeded successfully.")
    else:
        print("Database already initialized.")
        
    db.close()

if __name__ == '__main__':
    init_db()
