# OptiGrid-AI — Team Contract & Architecture Guide

## Module Ownership
- **Member 1 (Frontend)**: React 18, Vite, Tailwind CSS, Lucide icons, Recharts (`frontend/`)
- **Member 2 (Backend)**: FastAPI, SQLAlchemy, SQLite, WebSocket Manager, Pydantic schemas (`backend/`)
- **Member 3 (Optimization)**: PuLP MILP solver, Rolling-horizon MPC, Battery & Diesel physical subsystems (`optimization/`)
- **Member 4 (Data Services)**: Weather fallback chain (Open-Meteo / NASA POWER / Cache / Synthetic), 15-min forecasters, What-if crisis simulator (`data/`)

## Inter-Module Data Pipeline
```
[ Open-Meteo / NASA POWER Weather APIs ]
                    |
                    v
[ WeatherManager (Tiered Fallback: LIVE -> CACHED -> FALLBACK) ]
                    |
                    v
[ Forecasters (Solar / Wind / Village Load Demand) ]
                    |
                    v
[ get_mpc_inputs() ] ---> [ OptimizationInput (models.py) ]
                                    |
                                    v
                         [ optimize_dispatch() (milp.py) ]
                                    |
                                    v
                         [ OptimizationResult ]
                                    |
                                    v
                         [ FastAPI Backend API ]
                                    |
               +--------------------+--------------------+
               |                                         |
               v                                         v
        REST Endpoints (/api/...)                 WebSocket (/ws)
               |                                         |
               +--------------------+--------------------+
                                    |
                                    v
                         [ React Frontend (Member 1) ]
```

## Integration Principles
1. **Zero Rebuild**: Reused 100% of the completed modules built by Members 1, 2, 3, and 4.
2. **Resilience First**: If external meteorological APIs are rate-limited or offline, the system falls back seamlessly to local cache and physics-informed models.
3. **Strict Priority Protection**: P0 life-critical loads are mathematically protected by MILP constraint penalties; P1 loads are shifted; P2 loads are curtailed in deficit.
4. **Real-time Push**: Telemetry bus events are broadcasted over WebSocket to ensure low latency and live user feedback.
