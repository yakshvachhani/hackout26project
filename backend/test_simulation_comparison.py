import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_simulation_with_custom_slider_parameters():
    """Verify simulation responds with comparative metrics when given custom slider inputs."""
    payload = {
        "scenario": "SOLAR_FAILURE",
        "severity": 80,
        "durationHours": 24,
        "solarCapacityKw": 120.0,
        "batteryCapacityKwh": 250.0,
        "demandKw": 90.0,
        "rainProbability": 60.0,
        "gridPricePerKwh": 10.0,
        "optimizationMode": "balanced",
    }
    response = client.post("/api/simulation/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Legacy contract preservation
    assert data["scenario"] == "SOLAR_FAILURE"
    assert "before" in data
    assert "after" in data
    assert "impact" in data

    # Comparative structures
    assert "withoutOptimization" in data
    assert "withOptigrid" in data
    assert "comparison" in data
    assert "aiExplanation" in data
    assert "chartData" in data

    without_opt = data["withoutOptimization"]
    with_opt = data["withOptigrid"]
    comp = data["comparison"]

    assert without_opt is not None
    assert with_opt is not None
    assert "total_cost_inr" in without_opt
    assert "total_cost_inr" in with_opt
    assert "diesel_liters" in without_opt
    assert "diesel_liters" in with_opt
    assert "grid_usage_kwh" in without_opt
    assert "grid_usage_kwh" in with_opt
    assert "p0_reliability_pct" in with_opt

    # OptiGrid should provide savings or protect life-critical load
    assert "estimated_savings_inr" in comp
    assert len(data["chartData"]) == 5
    assert len(data["aiExplanation"]) > 50


def test_simulation_rain_impact():
    """Verify higher rain probability attenuates solar generation and increases costs."""
    payload_low_rain = {
        "scenario": "SOLAR_FAILURE",
        "severity": 40,
        "durationHours": 12,
        "rainProbability": 10.0,
    }
    res_low = client.post("/api/simulation/run", json=payload_low_rain).json()

    payload_high_rain = {
        "scenario": "SOLAR_FAILURE",
        "severity": 40,
        "durationHours": 12,
        "rainProbability": 90.0,
    }
    res_high = client.post("/api/simulation/run", json=payload_high_rain).json()

    # High rain should reduce renewable generation and increase total cost
    assert res_high["withoutOptimization"]["solar_usage_kwh"] < res_low["withoutOptimization"]["solar_usage_kwh"]
    assert res_high["withoutOptimization"]["total_cost_inr"] >= res_low["withoutOptimization"]["total_cost_inr"]


def test_simulation_optimization_modes():
    """Verify different optimization modes execute cleanly."""
    for mode in ["cost_saver", "green", "balanced"]:
        payload = {
            "scenario": "DEMAND_SPIKE",
            "severity": 50,
            "durationHours": 12,
            "optimizationMode": mode,
        }
        res = client.post("/api/simulation/run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["withOptigrid"]["p0_reliability_pct"] == 100.0
