import os
import sys
import pandas as pd

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pipeline.bronze_layer import load_latest_bronze
from pipeline.pipeline_runner import run_pipeline
from models.train import train_model

def main():
    print("🚀 Starting Maintenance Update...")
    
    # 1. Load latest raw data
    try:
        print("📥 Loading latest Bronze data...")
        df_raw = load_latest_bronze()
        print(f"✅ Loaded {len(df_raw)} players.")
    except Exception as e:
        print(f"❌ Error loading Bronze data: {e}")
        return

    # 2. Run Pipeline (Silver -> Gold)
    print("🥈🥉🥇 Running Pipeline (Silver -> Gold)...")
    results = run_pipeline(df_raw, progress_callback=lambda s, t, m: print(f"  [{s}/{t}] {m}"))
    
    if results["overall"] == "failed":
        print(f"❌ Pipeline failed: {results}")
        return
    print("✅ Pipeline complete.")

    # 3. Retrain Model
    try:
        print("🧠 Retraining XGBoost model with new features and tiers...")
        from pipeline.gold_layer import load_gold
        df_gold = load_gold()
        train_results = train_model(df_gold)
        print(f"✅ Model trained successfully (Accuracy: {train_results['accuracy']:.2f})")
        print(f"📝 Model path: {train_results['model_path']}")
    except Exception as e:
        print(f"❌ Error training model: {e}")
        import traceback
        traceback.print_exc()

    print("\n✨ Maintenance Update Finished!")

if __name__ == "__main__":
    main()
