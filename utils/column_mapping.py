"""
Column mapping utilities for new Wyscout format
Handles aliases and derived metric calculations
"""
import pandas as pd
import numpy as np

# Column name aliases (old_name → new_name)
COLUMN_ALIASES = {
    'League': 'Competition',
    'Minutes': 'Minutes played',
}


def apply_column_aliases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply column name aliases to dataframe
    Creates aliased columns for backward compatibility

    PATTERN: Only create alias if new column exists and old doesn't
    CRITICAL: Don't overwrite existing columns

    Args:
        df: Raw dataframe from CSV

    Returns:
        Dataframe with aliased columns added
    """
    df_copy = df.copy()

    for old_name, new_name in COLUMN_ALIASES.items():
        # Check: new column exists AND old column doesn't exist
        if new_name in df_copy.columns and old_name not in df_copy.columns:
            # Create alias: df['League'] = df['Competition']
            df_copy[old_name] = df_copy[new_name]

    return df_copy


def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate derived metrics missing from new format

    PATTERN: Check column exists before calculating
    GOTCHA: Handle NaN values after calculation
    CRITICAL: Use axis=1 for row-wise apply, handle division by zero

    Args:
        df: Dataframe with raw columns

    Returns:
        Dataframe with derived metrics added
    """
    df_copy = df.copy()

    # 1. pAdj Tkl+Int per 90 = PAdj Sliding tackles + PAdj Interceptions
    if 'PAdj Sliding tackles' in df_copy.columns and 'PAdj Interceptions' in df_copy.columns:
        df_copy['pAdj Tkl+Int per 90'] = (
            df_copy['PAdj Sliding tackles'] + df_copy['PAdj Interceptions']
        )

    # 2. Aerial duels won per 90 = Aerial duels per 90 × (Aerial duels won, % / 100)
    if 'Aerial duels per 90' in df_copy.columns and 'Aerial duels won, %' in df_copy.columns:
        df_copy['Aerial duels won per 90'] = (
            df_copy['Aerial duels per 90'] * (df_copy['Aerial duels won, %'] / 100)
        )

    # 3. Cards per 90 = Yellow cards per 90 + Red cards per 90
    if 'Yellow cards per 90' in df_copy.columns and 'Red cards per 90' in df_copy.columns:
        df_copy['Cards per 90'] = (
            df_copy['Yellow cards per 90'] + df_copy['Red cards per 90']
        )

    # 4. npxG per 90 = xG per 90 (assuming xG excludes penalties)
    # TODO: Validate this assumption - may need adjustment if xG includes penalties
    if 'xG per 90' in df_copy.columns:
        df_copy['npxG per 90'] = df_copy['xG per 90']

    # 5. npxG per shot = xG per 90 / Shots per 90
    # CRITICAL: Handle division by zero
    if 'xG per 90' in df_copy.columns and 'Shots per 90' in df_copy.columns:
        df_copy['npxG per shot'] = df_copy.apply(
            lambda row: (row['xG per 90'] / row['Shots per 90'])
                       if row['Shots per 90'] > 0
                       else 0,
            axis=1
        )

    # GOTCHA: Fill NaN values in derived metrics with 0
    derived_cols = ['pAdj Tkl+Int per 90', 'Aerial duels won per 90',
                   'Cards per 90', 'npxG per 90', 'npxG per shot']
    for col in derived_cols:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].fillna(0)

    return df_copy
