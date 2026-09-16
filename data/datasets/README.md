# OPTIGRID-AI Data Engineering, Weather & Simulation Documentation
**Role**: Member 4 — Data Engineering / Weather Telemetry / Forecasting / Synthetic Data / What-If Simulation

---

## 1. Overview & Architecture
The `data/` package serves as the single source of truth for all operational telemetry, meteorological forecasts, synthetic community profiles, and crisis simulation engines in OPTIGRID-AI. 

It is engineered with a strict 15-minute time resolution (96 intervals per 24 hours, 192 intervals for 48 hours) to directly feed:
- **Member 3 (MPC/MILP Optimization)**: Clean numpy/list arrays (`demand_forecast[96]`, `solar_forecast[96]`, `wind_forecast[96]`), battery state, fuel constraints, and load priority tiers without web framework overhead.
- **Member 2 (FastAPI Backend)**: Pluggable service functions for `GET /api/forecast`, `GET /api/fuel`, `POST /api/weather/refresh`, and `POST /api/simulation/run`.

```
data/
├── __init__.py               # Core service integration contracts for Member 2 & 3
├── synthetic/                # Physics-informed synthetic profiles
│   ├── village_load.py       # Diurnal village demand + P0/P1/P2 load tiering
│   ├── solar.py              # Clear-sky irradiance & PV model
│   ├── wind.py               # Stochastic wind speed & turbine power curve
│   ├── battery.py            # BESS state machine (SoC, C-rate, degradation)
│   └── fuel.py               # Fuel autonomy, burn rate, alert states & CO2
├── weather/                  # Multi-provider weather & resilient fallback
│   ├── open_meteo.py         # Open-Meteo live API client + 15m interpolation
│   ├── nasa_power.py         # NASA POWER API client (decoupled)
│   ├── weather_models.py     # Typed data classes (WeatherSnapshot, etc.)
│   └── weather_manager.py    # Fallback hierarchy (LIVE -> CACHED -> FALLBACK)
├── forecasting/              # 15-Minute forward operational forecasters
│   ├── demand_forecast.py    # Deterministic baseline diurnal forecaster
│   ├── solar_forecast.py     # Weather irradiance -> PV generation (kW)
│   └── wind_forecast.py      # Wind speed -> Turbine generation (kW)
├── simulation/               # What-if crisis engine & demo presets
│   ├── scenarios.py          # 7 Crisis scenarios + 5 Demo presets
│   ├── simulator.py          # run_scenario() dispatch simulator
│   └── metrics.py            # Energy, fuel, CO2, reliability & shedding metrics
└── datasets/                 # Pre-generated benchmark data & documentation
    ├── village_benchmark_24h.json
    ├── village_benchmark_48h.json
    └── README.md
```

---

## 2. Synthetic Data Generation

### 2.1 Off-Grid Village Load (`village_load.py`)
Microgrids in off-grid rural communities display distinct diurnal patterns:
- **Night Baseload (00:00 - 05:00)**: 18 - 25 kW (vaccine refrigeration, minimal security lighting).
- **Morning Rise (06:00 - 09:00)**: 35 - 45 kW (breakfast preparation, domestic chores, borehole water pumping).
- **Daytime Plateau (09:00 - 17:00)**: 30 - 40 kW (rural healthcare clinics, grain milling, primary school, small shops).
- **Evening Peak (17:30 - 21:30)**: 55 - 75 kW (residential lighting, appliance use, community television/hub).
- **Night Drop (22:00 - 24:00)**: Gradual tapering back to baseload.

#### Prioritized Load Tiers
The total demand is categorized into three critical dispatch tiers:
- **P0 (Critical ~28%)**: Rural clinic vaccine refrigerators, emergency medical equipment, water borehole extraction, emergency telecommunications. Must never be shed unless complete black-start failure.
- **P1 (Essential ~44%)**: Domestic refrigeration, school computers/lighting, commercial shops, public street lights. Shed only after P2 is fully exhausted.
- **P2 (Deferrable / Flexible ~28%)**: Water heating, agricultural milling, EV motorbike/cart charging, decorative lighting, non-essential water pumping. First to be curtailed during crisis.

