import numpy as np
from scipy.optimize import linprog
import pandas as pd

class OptimizationEngine:
    def __init__(self, horizon_hours=24, interval_hours=1.0):
        self.horizon_hours = horizon_hours
        self.interval_hours = interval_hours
        self.T = int(horizon_hours / interval_hours)
        
    def optimize_dispatch(self, demand, solar_forecast, wind_forecast, 
                          solar_cap, wind_cap, batt_cap_kwh, batt_max_kw, batt_min_soc, batt_max_soc, batt_init_soc,
                          diesel_cap, diesel_price, carbon_price,
                          diesel_carbon_factor=2.68, # kg CO2 per liter
                          diesel_l_per_kwh=0.3): # Liters per kWh generated
        
        # Variables per timestep t:
        # P_solar[t], P_wind[t], P_batt_dis[t], P_batt_chg[t], P_diesel[t], E_batt[t]
        # Total variables = 6 * T
        
        num_vars = 6 * self.T
        
        # Objective: Minimize cost and emissions
        # Cost = Diesel cost + Carbon Cost + Battery degradation (simplified) + unserved penalty (handled as bounds/dummy)
        # We will set up the objective vector c
        
        c = np.zeros(num_vars)
        
        # Variable indices
        def idx(var_name, t):
            offset = {"P_solar": 0, "P_wind": 1, "P_batt_dis": 2, "P_batt_chg": 3, "P_diesel": 4, "E_batt": 5}
            return t * 6 + offset[var_name]
        
        # Costs
        cost_per_kwh_diesel = diesel_l_per_kwh * diesel_price
        carbon_cost_per_kwh_diesel = diesel_l_per_kwh * diesel_carbon_factor * (carbon_price / 1000.0) # carbon_price in Rs/ton
        total_diesel_cost_per_kwh = cost_per_kwh_diesel + carbon_cost_per_kwh_diesel
        
        batt_deg_cost = 2.0 # Rs per kWh cycled
        
        for t in range(self.T):
            c[idx("P_diesel", t)] = total_diesel_cost_per_kwh * self.interval_hours
            c[idx("P_batt_dis", t)] = batt_deg_cost * self.interval_hours
            c[idx("P_batt_chg", t)] = batt_deg_cost * self.interval_hours
            
        # Constraints:
        # 1. Power balance: P_solar[t] + P_wind[t] + P_batt_dis[t] + P_diesel[t] - P_batt_chg[t] == demand[t]
        A_eq = []
        b_eq = []
        
        for t in range(self.T):
            row = np.zeros(num_vars)
            row[idx("P_solar", t)] = 1
            row[idx("P_wind", t)] = 1
            row[idx("P_batt_dis", t)] = 1
            row[idx("P_diesel", t)] = 1
            row[idx("P_batt_chg", t)] = -1
            A_eq.append(row)
            b_eq.append(demand[t])
            
        # 2. Battery Dynamics: E_batt[t] = E_batt[t-1] + P_batt_chg[t]*dt*eff - P_batt_dis[t]*dt/eff
        # -> E_batt[t] - E_batt[t-1] - P_batt_chg[t] + P_batt_dis[t] = 0 (assuming eff=1 for now to keep linear simple, or add eff)
        eff = 0.95
        for t in range(self.T):
            row = np.zeros(num_vars)
            row[idx("E_batt", t)] = 1
            row[idx("P_batt_chg", t)] = -self.interval_hours * eff
            row[idx("P_batt_dis", t)] = self.interval_hours / eff
            if t == 0:
                # E_batt[0] = init_soc * batt_cap_kwh + ...
                # Actually, E_batt[0] - P_chg + P_dis = init
                A_eq.append(row)
                b_eq.append(batt_init_soc * batt_cap_kwh)
            else:
                row[idx("E_batt", t-1)] = -1
                A_eq.append(row)
                b_eq.append(0)
                
        # Bounds
        bounds = []
        for t in range(self.T):
            # P_solar bounds (0, available forecast)
            bounds.append((0, min(solar_forecast[t], solar_cap)))
            # P_wind bounds
            bounds.append((0, min(wind_forecast[t], wind_cap)))
            # P_batt_dis
            bounds.append((0, batt_max_kw))
            # P_batt_chg
            bounds.append((0, batt_max_kw))
            # P_diesel
            bounds.append((0, diesel_cap))
            # E_batt bounds
            bounds.append((batt_min_soc * batt_cap_kwh, batt_max_soc * batt_cap_kwh))
            
        # Solve
        res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if res.success:
            # Extract results
            results = []
            for t in range(self.T):
                results.append({
                    "hour": t,
                    "solar": res.x[idx("P_solar", t)],
                    "wind": res.x[idx("P_wind", t)],
                    "batt_dis": res.x[idx("P_batt_dis", t)],
                    "batt_chg": res.x[idx("P_batt_chg", t)],
                    "diesel": res.x[idx("P_diesel", t)],
                    "soc": res.x[idx("E_batt", t)] / batt_cap_kwh,
                    "demand": demand[t]
                })
            return {"status": "Optimal", "results": results, "cost": res.fun}
        else:
            return {"status": "Infeasible or Failed", "message": res.message}

# Example usage/test if run directly
if __name__ == "__main__":
    eng = OptimizationEngine(horizon_hours=24)
    # mock data
    demand = [180] * 24
    solar = [0]*6 + [50, 100, 150, 200, 250, 250, 200, 150, 100, 50] + [0]*8
    wind = [30] * 24
    res = eng.optimize_dispatch(demand, solar, wind, 250, 100, 500, 100, 0.2, 0.9, 0.5, 150, 90, 1000)
    print(res["status"], res["cost"])
