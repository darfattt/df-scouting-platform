import sys
import os
import json
import xgboost as xgb
import shap

# Add project root to path
sys.path.insert(0, os.getcwd())

from models.predict import _load_model

def debug_booster():
    print("--- Booster Attribute Debug ---")
    model = _load_model()
    booster = model.get_booster()
    
    print(f"Model type: {type(model)}")
    print(f"Booster type: {type(booster)}")
    
    # Check attributes
    attrs = booster.attributes()
    print(f"Attributes: {attrs}")
    
    base_score = booster.attr("base_score")
    print(f"booster.attr('base_score'): {repr(base_score)}")
    
    # Check if it fails __init__
    print("\nTesting shap.TreeExplainer(model)...")
    try:
        explainer = shap.TreeExplainer(model)
        print("Success!")
    except Exception as e:
        print(f"FAILED: {e}")
        
    print("\nTesting shap.TreeExplainer(booster)...")
    try:
        explainer = shap.TreeExplainer(booster)
        print("Success!")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    debug_booster()
