import sys
import os
import json
import numpy as np
import pandas as pd
import traceback

# Add project root to path
sys.path.insert(0, os.getcwd())

from models.predict import compute_shap_values, _safe_float
from pipeline.gold_layer import load_gold

def run_diagnostic():
    print("--- SHAP Error Diagnostic (Deep Scan) ---")
    
    # 1. Load Gold Data
    try:
        df_gold = load_gold()
        print(f"Gold layer loaded. Shape: {df_gold.shape}")
    except Exception as e:
        print(f"Error loading Gold layer: {e}")
        return

    # 2. Search for the specific problematic string in the entire dataframe
    target_str = '[3.0380392E-1,5.917197E-1,-1.0165954E-1,-7.93864E-1]'
    print(f"\nSearching for target string: {target_str}")
    found = False
    for col in df_gold.columns:
        # Check if any value is exactly this string or contains it
        mask = df_gold[col].apply(lambda x: str(x) == target_str)
        if mask.any():
            count = mask.sum()
            indices = df_gold.index[mask].tolist()
            players = df_gold.loc[indices, 'Player'].tolist() if 'Player' in df_gold.columns else []
            print(f"  FOUND in column '{col}': {count} occurrences.")
            print(f"  Players affected: {players[:5]}")
            found = True

    if not found:
        print("  Target string not found via exact match. Trying contains check...")
        for col in df_gold.columns:
            mask = df_gold[col].apply(lambda x: target_str in str(x))
            if mask.any():
                print(f"  FOUND (substring) in column '{col}'.")
                found = True

    # 3. Load Model Meta to get features
    meta_file = os.path.join("data", "pipeline", "models", "model_meta.json")
    if not os.path.exists(meta_file):
        print("Model metadata not found.")
        return
        
    with open(meta_file) as f:
        meta = json.load(f)
    
    feature_names = meta.get("feature_names", [])
    print(f"\nFeatures in meta: {len(feature_names)}")

    # 4. Check all players for SHAP failure
    print("\nTesting compute_shap_values for a sample of players...")
    success_count = 0
    fail_count = 0
    # Try first 20 players
    players_to_test = df_gold['Player'].unique()[:50] if 'Player' in df_gold.columns else []
    
    for p_name in players_to_test:
        try:
            # Silence stdout during compute_shap_values to avoid clutter
            orig_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            result = compute_shap_values(df_gold, p_name)
            sys.stdout = orig_stdout
            success_count += 1
        except Exception as e:
            sys.stdout = orig_stdout
            print(f"  FAILED for '{p_name}': {e}")
            fail_count += 1
            # Log the full traceback for the first failure
            if fail_count == 1:
                print("\nFull traceback for the first failure:")
                # We need to reach inside compute_shap_values to see the original exception
                # But compute_shap_values catches everything and re-raises as RuntimeError.
                # So we'll have to modify predict.py to NOT catch or to log better.
                pass

    print(f"\nSummary: Successes: {success_count}, Failures: {fail_count}")

if __name__ == "__main__":
    run_diagnostic()
