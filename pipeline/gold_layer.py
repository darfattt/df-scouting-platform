"""
Gold Layer - Aggregated data with performance tiers and cross-position percentiles
Reads Silver, assigns Elite/Good/Average/Below Average tiers based on composite scoring
"""

import os
import pandas as pd
import numpy as np
from typing import List, Optional, Dict
import datetime

from config.position_groups import POSITION_GROUPS


GOLD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pipeline", "gold")
GOLD_FILE = os.path.join(GOLD_DIR, "players_gold.parquet")

# Tier thresholds (percentile-based)
TIER_THRESHOLDS = {
    "Elite": 90,       # top 10%
    "Good": 70,        # top 10–30%
    "Average": 30,     # 30–70%
    "Below Average": 0,  # bottom 30%
}

# Default features (legacy support)
SCORING_FEATURES = [
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
]

# Position-specific scoring features
POSITION_GROUP_FEATURES: Dict[str, List[str]] = {
    "CB": [
        "Defensive duels won, %", "Interceptions per 90", "Aerial duels won, %",
        "Successful defensive actions per 90", "Accurate passes, %", "Progressive passes per 90"
    ],
    "Fullback": [
        "Progressive runs per 90", "Crosses per 90", "Accurate crosses, %",
        "Successful defensive actions per 90", "Interceptions per 90", "Defensive duels won, %"
    ],
    "Defender": [
        "Defensive duels won, %", "Interceptions per 90", "Aerial duels won, %",
        "Successful defensive actions per 90", "Accurate passes, %", "Progressive runs per 90"
    ],
    "DM": [
        "Defensive duels per 90", "Interceptions per 90", "Duels won, %",
        "Accurate passes, %", "Progressive passes per 90", "Passes per 90"
    ],
    "Midfielder": [
        "Passes per 90", "Accurate passes, %", "Progressive passes per 90",
        "Interceptions per 90", "Duels won, %", "xA per 90"
    ],
    "AM": [
        "xA per 90", "Key passes per 90", "Smart passes per 90",
        "Shot assists per 90", "Dribbles per 90", "Progressive runs per 90"
    ],
    "Winger": [
        "Dribbles per 90", "Successful dribbles, %", "Crosses per 90",
        "Progressive runs per 90", "xA per 90", "Touches in box per 90"
    ],
    "Forward": [
        "xG per 90", "Shots per 90", "Touches in box per 90",
        "Dribbles per 90", "Assists per 90", "xA per 90"
    ],
    "CF": [
        "xG per 90", "Shots per 90", "Touches in box per 90",
        "Goal conversion, %", "Aerial duels won, %", "Non-penalty goals per 90"
    ]
}

TIER_ORDER = ["Elite", "Good", "Average", "Below Average"]
from styles.design_system import TIER_COLORS  # noqa: F401


def _get_position_group(pos: str) -> str:
    """Determine position group for a given primary position string."""
    if not isinstance(pos, str): return "Forward"
    # Specific check for CF to avoid picking Forward group first if it includes CF
    if pos == "CF": return "CF"
    
    for group, members in POSITION_GROUPS.items():
        if members and pos in members:
            # Prefer more specific groups (CB, DM, etc) over generic 'Defender' or 'Midfielder'
            if group in ["CB", "Fullback", "DM", "AM", "Winger", "CF"]:
                return group
    
    # Fallback to broader groups
    for group, members in POSITION_GROUPS.items():
        if members and pos in members:
            return group
            
    return "Forward"


