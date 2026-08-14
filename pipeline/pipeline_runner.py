"""
Pipeline Runner - Orchestrates Bronze -> Silver -> Gold transformation
"""

import traceback
from typing import Optional
import pandas as pd

from pipeline.bronze_layer import save_bronze, get_latest_bronze
from pipeline.silver_layer import process_silver, save_silver, get_silver_status, load_silver
from pipeline.gold_layer import process_gold, save_gold, get_gold_status


def get_pipeline_status() -> dict:
    """
    Get current status of all pipeline layers.

    Returns:
        dict with bronze, silver, gold status dicts
    """
    bronze = get_latest_bronze()
    silver = get_silver_status()
    gold = get_gold_status()
    return {"bronze": bronze, "silver": silver, "gold": gold}


def run_pipeline(df_raw: pd.DataFrame, progress_callback=None) -> dict:
    """
    Run full Bronze -> Silver -> Gold pipeline from a raw DataFrame.

    Args:
        df_raw: Raw filtered player DataFrame (from app.py / data_manager)
        progress_callback: Optional callable(step: int, total: int, message: str)

    Returns:
        dict with overall status and per-layer results
    """
    results = {"overall": "success", "steps": {}}
    total_steps = 3

    def _progress(step: int, msg: str):
        if progress_callback:
            progress_callback(step, total_steps, msg)

    # ── Step 1: Bronze ────────────────────────────────────────────────────────
    try:
        _progress(1, "📦 Saving Bronze layer (raw snapshot)...")
        bronze_result = save_bronze(df_raw)
        results["steps"]["bronze"] = bronze_result
    except Exception as e:
        results["overall"] = "failed"
        results["steps"]["bronze"] = {"status": "error", "error": str(e), "trace": traceback.format_exc()}
        return results

    # ── Step 2: Silver ────────────────────────────────────────────────────────
    try:
        _progress(2, "🥈 Processing Silver layer (feature engineering)...")
        df_bronze = pd.read_parquet(bronze_result["path"])
        df_silver = process_silver(df_bronze)
        silver_result = save_silver(df_silver)
        results["steps"]["silver"] = silver_result
    except Exception as e:
        results["overall"] = "failed"
        results["steps"]["silver"] = {"status": "error", "error": str(e), "trace": traceback.format_exc()}
        return results

    # ── Step 3: Gold ──────────────────────────────────────────────────────────
    try:
        _progress(3, "🥇 Building Gold layer (tiers & aggregations)...")
        df_gold = process_gold(df_silver)
        gold_result = save_gold(df_gold)
        results["steps"]["gold"] = gold_result
    except Exception as e:
        results["overall"] = "failed"
        results["steps"]["gold"] = {"status": "error", "error": str(e), "trace": traceback.format_exc()}
        return results

    _progress(3, "✅ Pipeline complete!")
    return results
