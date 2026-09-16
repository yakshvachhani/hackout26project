# OptiGrid-AI — API Contract Documentation

This document specifies the unified REST and WebSocket contracts connecting Frontend (Member 1), Backend (Member 2), Optimization (Member 3), and Data Services (Member 4).

## 1. REST Endpoints

### System Status & Telemetry
- **Endpoint**: `GET /api/system/status`
- **Method**: GET
- **Description**: Returns live telemetry, grid health, renewable share, and active weather.

### 24-Hour Forecast
- **Endpoint**: `GET /api/forecast`
- **Method**: GET
- **Description**: 96 intervals (15-min resolution) of load demand, solar, wind, battery SOC, and diesel requirements.

### Battery Storage (BESS)
- **Endpoint**: `GET /api/battery`
- **Method**: GET
- **Endpoint**: `POST /api/battery/storm-mode`
- **Payload**: `{"active": true}`

### Fuel Intelligence & Logistics
- **Endpoint**: `GET /api/fuel`
- **Method**: GET
- **Description**: Tank level, fuel burn rate, generator operational hours, and autonomy days.

### Priority Load Management
- **Endpoint**: `GET /api/loads`
- **Method**: GET
- **Description**: P0 (Life-critical), P1 (Shiftable productive), P2 (Deferrable) load metrics.

### Optimization Engine
- **Endpoint**: `POST /api/optimize`
- **Method**: POST
- **Payload**:
  - `demand_kw`: Community load demand in kW (e.g., 50.0)
  - `solar_available_kw`: Available solar in kW (e.g., 30.0)
  - `wind_available_kw`: Available wind in kW (e.g., 15.0)
  - `battery_soc`: Current Battery SOC % (e.g., 70.0)
  - `battery_capacity_kwh`: Battery capacity in kWh (e.g., 100.0)
  - `diesel_available`: Diesel generator availability (bool)
  - `fuel_price`: Fuel price per liter (e.g., 95.0)
  - `min_soc`: Minimum reserve SOC % (e.g., 20.0)
  - `max_soc`: Maximum operational SOC % (e.g., 95.0)
- **Response**: Optimal power dispatch breakdown (solar, wind, battery, diesel) and performance metrics.

### Crisis What-If Simulator
- **Endpoint**: `POST /api/simulation/run`
- **Method**: POST
- **Payload**:
  - `scenario`: SOLAR_FAILURE | WIND_FAILURE | BATTERY_LOW | DIESEL_UNAVAILABLE | DEMAND_SPIKE | STORM_48H | FUEL_PRICE_INCREASE
  - `severity`: float (0 - 100)
  - `durationHours`: float (1 - 168)
- **Response**: Before/after power balance comparison and granular reliability/cost impact metrics.

### Meteorological Telemetry Refresh
- **Endpoint**: `POST /api/weather/refresh`
- **Method**: POST

### Alerts & Notifications
- **Endpoint**: `GET /api/alerts`
- **Endpoint**: `POST /api/alerts`

### Health Check
- **Endpoint**: `GET /api/health`
- **Method**: GET

## 2. WebSocket Telemetry Stream
- **URL**: `ws://<host>:<port>/ws`
- **Broadcast Events**:
  - `SYSTEM_STATUS_UPDATED`: Live power bus fluctuations (demand, solar, wind, battery)
  - `SOLAR_CHANGED`: Solar generation shifts
  - `WIND_CHANGED`: Wind generation shifts
  - `BATTERY_CHANGED`: Battery SOC and charge/discharge power
  - `DIESEL_STARTED`: Diesel generator startup event
  - `DIESEL_STOPPED`: Diesel generator shutdown event
  - `STORM_MODE`: Severe weather reserve toggle (50% SOC minimum floor)
  - `NEW_OPTIMIZATION`: Broadcast of latest converged dispatch decision
  - `LOAD_SHED`: Priority tier curtailment alert
  - `FUEL_WARNING`: Fuel level depletion warning
  - `ALERT_CREATED`: New high-priority system alert notification
