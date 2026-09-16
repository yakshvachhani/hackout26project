"""
OptiGrid-AI: Diesel Generator Subsystem Model.
Enforces minimum loading constraints (30% rule), binary commitment states,
linear fuel consumption curve, and operational costs.
"""

from typing import Optional
from optimization.config import DieselConfig


class DieselSubsystem:
    """
    Physical and economic model of microgrid backup diesel generator.
    Enforces the industry-standard 30% minimum loading rule to prevent engine wet stacking,
    and models fuel consumption via intercept-slope generator curves.
    """

    def __init__(
        self,
        config: Optional[DieselConfig] = None,
        rated_capacity_kw: Optional[float] = None,
        min_loading_ratio: Optional[float] = None,
        fuel_price: Optional[float] = None,
        is_available: bool = True,
    ):
        self.config = config or DieselConfig()
        self.rated_capacity_kw = rated_capacity_kw if rated_capacity_kw is not None else self.config.rated_capacity_kw
        self.min_loading_ratio = min_loading_ratio if min_loading_ratio is not None else self.config.min_loading_ratio
        self.fuel_price = fuel_price if fuel_price is not None else self.config.default_fuel_price
        self.is_available = is_available

        # Fuel curve coefficients
        self.alpha_intercept = self.config.fuel_curve_intercept  # L/hr per kW rated
        self.beta_slope = self.config.fuel_curve_slope           # L/kWh active generation

    @property
    def min_output_kw(self) -> float:
        """Minimum allowable output when committed (30% rated)."""
        return self.rated_capacity_kw * self.min_loading_ratio

    @property
    def max_output_kw(self) -> float:
        """Maximum rated active power output."""
        return self.rated_capacity_kw if self.is_available else 0.0

    def calculate_fuel_consumption_liters(
        self,
        power_kw: float,
        is_on: bool,
        dt_hours: float = 0.25
    ) -> float:
        """
        Calculate fuel consumed (Liters) over interval dt:
        F = [ u * (alpha * P_rated) + beta * P_diesel ] * dt
        """
        if not is_on or power_kw <= 0.0 or not self.is_available:
            return 0.0
        
        idle_burn_rate = self.alpha_intercept * self.rated_capacity_kw  # L/hr
        load_burn_rate = self.beta_slope * power_kw                    # L/hr
        return (idle_burn_rate + load_burn_rate) * dt_hours

    def calculate_fuel_cost(
        self,
        fuel_liters: float,
        custom_fuel_price: Optional[float] = None
    ) -> float:
        """Calculate total monetary cost for consumed fuel."""
        price = custom_fuel_price if custom_fuel_price is not None else self.fuel_price
        return fuel_liters * price

    def estimate_co2_emissions_kg(self, fuel_liters: float) -> float:
        """Standard combustion factor ~ 2.68 kg CO2 per liter of diesel fuel burned."""
        return round(fuel_liters * 2.68, 2)
