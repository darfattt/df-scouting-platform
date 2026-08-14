import pandas as pd
import streamlit as st
import os
import glob
from utils.data_loader import (
    load_all_league_data,
    load_player_data,
    filter_players,
    get_all_stat_columns,
    calculate_percentiles,
    calculate_composite_attributes_batch,
)
from utils.column_mapping import apply_column_aliases, calculate_derived_metrics
from config.stat_categories import STAT_CATEGORIES
from config.position_groups import POSITION_GROUPS
from config.composite_attributes import COMPOSITE_ATTRIBUTES


def get_data_root():
    """Get the root data directory path."""
    return os.path.join(os.getcwd(), "data", "2025")


def get_available_continents():
    """
    List available continent folders inside data/2025/

    Returns:
        Sorted list of continent folder names
    """
    data_root = get_data_root()
    print(data_root)
    if not os.path.exists(data_root):
        return []
    return sorted([
        d for d in os.listdir(data_root)
        if os.path.isdir(os.path.join(data_root, d))
    ])


@st.cache_data
def load_data_by_continents(continents: tuple) -> pd.DataFrame:
    """
    Load raw player data from selected continent subfolders.
    Each continent folder contains CSV files for its leagues.

    Args:
        continents: Tuple of continent folder names to load from

    Returns:
        Combined DataFrame with raw player data
    """
    data_root = get_data_root()

    if not os.path.exists(data_root):
        st.error(f"Data folder not found: {data_root}")
        st.stop()

    all_dataframes = []
    errors = []

    for continent in continents:
        continent_path = os.path.join(data_root, continent)
        if not os.path.isdir(continent_path):
            errors.append(f"Folder not found: {continent}")
            continue

        csv_files = glob.glob(os.path.join(continent_path, "*.csv"))
        csv_files = [f for f in csv_files if "old_format" not in f.lower()]

        for csv_path in csv_files:
            try:
                df = load_player_data(csv_path)
                df = apply_column_aliases(df)
                df = calculate_derived_metrics(df)

                # Add a Continent column for reference
                df["Continent"] = continent

                required_cols = ["Player", "Age", "Competition", "Position", "Team", "Birth country"]
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    errors.append(f"{os.path.basename(csv_path)}: Missing columns {missing_cols}")
                    continue

                all_dataframes.append(df)
            except Exception as e:
                errors.append(f"{os.path.basename(csv_path)}: {str(e)}")
                continue

    if errors:
        print(f"Warning: Some files failed to load:\n" + "\n".join(errors))

    if not all_dataframes:
        return pd.DataFrame()

    return pd.concat(all_dataframes, ignore_index=True)


@st.cache_data
def prepare_filtered_data(
    df_all: pd.DataFrame,
    leagues: tuple,
    position_group: str,
    is_calculate_percentile: bool,
    is_calculate_composite: bool,
) -> pd.DataFrame:
    """
    Filter data and calculate percentiles/composites on filtered subset
    Cached with filter parameters - recalculates when filters change

    Args:
        df_all: Raw player data from load_all_data()
        leagues: Tuple of selected league names (must be tuple for hashable cache key)
        position_group: Selected position group name (e.g., "CB", "DM/CM", "All")

    Returns:
        Filtered DataFrame with percentile and composite columns
    """
    # STEP 1: Determine filter values
    # Handle "All Leagues" selection
    if leagues == ("All Leagues",) or len(leagues) == 0:
        league_filter = None
    else:
        league_filter = list(leagues)  # Convert tuple back to list for filter_players()

    # Handle "All" position group
    if position_group == "All":
        position_filter = None
    else:
        position_filter = POSITION_GROUPS.get(position_group, None)

    # STEP 2: Filter players
    df_filtered = filter_players(
        df_all, positions=position_filter, leagues=league_filter
    )

    # STEP 3: Calculate percentiles on FILTERED dataset
    stat_columns = get_all_stat_columns(STAT_CATEGORIES)
    if is_calculate_percentile:
        df_filtered = calculate_percentiles(df_filtered, stat_columns)

    if is_calculate_composite:
        # STEP 4: Calculate composite attributes on FILTERED dataset with new percentiles
        df_filtered = calculate_composite_attributes_batch(
            df_filtered, stat_columns, COMPOSITE_ATTRIBUTES
        )

    return df_filtered
