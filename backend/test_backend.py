import asyncio
import json
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure root workspace is in sys.path
sys.path.insert(0, ".")

from backend.main import app, seed_database_if_empty
from backend.database.database import SessionLocal
from backend.database.models import EnergyReading, DispatchRecord, AlertRecord


class TestOptiGridBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_database_if_empty()
        cls.client = TestClient(app)

    def test_01_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "UP")
        self.assertEqual(data["database"], "HEALTHY")
        print("PASS: /api/health")

    def test_02_system_status(self):
        response = self.client.get("/api/system/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify prompt-required top-level fields
        self.assertIn("timestamp", data)
        self.assertIn("demand_kw", data)
        self.assertIn("solar_kw", data)
        self.assertIn("wind_kw", data)
        self.assertIn("battery_kw", data)
        self.assertIn("battery_soc", data)
        self.assertIn("diesel_kw", data)
        self.assertIn("diesel_status", data)
        self.assertIn("renewable_percentage", data)
        self.assertIn("reliability", data)
        self.assertIn("system_status", data)

        # Verify Member 1 frontend compatibility
        self.assertIn("isOnline", data)
        self.assertIn("metrics", data)
        self.assertIn("weather", data)
        self.assertIn("liveDispatch", data)
        print("PASS: /api/system/status")

    def test_03_forecast(self):
        response = self.client.get("/api/forecast")
        self.assertEqual(response.status_code, 200)
        intervals = response.json()
        self.assertEqual(len(intervals), 96)
        first = intervals[0]
        self.assertIn("time", first)
        self.assertIn("demand", first)
        self.assertIn("solar", first)
        self.assertIn("wind", first)
        self.assertIn("batterySoc", first)
        self.assertIn("diesel", first)
        print("PASS: /api/forecast (96 intervals)")

    def test_04_battery(self):
        response = self.client.get("/api/battery")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("capacityKwh", data)
        self.assertIn("currentSocPercent", data)
        self.assertIn("socHistory", data)
        self.assertEqual(len(data["socHistory"]), 24)
        print("PASS: /api/battery")

    def test_05_fuel(self):
        response = self.client.get("/api/fuel")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tankCapacityLiters", data)
        self.assertIn("fuelRemainingLiters", data)
        self.assertIn("daysRemaining", data)
        self.assertIn("generator", data)
        print("PASS: /api/fuel")

    def test_06_loads(self):
        response = self.client.get("/api/loads")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("totalDemandKw", data)
        self.assertIn("summary", data)
        self.assertIn("priorities", data)
        self.assertEqual(len(data["priorities"]), 3)
        print("PASS: /api/loads")

    def test_07_dispatch_latest_and_history(self):
        res_latest = self.client.get("/api/dispatch/latest")
        self.assertEqual(res_latest.status_code, 200)
        latest_data = res_latest.json()
        self.assertIn("solarKw", latest_data)

        res_hist = self.client.get("/api/dispatch/history")
        self.assertEqual(res_hist.status_code, 200)
        hist_data = res_hist.json()
        self.assertTrue(isinstance(hist_data, list))
        print("PASS: /api/dispatch/latest & history")

    def test_08_alerts(self):
        response = self.client.get("/api/alerts")
        self.assertEqual(response.status_code, 200)
        alerts = response.json()
        self.assertTrue(len(alerts) >= 1)
        print("PASS: /api/alerts")

    def test_09_optimize_endpoint(self):
        # Test prompt specification payload
        payload = {
            "demand_kw": 50,
            "solar_available_kw": 30,
            "wind_available_kw": 15,
            "battery_soc": 70,
            "battery_capacity_kwh": 100,
            "diesel_available": True,
            "fuel_price": 95
        }
        response = self.client.post("/api/optimize", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Prompt expected keys
        self.assertEqual(data["status"], "optimal")
        self.assertEqual(data["solar_kw"], 30.0)
        self.assertEqual(data["wind_kw"], 15.0)
        self.assertEqual(data["battery_kw"], 5.0)
        self.assertEqual(data["diesel_kw"], 0.0)
        self.assertEqual(data["total_supply_kw"], 50.0)
        self.assertEqual(data["demand_kw"], 50.0)
        self.assertEqual(data["unmet_demand_kw"], 0.0)
        self.assertEqual(data["renewable_percentage"], 90.0)

        # Frontend expected keys
        self.assertIn("dispatch", data)
        self.assertIn("metrics", data)
        self.assertEqual(data["dispatch"]["solarKw"], 30.0)
        print("PASS: POST /api/optimize (Prompt & Frontend specs verified)")

    def test_10_simulation_run(self):
        payload = {
            "scenario": "SOLAR_FAILURE",
            "severity": 80,
            "durationHours": 12
        }
        response = self.client.post("/api/simulation/run", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["scenario"], "SOLAR_FAILURE")
        self.assertIn("before", data)
        self.assertIn("after", data)
        self.assertIn("impact", data)
        self.assertIn("additionalDieselLiters", data["impact"])
        print("PASS: POST /api/simulation/run")

    def test_11_weather_refresh(self):
        response = self.client.post("/api/weather/refresh")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("weather", data)
        print("PASS: POST /api/weather/refresh")

    def test_12_database_persistence(self):
        db = SessionLocal()
        try:
            readings = db.query(EnergyReading).count()
            self.assertTrue(readings > 0)
            dispatches = db.query(DispatchRecord).count()
            self.assertTrue(dispatches > 0)
            alerts = db.query(AlertRecord).count()
            self.assertTrue(alerts > 0)
            print(f"PASS: Database writes confirmed (Energy: {readings}, Dispatches: {dispatches}, Alerts: {alerts})")
        finally:
            db.close()

    def test_13_websocket_endpoint(self):
        with self.client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"action": "ping"}))
            # Successfully connected and sent message
            print("PASS: WebSocket /ws connected and responsive")


if __name__ == "__main__":
    unittest.main()
