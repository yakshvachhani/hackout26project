"""
Synthetic Battery Energy Storage System (BESS) Model for Off-Grid Microgrids.
Tracks State of Charge (SoC), charge/discharge constraints, degradation throughput, and reserves.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple


@dataclass
class BatteryConfig:
    capacity_kwh: float = 120.0
    initial_soc_pct: float = 75.0
    min_soc_pct: float = 20.0
    max_soc_pct: float = 95.0
    storm_min_soc_pct: float = 40.0
    max_charge_kw: float = 40.0
    max_discharge_kw: float = 40.0
    charge_efficiency: float = 0.94
    discharge_efficiency: float = 0.94


class BatteryStorage:
    """
    Physical BESS simulation state tracker:
    - Maintains SoC within [min_soc, max_soc] bounds.
    - Respects charge and discharge kW ratings.
    - Applies round-trip efficiency losses.
    - Dynamically updates min reserve under storm mode.
    - Tracks cumulative energy throughput for degradation metrics.
    """

    def __init__(self, config: BatteryConfig = None):
        self.config = config or BatteryConfig()
        self.capacity_kwh = self.config.capacity_kwh
        self.current_soc = min(max(self.config.initial_soc_pct, self.config.min_soc_pct), self.config.max_soc_pct)
        self.cumulative_charge_kwh = 0.0
        self.cumulative_discharge_kwh = 0.0
        self.storm_mode = False

    def get_effective_min_soc(self) -> float:
        """Returns effective minimum SoC depending on storm mode status."""
        return self.config.storm_min_soc_pct if self.storm_mode else self.config.min_soc_pct

    def set_storm_mode(self, enabled: bool):
        self.storm_mode = enabled

    def step(self, requested_power_kw: float, dt_hours: float = 0.25) -> Tuple[float, float]:
        """
        Simulates battery action for one time interval.
        Positive requested_power_kw = Discharge requested (supplying power to grid).
        Negative requested_power_kw = Charge requested (absorbing excess renewable power).

        Returns:
            (actual_power_kw, new_soc_pct)
            actual_power_kw > 0 indicates grid power supplied.
            actual_power_kw < 0 indicates power stored into battery.
        """
        effective_min_soc = self.get_effective_min_soc()
        current_energy_kwh = (self.current_soc / 100.0) * self.capacity_kwh
        min_energy_kwh = (effective_min_soc / 100.0) * self.capacity_kwh
        max_energy_kwh = (self.config.max_soc_pct / 100.0) * self.capacity_kwh

        if requested_power_kw > 0:
            # Discharging to support load
            max_available_discharge_kw = (current_energy_kwh - min_energy_kwh) * self.config.discharge_efficiency / dt_hours
            deliverable_kw = max(0.0, min(requested_power_kw, self.config.max_discharge_kw, max_available_discharge_kw))
            
            # Energy extracted from internal storage
            extracted_energy_kwh = (deliverable_kw * dt_hours) / self.config.discharge_efficiency
            current_energy_kwh -= extracted_energy_kwh
            self.cumulative_discharge_kwh += deliverable_kw * dt_hours
            actual_power = deliverable_kw

        elif requested_power_kw < 0:
            # Charging from surplus generation
            surplus_kw = abs(requested_power_kw)
            max_absorbable_kw = (max_energy_kwh - current_energy_kwh) / (self.config.charge_efficiency * dt_hours)
            charge_kw = max(0.0, min(surplus_kw, self.config.max_charge_kw, max_absorbable_kw))
            
            added_energy_kwh = charge_kw * dt_hours * self.config.charge_efficiency
            current_energy_kwh += added_energy_kwh
            self.cumulative_charge_kwh += charge_kw * dt_hours
            actual_power = -charge_kw

        else:
            actual_power = 0.0

        self.current_soc = round((current_energy_kwh / self.capacity_kwh) * 100.0, 2)
        return actual_power, self.current_soc

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capacity_kwh": self.capacity_kwh,
            "soc_pct": self.current_soc,
            "min_soc_pct": self.get_effective_min_soc(),
            "max_soc_pct": self.config.max_soc_pct,
            "storm_mode": self.storm_mode,
            "cumulative_charge_kwh": round(self.cumulative_charge_kwh, 2),
            "cumulative_discharge_kwh": round(self.cumulative_discharge_kwh, 2),
            "equivalent_full_cycles": round((self.cumulative_discharge_kwh) / max(1.0, self.capacity_kwh), 2),
        }
