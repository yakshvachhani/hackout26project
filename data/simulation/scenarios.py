"""
Crisis Simulation Scenarios and Deterministic Hackathon Demo Presets.
Modifies input baseline profiles (demand, solar, wind, battery, diesel, fuel)
to simulate extreme operational microgrid stresses.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
import copy
import numpy as np


class ScenarioType(str, Enum):
    SOLAR_FAILURE = "SOLAR_FAILURE"
    WIND_FAILURE = "WIND_FAILURE"
    BATTERY_LOW = "BATTERY_LOW"
    DIESEL_UNAVAILABLE = "DIESEL_UNAVAILABLE"
    DEMAND_SPIKE = "DEMAND_SPIKE"
    STORM_48H = "STORM_48H"
    FUEL_PRICE_INCREASE = "FUEL_PRICE_INCREASE"
    CUSTOM = "CUSTOM"


@dataclass
class ScenarioDefinition:
    scenario_type: ScenarioType
    name: str
    description: str
    severity: float = 50.0  # 0 to 100%
    duration_hours: float = 24.0
    solar_multiplier: float = 1.0
    wind_multiplier: float = 1.0
    demand_multiplier: float = 1.0
    initial_battery_soc: Optional[float] = None
    battery_min_reserve_soc: Optional[float] = None
    diesel_available: bool = True
    fuel_remaining_l: Optional[float] = None
    fuel_price_multiplier: float = 1.0
    storm_mode: bool = False


def apply_scenario(
    baseline_data: Dict[str, Any],
    scenario_name: str,
    severity: float = 50.0,
    duration_hours: float = 24.0,
) -> Tuple[Dict[str, Any], ScenarioDefinition]:
    """
    Applies scenario transformations onto baseline microgrid data.

    Returns:
        (modified_data, scenario_definition)
    """
    sc_key = scenario_name.upper().strip()
    data = copy.deepcopy(baseline_data)
    sev_frac = max(0.0, min(100.0, severity)) / 100.0

    definition = ScenarioDefinition(
        scenario_type=ScenarioType.CUSTOM,
        name=scenario_name,
        description=f"Crisis scenario {scenario_name} at {severity}% severity",
        severity=severity,
        duration_hours=duration_hours,
    )

    n_steps = len(data.get("demand_kw", []))
    active_steps = min(n_steps, int(duration_hours * 4))

    if sc_key in ("SOLAR_FAILURE", "SOLAR_OUTAGE"):
        definition.scenario_type = ScenarioType.SOLAR_FAILURE
        definition.description = "Sudden PV inverter trip or physical array failure."
        # Severity 100% -> 0 generation; Severity 50% -> 50% generation
        factor = max(0.0, 1.0 - sev_frac)
        definition.solar_multiplier = factor
        for i in range(active_steps):
            data["solar_kw"][i] = round(data["solar_kw"][i] * factor, 2)

    elif sc_key in ("WIND_FAILURE", "WIND_OUTAGE"):
        definition.scenario_type = ScenarioType.WIND_FAILURE
        definition.description = "Turbine mechanical brake lock or high-wind cut-out trip."
        factor = max(0.0, 1.0 - sev_frac)
        definition.wind_multiplier = factor
        for i in range(active_steps):
            data["wind_kw"][i] = round(data["wind_kw"][i] * factor, 2)

    elif sc_key in ("BATTERY_LOW", "BATTERY_DEPLETED"):
        definition.scenario_type = ScenarioType.BATTERY_LOW
        definition.description = "BESS initialized near minimum threshold with depleted reserve."
        target_soc = max(10.0, 20.0 - (sev_frac * 10.0))
        definition.initial_battery_soc = target_soc
        data["battery_soc"] = target_soc

    elif sc_key in ("DIESEL_UNAVAILABLE", "GENERATOR_OUTAGE"):
        definition.scenario_type = ScenarioType.DIESEL_UNAVAILABLE
        definition.description = "Diesel generator mechanical fault or fuel pipeline blockage."
        definition.diesel_available = False
        data["diesel_available"] = False

    elif sc_key in ("DEMAND_SPIKE", "LOAD_SURGE"):
        definition.scenario_type = ScenarioType.DEMAND_SPIKE
        definition.description = "Abnormal surge in community productive use or heating."
        spike_multiplier = 1.0 + (sev_frac * 0.6)  # up to +60% at 100% severity
        definition.demand_multiplier = spike_multiplier
        for i in range(active_steps):
            data["demand_kw"][i] = round(data["demand_kw"][i] * spike_multiplier, 2)
            if "p0_kw" in data and i < len(data["p0_kw"]):
                data["p0_kw"][i] = round(data["p0_kw"][i] * (1.0 + sev_frac * 0.2), 2)
            if "p1_kw" in data and i < len(data["p1_kw"]):
                data["p1_kw"][i] = round(data["p1_kw"][i] * (1.0 + sev_frac * 0.4), 2)
            if "p2_kw" in data and i < len(data["p2_kw"]):
                data["p2_kw"][i] = round(data["demand_kw"][i] - data["p0_kw"][i] - data["p1_kw"][i], 2)

    elif sc_key in ("STORM_48H", "STORM"):
        definition.scenario_type = ScenarioType.STORM_48H
        definition.description = "Severe 48-hour storm with dense cloud cover and heightened reserve requirements."
        definition.storm_mode = True
        definition.battery_min_reserve_soc = 40.0
        data["storm_mode"] = True
        data["battery_min_soc"] = 40.0
        # Heavily attenuate solar, wind fluctuates
        for i in range(active_steps):
            data["solar_kw"][i] = round(data["solar_kw"][i] * 0.15, 2)
            data["wind_kw"][i] = round(data["wind_kw"][i] * (1.2 + 0.3 * np.sin(i * 0.1)), 2)

    elif sc_key in ("FUEL_PRICE_INCREASE", "FUEL_SHOCK"):
        definition.scenario_type = ScenarioType.FUEL_PRICE_INCREASE
        definition.description = "Global supply chain disruption escalating diesel procurement prices."
        price_mult = 1.0 + (sev_frac * 1.5)  # up to 2.5x
        definition.fuel_price_multiplier = price_mult
        data["fuel_price_per_l"] = round(data.get("fuel_price_per_l", 1.45) * price_mult, 2)

    return data, definition


# 5 Deterministic Hackathon Demo Scenarios
def get_hackathon_demo_presets() -> Dict[str, Dict[str, Any]]:
    """Returns the 5 official deterministic demo scenario configurations."""
    return {
        "DEMO_1_SUNNY_DAY": {
            "name": "DEMO 1: Sunny Day",
            "description": "Ideal conditions. High solar, moderate steady wind, normal demand. Battery operates smoothly, diesel generator completely OFF.",
            "scenario": "CUSTOM",
            "severity": 0.0,
            "duration_hours": 24,
            "solar_factor": 1.1,
            "wind_factor": 1.0,
            "demand_factor": 1.0,
            "battery_soc": 75.0,
            "fuel_l": 500.0,
            "storm_mode": False,
        },
        "DEMO_2_CLOUD_EVENT": {
            "name": "DEMO 2: Cloud Event",
            "description": "Midday cloud cover causes sudden 70% drop in PV generation. System discharges battery and ramps diesel if needed.",
            "scenario": "SOLAR_FAILURE",
            "severity": 70.0,
            "duration_hours": 12,
            "solar_factor": 0.3,
            "wind_factor": 1.0,
            "demand_factor": 1.0,
            "battery_soc": 60.0,
            "fuel_l": 500.0,
            "storm_mode": False,
        },
        "DEMO_3_STORM_48H": {
            "name": "DEMO 3: 48-Hour Storm",
            "description": "Prolonged overcast tempest. Solar drops by 85%. Storm reserve activates (min battery SoC boosted to 40%). Controlled diesel backup.",
            "scenario": "STORM_48H",
            "severity": 85.0,
            "duration_hours": 48,
            "solar_factor": 0.15,
            "wind_factor": 1.3,
            "demand_factor": 1.05,
            "battery_soc": 65.0,
            "fuel_l": 600.0,
            "storm_mode": True,
        },
        "DEMO_4_DEMAND_SPIKE": {
            "name": "DEMO 4: Demand Spike (+30%)",
            "description": "Community agricultural harvesting & evening festival triggers +30% demand surge. P2/P1 shedding protects P0 clinic.",
            "scenario": "DEMAND_SPIKE",
            "severity": 60.0,  # yields +30% demand
            "duration_hours": 24,
            "solar_factor": 1.0,
            "wind_factor": 1.0,
            "demand_factor": 1.30,
            "battery_soc": 70.0,
            "fuel_l": 450.0,
            "storm_mode": False,
        },
        "DEMO_5_DIESEL_SHORTAGE": {
            "name": "DEMO 5: Diesel Fuel Shortage",
            "description": "Fuel reserves drop below critical threshold (<7 days autonomy). System restricts generator run-time and preserves critical P0 loads.",
            "scenario": "CUSTOM",
            "severity": 90.0,
            "duration_hours": 24,
            "solar_factor": 1.0,
            "wind_factor": 1.0,
            "demand_factor": 1.0,
            "battery_soc": 40.0,
            "fuel_l": 75.0,  # Low fuel warning/critical
            "diesel_available": True,
            "storm_mode": False,
        },
    }
