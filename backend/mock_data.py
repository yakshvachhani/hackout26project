import math
import random
from datetime import datetime, timedelta

def generate_forecast(hours: int, weather_scenario: str = "normal", demand_multiplier: float = 1.0, 
                      solar_capacity_kw: float = 100.0, wind_capacity_kw: float = 100.0):
    records = []
    base_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    
    current_wind = wind_capacity_kw * random.uniform(0.3, 0.7)
    
    for i in range(hours):
        current_time = base_time + timedelta(hours=i)
        hour_of_day = current_time.hour
        
        # Diurnal Solar (Peak at 13:00)
        if 6 <= hour_of_day <= 19:
            solar_pct = math.sin((hour_of_day - 6) * math.pi / 13)
            # Add some cloud noise
            solar_pct *= random.uniform(0.8, 1.0)
        else:
            solar_pct = 0.0
            
        # Autocorrelated Wind
        wind_delta = random.uniform(-0.1, 0.1) * wind_capacity_kw
        current_wind = max(0, min(wind_capacity_kw, current_wind + wind_delta))
        wind_pct = current_wind / wind_capacity_kw
        
        # Demand (morning peak 8-10, evening peak 18-21)
        base_demand = 50.0
        if 8 <= hour_of_day <= 10:
            demand = base_demand + random.uniform(20, 40)
        elif 18 <= hour_of_day <= 21:
            demand = base_demand + random.uniform(30, 60)
        else:
            demand = base_demand + random.uniform(0, 10)
            
        demand *= demand_multiplier
        
        # Apply weather scenarios
        weather_condition = "clear"
        
        # Simple scenario logic: block of bad weather
        is_bad_weather = False
        if weather_scenario == "cloudy" and 10 <= i <= 15:
            is_bad_weather = True
            weather_condition = "cloudy"
            solar_pct *= 0.3
        elif weather_scenario == "storm" and 5 <= i <= 12:
            is_bad_weather = True
            weather_condition = "storm"
            solar_pct = 0.0
            wind_pct *= 1.5 # storms have high wind
            current_wind = min(wind_capacity_kw, wind_pct * wind_capacity_kw)
            
        if not is_bad_weather:
            if solar_pct == 0:
                weather_condition = "night"
            else:
                weather_condition = "clear" if random.random() > 0.3 else "partly cloudy"
                
        records.append({
            "timestamp": current_time.isoformat(),
            "solar_kw": round(solar_pct * solar_capacity_kw, 2),
            "wind_kw": round(current_wind, 2),
            "demand_kw": round(demand, 2),
            "weather_condition": weather_condition
        })
        
    return records

def generate_dispatch(forecast_data, battery_capacity_kwh: float, diesel_capacity_kw: float, 
                      start_soc: float = 50.0, is_history: bool = False):
    schedule = []
    current_soc_percent = start_soc
    max_charge_rate_kw = battery_capacity_kwh * 0.25  # C/4 charge rate
    max_discharge_rate_kw = battery_capacity_kwh * 0.5 # C/2 discharge rate
    
    for f in forecast_data:
        solar = f['solar_kw']
        wind = f['wind_kw']
        demand = f['demand_kw']
        
        if is_history:
            # Add slight random deviation to simulate real-world error vs forecast
            solar = max(0.0, solar * random.uniform(0.9, 1.1))
            wind = max(0.0, wind * random.uniform(0.85, 1.15))
            demand = max(0.0, demand * random.uniform(0.95, 1.05))
            
        renewables = solar + wind
        net_demand = demand - renewables
        
        solar_used = solar
        wind_used = wind
        battery_kw = 0.0
        diesel_kw = 0.0
        unmet_demand = 0.0
        reason = ""
        
        # Calculate available battery energy in kWh based on SOC
        available_kwh = (current_soc_percent / 100.0) * battery_capacity_kwh
        # Calculate empty battery space
        empty_kwh = battery_capacity_kwh - available_kwh
        
        if net_demand > 0:
            # We need more power. Try battery first.
            max_possible_discharge = min(available_kwh, max_discharge_rate_kw) # Can't discharge more than we have or max rate
            
            if max_possible_discharge >= net_demand:
                battery_kw = net_demand
                reason = "Discharging battery to meet demand"
            else:
                battery_kw = max_possible_discharge
                shortfall = net_demand - battery_kw
                
                # Try diesel for shortfall
                if diesel_capacity_kw >= shortfall:
                    diesel_kw = shortfall
                    reason = "Using diesel and battery to meet demand"
                else:
                    diesel_kw = diesel_capacity_kw
                    unmet_demand = shortfall - diesel_kw
                    reason = "Insufficient power. Unmet demand recorded."
        elif net_demand < 0:
            # We have excess power. Try to charge battery.
            excess_power = -net_demand
            max_possible_charge = min(empty_kwh, max_charge_rate_kw) # Can't charge more than empty space or max rate
            
            if max_possible_charge >= excess_power:
                battery_kw = -excess_power
                reason = "Storing excess renewable energy in battery"
            else:
                battery_kw = -max_possible_charge
                # Curtail the rest
                curtailed = excess_power - max_possible_charge
                # Reduce used renewables
                curtail_ratio = curtailed / renewables if renewables > 0 else 0
                solar_used -= solar * curtail_ratio
                wind_used -= wind * curtail_ratio
                reason = f"Battery full/charge limited. Curtailed {round(curtailed,2)}kW renewables."
        else:
            reason = "Renewables exactly match demand"
            
        # Update SOC
        # battery_kw is power (kW) for 1 hour. So it's equivalent to energy (kWh).
        # Positive battery_kw means discharging (losing energy), negative means charging (gaining energy)
        new_kwh = available_kwh - battery_kw
        
        # Clamp just in case of float math issues
        new_kwh = max(0.0, min(battery_capacity_kwh, new_kwh))
        current_soc_percent = (new_kwh / battery_capacity_kwh) * 100.0
        
        schedule.append({
            "timestamp": f['timestamp'],
            "solar_used_kw": round(solar_used, 2),
            "wind_used_kw": round(wind_used, 2),
            "battery_kw": round(battery_kw, 2),
            "diesel_kw": round(diesel_kw, 2),
            "battery_soc_percent": round(current_soc_percent, 2),
            "unmet_demand_kw": round(unmet_demand, 2),
            "decision_reason": reason
        })
        
    return schedule
