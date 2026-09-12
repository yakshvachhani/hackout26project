import pytest
from fastapi.testclient import TestClient
from main import app
from mock_data import generate_forecast, generate_dispatch

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_invalid_hours():
    response = client.get("/forecast?hours=-5")
    assert response.status_code == 400
    assert "positive integer" in response.json()["detail"]
    
    response = client.get("/forecast?hours=0")
    assert response.status_code == 400

def test_demand_never_negative():
    forecast = generate_forecast(hours=100)
    for record in forecast:
        assert record["demand_kw"] >= 0

def test_soc_bounds():
    # High demand scenario to try and drain the battery
    forecast = generate_forecast(hours=200, demand_multiplier=5.0)
    dispatch = generate_dispatch(forecast, battery_capacity_kwh=100, diesel_capacity_kw=0, start_soc=50.0)
    for record in dispatch:
        assert 0.0 <= record["battery_soc_percent"] <= 100.0

    # Low demand scenario to try and overfill the battery
    forecast2 = generate_forecast(hours=200, demand_multiplier=0.1)
    dispatch2 = generate_dispatch(forecast2, battery_capacity_kwh=100, diesel_capacity_kw=0, start_soc=50.0)
    for record in dispatch2:
        assert 0.0 <= record["battery_soc_percent"] <= 100.0
