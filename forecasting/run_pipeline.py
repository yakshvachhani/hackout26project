"""End-to-end forecasting pipeline runner.

Executes:
1. Historical weather ingestion (Open-Meteo API + fallback)
2. Model training & candidate benchmarking (Persistence, PyTorch LSTM, XGBoost)
3. Model serialization to /forecasting/models/
4. High-resolution evaluation plotting to /forecasting/predicted_vs_actual.png
5. Standalone 48-hour forward forecast generation and validation
"""

import os
import sys
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from forecasting.config import MODELS_DIR, PLOT_PATH
from forecasting.plot_results import plot_predicted_vs_actual
from forecasting.predict import forecast
from forecasting.train_and_compare import run_model_training_and_benchmarking


def main():
    print("\n" + "#" * 80)
    print("#  DHRUVI FORECASTING PIPELINE: RENEWABLE GENERATION & DEMAND")
    print("#" * 80 + "\n")

    # Step 1 & 2: Ingestion, Candidate Benchmarks, Serialization
    print(">>> STEP 1 & 2: Ingesting data, training candidate models, and printing benchmark...")
    metadata = run_model_training_and_benchmarking(days=90)

    # Step 3: Plot results
    print("\n>>> STEP 3: Generating evaluation plot for pitch slides...")
    plot_file = plot_predicted_vs_actual(sample_hours=96, output_path=PLOT_PATH)
    print(f"Chart saved: {plot_file}")

    # Step 4: Standalone 48-hour forward forecast test
    print("\n>>> STEP 4: Executing standalone forecast(horizon_hours=48)...")
    results = forecast(horizon_hours=48)
    print(f"Successfully generated {len(results)} hours of forecast.\n")

    print(f"{'Hour':<5} | {'Timestamp':<20} | {'Solar (kW)':<11} | {'Wind (kW)':<11} | {'Demand (kW)':<11} | {'Solar Conf':<10} | {'Wind Conf':<10} | {'Weather'}")
    print("-" * 105)
    for i, r in enumerate(results):
        print(
            f"{i+1:<5} | "
            f"{r['timestamp'][:19]:<20} | "
            f"{r['solar_kw']:<11.2f} | "
            f"{r['wind_kw']:<11.2f} | "
            f"{r['demand_kw']:<11.2f} | "
            f"{r['solar_confidence']:<10.3f} | "
            f"{r['wind_confidence']:<10.3f} | "
            f"{r['weather_condition']}"
        )

    print("-" * 105)
    print("\n[SUCCESS] Pipeline completed successfully!")
    print(f"  - Serialized Models: {MODELS_DIR}")
    print(f"  - Evaluation Plot:   {PLOT_PATH}")
    print(f"  - Data Mode:         {metadata.get('data_mode')}")
    print(f"  - Solar Residual SD: {metadata.get('residuals', {}).get('solar_res_std', 0):.2f} kW")
    print(f"  - Wind Residual SD:  {metadata.get('residuals', {}).get('wind_res_std', 0):.2f} kW")


if __name__ == "__main__":
    main()
