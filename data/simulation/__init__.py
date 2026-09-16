"""
Simulation package for OptiGrid-AI.
Exports scenarios, what-if simulator engine, and metrics.
"""

from data.simulation.scenarios import (
    ScenarioType,
    ScenarioDefinition,
    apply_scenario,
    get_hackathon_demo_presets,
)
from data.simulation.metrics import (
    SimulationMetrics,
    compute_metrics,
)
from data.simulation.simulator import (
    run_scenario,
    simulate_microgrid_dispatch,
    build_default_baseline_data,
)

__all__ = [
    "ScenarioType",
    "ScenarioDefinition",
    "apply_scenario",
    "get_hackathon_demo_presets",
    "SimulationMetrics",
    "compute_metrics",
    "run_scenario",
    "simulate_microgrid_dispatch",
    "build_default_baseline_data",
]
