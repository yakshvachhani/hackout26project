import importlib
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from backend.database.models import DispatchRecord
from backend.schemas.dispatch import (
    OptimizeRequest,
    OptimizeResponse,
    DispatchDetail,
    MetricsDetail
)
from backend.websocket.manager import ws_manager

logger = logging.getLogger(__name__)


class OptimizerService:
    """
    Bridge to Member 3's MILP / MPC optimization engine.
    Imports dynamically from optimization package if available,
    otherwise provides a high-fidelity merit-order optimization solver.
    """

    def __init__(self):
        self._member3_module = None
        self._detect_member3_optimizer()

    def _detect_member3_optimizer(self):
        """Attempts to discover Member 3's optimization module dynamically."""
        possible_modules = [
            "optimization.milp",
            "optimization.mpc",
            "optimization.optimizer",
            "optimization.engine"
        ]
        for mod_name in possible_modules:
            try:
                mod = importlib.import_module(mod_name)
                self._member3_module = mod
                logger.info(f"Successfully linked Member 3 optimization module: {mod_name}")
                return
            except (ImportError, ModuleNotFoundError):
                continue
        logger.info("Member 3 optimization code not yet committed. Using integrated fallback optimizer.")

    async def optimize(self, req: OptimizeRequest, db: Optional[Session] = None) -> OptimizeResponse:
        # Check if Member 3's optimizer is available
        if self._member3_module is not None:
            try:
                raw_res = None
                if hasattr(self._member3_module, "optimize_dispatch"):
                    raw_res = self._member3_module.optimize_dispatch(req.model_dump())
                elif hasattr(self._member3_module, "optimize"):
                    raw_res = self._member3_module.optimize(req.model_dump())
                elif hasattr(self._member3_module, "run_milp_optimization"):
                    raw_res = self._member3_module.run_milp_optimization(req.model_dump())
                
                if raw_res is not None:
                    res_dict = raw_res.to_dict() if hasattr(raw_res, "to_dict") else dict(raw_res)
                    return await self._format_and_save_async(res_dict, req, db)
            except Exception as e:
                logger.warning(f"Member 3 optimizer execution error ({e}); using fallback solver.")

        # Integrated High-Fidelity Microgrid Merit-Order Dispatch
        result = self._solve_merit_order(req)
        return await self._format_and_save_async(result, req, db)

    def _solve_merit_order(self, req: OptimizeRequest) -> dict:
        demand = req.demand_kw
        solar_avail = req.solar_available_kw
        wind_avail = req.wind_available_kw
        battery_soc = req.battery_soc
        min_soc = req.min_soc
        diesel_avail = req.diesel_available

        # 1. Solar Dispatch (Zero marginal cost)
        solar_disp = min(solar_avail, demand)
        remaining = demand - solar_disp

        # 2. Wind Dispatch (Zero marginal cost)
        wind_disp = min(wind_avail, remaining)
        remaining -= wind_disp

        # 3. Battery Discharge (Stored renewable energy)
        battery_disp = 0.0
        if remaining > 0 and battery_soc > min_soc:
            # Maximum 15 kW discharge power limit or available stored kWh
            max_discharge = min(15.0, (battery_soc - min_soc) / 100.0 * req.battery_capacity_kwh)
            battery_disp = min(remaining, max_discharge)
            remaining -= battery_disp

        # 4. Diesel Generator Dispatch
        diesel_disp = 0.0
        if remaining > 0 and diesel_avail:
            # Generator rated up to 45 kW
            diesel_disp = min(remaining, 45.0)
            remaining -= diesel_disp

        unmet = max(0.0, remaining)
        total_supply = solar_disp + wind_disp + battery_disp + diesel_disp

        # Calculations
        renewable_pct = 0.0
        if total_supply > 0:
            renewable_pct = round(((solar_disp + wind_disp) / total_supply) * 100.0, 1)

        # Standard fuel burn rate 0.28 L / kWh
        fuel_burn = round(diesel_disp * 0.28, 1)
        cost = round(diesel_disp * (req.fuel_price / 65.0) + battery_disp * 0.05, 2)
        co2 = round(diesel_disp * 0.72, 1)
        reliability = 100.0 if unmet == 0 else round(max(0.0, (1.0 - unmet / max(1.0, demand)) * 100.0), 1)

        status = "optimal" if unmet == 0 else "suboptimal"

        return {
            "status": status,
            "solar_kw": round(solar_disp, 1),
            "wind_kw": round(wind_disp, 1),
            "battery_kw": round(battery_disp, 1),
            "diesel_kw": round(diesel_disp, 1),
            "total_supply_kw": round(total_supply, 1),
            "demand_kw": round(demand, 1),
            "unmet_demand_kw": round(unmet, 1),
            "renewable_percentage": renewable_pct,
            "cost_per_hour": cost,
            "fuel_burn_lh": fuel_burn,
            "co2_emissions_kgh": co2,
            "reliability_pct": reliability,
        }

    async def _format_and_save_async(
        self,
        data: dict,
        req: OptimizeRequest,
        db: Optional[Session]
    ) -> OptimizeResponse:
        dispatch_detail = DispatchDetail(
            solarKw=data["solar_kw"],
            windKw=data["wind_kw"],
            batteryKw=data["battery_kw"],
            dieselKw=data["diesel_kw"]
        )

        m_dict = data.get("metrics", {}) if isinstance(data.get("metrics"), dict) else {}
        cost_val = m_dict.get("estimatedCostPerHour", data.get("cost_per_hour", 4.25))
        fuel_val = m_dict.get("fuelConsumptionLitersHour", data.get("fuel_burn_lh", 0.0))
        co2_val = m_dict.get("co2EmissionsKgHour", data.get("co2_emissions_kgh", 0.0))
        rel_val = m_dict.get("reliabilityPercent", data.get("reliability_pct", 100.0))

        metrics_detail = MetricsDetail(
            totalGenerationKw=data["total_supply_kw"],
            unmetDemandKw=data["unmet_demand_kw"],
            renewablePercent=data["renewable_percentage"],
            estimatedCostPerHour=float(cost_val),
            fuelConsumptionLitersHour=float(fuel_val),
            co2EmissionsKgHour=float(co2_val),
            reliabilityPercent=float(rel_val)
        )

        response = OptimizeResponse(
            status=data["status"],
            solar_kw=data["solar_kw"],
            wind_kw=data["wind_kw"],
            battery_kw=data["battery_kw"],
            diesel_kw=data["diesel_kw"],
            total_supply_kw=data["total_supply_kw"],
            demand_kw=data["demand_kw"],
            unmet_demand_kw=data["unmet_demand_kw"],
            renewable_percentage=data["renewable_percentage"],
            dispatch=dispatch_detail,
            metrics=metrics_detail
        )

        # 1. Save to database
        if db:
            try:
                record = DispatchRecord(
                    timestamp=datetime.now(timezone.utc),
                    status=response.status,
                    solar_kw=response.solar_kw,
                    wind_kw=response.wind_kw,
                    battery_kw=response.battery_kw,
                    diesel_kw=response.diesel_kw,
                    total_supply_kw=response.total_supply_kw,
                    demand_kw=response.demand_kw,
                    unmet_demand_kw=response.unmet_demand_kw,
                    renewable_percentage=response.renewable_percentage,
                    cost_per_hour=metrics_detail.estimatedCostPerHour,
                    co2_avoided_kg=round(data["total_supply_kw"] * 0.5, 1),
                    reliability_pct=metrics_detail.reliabilityPercent
                )
                db.add(record)
                db.commit()
            except Exception as e:
                logger.warning(f"Failed to persist dispatch to database: {e}")
                db.rollback()

        # 2. Broadcast to WebSocket
        try:
            await ws_manager.broadcast_new_optimization(response.model_dump())
        except Exception as e:
            logger.warning(f"WebSocket broadcast error: {e}")

        return response


optimizer_service = OptimizerService()
