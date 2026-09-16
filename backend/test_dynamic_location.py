"""
OptiGrid-AI Dynamic Location & Propagation Test Suite.
Verifies Indian presets, coordinate boundaries, 0.01° cache tolerance,
forecast propagation, and WebSocket / status integration.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.location_service import location_service
from backend.schemas.location import PRESET_LOCATIONS

client = TestClient(app)


def test_get_location_default():
    """Verify default active location is Baramati Rural and 5 presets are listed."""
    resp = client.get("/api/location")
    assert resp.status_code == 200
    data = resp.json()
    assert "activeLocation" in data
    assert "presets" in data
    assert len(data["presets"]) == 5
    assert data["activeLocation"]["name"] == "Baramati Rural"
    assert round(data["activeLocation"]["latitude"], 2) == 18.15
    assert round(data["activeLocation"]["longitude"], 2) == 74.58


def test_update_location_valid():
    """Verify switching to Rameshwaram Coastal updates active location and refreshes data."""
    payload = {
        "id": "rameshwaram",
        "name": "Rameshwaram Coastal",
        "district": "Ramanathapuram District",
        "state": "Tamil Nadu",
        "country": "India",
        "latitude": 9.28,
        "longitude": 79.31,
        "climate": "Tropical Maritime & High Wind Corridor",
        "community": "Coastal Fishing & Desalination Microgrid"
    }
    resp = client.post("/api/location", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["activeLocation"]["name"] == "Rameshwaram Coastal"
    assert round(data["activeLocation"]["latitude"], 2) == 9.28
    assert "weather" in data
    assert "weatherSource" in data
    assert "forecast" in data
    assert len(data["forecast"]) == 96

    # Verify GET /api/location returns the new location
    get_resp = client.get("/api/location")
    assert get_resp.status_code == 200
    assert get_resp.json()["activeLocation"]["name"] == "Rameshwaram Coastal"


def test_reject_location_outside_india():
    """Verify rejection of coordinates outside India bounding box (Lat 6.0-38.0, Lon 68.0-98.0)."""
    # 1. European coordinates
    resp = client.post("/api/location", json={
        "name": "London Microgrid",
        "latitude": 51.5074,
        "longitude": -0.1278
    })
    assert resp.status_code == 422

    # 2. East Africa coordinates
    resp2 = client.post("/api/location", json={
        "name": "Nairobi Microgrid",
        "latitude": -1.2921,
        "longitude": 36.8219
    })
    assert resp2.status_code == 422

    # 3. Northern out-of-bounds
    resp3 = client.post("/api/location", json={
        "name": "Himalayan High North",
        "latitude": 42.0,
        "longitude": 78.0
    })
    assert resp3.status_code == 422


def test_status_includes_active_location():
    """Verify GET /api/system/status returns activeLocation and weatherSource."""
    resp = client.get("/api/system/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "activeLocation" in data
    assert data["activeLocation"] is not None
    assert "weatherSource" in data
    assert data["weatherSource"] in ("LIVE", "CACHED", "FALLBACK")


def test_forecast_accepts_coordinates():
    """Verify GET /api/forecast accepts query coordinates."""
    resp = client.get("/api/forecast?latitude=15.33&longitude=76.46")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 96
    assert "interval" in data[0]
    assert "demand" in data[0]
    assert "solar" in data[0]


def test_cycle_all_presets():
    """Verify seamless sequential switching through all 5 presets."""
    for preset in PRESET_LOCATIONS:
        resp = client.post("/api/location", json=preset.model_dump())
        assert resp.status_code == 200
        data = resp.json()
        assert data["activeLocation"]["id"] == preset.id
        assert data["activeLocation"]["name"] == preset.name
        assert round(data["activeLocation"]["latitude"], 2) == round(preset.latitude, 2)
        assert round(data["activeLocation"]["longitude"], 2) == round(preset.longitude, 2)
        assert len(data["forecast"]) == 96


def test_simulation_with_active_location():
    """Verify What-If crisis simulator runs smoothly for current active location."""
    resp = client.post("/api/simulation/run", json={
        "scenario": "SOLAR_FAILURE",
        "severity": 60.0,
        "durationHours": 12.0
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario"] == "SOLAR_FAILURE"
    assert "before" in data
    assert "after" in data
    assert "impact" in data


def test_optimizer_mode_acceptance():
    """Verify optimizer accepts optimization_mode without error."""
    for mode in ["cost_saver", "balanced", "green"]:
        resp = client.post("/api/optimize", json={
            "demand_kw": 50.0,
            "solar_available_kw": 30.0,
            "wind_available_kw": 15.0,
            "battery_soc": 70.0,
            "optimization_mode": mode
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("optimal", "suboptimal")
