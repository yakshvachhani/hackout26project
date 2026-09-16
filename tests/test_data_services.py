"""
Comprehensive Test Suite for OPTIGRID-AI Data Engineering Services.
Validates:
- 96-timestep output (24h) and 192-timestep (48h)
- Bounds constraints: non-negative demand, solar <= capacity, wind <= rated capacity
- Monotonic 15-minute timestamps
- Weather resilience & Fallback hierarchy (LIVE -> CACHED -> FALLBACK)
- Fuel autonomy calculations & alert levels (NORMAL, WARNING, CRITICAL)
- What-If simulation reproducibility & metrics
- All 5 Hackathon demo scenario presets
- Member 2 and Member 3 integration payload structures
"""

import unittest
from datetime import datetime, timedelta, timezone

from data import (
    generate_village_load,
    generate_solar_profile,
    generate_wind_profile,
    wind_turbine_power_curve,
    BatteryStorage,
    BatteryConfig,
    calculate_fuel_autonomy,
    FuelAlertLevel,
    WeatherManager,
    WeatherSource,
    WeatherSnapshot,
    demand_forecaster,
    solar_forecaster,
    wind_forecaster,
    run_scenario,
    build_default_baseline_data,
    get_hackathon_demo_presets,
    get_mpc_inputs,
    get_api_forecast_payload,
    get_api_fuel_payload,
)


