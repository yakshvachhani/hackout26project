import json
from data import build_default_baseline_data, get_mpc_inputs

b24 = build_default_baseline_data(duration_hours=24)
with open('data/datasets/village_benchmark_24h.json', 'w') as f:
    json.dump(b24, f, indent=2)

b48 = build_default_baseline_data(duration_hours=48)
with open('data/datasets/village_benchmark_48h.json', 'w') as f:
    json.dump(b48, f, indent=2)

mpc = get_mpc_inputs(duration_hours=24)
print("Generated 24h & 48h datasets successfully!")
print("MPC horizon:", len(mpc["demand_forecast"]), "timesteps")
