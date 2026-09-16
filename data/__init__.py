"""
OptiGrid-AI Data Services Core Module.
Provides high-level integration service functions for Member 2 (Backend API) and Member 3 (MPC Optimizer).
"""

from typing import Dict, Any, Optional, List

# Sub-package exports
from data.synthetic import (
    generate_village_load,
    generate_village_load_dict,
    generate_solar_profile,
    generate_solar_dict,
    generate_wind_profile,
    generate_wind_dict,
    wind_turbine_power_curve,
    BatteryStorage,
    BatteryConfig,
    calculate_fuel_autonomy,
    estimate_generator_fuel_burn,
    calculate_diesel_emissions_and_cost,
    FuelAlertLevel,
)
from data.weather import (
    WeatherSource,
    WeatherSnapshot,
    WeatherForecastSeries,
    WeatherInterval,
    OpenMeteoClient,
    NasaPowerClient,
    WeatherManager,
)
from data.forecasting import (
    DemandForecaster,
    demand_forecaster,
    SolarForecaster,
    solar_forecaster,
    WindForecaster,
    wind_forecaster,
)
from data.simulation import (
    ScenarioType,
    ScenarioDefinition,
    apply_scenario,
    get_hackathon_demo_presets,
    SimulationMetrics,
    compute_metrics,
    run_scenario,
    simulate_microgrid_dispatch,
    build_default_baseline_data,
)

# Global singleton weather manager instance
_weather_manager = WeatherManager()


# =====================================================================
# MEMBER 3: MPC / MILP OPTIMIZER INTEGRATION CONTRACT
# =====================================================================

