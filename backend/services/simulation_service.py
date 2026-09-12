import math
import random
from datetime import datetime
import pandas as pd

class SimulationService:
    def __init__(self, seed=42):
        random.seed(seed)
        
    def generate_demand_forecast(self, num_households, num_pumps, num_businesses, horizon_hours=24, interval_hours=1.0):
        # Base daily curve (normalized 0 to 1) for a typical rural community
        base_curve = {
            0: 0.2, 1: 0.15, 2: 0.15, 3: 0.15, 4: 0.2, 5: 0.3,
            6: 0.6, 7: 0.8, 8: 0.7, 9: 0.5, 10: 0.4, 11: 0.4,
            12: 0.4, 13: 0.4, 14: 0.4, 15: 0.4, 16: 0.5, 17: 0.6,
            18: 0.9, 19: 1.0, 20: 0.95, 21: 0.8, 22: 0.5, 23: 0.3
        }
        
        # Approximate max kW per unit
        household_peak_kw = 0.5
        pump_peak_kw = 5.0
        business_peak_kw = 2.0
        
        # Calculate theoretical peak
        total_peak = (num_households * household_peak_kw) + \
                     (num_pumps * pump_peak_kw) + \
                     (num_businesses * business_peak_kw)
                     
        demand = []
        for t in range(int(horizon_hours / interval_hours)):
            hour_of_day = t % 24
            # Add some noise
            noise = random.uniform(-0.05, 0.05)
            val = base_curve[hour_of_day] + noise
            val = max(0.1, min(1.0, val)) # bound
            demand.append(round(val * total_peak, 2))
            
        return demand
        
    def simulate_solar_generation(self, solar_radiation_w_m2, capacity_kw, efficiency=0.18, temp_c=25):
        # Very simplified solar model based on radiation
        # Radiation is usually ~1000 W/m2 at peak
        # capacity_kw is the rated peak capacity
        
        gen = []
        for rad, temp in zip(solar_radiation_w_m2, temp_c):
            # Panel temperature degrades efficiency by ~0.4% per degC above 25
            temp_derate = 1.0 - max(0, (temp - 25)) * 0.004
            # Normalize rad to 1000 (standard test conditions)
            power = capacity_kw * (rad / 1000.0) * temp_derate
            gen.append(round(max(0, power), 2))
            
        return gen

    def simulate_wind_generation(self, wind_speeds_m_s, capacity_kw, cut_in=3.0, rated=12.0, cut_out=25.0):
        gen = []
        for v in wind_speeds_m_s:
            if v < cut_in or v > cut_out:
                p = 0
            elif v >= rated:
                p = capacity_kw
            else:
                # Cubic power curve approximation
                p = capacity_kw * ((v**3 - cut_in**3) / (rated**3 - cut_in**3))
            gen.append(round(max(0, p), 2))
        return gen

if __name__ == "__main__":
    sim = SimulationService()
    print("Demand:", sim.generate_demand_forecast(120, 4, 18, 24))
