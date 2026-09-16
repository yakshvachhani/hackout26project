# OptiGrid-AI — Backend & Telemetry Platform

OptiGrid-AI is a microgrid energy mix optimization and real-time telemetry engine for off-grid communities.

This backend serves as the core integration hub connecting the React UI (Member 1), the MILP/MPC optimization engine (Member 3), external meteorological satellite telemetry (Open-Meteo & NASA POWER), and local SQLite persistence with real-time WebSocket event streaming.

---

## Architecture Overview

```text
               ┌───────────────────────┐
               │    React Dashboard    │ (Member 1)
               └───────────▲───────────┘
                           │ HTTP / WebSocket (/ws)
                           ▼
               ┌───────────────────────┐
               │   FastAPI REST API    │ (Member 2)
               └───────▲───────▲───────┘
                       │       │
      ┌────────────────┴┐     ┌┴──────────────────┐
      │ SQLite Database │     │ Services Layer    │
      │ (SQLAlchemy ORM)│     │  - Weather (API)  │
      └─────────────────┘     │  - BESS & Fuel    │
                              │  - 24h Forecast   │
                              └─────────▲─────────┘
                                        │
                       ┌────────────────┴──────────────────┐
                       │ Optimization Engine (Member 3)    │
                       │ (MILP / MPC merit-order dispatch) │
                       └───────────────────────────────────┘
```

---

## 1. Quickstart & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Pip

### Setup Virtual Environment
```bash
# Clone the repository
cd hackout

# Create and activate virtual environment (optional but recommended)
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Running the Server
```bash
# Run using uvicorn directly from workspace root:
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 2. Environment Variables

Create a `.env` file in the root directory (or configure system environment variables):

| Variable | Default Value | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./optigrid.db` | SQLAlchemy SQLite or PostgreSQL connection string |
| `OPEN_METEO_BASE_URL` | `https://api.open-meteo.com/v1` | Open-Meteo meteorological telemetry API base |
| `NASA_POWER_BASE_URL` | `https://power.larc.nasa.gov/api` | NASA POWER solar & irradiance API base |
| `FRONTEND_ORIGINS` | `["http://localhost:5173", "*"]` | CORS allowed origins for React development |
| `DEMO_MODE` | `True` | Fallback simulation stream when sensors are offline |
| `HOST` | `0.0.0.0` | Host interface |
| `PORT` | `8000` | Port number |
| `TELEMETRY_INTERVAL_SECONDS` | `5` | Frequency of WebSocket background telemetry updates |

---

## 3. Database Schema (SQLite)

Tables are automatically created and seeded on application startup:

1. **`energy_readings`**: High-frequency bus readings (demand, solar, wind, battery, diesel kW, renewable %).
2. **`battery_records`**: 100 kWh BESS telemetry, SOC %, battery health %, cycle counts, storm mode flag.
3. **`diesel_records`**: Generator state, power kW, fuel level (liters), daily burn rate, run hours.
4. **`weather_records`**: Solar irradiance (W/m²), ambient temperature, wind velocity, weather condition.
5. **`dispatch_records`**: Historical MILP/MPC optimal dispatch decisions, cost/hour, and CO2 emissions avoided.
6. **`load_records`**: P0 (Critical/Hospital), P1 (Shiftable/Well pumps), and P2 (Curtailable/AC) load status.
7. **`alerts`**: Grid warning, advisory, and optimization notification events.
8. **`simulation_records`**: Saved what-if crisis scenarios (solar failure, wind lull, fuel outage, storm mode).

---

## 4. API Endpoints

### System & Telemetry
- `GET /api/system/status`: Returns current microgrid status, generation mix, renewable penetration, and health.
- `POST /api/weather/refresh`: Forces real-time refresh of meteorological sensors via Open-Meteo.
- `GET /api/health`: Health-check endpoint verifying API and SQLite connectivity.

### Energy Storage & Logistics
- `GET /api/battery`: 100 kWh BESS operational state, 24-hour SOC curve, and storm reserve mode.
- `POST /api/battery/storm-mode`: Toggles 50% SOC storm reserve mode.
- `GET /api/fuel`: Diesel tank level, burn rate, days remaining, and generator status.
- `GET /api/loads`: P0, P1, and P2 priority load classification and curtailment status.

### Forecast & Optimization
- `GET /api/forecast`: 24-hour predictive forecast across 96 fifteen-minute intervals.
- `POST /api/optimize`: Solves optimal microgrid energy dispatch. Bridges to Member 3's MILP module.
- `GET /api/dispatch/latest`: Returns the latest calculated dispatch solution.
- `GET /api/dispatch/history`: Returns historical dispatch records for time-series charts.
- `POST /api/simulation/run`: Runs crisis simulator (solar outage, battery trip, diesel outage, 48h storm).
- `GET /api/alerts`: Returns system alerts and operator notifications.

