import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import SimulationRecord
from backend.schemas.simulation import SimulationRequest, SimulationResponse, SimulationImpact

router = APIRouter(tags=["Crisis What-If Simulator"])


@router.post("/simulation/run", response_model=SimulationResponse)
async def run_simulation(req: SimulationRequest, db: Session = Depends(get_db)):
    """Simulates grid crisis scenarios (outages, storm, fuel exhaustion, demand surge)."""
    try:
        sev_multiplier = (req.severity or 50.0) / 100.0
        duration = req.durationHours or 12.0

        # 1. Attempt Member 4 What-If Microgrid Simulation Engine with active location & parameters
        sim_data = None
        try:
            from data import run_simulation_api
            from backend.services.location_service import location_service
            loc = location_service.get_active_location()
            lat = req.latitude if req.latitude is not None else (loc.latitude if loc else None)
            lon = req.longitude if req.longitude is not None else (loc.longitude if loc else None)
            loc_name = loc.name if loc else "Baramati Rural"

            sim_data = run_simulation_api(
                scenario=req.scenario,
                severity=req.severity,
                duration_hours=req.durationHours,
                latitude=lat,
                longitude=lon,
                solar_capacity_kw=req.solar_capacity_kw,
                battery_capacity_kwh=req.battery_capacity_kwh,
                demand_kw=req.demand_kw,
                rain_probability=req.rain_probability,
                grid_price_per_kwh=req.grid_price_per_kwh,
                optimization_mode=req.optimization_mode,
                location_name=loc_name,
            )
        except Exception as e:
            try:
                from data.simulation.simulator import run_scenario
                sim_data = run_scenario(
                    scenario=req.scenario,
                    severity=req.severity,
                    duration_hours=req.durationHours,
                    solar_capacity_kw=req.solar_capacity_kw,
                    battery_capacity_kwh=req.battery_capacity_kwh,
                    demand_kw=req.demand_kw,
                    rain_probability=req.rain_probability,
                    grid_price_per_kwh=req.grid_price_per_kwh,
                    optimization_mode=req.optimization_mode,
                )
            except Exception:
                pass

        without_opt = None
        with_opt = None
        comparison = None
        ai_explanation = None
        chart_data = None

        if sim_data:
            before = {
                "solar": round(float(sim_data["before"]["solar_avg_kw"]), 1),
                "wind": round(float(sim_data["before"]["wind_avg_kw"]), 1),
                "battery": round(float(sim_data["before"]["battery_soc_end"]), 1),
                "diesel": round(float(sim_data["before"]["diesel_avg_kw"]), 1),
                "demand": round(float(sim_data["before"]["demand_avg_kw"]), 1),
            }
            after = {
                "solar": round(float(sim_data["after"]["solar_avg_kw"]), 1),
                "wind": round(float(sim_data["after"]["wind_avg_kw"]), 1),
                "battery": round(float(sim_data["after"]["battery_soc_end"]), 1),
                "diesel": round(float(sim_data["after"]["diesel_avg_kw"]), 1),
                "demand": round(float(sim_data["after"]["demand_avg_kw"]), 1),
            }
            p0 = round(float(sim_data["metrics"]["p0_served_pct"]), 1)
            p1 = round(float(sim_data["metrics"]["p1_served_pct"]), 1)
            p2 = round(float(sim_data["metrics"]["p2_served_pct"]), 1)
            add_diesel = round(float(sim_data["deltas"]["additional_diesel_liters"]), 1)
            add_co2 = round(float(sim_data["deltas"]["additional_co2_kg"]), 1)
            cost_diff = f"{float(sim_data['deltas']['cost_difference_dollars']):.2f}"

            without_opt = sim_data.get("without_optimization")
            with_opt = sim_data.get("with_optigrid")
            comparison = sim_data.get("comparison")
            ai_explanation = sim_data.get("ai_explanation")
            chart_data = sim_data.get("chart_data")
        else:
            # 2. Fallback Rule-Based Crisis Model
            before = {"solar": 30.0, "wind": 15.0, "battery": 5.0, "diesel": 0.0, "demand": 50.0}
            after = dict(before)

            p0 = 100.0
            p1 = 92.0
            p2 = 61.0
            add_diesel = 0.0
            add_co2 = 0.0
            cost_diff = "0.00"

            sc = req.scenario.upper()

            if sc == "SOLAR_FAILURE":
                after["solar"] = round(before["solar"] * (1.0 - sev_multiplier), 1)
                delta = before["solar"] - after["solar"]
                after["diesel"] = round(delta * 0.8, 1)
                after["battery"] = round(before["battery"] + delta * 0.2, 1)
                p2 = max(0.0, 61.0 - round(sev_multiplier * 50.0))
                p1 = max(40.0, 92.0 - round(sev_multiplier * 20.0))
                add_diesel = round(after["diesel"] * duration * 0.28, 1)
                add_co2 = round(add_diesel * 2.68, 1)
                cost_diff = f"{round(add_diesel * 1.50, 2):.2f}"

            elif sc == "WIND_FAILURE":
                after["wind"] = round(before["wind"] * (1.0 - sev_multiplier), 1)
                delta = before["wind"] - after["wind"]
                after["diesel"] = round(delta * 0.7, 1)
                p2 = max(20.0, 61.0 - round(sev_multiplier * 30.0))
                add_diesel = round(after["diesel"] * duration * 0.28, 1)
                add_co2 = round(add_diesel * 2.68, 1)
                cost_diff = f"{round(add_diesel * 1.50, 2):.2f}"

            elif sc == "BATTERY_LOW":
                after["battery"] = 0.0
                after["diesel"] = round(before["battery"], 1)
                p2 = 45.0
                add_diesel = round(after["diesel"] * duration * 0.28, 1)
                add_co2 = round(add_diesel * 2.68, 1)
                cost_diff = f"{round(add_diesel * 1.50, 2):.2f}"

            elif sc == "DIESEL_UNAVAILABLE":
                after["diesel"] = 0.0
                p2 = 0.0
                p1 = max(10.0, 92.0 - round(sev_multiplier * 60.0))
                p0 = 95.0 if sev_multiplier > 0.8 else 100.0
                add_diesel = 0.0
                add_co2 = 0.0
                cost_diff = "-45.00"

            elif sc == "DEMAND_SPIKE":
                after["demand"] = round(before["demand"] * (1.0 + sev_multiplier * 0.5), 1)
                spike = after["demand"] - before["demand"]
                after["diesel"] = round(spike * 0.9, 1)
                p2 = 30.0
                add_diesel = round(after["diesel"] * duration * 0.28, 1)
                add_co2 = round(add_diesel * 2.68, 1)
                cost_diff = f"{round(add_diesel * 1.50, 2):.2f}"

            elif sc == "STORM_48H":
                after["solar"] = 2.0
                after["wind"] = 22.0
                after["diesel"] = 18.0
                after["battery"] = 8.0
                p2 = 15.0
                p1 = 70.0
                add_diesel = round(18.0 * duration * 0.28, 1)
                add_co2 = round(add_diesel * 2.68, 1)
                cost_diff = f"{round(add_diesel * 1.50, 2):.2f}"

            elif sc == "FUEL_PRICE_INCREASE":
                cost_diff = f"{round(45.0 * sev_multiplier * duration, 2):.2f}"

        impact = SimulationImpact(
            p0ReliabilityPercent=p0,
            p1ServedPercent=p1,
            p2ServedPercent=p2,
            additionalDieselLiters=add_diesel,
            additionalCo2Kg=add_co2,
            costDifferenceDollars=cost_diff
        )

        res = SimulationResponse(
            scenario=req.scenario,
            severity=req.severity,
            durationHours=req.durationHours,
            before=before,
            after=after,
            impact=impact,
            withoutOptimization=without_opt,
            withOptigrid=with_opt,
            comparison=comparison,
            aiExplanation=ai_explanation,
            chartData=chart_data,
        )

        # Save to database
        try:
            record = SimulationRecord(
                timestamp=datetime.now(timezone.utc),
                scenario=req.scenario,
                severity=req.severity,
                duration_hours=req.durationHours,
                p0_reliability_pct=p0,
                p1_served_pct=p1,
                p2_served_pct=p2,
                extra_diesel_liters=float(add_diesel),
                extra_co2_kg=float(add_co2),
                cost_diff_dollars=float(cost_diff),
                details_json=json.dumps(res.model_dump())
            )
            db.add(record)
            db.commit()
        except Exception as e:
            db.rollback()

        return res

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
