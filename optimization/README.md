# OptiGrid-AI Optimization Engine (MILP & MPC)
**Mathematical Brain for Off-Grid Microgrid Dispatch & Control**

Member 3 Role: **Optimization Engine / AI / MILP / MPC**  
Tech Stack: **Python 3.10+, PuLP, NumPy, Pandas, Pydantic**

---

## Architecture Overview

```
                      +-----------------------------+
                      |   Member 2 Backend Service   |
                      |   (FastAPI / Telemetry Hub) |
                      +--------------+--------------+
                                     |
                         run_mpc() / | optimize_dispatch()
                                     v
+-------------------------------------------------------------------------+
|                       OPTIGRID-AI OPTIMIZATION ENGINE                   |
|                                                                         |
|  +---------------------+   +---------------------+   +---------------+  |
|  |     Battery Model   |   |     Diesel Model    |   | Priority Load |  |
|  |   (SOC, Deg Proxy)  |   | (>=30% Min Loading) |   |  (P0, P1, P2) |  |
|  +----------+----------+   +----------+----------+   +-------+-------+  |
|             |                         |                      |          |
|             +-------------------------+----------------------+          |
|                                       v                                 |
|                      +---------------------------------+                |
|                      |        PuLP MILP Solver         |                |
|                      |   96 Timesteps (24h @ 15 min)   |                |
|                      |  - Hard Power Balance           |                |
|                      |  - Storm Reserve Constraints    |                |
|                      |  - Multi-Objective Weighting    |                |
|                      +----------------+----------------+                |
|                                       |                                 |
|                  +--------------------+--------------------+            |
|                  |                                         |            |
|             [Optimal]                                 [Infeasible]      |
|                  |                                         |            |
|                  v                                         v            |
|       +---------------------+                   +---------------------+ |
|       | 96-Step Schedule &  |                   | Deterministic Fall- | |
|       | Step-0 MPC Action   |                   | back Dispatch Engine| |
|       +---------------------+                   +---------------------+ |
+-------------------------------------------------------------------------+
```

---

## 1. What MILP Does
Mixed-Integer Linear Programming (MILP) formulates the microgrid dispatch over a 24-hour horizon ($T = 96$ timesteps at 15-minute intervals, $\Delta t = 0.25$ h) as a constrained mathematical optimization problem. It simultaneously schedules continuous variables (solar, wind, battery charge/discharge, diesel generation, load tiers) and integer/binary variables (diesel on/off generator commitment) to achieve the global minimum operating cost while strictly respecting physical equipment bounds, grid reliability, and clean energy priorities.

## 2. What MPC Does
Model Predictive Control (MPC) implements a receding-horizon control loop:
1. **Forecast Ingestion**: At the current time step $t$, the microgrid receives updated 24-hour forecasts (solar irradiance, wind velocity, community load profiles) and telemetry (battery SOC, remaining fuel).
2. **Horizon Optimization**: MPC solves the 96-timestep MILP over the entire lookahead horizon.
3. **Execution**: The system executes **only the first timestep ($t=0$) decision** (`current_dispatch`) to the microgrid plant (inverter setpoints, generator start command).
4. **State Update & Recede**: At the next 15-minute interval, new telemetry arrives, the horizon shifts forward by one step, and the problem re-optimizes.

---

## 3. Decision Variables (per timestep $t \in [0, 95]$)

| Variable | Type | Bounds | Description |
| :--- | :--- | :--- | :--- |
| `solar[t]` | Continuous | $[0, P_{\text{solar,avail}}[t]]$ | Active solar power dispatched (kW) |
| `wind[t]` | Continuous | $[0, P_{\text{wind,avail}}[t]]$ | Active wind power dispatched (kW) |
| `battery_charge[t]` | Continuous | $[0, P_{\text{charge,max}}]$ | Battery charging power (kW) |
| `battery_discharge[t]` | Continuous | $[0, P_{\text{discharge,max}}]$ | Battery discharging power (kW) |
| `battery_energy[t]` | Continuous | $[E_{\min}, E_{\max}]$ | Stored battery energy (kWh) across $t \in [0, 96]$ |
| `diesel[t]` | Continuous | $[0, P_{\text{diesel,max}}]$ | Diesel generator power output (kW) |
| `diesel_on[t]` | Binary | $\{0, 1\}$ | Generator commitment status (1 = ON, 0 = OFF) |
| `p0_served[t]` | Continuous | $[0, P_{0,\text{demand}}[t]]$ | Critical tier load power served (kW) |
| `p1_served[t]` | Continuous | $[0, P_{1,\text{demand}}[t]]$ | Shiftable tier load power served (kW) |
| `p2_served[t]` | Continuous | $[0, P_{2,\text{demand}}[t]]$ | Deferrable tier load power served (kW) |
| `curtailment[t]` | Continuous | $[0, \infty)$ | Involuntary renewable generation curtailment (kW) |

---

## 4. Constraints