---

## 5. Sample Requests & Responses

### POST `/api/optimize`
**Request Body:**
```json
{
  "demand_kw": 50,
  "solar_available_kw": 30,
  "wind_available_kw": 15,
  "battery_soc": 70,
  "battery_capacity_kwh": 100,
  "diesel_available": true,
  "fuel_price": 95
}
```

**Response (200 OK):**
```json
{
  "status": "optimal",
  "solar_kw": 30.0,
  "wind_kw": 15.0,
  "battery_kw": 5.0,
  "diesel_kw": 0.0,
  "total_supply_kw": 50.0,
  "demand_kw": 50.0,
  "unmet_demand_kw": 0.0,
  "renewable_percentage": 90.0,
  "dispatch": {
    "solarKw": 30.0,
    "windKw": 15.0,
    "batteryKw": 5.0,
    "dieselKw": 0.0
  },
  "metrics": {
    "totalGenerationKw": 50.0,
    "unmetDemandKw": 0.0,
    "renewablePercent": 90.0,
    "estimatedCostPerHour": 4.25,
    "fuelConsumptionLitersHour": 0.0,
    "co2EmissionsKgHour": 0.0,
    "reliabilityPercent": 100.0
  }
}
```

---

### POST `/api/simulation/run`
**Request Body:**
```json
{
  "scenario": "STORM_48H",
  "severity": 90,
  "durationHours": 48
}
```

**Response (200 OK):**
```json
{
  "scenario": "STORM_48H",
  "severity": 90.0,
  "durationHours": 48.0,
  "before": { "solar": 30.0, "wind": 15.0, "battery": 5.0, "diesel": 0.0, "demand": 50.0 },
  "after": { "solar": 2.0, "wind": 22.0, "battery": 8.0, "diesel": 18.0, "demand": 50.0 },
  "impact": {
    "p0ReliabilityPercent": 100.0,
    "p1ServedPercent": 70.0,
    "p2ServedPercent": 15.0,
    "additionalDieselLiters": 241.9,
    "additionalCo2Kg": 648.3,
    "costDifferenceDollars": "362.85"
  }
}
```

---

## 6. WebSocket Protocol (`/ws`)

Connect via WebSocket to: `ws://localhost:8000/ws`

### Event Format
All WebSocket frames sent by the server follow the JSON structure:
```json
{
  "type": "<EVENT_TYPE>",
  "data": { ... }
}
```

### Supported Event Types:
1. `SYSTEM_STATUS_UPDATED`: Periodic telemetry updates containing real-time load, generation, and renewable share.
2. `SOLAR_CHANGED`: Emitted when solar PV output changes.
3. `WIND_CHANGED`: Emitted when wind generation fluctuates.
4. `BATTERY_CHANGED`: Emitted upon state-of-charge or battery charging/discharging power changes.
5. `DIESEL_STARTED`: Emitted when diesel generator starts up to cover a deficit.
6. `DIESEL_STOPPED`: Emitted when diesel generator stops.
7. `NEW_OPTIMIZATION`: Broadcast when a new optimal dispatch solution is solved.
8. `LOAD_SHED`: Broadcast when P1 or P2 loads are curtailed to maintain P0 hospital reliability.
9. `STORM_MODE`: Broadcast when severe weather storm reserve is toggled.
10. `FUEL_WARNING`: Broadcast when fuel tank level drops below reserve threshold.
11. `ALERT_CREATED`: Emitted when a new grid notification is published.

---

## 7. Member 3 Optimizer Integration

The backend is pre-configured to automatically discover Member 3's MILP / MPC optimization module if present in the `optimization/` directory.

### Integration Contract:
Member 3 can provide any of:
- `optimization/milp.py`
- `optimization/mpc.py`
- `optimization/optimizer.py`

Implementing either:
```python
def optimize(params: dict) -> dict:
    ...
```
or:
```python
def run_milp_optimization(params: dict) -> dict:
    ...
```

If Member 3's module is not yet committed or throws an exception, `backend/services/optimizer_service.py` automatically falls back to an integrated high-fidelity merit-order solver without crashing the API.

---

## 8. Automated Testing

Run the comprehensive unit and integration test suite:
```bash
python -m unittest backend/test_backend.py
```

Run the live network & WebSocket telemetry test against a running instance:
```bash
python backend/test_live_server.py
```
