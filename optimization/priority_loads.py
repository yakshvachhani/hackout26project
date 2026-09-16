"""
OptiGrid-AI: Multi-Tier Priority Load Subsystem.
Implements hierarchical load shedding logic and penalty structures:
  P0: Critical (Hospital, Vaccine cold-chain, Emergency communications)
  P1: Shiftable (Water supply pumps, Agricultural processing)
  P2: Deferrable (Domestic discretionary loads, HVAC)
"""

from typing import List, Tuple, Optional
from optimization.config import PriorityLoadConfig


class PriorityLoadSubsystem:
    """
    Manages priority-tiered community demand and calculates penalties for load shedding.
    Enforces the hierarchy: P2 shed first -> P1 shed second -> P0 strictly protected.
    """

    def __init__(self, config: Optional[PriorityLoadConfig] = None):
        self.config = config or PriorityLoadConfig()
        self.p0_penalty = self.config.p0_penalty
        self.p1_penalty = self.config.p1_penalty
        self.p2_penalty = self.config.p2_penalty
        self.curtailment_penalty = self.config.curtailment_penalty

    def split_demand(
        self,
        total_demand: List[float],
        p0_input: Optional[List[float]] = None,
        p1_input: Optional[List[float]] = None,
        p2_input: Optional[List[float]] = None,
    ) -> Tuple[List[float], List[float], List[float]]:
        """
        Ensures consistent P0, P1, and P2 demand arrays for the entire horizon.
        If explicit tier profiles are not supplied, splits total demand using configured ratios.
        """
        n = len(total_demand)
        p0 = list(p0_input) if p0_input is not None and len(p0_input) == n else []
        p1 = list(p1_input) if p1_input is not None and len(p1_input) == n else []
        p2 = list(p2_input) if p2_input is not None and len(p2_input) == n else []

        if not p0 or not p1 or not p2:
            r0 = self.config.default_p0_ratio
            r1 = self.config.default_p1_ratio
            r2 = self.config.default_p2_ratio
            # Normalize ratios in case they don't sum to exactly 1.0
            total_r = r0 + r1 + r2
            r0, r1, r2 = r0 / total_r, r1 / total_r, r2 / total_r

            p0 = [round(d * r0, 3) for d in total_demand]
            p1 = [round(d * r1, 3) for d in total_demand]
            p2 = [round(d * r2, 3) for d in total_demand]

        return p0, p1, p2

    def calculate_shed_penalties(
        self,
        p0_demand: float,
        p0_served: float,
        p1_demand: float,
        p1_served: float,
        p2_demand: float,
        p2_served: float,
        dt_hours: float = 0.25,
    ) -> float:
        """
        Calculates monetary unserved load penalty across tiers.
        Penalty = sum(W_i * unserved_i * dt)
        """
        unserved_0 = max(0.0, p0_demand - p0_served)
        unserved_1 = max(0.0, p1_demand - p1_served)
        unserved_2 = max(0.0, p2_demand - p2_served)

        cost = (
            self.p0_penalty * unserved_0
            + self.p1_penalty * unserved_1
            + self.p2_penalty * unserved_2
        ) * dt_hours
        return cost

    def allocate_available_power_hierarchical(
        self,
        available_power_kw: float,
        p0_demand: float,
        p1_demand: float,
        p2_demand: float,
    ) -> Tuple[float, float, float, float]:
        """
        Deterministic hierarchical load dispatcher for fallback:
        Protects P0 first -> P1 second -> P2 last.
        Returns: (p0_served, p1_served, p2_served, remaining_excess_power)
        """
        remaining = max(0.0, available_power_kw)

        # 1. P0 Critical
        p0_served = min(remaining, p0_demand)
        remaining -= p0_served

        # 2. P1 Shiftable
        p1_served = min(remaining, p1_demand)
        remaining -= p1_served

        # 3. P2 Deferrable
        p2_served = min(remaining, p2_demand)
        remaining -= p2_served

        return p0_served, p1_served, p2_served, remaining