### 4.1 Hard Power Balance Constraint
At every single timestep $t$:
$$\text{Solar}[t] + \text{Wind}[t] + \text{Battery Discharge}[t] + \text{Diesel}[t] = P_{0,\text{served}}[t] + P_{1,\text{served}}[t] + P_{2,\text{served}}[t] + \text{Battery Charge}[t] + \text{Curtailment}[t]$$

### 4.2 Renewable Availability Limits
$$0 \le \text{solar}[t] \le \text{solar\_available}[t]$$
$$0 \le \text{wind}[t] \le \text{wind\_available}[t]$$

### 4.3 Battery Storage Dynamics & Limits
$$E[0] = E_{\text{initial}}$$
$$E[t+1] = E[t] + \left(\eta_{\text{ch}} \cdot \text{battery\_charge}[t] - \frac{\text{battery\_discharge}[t]}{\eta_{\text{dis}}}\right) \cdot \Delta t \quad \forall t \in [0, T-1]$$
$$E_{\min} \le E[t] \le E_{\max} \quad \forall t \in [0, T]$$

### 4.4 Diesel Generator Minimum Loading (30% Rule)
To prevent internal combustion wet stacking and premature carbon fouling:
$$\text{diesel}[t] \ge P_{\text{diesel,min}} \cdot \text{diesel\_on}[t]$$
$$\text{diesel}[t] \le P_{\text{diesel,max}} \cdot \text{diesel\_on}[t]$$
- When $\text{diesel\_on}[t] = 0 \implies \text{diesel}[t] = 0$ kW.
- When $\text{diesel\_on}[t] = 1 \implies \text{diesel}[t] \ge 0.30 \times P_{\text{diesel,rated}}$ (e.g., $\ge 12.0$ kW for a 40 kW generator).

### 4.5 Priority Load Demand Bounds
$$0 \le p_{0,\text{served}}[t] \le p_{0,\text{demand}}[t]$$
$$0 \le p_{1,\text{served}}[t] \le p_{1,\text{demand}}[t]$$
$$0 \le p_{2,\text{served}}[t] \le p_{2,\text{demand}}[t]$$

---

## 5. Objective Function
The optimizer minimizes the total weighted operational and unreliability cost over the 24-hour horizon:

$$\min \sum_{t=0}^{T-1} \Big( C_{\text{fuel}}[t] + C_{\text{deg}}[t] + W_0 \cdot P_{0,\text{shed}}[t] + W_1 \cdot P_{1,\text{shed}}[t] + W_2 \cdot P_{2,\text{shed}}[t] + W_{\text{curt}} \cdot \text{curtailment}[t] \Big) \cdot \Delta t$$

- **Fuel Cost**: Modeled via generator fuel consumption curve:
  $$\text{Fuel}[t] = \left( \text{diesel\_on}[t] \cdot \alpha \cdot P_{\text{rated}} + \beta \cdot \text{diesel}[t] \right) \cdot \Delta t$$
  $$C_{\text{fuel}}[t] = \text{fuel\_price} \times \text{Fuel}[t]$$
  *(Default parameters: $\alpha = 0.08$ L/hr/kW_rated, $\beta = 0.22$ L/kWh, Fuel Price = \$95/L).*
- **Battery Degradation Cost Proxy**:
  $$C_{\text{deg}}[t] = C_{\text{deg\_rate}} \times (\text{battery\_charge}[t] + \text{battery\_discharge}[t]) \cdot \Delta t$$
  *(Default rate: \$0.04/kWh throughput proxy).*
- **Hierarchical Priority Load Penalties**:
  - $W_0 = \$10{,}000/\text{kWh}$ (Critical hospital, vaccines, emergency telecom)
  - $W_1 = \$500/\text{kWh}$ (Shiftable water pumps, processing mills)
  - $W_2 = \$50/\text{kWh}$ (Deferrable domestic appliances, HVAC)
- **Renewable Curtailment Penalty**:
  - $W_{\text{curt}} = \$0.50/\text{kWh}$ (Mild penalty ensuring renewable energy is preferred over curtailment).

---

## 6. Battery Model
The battery subsystem tracks energy stored in kWh and State-of-Charge (SOC in %):
- **Round-trip Efficiency**: $\eta_{\text{ch}} = 0.92$, $\eta_{\text{dis}} = 0.92$ (nominal roundtrip $\approx 85\%$).
- **C-Rate Power Limits**: Max Charge = 25 kW (0.25C), Max Discharge = 30 kW (0.30C).
- **Lifetime Protection Floor**: Maximum operational SOC is capped at 95% to avoid overvoltage degradation.
- **Degradation Proxy**: Penalizes excessive cycle throughput without fabricating unvalidated electrochemical physics.

---