def _compute_composite_score(df: pd.DataFrame) -> pd.Series:
    """
    Compute composite score as mean of cross-sectional percentile ranks
    using position-specific feature sets.

    Args:
        df: Silver DataFrame

    Returns:
        Series of composite scores (0–100)
    """
    # Get all unique features across all groups
    all_features = set()
    for features in POSITION_GROUP_FEATURES.values():
        all_features.update(features)
    all_features.update(SCORING_FEATURES)
    
    available_all = [f for f in all_features if f in df.columns]
    if not available_all:
        return pd.Series(50.0, index=df.index)

    # Compute global percentiles for all available features once
    percentile_df = pd.DataFrame(index=df.index)
    for col in available_all:
        col_data = pd.to_numeric(df[col], errors="coerce")
        percentile_df[col] = col_data.rank(pct=True) * 100

    # Map each row to its position group and calculate mean of its specific features
    composite_scores = []
    for idx, row in df.iterrows():
        pos = row.get("Primary position", "CF")
        group = _get_position_group(pos)
        features = POSITION_GROUP_FEATURES.get(group, SCORING_FEATURES)
        
        row_available = [f for f in features if f in percentile_df.columns]
        if not row_available:
            composite_scores.append(50.0)
        else:
            composite_scores.append(percentile_df.loc[idx, row_available].mean())

    return pd.Series(composite_scores, index=df.index).fillna(50.0)


def _assign_tier(score: float) -> str:
    """Assign performance tier based on composite score percentile."""
    if score >= TIER_THRESHOLDS["Elite"]:
        return "Elite"
    elif score >= TIER_THRESHOLDS["Good"]:
        return "Good"
    elif score >= TIER_THRESHOLDS["Average"]:
        return "Average"
    else:
        return "Below Average"


def _encode_tier(tier: str) -> int:
    """Encode tier to integer for ML model."""
    return {"Below Average": 0, "Average": 1, "Good": 2, "Elite": 3}.get(tier, 1)


def process_gold(df_silver: pd.DataFrame) -> pd.DataFrame:
    """
    Transform Silver data into Gold layer.
    Adds: composite_score, performance_tier, tier_encoded, position_percentiles.

    Args:
        df_silver: Silver-layer DataFrame

    Returns:
        DataFrame with Gold-layer enrichments
    """
    df = df_silver.copy()

    # Compute composite score using position-specific metrics
    df["composite_score"] = _compute_composite_score(df)

    # Assign tiers
    composite_pct = df["composite_score"].rank(pct=True) * 100
    df["composite_percentile"] = composite_pct
    df["performance_tier"] = composite_pct.apply(_assign_tier)
    df["tier_encoded"] = df["performance_tier"].apply(_encode_tier)

    # Position-level percentile rank (within position group)
    if "Primary position" in df.columns:
        for col in SCORING_FEATURES:
            if col in df.columns:
                df[f"{col}_pos_pct"] = df.groupby("Primary position")[col].rank(pct=True) * 100

    # League-level composite rank
    if "League" in df.columns:
        df["league_rank"] = df.groupby("League")["composite_score"].rank(
            ascending=False, method="min"
        )

    return df


def save_gold(df: pd.DataFrame) -> dict:
    """
    Save Gold DataFrame to Parquet.

    Args:
        df: Gold-processed DataFrame

    Returns:
        dict with status, path, row_count
    """
    os.makedirs(GOLD_DIR, exist_ok=True)
    df.to_parquet(GOLD_FILE, index=False)
    return {
        "status": "success",
        "path": GOLD_FILE,
        "row_count": len(df),
        "col_count": len(df.columns),
    }


def get_gold_status() -> dict:
    """Get metadata about the Gold layer file."""
    if not os.path.exists(GOLD_FILE):
        return {"exists": False, "path": GOLD_FILE, "row_count": 0}
    try:
        df = pd.read_parquet(GOLD_FILE)
        mod_time = os.path.getmtime(GOLD_FILE)
        return {
            "exists": True,
            "path": GOLD_FILE,
            "row_count": len(df),
            "col_count": len(df.columns),
            "last_modified": datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S"),
            "tier_counts": df["performance_tier"].value_counts().to_dict() if "performance_tier" in df.columns else {},
        }
    except Exception as e:
        return {"exists": False, "path": GOLD_FILE, "error": str(e)}


def load_gold() -> pd.DataFrame:
    """
    Load Gold Parquet file.

    Raises:
        FileNotFoundError: If Gold layer not yet generated
    """
    if not os.path.exists(GOLD_FILE):
        raise FileNotFoundError("No Gold layer data. Run the pipeline first.")
    return pd.read_parquet(GOLD_FILE)