def get_mpc_inputs(
    duration_hours: int = 24,
    battery_soc: float = 75.0,
    fuel_remaining_l: float = 450.0,
    fuel_price_per_l: float = 1.45,
    storm_mode: bool = False,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Returns clean, standardized data dictionary tailored for Member 3's MPC/MILP optimizer.
    
    Contains:
      - demand_forecast (96 floats for 24h)
      - p0_forecast, p1_forecast, p2_forecast (96 floats each)
      - solar_forecast (96 floats)
      - wind_forecast (96 floats)
      - battery state: capacity_kwh, soc_pct, min_soc_pct, max_charge_kw, max_discharge_kw
      - fuel state: fuel_remaining_l, price_per_l, est_burn_rate_l_per_kwh
      - operational mode: storm_mode
    """
    n_intervals = duration_hours * 4

    # 1. Weather series (LIVE -> CACHED -> FALLBACK)
    weather_series = _weather_manager.get_forecast_15min(
        duration_hours=duration_hours,
        latitude=latitude,
        longitude=longitude
    )

    # 2. 96-timestep forecasts
    solar_kw = solar_forecaster.forecast_from_weather(weather_series)
    wind_kw = wind_forecaster.forecast_from_weather(weather_series)
    demand_detailed = demand_forecaster.forecast_detailed(duration_hours=duration_hours)

    # Pad or slice to exact horizon
    solar_96 = (solar_kw + [0.0] * n_intervals)[:n_intervals]
    wind_96 = (wind_kw + [0.0] * n_intervals)[:n_intervals]
    demand_96 = demand_detailed["demand_kw"][:n_intervals]
    p0_96 = demand_detailed["p0_kw"][:n_intervals]
    p1_96 = demand_detailed["p1_kw"][:n_intervals]
    p2_96 = demand_detailed["p2_kw"][:n_intervals]

    min_soc = 40.0 if storm_mode else 20.0

    return {
        "horizon_intervals": n_intervals,
        "interval_minutes": 15,
        "timestamps": demand_detailed["timestamps"][:n_intervals],
        "time_strings": demand_detailed["time_strings"][:n_intervals],
        "demand_forecast": demand_96,
        "p0_forecast": p0_96,
        "p1_forecast": p1_96,
        "p2_forecast": p2_96,
        "solar_forecast": solar_96,
        "wind_forecast": wind_96,
        "p0_demand": p0_96,
        "p1_demand": p1_96,
        "p2_demand": p2_96,
        "battery_capacity": 120.0,
        "initial_battery_soc": battery_soc,
        "min_soc": min_soc,
        "max_soc": 95.0,
        "diesel_available": True,
        "diesel_capacity_kw": 60.0,
        "fuel_remaining": fuel_remaining_l,
        "fuel_price": fuel_price_per_l,
        "storm_mode": storm_mode,
        "battery": {
            "capacity_kwh": 120.0,
            "current_soc_pct": battery_soc,
            "min_soc_pct": min_soc,
            "max_soc_pct": 95.0,
            "max_charge_kw": 40.0,
            "max_discharge_kw": 40.0,
            "efficiency_roundtrip": 0.90,
        },
        "diesel": {
            "rated_capacity_kw": 60.0,
            "is_available": True,
            "fuel_remaining_l": fuel_remaining_l,
            "fuel_price_per_l": fuel_price_per_l,
            "marginal_burn_l_per_kwh": 0.26,
            "base_idle_burn_lph": 2.0,
            "co2_kg_per_l": 2.68,
        },
        "grid_flags": {
            "storm_mode": storm_mode,
            "weather_source": weather_series.source.value,
            "weather_provider": weather_series.provider,
        },
    }


# =====================================================================
# MEMBER 2: FASTAPI BACKEND SERVICE CONTRACTS
# =====================================================================

def get_api_forecast_payload(
    duration_hours: int = 24,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Returns data ready to be returned by Member 2's `GET /api/forecast`.
    Matches the backend `ForecastInterval` schema across 96 15-minute intervals.
    """
    inputs = get_mpc_inputs(duration_hours=duration_hours, latitude=latitude, longitude=longitude)
    n_intervals = inputs["horizon_intervals"]
    intervals: List[Dict[str, Any]] = []

    # Run quick dispatch simulation to generate batterySoc and diesel estimate
    baseline = build_default_baseline_data(duration_hours=duration_hours)
    baseline["demand_kw"] = inputs["demand_forecast"]
    baseline["solar_kw"] = inputs["solar_forecast"]
    baseline["wind_kw"] = inputs["wind_forecast"]
    dispatch, _ = simulate_microgrid_dispatch(baseline)

    for i in range(n_intervals):
        d_val = float(inputs["demand_forecast"][i])
        s_val = float(inputs["solar_forecast"][i])
        w_val = float(inputs["wind_forecast"][i])
        b_soc = float(dispatch["battery_soc"][i])
        g_val = float(dispatch["diesel_kw"][i])
        t_str = inputs["time_strings"][i]

        intervals.append({
            "interval": i + 1,
            "time": t_str,
            "demand": d_val,
            "solar": s_val,
            "wind": w_val,
            "batterySoc": b_soc,
            "diesel": g_val,
            # snake_case aliases
            "demand_kw": d_val,
            "solar_kw": s_val,
            "wind_kw": w_val,
            "battery_soc": b_soc,
            "diesel_kw": g_val,
        })

    return intervals


def get_api_fuel_payload(
    fuel_remaining_l: float = 450.0,
    daily_burn_l: float = 24.5,
) -> Dict[str, Any]:
    """
    Returns data ready to be returned by Member 2's `GET /api/fuel`.
    """
    autonomy = calculate_fuel_autonomy(fuel_remaining_l=fuel_remaining_l, daily_burn_l=daily_burn_l)
    return {
        "fuel_remaining_l": autonomy["fuel_remaining_l"],
        "daily_burn_l": autonomy["daily_burn_l"],
        "autonomy_days": autonomy["days_remaining"],
        "depletion_date": autonomy["depletion_date"],
        "alert_level": autonomy["status"],
        "co2_factor_kg_per_l": 2.68,
        "is_generator_running": daily_burn_l > 0.0,
    }


def refresh_weather_telemetry(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> WeatherSnapshot:
    """
    Refreshes weather telemetry from Open-Meteo or fallback for Member 2's `POST /api/weather/refresh`.
    """
    return _weather_manager.get_current_weather(latitude=latitude, longitude=longitude)


def run_simulation_api(
    scenario: str,
    severity: float = 50.0,
    duration_hours: float = 24.0,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    solar_capacity_kw: Optional[float] = None,
    battery_capacity_kwh: Optional[float] = None,
    demand_kw: Optional[float] = None,
    rain_probability: Optional[float] = None,
    grid_price_per_kwh: Optional[float] = None,
    optimization_mode: str = "balanced",
    location_name: str = "Baramati Rural",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Executes what-if simulation for Member 2's `POST /api/simulation/run` using location baseline.
    """
    baseline = None
    if latitude is not None and longitude is not None:
        try:
            inputs = get_mpc_inputs(duration_hours=int(duration_hours), latitude=latitude, longitude=longitude)
            baseline = build_default_baseline_data(duration_hours=int(duration_hours))
            baseline["demand_kw"] = inputs["demand_forecast"]
            baseline["solar_kw"] = inputs["solar_forecast"]
            baseline["wind_kw"] = inputs["wind_forecast"]
        except Exception:
            baseline = None

    return run_scenario(
        baseline_data=baseline,
        scenario=scenario,
        severity=severity,
        duration_hours=duration_hours,
        solar_capacity_kw=solar_capacity_kw,
        battery_capacity_kwh=battery_capacity_kwh,
        demand_kw=demand_kw,
        rain_probability=rain_probability,
        grid_price_per_kwh=grid_price_per_kwh,
        optimization_mode=optimization_mode,
        location_name=location_name,
        **kwargs,
    )

