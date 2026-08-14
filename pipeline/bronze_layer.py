"""
Bronze Layer - Raw data snapshot
Saves the current filtered DataFrame as immutable Parquet (raw, unprocessed)
"""

import os
import pandas as pd
from datetime import datetime


BRONZE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pipeline", "bronze")


def save_bronze(df: pd.DataFrame) -> dict:
    """
    Save raw DataFrame snapshot to Bronze Parquet layer.
    Files are partitioned by timestamp (immutable, append-only).

    Args:
        df: Raw filtered player DataFrame from Wyscout CSV

    Returns:
        dict with status, path, row_count, timestamp
    """
    os.makedirs(BRONZE_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"players_raw_{timestamp}.parquet"
    filepath = os.path.join(BRONZE_DIR, filename)

    # Save as-is — no transformation in Bronze
    df_copy = df.copy()
    df_copy.to_parquet(filepath, index=False)

    return {
        "status": "success",
        "path": filepath,
        "filename": filename,
        "row_count": len(df_copy),
        "col_count": len(df_copy.columns),
        "timestamp": timestamp,
    }


def get_latest_bronze() -> dict:
    """
    Get metadata about the latest Bronze Parquet file.

    Returns:
        dict with exists, path, row_count, timestamp
    """
    if not os.path.exists(BRONZE_DIR):
        return {"exists": False, "path": None, "row_count": 0, "timestamp": None}

    parquet_files = sorted(
        [f for f in os.listdir(BRONZE_DIR) if f.endswith(".parquet")],
        reverse=True,
    )

    if not parquet_files:
        return {"exists": False, "path": None, "row_count": 0, "timestamp": None}

    latest = parquet_files[0]
    filepath = os.path.join(BRONZE_DIR, latest)

    try:
        df = pd.read_parquet(filepath)
        return {
            "exists": True,
            "path": filepath,
            "filename": latest,
            "row_count": len(df),
            "col_count": len(df.columns),
            "timestamp": latest.replace("players_raw_", "").replace(".parquet", ""),
        }
    except Exception as e:
        return {"exists": False, "path": None, "row_count": 0, "error": str(e)}


def load_latest_bronze() -> pd.DataFrame:
    """
    Load the latest Bronze Parquet file.

    Returns:
        DataFrame with raw player data

    Raises:
        FileNotFoundError: If no Bronze files exist
    """
    meta = get_latest_bronze()
    if not meta["exists"]:
        raise FileNotFoundError("No Bronze layer data found. Run the pipeline first.")
    return pd.read_parquet(meta["path"])
