"""
OptiGrid-AI: Battery Storage Subsystem Model.
Handles State-of-Charge (SOC) tracking, storm reserves, charging/discharging limits,
and battery throughput degradation modeling.
"""

from typing import Optional, Tuple
from optimization.config import BatteryConfig


class BatterySubsystem:
    """
    Physical model of Lithium-ion / LFP Battery Energy Storage System (BESS).
    Enforces SOC boundaries, dynamic storm reserve margins, charge/discharge rates,
    and degradation penalty calculations.
    """

    def __init__(
        self,
        config: Optional[BatteryConfig] = None,
        capacity_kwh: Optional[float] = None,
        storm_mode: bool = False,
        min_soc_override: Optional[float] = None,
        max_soc_override: Optional[float] = None,
    ):
        self.config = config or BatteryConfig()
        self.capacity_kwh = capacity_kwh if capacity_kwh is not None else self.config.capacity_kwh
        self.storm_mode = storm_mode

        # Determine effective minimum SOC
        if storm_mode:
            self.min_soc = self.config.storm_min_soc
        elif min_soc_override is not None:
            self.min_soc = min_soc_override / 100.0 if min_soc_override > 1.0 else min_soc_override
        else:
            self.min_soc = self.config.normal_min_soc

        # Determine effective maximum SOC
        if max_soc_override is not None:
            self.max_soc = max_soc_override / 100.0 if max_soc_override > 1.0 else max_soc_override
        else:
            self.max_soc = self.config.max_soc

        # Operational boundaries in kWh
        self.min_energy_kwh = self.min_soc * self.capacity_kwh
        self.max_energy_kwh = self.max_soc * self.capacity_kwh

        # Rate limits
        self.max_charge_kw = self.config.max_charge_kw
        self.max_discharge_kw = self.config.max_discharge_kw
        self.charge_eff = self.config.charge_efficiency
        self.discharge_eff = self.config.discharge_efficiency
        self.degradation_cost_per_kwh = self.config.degradation_cost_per_kwh

    def get_soc_percent(self, energy_kwh: float) -> float:
        """Convert stored energy (kWh) to State of Charge percentage (0-100%)."""
        if self.capacity_kwh <= 0:
            return 0.0
        return round((energy_kwh / self.capacity_kwh) * 100.0, 2)

    def next_energy_state(
        self,
        current_energy_kwh: float,
        charge_kw: float,
        discharge_kw: float,
        dt_hours: float = 0.25
    ) -> float:
        """
        Calculate next timestep energy state E[t+1] based on power dispatch.
        E[t+1] = E[t] + (eta_ch * P_ch - P_dis / eta_dis) * dt
        """
        delta_charge = self.charge_eff * charge_kw * dt_hours
        delta_discharge = (discharge_kw / self.discharge_eff) * dt_hours
        next_energy = current_energy_kwh + delta_charge - delta_discharge
        # Clamp within numerical tolerance of physical limits
        return max(0.0, min(self.capacity_kwh, next_energy))

    def calculate_degradation_cost(
        self,
        charge_kw: float,
        discharge_kw: float,
        dt_hours: float = 0.25
    ) -> float:
        """
        Calculates battery cycling cost proxy.
        Note: Uses total energy throughput (charge + discharge) * cost_per_kwh.
        This provides an economic proxy for cycle wear without making unverified
        electrochemical cell wear claims.
        """
        throughput_kwh = (charge_kw + discharge_kw) * dt_hours
        return throughput_kwh * self.degradation_cost_per_kwh

    def max_available_discharge_power(
        self,
        current_energy_kwh: float,
        dt_hours: float = 0.25
    ) -> float:
        """Maximum power (kW) that can be safely discharged over dt without breaching min_soc."""
        available_energy_kwh = max(0.0, current_energy_kwh - self.min_energy_kwh)
        power_energy_limited = (available_energy_kwh * self.discharge_eff) / dt_hours
        return min(self.max_discharge_kw, power_energy_limited)

    def max_available_charge_power(
        self,
        current_energy_kwh: float,
        dt_hours: float = 0.25
    ) -> float:
        """Maximum power (kW) that can be safely charged over dt without exceeding max_soc."""
        headroom_energy_kwh = max(0.0, self.max_energy_kwh - current_energy_kwh)
        power_energy_limited = headroom_energy_kwh / (self.charge_eff * dt_hours)
        return min(self.max_charge_kw, power_energy_limited)
