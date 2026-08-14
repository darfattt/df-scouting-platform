"""
Silver Layer - Cleaned, normalized data with feature engineering
Reads Bronze, applies cleaning, derives per-90 features, computes rolling stats
"""

import os
import pandas as pd
import numpy as np
from typing import Optional


SILVER_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pipeline", "silver")
SILVER_FILE = os.path.join(SILVER_DIR, "players_silver.parquet")

# Features the ML model and Gold layer will rely on
ML_FEATURE_CANDIDATES = [
    "xG per 90",
    "Assists per 90",
    "xA per 90",
    "Shots per 90",
    "Dribbles per 90",
    "Key passes per 90",
    "Shot assists per 90",
    "Crosses per 90",
    "Progressive runs per 90",
    "Accelerations per 90",
    "Touches in box per 90",
    "Offensive duels per 90",
    "Smart passes per 90",
    "Deep completions per 90",
    "Aerial duels per 90",
    "Passes to penalty area per 90",
    # Defensive
    "Defensive duels won, %",
    "Aerial duels won, %",
    "Interceptions per 90",
    "Tackles per 90",
    # Passing
    "Accurate passes, %",
    "Progressive passes per 90",
]


def _safe_divide(numerator: pd.Series, denominator: pd.Series, default: float = 0.0) -> pd.Series:
    """Safe division, returns default when denominator is 0 or NaN."""
    return numerator.divide(denominator.replace(0, np.nan)).fillna(default)


def _derive_per90_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive per-90 metrics if raw counts + minutes are present but per-90 columns missing.
    Only generates columns that don't already exist.
    """
    df_copy = df.copy()
    minutes_col = "Minutes played"

    if minutes_col not in df_copy.columns:
        return df_copy

    minutes = df_copy[minutes_col].clip(lower=1)

    derivation_map = {
        "xG per 90": "xG",
        "Assists per 90": "Assists",
        "Shots per 90": "Shots",
        "Key passes per 90": "Key passes",
        "Crosses per 90": "Crosses",
        "Progressive runs per 90": "Progressive runs",
        "Accelerations per 90": "Accelerations",
        "Interceptions per 90": "Interceptions",
        "Tackles per 90": "Tackles",
        "Progressive passes per 90": "Progressive passes",
    }

    for per90_col, raw_col in derivation_map.items():
        if per90_col not in df_copy.columns and raw_col in df_copy.columns:
            df_copy[per90_col] = _safe_divide(df_copy[raw_col], minutes / 90)

    return df_copy


def _fill_missing_features(df: pd.DataFrame) -> pd.DataFrame:
    """Fill NaN in numeric feature columns with column median."""
    df_copy = df.copy()
    numeric_cols = df_copy.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        median_val = df_copy[col].median()
        df_copy[col] = df_copy[col].fillna(median_val if not np.isnan(median_val) else 0.0)
    return df_copy


def _add_rolling_approximation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Approximate rolling performance via League + Team grouping.
    Since we have cross-sectional (not time-series) data, we compute 
    within-team z-scores as a proxy for relative form.
    """
    df_copy = df.copy()

    feature_cols = [c for c in ML_FEATURE_CANDIDATES if c in df_copy.columns]
    if not feature_cols or "Team" not in df_copy.columns:
        return df_copy

    for col in feature_cols:
        rolling_col = f"{col}_team_zscore"
        team_mean = df_copy.groupby("Team")[col].transform("mean")
        team_std = df_copy.groupby("Team")[col].transform("std").replace(0, 1)
        df_copy[rolling_col] = ((df_copy[col] - team_mean) / team_std).fillna(0)

    return df_copy


def process_silver(df_bronze: pd.DataFrame) -> pd.DataFrame:
    """
    Transform Bronze data into Silver layer.
    Steps: clean types → derive features → fill NaN → add rolling proxy.

    Args:
        df_bronze: Raw DataFrame from Bronze layer

    Returns:
        Cleaned, feature-engineered DataFrame
    """
    df = df_bronze.copy()

    # Ensure numeric types for all stat columns
    skip_cols = {"Player", "Full name", "Team", "Position", "Primary position", "League",
                 "Birth country", "Passport country", "Foot", "Contract expires"}
    for col in df.columns:
        if col not in skip_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            except Exception:
                pass  # Keep column as-is if conversion fails entirely

    # Derive per-90 features if missing
    df = _derive_per90_features(df)

    # Fill missing values
    df = _fill_missing_features(df)

    # Add team-relative rolling proxy
    df = _add_rolling_approximation(df)

    return df


def save_silver(df: pd.DataFrame) -> dict:
    """
    Save Silver DataFrame to Parquet.

    Args:
        df: Silver-processed DataFrame

    Returns:
        dict with status, path, row_count
    """
    os.makedirs(SILVER_DIR, exist_ok=True)
    df.to_parquet(SILVER_FILE, index=False)
    return {
        "status": "success",
        "path": SILVER_FILE,
        "row_count": len(df),
        "col_count": len(df.columns),
    }


def get_silver_status() -> dict:
    """Get metadata about the Silver layer file."""
    if not os.path.exists(SILVER_FILE):
        return {"exists": False, "path": SILVER_FILE, "row_count": 0}
    try:
        df = pd.read_parquet(SILVER_FILE)
        mod_time = os.path.getmtime(SILVER_FILE)
        import datetime
        return {
            "exists": True,
            "path": SILVER_FILE,
            "row_count": len(df),
            "col_count": len(df.columns),
            "last_modified": datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        return {"exists": False, "path": SILVER_FILE, "error": str(e)}


def load_silver() -> pd.DataFrame:
    """
    Load Silver Parquet file.

    Raises:
        FileNotFoundError: If Silver layer not yet generated
    """
    if not os.path.exists(SILVER_FILE):
        raise FileNotFoundError("No Silver layer data. Run the pipeline first.")
    return pd.read_parquet(SILVER_FILE)
