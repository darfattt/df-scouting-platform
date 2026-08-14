"""
Feature Engineering - ML feature definitions for player performance prediction
"""

from typing import List

# Primary ML features (Representing Defense, Progression, and Attack)
ML_FEATURES: List[str] = [
    # --- Attacking / Goal Threat ---
    "xG per 90",
    "Assists per 90",
    "xA per 90",
    "Shots per 90",
    "Touches in box per 90",
    "Non-penalty goals per 90",
    
    # --- Creative / Progression ---
    "Dribbles per 90",
    "Key passes per 90",
    "Shot assists per 90",
    "Crosses per 90",
    "Progressive runs per 90",
    "Progressive passes per 90",
    "Smart passes per 90",
    "Passes to penalty area per 90",
    "Accurate passes, %",
    
    # --- Defensive / Physical ---
    "Defensive duels won, %",
    "Interceptions per 90",
    "Aerial duels won, %",
    "Successful defensive actions per 90",
    "Tackles per 90",
]

# Supplementary features (added if available)
SUPPLEMENTARY_FEATURES: List[str] = [
    "Accelerations per 90",
    "Deep completions per 90",
    "Aerial duels per 90",
    "Minutes played",
    "Age",
]

# ML target
ML_TARGET = "tier_encoded"

# Tier label mapping
TIER_LABELS = {0: "Below Average", 1: "Average", 2: "Good", 3: "Elite"}
from styles.design_system import TIER_COLORS  # noqa: F401


def get_available_features(df) -> List[str]:
    """
    Return the subset of ML_FEATURES + SUPPLEMENTARY_FEATURES that exist in the DataFrame.

    Args:
        df: Gold-layer DataFrame

    Returns:
        List of available feature column names
    """
    all_candidates = ML_FEATURES + SUPPLEMENTARY_FEATURES
    return [f for f in all_candidates if f in df.columns]