### 2.2 Solar PV Generation Model (`solar.py`)
Converts solar elevation angles and atmospheric clear-sky models into AC kilowatt output:
$$P_{pv}(t) = P_{pv\_cap} \times \left( \frac{\text{GHI}(t)}{1000 \, \text{W/m}^2} \right) \times \eta_{system} \times [1 - \gamma (T_{cell}(t) - 25^\circ\text{C})]$$
- Strictly 0 kW before sunrise (~06:15) and after sunset (~18:30).
- Midday peak reaching ~85-95% of installed nameplate capacity under clear skies.
- Clamped strictly within $[0, P_{pv\_cap}]$.

### 2.3 Wind Turbine Model (`wind.py`)
Employs an aerodynamic power curve parameterized by wind speed $v$:
- $v < v_{cut\_in}$ ($3.0 \, \text{m/s}$): $0 \, \text{kW}$
- $v_{cut\_in} \le v < v_{rated}$ ($11.5 \, \text{m/s}$): $P = P_{rated} \cdot \left(\frac{v - v_{cut\_in}}{v_{rated} - v_{cut\_in}}\right)^3$
- $v_{rated} \le v \le v_{cut\_out}$ ($25.0 \, \text{m/s}$): $P_{rated} \, \text{kW}$
- $v > v_{cut\_out}$: $0 \, \text{kW}$ (Turbine pitches to feather and applies mechanical brake for storm safety).

### 2.4 Battery Energy Storage System (BESS) (`battery.py`)
- Tracks SoC ($0 - 100\%$) subject to $[SoC_{min}, SoC_{max}]$ constraints.
- Maximum charge/discharge C-rate limits.
- Applies bidirectional round-trip efficiency ($\sim 90\%$).
- Tracks cumulative energy throughput and equivalent full cycles (EFC).
- Dynamically increases minimum reserve to $40\%$ when `storm_mode` is enabled.

### 2.5 Fuel Logistics & CO2 Calculation (`fuel.py`)
- **Autonomy calculation**:
  $$\text{days\_remaining} = \frac{\text{fuel\_remaining\_liters}}{\text{average\_daily\_burn\_liters}}$$
- **Depletion Date**: $\text{Current Date} + \text{days\_remaining}$
- **Alert Levels**:
  - $> 15 \text{ days}$: `NORMAL`
  - $7 - 15 \text{ days}$: `WARNING`
  - $< 7 \text{ days}$: `CRITICAL`
- **CO2 Emissions Model**:
  $$\text{CO}_2 \, (\text{kg}) = \text{diesel\_liters} \times \text{DIESEL\_CO2\_KG\_PER\_LITER}$$
  Default factor: `2.68 kg CO2/L` (standard EPA/IPCC stoichiometric diesel combustion factor). Clearly documented as an empirical engineering estimate.

---

## 3. Weather Integration & Resilient Fallback

### 3.1 Multi-Provider Weather Hierarchy
The microgrid controller must **never fail** if an external API or internet link goes down. The `WeatherManager` enforces a 4-tier fallback:

```
1. Live Open-Meteo API
       ↓ (network timeout / API error)
2. Live NASA POWER API
       ↓ (network failure)
3. Local Cached Forecast (TTL protected)
       ↓ (fresh microgrid installation / cache missing)
4. Deterministic Physics-Informed Synthetic Fallback
```

Every forecast and snapshot returned carries an explicit `source` attribute:
- `LIVE`
- `CACHED`
- `FALLBACK`

### 3.2 15-Minute Normalization
Both Open-Meteo and NASA POWER deliver data either at 15-minute or hourly intervals. The system dynamically resamples and interpolates hourly series using linear interpolation to guarantee uniform 15-minute resolution across all 96 horizon steps.

---

## 4. Forecasting Engines

### 4.1 Demand Forecast (`demand_forecast.py`)
- Produces 96 future 15-minute demand values ($kW$).
- **Methodology**: Diurnal empirical template matching blended with exponential continuity smoothing at $t=0$.
- **Adjustments**: Day-type multipliers (weekday vs weekend / market day) and temperature sensitivity factor ($+1.2\%$ demand per $^\circ\text{C}$ above $26^\circ\text{C}$ for refrigeration/ventilation).
- Avoids unverified "AI/ML" hype: transparent, robust, deterministic baseline.