class TestDataServices(unittest.TestCase):

    def test_synthetic_load_resolution_and_bounds(self):
        """Test 24h (96 intervals) and 48h (192 intervals) synthetic load generation."""
        df_24 = generate_village_load(duration_hours=24, seed=42)
        self.assertEqual(len(df_24), 96, "24-hour load must have exactly 96 intervals")
        self.assertTrue((df_24["demand_kw"] >= 0).all(), "Demand must be strictly non-negative")
        self.assertTrue((df_24["p0_kw"] >= 0).all(), "P0 must be non-negative")
        self.assertTrue((df_24["p1_kw"] >= 0).all(), "P1 must be non-negative")
        self.assertTrue((df_24["p2_kw"] >= 0).all(), "P2 must be non-negative")

        # Sum of priorities should match total demand
        sum_p = df_24["p0_kw"] + df_24["p1_kw"] + df_24["p2_kw"]
        self.assertTrue(((sum_p - df_24["demand_kw"]).abs() < 0.1).all())

        # Test 48h
        df_48 = generate_village_load(duration_hours=48, seed=42)
        self.assertEqual(len(df_48), 192, "48-hour load must have exactly 192 intervals")

        # Verify monotonic timestamps with 15-min spacing
        dt_list = [datetime.fromisoformat(ts) for ts in df_24["timestamp"]]
        for i in range(1, len(dt_list)):
            diff = (dt_list[i] - dt_list[i - 1]).total_seconds()
            self.assertEqual(diff, 900.0, "Timestamps must be exactly 15 minutes apart")

    def test_synthetic_solar_bounds_and_diurnal_shape(self):
        """Test solar generation bounds, night zeroes, and peak cap."""
        cap = 50.0
        df_solar = generate_solar_profile(duration_hours=24, pv_capacity_kw=cap, seed=42)
        self.assertEqual(len(df_solar), 96)
        
        solar = df_solar["solar_available_kw"].to_numpy()
        self.assertTrue((solar >= 0.0).all(), "Solar generation must never be negative")
        self.assertTrue((solar <= cap).all(), "Solar generation must never exceed capacity")

        # Night generation check (midnight to 05:00 should be 0)
        night_intervals = df_solar[df_solar["time_str"].isin(["00:00", "01:00", "02:00", "03:00", "04:00"])]
        self.assertTrue((night_intervals["solar_available_kw"] == 0.0).all(), "Night solar must be zero")

        # Midday peak check (11:00 to 14:00 should be generating power)
        midday_intervals = df_solar[df_solar["time_str"].isin(["11:30", "12:00", "12:30", "13:00"])]
        self.assertTrue((midday_intervals["solar_available_kw"] > 10.0).all(), "Midday solar should have active generation")

    def test_synthetic_wind_turbine_curve(self):
        """Test wind power curve regions: cut-in, rated, and cut-out."""
        rated_cap = 30.0
        # Cut-in is 3.0, rated is 11.5, cut-out is 25.0
        self.assertEqual(wind_turbine_power_curve(1.5, rated_capacity_kw=rated_cap), 0.0)
        self.assertEqual(wind_turbine_power_curve(2.9, rated_capacity_kw=rated_cap), 0.0)
        
        # Mid-ramp
        mid_power = wind_turbine_power_curve(7.0, rated_capacity_kw=rated_cap)
        self.assertTrue(0.0 < mid_power < rated_cap)

        # At rated speed
        self.assertEqual(wind_turbine_power_curve(11.5, rated_capacity_kw=rated_cap), rated_cap)
        # Above rated speed but below cut-out
        self.assertEqual(wind_turbine_power_curve(15.0, rated_capacity_kw=rated_cap), rated_cap)
        # Above cut-out safety shutdown
        self.assertEqual(wind_turbine_power_curve(26.0, rated_capacity_kw=rated_cap), 0.0)

        df_wind = generate_wind_profile(duration_hours=24, rated_capacity_kw=rated_cap, seed=42)
        self.assertEqual(len(df_wind), 96)
        self.assertTrue((df_wind["wind_available_kw"] >= 0.0).all())
        self.assertTrue((df_wind["wind_available_kw"] <= rated_cap).all())

    def test_battery_storage_state_and_reserves(self):
        """Test battery charge, discharge, efficiency, and storm reserve mode."""
        b = BatteryStorage(BatteryConfig(capacity_kwh=100.0, initial_soc_pct=50.0, min_soc_pct=20.0))
        self.assertEqual(b.current_soc, 50.0)

        # Discharge 20 kW for 15 mins (5 kWh)
        power_out, new_soc = b.step(20.0, dt_hours=0.25)
        self.assertEqual(power_out, 20.0)
        self.assertTrue(new_soc < 50.0)

        # Storm mode: minimum reserve should increase
        b.set_storm_mode(True)
        self.assertEqual(b.get_effective_min_soc(), 40.0)

    def test_fuel_logistics_and_alert_thresholds(self):
        """Test fuel days remaining formula and alert thresholds: NORMAL, WARNING, CRITICAL."""
        # Case 1: >15 days -> NORMAL
        norm_res = calculate_fuel_autonomy(fuel_remaining_l=500.0, daily_burn_l=20.0)
        self.assertEqual(norm_res["days_remaining"], 25.0)
        self.assertEqual(norm_res["status"], FuelAlertLevel.NORMAL.value)
        self.assertIsNotNone(norm_res["depletion_date"])

        # Case 2: 7-15 days -> WARNING
        warn_res = calculate_fuel_autonomy(fuel_remaining_l=200.0, daily_burn_l=20.0)
        self.assertEqual(warn_res["days_remaining"], 10.0)
        self.assertEqual(warn_res["status"], FuelAlertLevel.WARNING.value)

        # Case 3: <7 days -> CRITICAL
        crit_res = calculate_fuel_autonomy(fuel_remaining_l=80.0, daily_burn_l=20.0)
        self.assertEqual(crit_res["days_remaining"], 4.0)
        self.assertEqual(crit_res["status"], FuelAlertLevel.CRITICAL.value)

    def test_weather_fallback_hierarchy(self):
        """Test that weather service gracefully recovers via fallback when endpoints fail."""
        wm = WeatherManager()
        # Retrieve forecast (either live if internet connected, or fallback)
        forecast = wm.get_forecast_15min(duration_hours=24)
        self.assertEqual(len(forecast.intervals), 96)
        self.assertIn(forecast.source, [WeatherSource.LIVE, WeatherSource.CACHED, WeatherSource.FALLBACK])

        # Force offline fallback simulation
        synthetic_fb = wm._generate_synthetic_fallback_forecast(duration_hours=24)
        self.assertEqual(synthetic_fb.source, WeatherSource.FALLBACK)
        self.assertEqual(len(synthetic_fb.intervals), 96)

    def test_forecasting_engines_96_timesteps(self):
        """Test that demand, solar, and wind forecasters produce strictly 96 values."""
        d_vals = demand_forecaster.forecast_96()
        self.assertEqual(len(d_vals), 96)
        self.assertTrue(all(v >= 0.0 for v in d_vals))

        # Solar forecast 96
        s_vals = solar_forecaster.forecast_96()
        self.assertEqual(len(s_vals), 96)
        self.assertTrue(all(0.0 <= v <= solar_forecaster.pv_capacity_kw for v in s_vals))

        # Wind forecast 96
        w_vals = wind_forecaster.forecast_96()
        self.assertEqual(len(w_vals), 96)
        self.assertTrue(all(0.0 <= v <= wind_forecaster.rated_capacity_kw for v in w_vals))

    def test_what_if_simulation_reproducibility_and_metrics(self):
        """Test run_scenario for Solar Failure, Demand Spike, and Diesel Unavailable."""
        # 1. Solar Failure scenario
        res_solar = run_scenario(scenario="SOLAR_FAILURE", severity=100.0, duration_hours=24)
        self.assertIn("before", res_solar)
        self.assertIn("after", res_solar)
        self.assertIn("metrics", res_solar)
        self.assertEqual(res_solar["after"]["solar_avg_kw"], 0.0, "100% solar failure must result in 0 solar kW")

        # 2. Demand Spike scenario
        res_spike = run_scenario(scenario="DEMAND_SPIKE", severity=50.0, duration_hours=24)
        self.assertTrue(res_spike["after"]["demand_avg_kw"] > res_spike["before"]["demand_avg_kw"])

        # 3. Diesel Unavailable scenario
        res_diesel = run_scenario(scenario="DIESEL_UNAVAILABLE", severity=100.0, duration_hours=24)
        self.assertEqual(res_diesel["after"]["diesel_avg_kw"], 0.0)
        self.assertEqual(res_diesel["metrics"]["diesel_fuel_liters"], 0.0)

        # Verify CO2 emission calculation estimate
        metrics = res_solar["metrics"]
        expected_co2 = round(metrics["diesel_fuel_liters"] * metrics["co2_emission_factor_kg_per_l"], 2)
        self.assertAlmostEqual(metrics["co2_emissions_kg"], expected_co2, places=1)

    def test_all_seven_crisis_scenarios(self):
        """Test all 7 crisis scenarios run without error and apply expected modifications."""
        scenarios = [
            ("SOLAR_FAILURE", 80.0, 24),
            ("WIND_FAILURE", 80.0, 24),
            ("BATTERY_LOW", 50.0, 24),
            ("DIESEL_UNAVAILABLE", 100.0, 24),
            ("DEMAND_SPIKE", 50.0, 24),
            ("STORM_48H", 85.0, 48),
            ("FUEL_PRICE_INCREASE", 100.0, 24),
        ]
        for sc, sev, dur in scenarios:
            res = run_scenario(scenario=sc, severity=sev, duration_hours=dur)
            self.assertIn("before", res)
            self.assertIn("after", res)
            self.assertIn("metrics", res)
            self.assertIn("deltas", res)
            self.assertTrue(res["metrics"]["total_demand_kwh"] > 0.0)

    def test_all_five_hackathon_demo_presets(self):
        """Test all 5 deterministic demo presets execute smoothly."""
        presets = get_hackathon_demo_presets()
        self.assertEqual(len(presets), 5)

        for key, config in presets.items():
            res = run_scenario(
                scenario=config["scenario"],
                severity=config["severity"],
                duration_hours=config["duration_hours"],
            )
            self.assertIsNotNone(res["metrics"])
            self.assertTrue(res["metrics"]["overall_reliability_pct"] >= 0.0)

    def test_member_2_and_3_integration_contracts(self):
        """Test Member 2 and Member 3 payload formats."""
        # Member 3 MPC inputs
        mpc_inputs = get_mpc_inputs(duration_hours=24)
        self.assertEqual(len(mpc_inputs["demand_forecast"]), 96)
        self.assertEqual(len(mpc_inputs["solar_forecast"]), 96)
        self.assertEqual(len(mpc_inputs["wind_forecast"]), 96)
        self.assertIn("battery", mpc_inputs)
        self.assertIn("diesel", mpc_inputs)

        # Member 2 API forecast payload
        api_forecast = get_api_forecast_payload(duration_hours=24)
        self.assertEqual(len(api_forecast), 96)
        first_item = api_forecast[0]
        self.assertIn("interval", first_item)
        self.assertIn("time", first_item)
        self.assertIn("demand_kw", first_item)
        self.assertIn("solar_kw", first_item)
        self.assertIn("wind_kw", first_item)

        # Member 2 API fuel payload
        api_fuel = get_api_fuel_payload(fuel_remaining_l=300.0, daily_burn_l=20.0)
        self.assertEqual(api_fuel["autonomy_days"], 15.0)
        self.assertEqual(api_fuel["alert_level"], FuelAlertLevel.WARNING.value)


if __name__ == "__main__":
    unittest.main()
