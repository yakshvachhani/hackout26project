import asyncio
import json
import httpx
import websockets

BASE_URL = "http://127.0.0.1:8000/api"
WS_URL = "ws://127.0.0.1:8000/ws"


async def main():
    print("Testing live HTTP endpoints against running Uvicorn server...")
    async with httpx.AsyncClient(timeout=5.0) as client:
        # 1. Health
        r = await client.get(f"{BASE_URL}/health")
        assert r.status_code == 200, f"Health failed: {r.status_code}"
        print("  [OK] GET /api/health ->", r.json())

        # 2. System Status
        r = await client.get(f"{BASE_URL}/system/status")
        assert r.status_code == 200, f"Status failed: {r.status_code}"
        data = r.json()
        print("  [OK] GET /api/system/status -> demand:", data["demand_kw"], "solar:", data["solar_kw"], "status:", data["system_status"])

        # 3. Forecast
        r = await client.get(f"{BASE_URL}/forecast")
        assert r.status_code == 200
        intervals = r.json()
        assert len(intervals) == 96
        print("  [OK] GET /api/forecast -> 96 intervals verified")

        # 4. Battery
        r = await client.get(f"{BASE_URL}/battery")
        assert r.status_code == 200
        print("  [OK] GET /api/battery -> SOC:", r.json()["currentSocPercent"], "%")

        # 5. Fuel
        r = await client.get(f"{BASE_URL}/fuel")
        assert r.status_code == 200
        print("  [OK] GET /api/fuel -> Remaining:", r.json()["fuelRemainingLiters"], "L, Days:", r.json()["daysRemaining"])

        # 6. Loads
        r = await client.get(f"{BASE_URL}/loads")
        assert r.status_code == 200
        print("  [OK] GET /api/loads -> Total:", r.json()["totalDemandKw"], "kW")

        # 7. Optimize
        opt_payload = {
            "demand_kw": 50,
            "solar_available_kw": 30,
            "wind_available_kw": 15,
            "battery_soc": 70,
            "battery_capacity_kwh": 100,
            "diesel_available": True,
            "fuel_price": 95
        }
        r = await client.post(f"{BASE_URL}/optimize", json=opt_payload)
        assert r.status_code == 200
        res = r.json()
        print("  [OK] POST /api/optimize -> Status:", res["status"], "Solar:", res["solar_kw"], "Wind:", res["wind_kw"], "Battery:", res["battery_kw"], "Diesel:", res["diesel_kw"])

        # 8. Simulation
        sim_payload = {
            "scenario": "STORM_48H",
            "severity": 90,
            "durationHours": 48
        }
        r = await client.post(f"{BASE_URL}/simulation/run", json=sim_payload)
        assert r.status_code == 200
        print("  [OK] POST /api/simulation/run (STORM_48H) -> Impact:", r.json()["impact"])

        # 9. Alerts
        r = await client.get(f"{BASE_URL}/alerts")
        assert r.status_code == 200
        print("  [OK] GET /api/alerts -> Total alerts:", len(r.json()))

    # 10. Live WebSocket Telemetry Test
    print("\nTesting live WebSocket telemetry stream...")
    async with websockets.connect(WS_URL) as ws:
        print("  [OK] Connected to", WS_URL)
        # Wait for a broadcast event from background telemetry task
        msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
        event = json.loads(msg)
        print("  [OK] Received WebSocket Event:", event["type"], "->", event.get("data", {}))

    print("\nALL LIVE SERVER TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    asyncio.run(main())
