export interface ForecastRecord {
    timestamp: string;
    solar_kw: number;
    wind_kw: number;
    demand_kw: number;
    weather_condition: string;
}

export interface DispatchRecord {
    timestamp: string;
    solar_used_kw: number;
    wind_used_kw: number;
    battery_kw: number;
    diesel_kw: number;
    battery_soc_percent: number;
    unmet_demand_kw: number;
    decision_reason: string;
}

export interface SimulationRequest {
    solar_capacity_kw: number;
    wind_capacity_kw: number;
    battery_capacity_kwh: number;
    diesel_capacity_kw: number;
    demand_multiplier: number;
    weather_scenario: string; // "normal" | "cloudy" | "storm"
}