### 4.2 Solar PV Forecast (`solar_forecast.py`)
- Converts forecast irradiance ($\text{W/m}^2$) and ambient temperature ($^\circ\text{C}$) into AC power ($kW$).
- Configurable PV nameplate capacity, system efficiency (soiling, cabling, inverter), and cell temperature derating coefficient.

### 4.3 Wind Turbine Forecast (`wind_forecast.py`)
- Converts forecast wind speed ($m/s$) into power ($kW$) using the cubic turbine power curve.
- Clamped strictly between $0$ and $P_{rated}$.

---

## 5. What-If Crisis Simulator & Scenarios

### 5.1 The `run_scenario()` Engine
Function signature:
```python
run_scenario(baseline_data, scenario, severity, duration_hours, co2_kg_per_liter, fuel_price_per_l)
```
Dispatches energy sequentially:
1. **Solar + Wind**: Injected first with priority.
2. **Battery BESS**: Charged by surplus renewables, discharged to cover deficit.
3. **Diesel Genset**: Activated if deficit remains and fuel is available.
4. **Prioritized Load Shedding**: If generation cannot cover demand, loads are curtailed in strict order: $P_2 \rightarrow P_1 \rightarrow P_0$.

### 5.2 The 7 Crisis Scenarios
1. `SOLAR_FAILURE`: PV output reduced to $0\%$ or scaled down by severity.
2. `WIND_FAILURE`: Turbine output reduced to $0\%$ or scaled down by severity.
3. `BATTERY_LOW`: Initial battery SoC constrained to $\le 20\%$.
4. `DIESEL_UNAVAILABLE`: Generator forced offline ($0 \, kW$).
5. `DEMAND_SPIKE`: Village demand multiplied by $(1.0 + \text{severity} \times 0.6)$ (e.g. $+30\%$).
6. `STORM_48H`: 48-hour dense cloud cover, solar reduced by $85\%$, storm reserve active (battery min SoC $40\%$), `storm_mode = True`.
7. `FUEL_PRICE_INCREASE`: Fuel price multiplied by parameter (e.g. $1.5\times$ to $2.5\times$).

### 5.3 Deterministic Hackathon Demo Presets
- **DEMO 1 (Sunny Day)**: Solar high ($60 \, kW$), wind moderate ($14 \, kW$), normal demand, battery healthy ($75\%$), diesel generator completely **OFF** ($0 \, L$ diesel, $0 \, kg$ CO2).
- **DEMO 2 (Cloud Event)**: Solar drops by $70\%$. Battery ramps discharge, diesel fires up to protect critical loads.
- **DEMO 3 (48-Hour Storm)**: 48 hours of heavy rain, solar $-85\%$, storm reserve engaged (battery min SoC $40\%$).
- **DEMO 4 (Demand Spike)**: Village load increases by $+30\%$. P2 loads are curtailed to preserve $100\%$ P0 clinic uptime.
- **DEMO 5 (Diesel Shortage)**: Tank at $75 \, L$ ($< 7$ days autonomy $\rightarrow$ `CRITICAL`). Microgrid enters conservative fuel-saving mode.

---

## 6. Integration Contracts

### Member 3: MPC / MILP Optimizer Contract
Call:
```python
from data import get_mpc_inputs

mpc_inputs = get_mpc_inputs(duration_hours=24, battery_soc=75.0, fuel_remaining_l=450.0)
```
Returns a pure Python dictionary:
- `horizon_intervals`: 96
- `demand_forecast`: `List[float]` of 96 values
- `p0_forecast`, `p1_forecast`, `p2_forecast`: `List[float]` of 96 values each
- `solar_forecast`: `List[float]` of 96 values
- `wind_forecast`: `List[float]` of 96 values
- `battery`: `dict` with capacity, current SoC, min/max limits, charge/discharge rates
- `diesel`: `dict` with capacity, fuel remaining, price, burn curves
- `grid_flags`: `dict` with `storm_mode`, `weather_source`, `weather_provider`

### Member 2: FastAPI Backend Contract
Member 2 can cleanly import and call:
```python
from data import (
    get_api_forecast_payload,   # For GET /api/forecast
    get_api_fuel_payload,       # For GET /api/fuel
    refresh_weather_telemetry,  # For POST /api/weather/refresh
    run_simulation_api,         # For POST /api/simulation/run
)
```
No FastAPI or database dependencies exist within the `data/` modules, ensuring zero circular imports.