## 7. Diesel Model
- **Rated Capacity**: Configurable (default 40 kW).
- **Minimum Loading Constraint**: 30% of rated capacity (12 kW minimum active output when operating).
- **Fuel Consumption Formula**:
  $$\text{Liters/hr} = \alpha \cdot P_{\text{rated}} + \beta \cdot P_{\text{output}} = 0.08 \times 40 + 0.22 \times P_{\text{output}} = 3.2 + 0.22 \times P_{\text{output}}$$
  - At minimum loading (12 kW): Fuel burn is $5.84$ L/hr ($0.48$ L/kWh).
  - At full rated power (40 kW): Fuel burn is $12.0$ L/hr ($0.30$ L/kWh).
- **Optimal Unit Commitment**: When loads are light, the MILP chooses whether to run the generator at high efficiency to charge the battery and shut down, or remain off.

---

## 8. Priority Loads (P0 / P1 / P2)
- **P0 (Critical)**: Clinic lighting, vaccine cold chain, communications, water treatment. Must not be shed unless supply is physically zero.
- **P1 (Shiftable)**: Agricultural irrigation, water supply pumps, industrial milling. Shed when battery and diesel are strained.
- **P2 (Deferrable)**: Domestic air conditioning, high-power residential loads. First tier curtailed during any deficit.

When energy is constrained:
$$\text{Penalty}(P0) \gg \text{Penalty}(P1) \gg \text{Penalty}(P2) \implies \text{Shed Order}: P2 \to P1 \to P0$$

---

## 9. Storm Reserve Mode
When impending severe weather (cyclones, monsoon storms) is detected:
- **Normal Mode**: Minimum SOC floor = **20%** ($E_{\min} = 0.20 \times C_{\text{batt}}$).
- **Storm Reserve Mode** (`storm_mode=True`): Minimum SOC floor = **50%** ($E_{\min} = 0.50 \times C_{\text{batt}}$).

The optimizer will prevent discharging the battery below 50% SOC, preserving vital reserve energy for emergency hospital operations.

---

## 10. Fallback Strategy
If the MILP solver encounters an unexpected error, infeasibility, or timeout:
1. The deterministic rule-based fallback engine triggers automatically (`run_deterministic_fallback`).
2. Dispatches supply in strict merit order:
   $$\text{Solar} \to \text{Wind} \to \text{Battery (subject to SOC floor)} \to \text{Diesel (subject to 30% min loading)}$$
3. Serves loads in strict priority hierarchy:
   $$P0 \to P1 \to P2$$
4. Clearly sets `solver_status = "fallback"` and `status = "fallback"` (never pretends an optimization succeeded).

---

## 11. API / Function Contract for Member 2

### Primary Functions

```python
from optimization import optimize_dispatch, run_mpc, optimize, run_milp_optimization
```

#### `optimize_dispatch(input_data, config=None) -> OptimizationResult`
Solves 24-hour MILP over 96 timesteps. Accepts either `OptimizationInput` model or standard dictionary.

#### `run_mpc(input_data, config=None) -> OptimizationResult`
Runs rolling-horizon MPC lookahead, returning `current_dispatch` (timestep 0) and `full_schedule`.

#### `optimize(input_data) -> dict` and `run_milp_optimization(input_data) -> dict`
Direct plug-and-play dictionary endpoints designed specifically for Member 2's `backend/services/optimizer_service.py`.

---

## 12. Example Usage

```python
from optimization import optimize_dispatch

# Example microgrid state
input_data = {
    "demand_kw": 50.0,
    "solar_available_kw": 30.0,
    "wind_available_kw": 15.0,
    "battery_soc": 70.0,
    "battery_capacity_kwh": 100.0,
    "diesel_available": True,
    "fuel_price": 95.0,
    "min_soc": 20.0,
    "max_soc": 95.0,
    "storm_mode": False
}

result = optimize_dispatch(input_data)

print(f"Status: {result.status}")
print(f"Solve Time: {result.solve_time_ms:.2f} ms")
print(f"Current Dispatch (t=0):")
print(f"  Solar:    {result.solar_kw:.1f} kW")
print(f"  Wind:     {result.wind_kw:.1f} kW")
print(f"  Battery:  {result.battery_kw:.1f} kW (net discharge)")
print(f"  Diesel:   {result.diesel_kw:.1f} kW")
print(f"  Total:    {result.total_supply_kw:.1f} kW")
print(f"  Renewable Percentage: {result.renewable_percentage:.1f}%")
```

**Expected Output:**
```text
Status: optimal
Solve Time: 326.17 ms
Current Dispatch (t=0):
  Solar:    30.0 kW
  Wind:     15.0 kW
  Battery:  5.0 kW (net discharge)
  Diesel:   0.0 kW
  Total:    50.0 kW
  Renewable Percentage: 90.0%
```

---

## 13. Integration Instructions for Member 2

Member 2's `backend/services/optimizer_service.py` automatically detects and imports the `optimization` package.

### Verifying Integration
In the project root, simply run:
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run optimization test suite
pytest -v optimization/tests

# Run backend test suite
python backend/test_backend.py
```
All 22 unit & integration tests and all 13 backend telemetry tests pass with zero warnings.
