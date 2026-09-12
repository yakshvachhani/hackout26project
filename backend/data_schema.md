# Microgrid Dispatch Data Schemas

## ForecastRecord
Represents a single hour's forecasted metrics.
- `timestamp`: (string) ISO-8601 datetime
- `solar_kw`: (float) Predicted solar generation in kW
- `wind_kw`: (float) Predicted wind generation in kW
- `demand_kw`: (float) Predicted load demand in kW
- `weather_condition`: (string) e.g., "clear", "partly cloudy", "cloudy", "storm", "night"

## DispatchRecord
Represents the state of the microgrid after dispatch decisions are made for an hour.
- `timestamp`: (string) ISO-8601 datetime
- `solar_used_kw`: (float) Solar power utilized in kW
- `wind_used_kw`: (float) Wind power utilized in kW
- `battery_kw`: (float) Battery usage. Positive = discharging (supplying load), Negative = charging (storing excess).
- `diesel_kw`: (float) Diesel generator output in kW
- `battery_soc_percent`: (float) State of Charge (0-100%)
- `unmet_demand_kw`: (float) Demand that could not be met by any source
- `decision_reason`: (string) Explanation of the dispatch logic applied

## SimulationRequest
Payload to dynamically simulate scenarios.
- `solar_capacity_kw`: (float) Total installed solar capacity
- `wind_capacity_kw`: (float) Total installed wind capacity
- `battery_capacity_kwh`: (float) Maximum battery storage
- `diesel_capacity_kw`: (float) Maximum diesel output
- `demand_multiplier`: (float) Scales the base load curve up or down
- `weather_scenario`: (string) One of "normal", "cloudy", "storm"
