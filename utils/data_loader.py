"""
Data loading and processing utilities
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import glob
import os
import re
from utils.column_mapping import apply_column_aliases, calculate_derived_metrics


def load_player_data(csv_path: str) -> pd.DataFrame:
    """
    Load player data from CSV file

    Args:
        csv_path: Path to the CSV file

    Returns:
        DataFrame with player statistics
    """
    # Read CSV with UTF-8 BOM encoding
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    # Remove the first unnamed column if it exists
    if df.columns[0] == "" or "Unnamed" in df.columns[0]:
        df = df.iloc[:, 1:]

    # Handle duplicate columns ending in .1, .2 etc (often from Wyscout exports)
    cols_to_keep = []
    for col in df.columns:
        if re.search(r"\.\d+$", col):
            # Check if base column exists
            base_col = re.sub(r"\.\d+$", "", col)
            if base_col in df.columns:
                # Use .equals() as it handles NaNs correctly (NaN == NaN is True for .equals)
                if df[col].equals(df[base_col]):
                    continue
        cols_to_keep.append(col)

    if len(cols_to_keep) < len(df.columns):
        df = df[cols_to_keep]

    return df


def load_all_league_data(data_folder: str) -> pd.DataFrame:
    """
    Load all CSV files from data folder (flat structure, no subfolders)
    Applies column mapping and derives missing metrics

    Args:
        data_folder: Path to the folder containing CSV files

    Returns:
        Combined DataFrame with all players from all leagues

    Raises:
        ValueError: If no valid CSV files found or all files failed to load
    """
    # Load from flat structure (no subfolders)
    csv_files = glob.glob(os.path.join(data_folder, "*.csv"))

    # Filter out old_format.csv to avoid loading both formats
    csv_files = [f for f in csv_files if "old_format" not in f.lower()]

    # Handle empty folder
    if not csv_files:
        raise ValueError(f"No CSV files found in {data_folder}")

    all_dataframes = []
    errors = []

    # Iterate through files, catch errors, continue on failure
    for csv_path in csv_files:
        try:
            # Use existing load_player_data() function
            df = load_player_data(csv_path)

            # Apply column aliases (Competition → League)
            df = apply_column_aliases(df)

            # Calculate derived metrics
            df = calculate_derived_metrics(df)

            # Validate schema (required columns must exist)
            required_cols = [
                "Player",
                "Age",
                "Competition",
                "Position",
                "Team",
                "Birth country",
            ]
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                errors.append(
                    f"{os.path.basename(csv_path)}: Missing columns {missing_cols}"
                )
                continue  # Skip this file

            all_dataframes.append(df)

        except Exception as e:
            errors.append(f"{os.path.basename(csv_path)}: {str(e)}")
            continue  # Skip this file, load others

    # Must have at least one valid DataFrame
    if not all_dataframes:
        raise ValueError(f"Failed to load any CSV files. Errors: {'; '.join(errors)}")

    # Print warnings for failed files (optional)
    if errors:
        print(f"Warning: Some files failed to load:\n" + "\n".join(errors))

    # Combine with ignore_index=True to reset row numbers
    combined_df = pd.concat(all_dataframes, ignore_index=True)

    return combined_df


def get_distinct_values(df: pd.DataFrame) -> Dict:
    """
    Extract distinct positions and leagues from DataFrame

    Args:
        df: Combined DataFrame with all players

    Returns:
        Dictionary with sorted lists of positions and leagues
    """
    # Get unique positions and leagues, remove NaN values
    positions = df["Position"].dropna().unique()
    leagues = df["League"].dropna().unique()

    # Sort alphabetically for consistent display
    positions_sorted = sorted(positions)
    leagues_sorted = sorted(leagues)

    return {"positions": positions_sorted, "leagues": leagues_sorted}


def filter_players(
    df: pd.DataFrame, positions: List[str] = None, leagues: List[str] = None
) -> pd.DataFrame:
    """
    Filter DataFrame by positions and leagues

    Args:
        df: DataFrame with all players
        positions: List of positions to include (None or empty = all positions)
        leagues: List of leagues to include (None or empty = all leagues)

    Returns:
        Filtered DataFrame
    """
    # Work on copy to avoid mutation
    filtered_df = df.copy()
    print(f"positions : {positions}")

    # Apply position filter if specified
    if positions and len(positions) > 0:
        # filtered_df = filtered_df[filtered_df['Position'].isin(positions)]
        # filtered_df = filtered_df[
        #     filtered_df['Position']
        #     .str.split(',')
        #     .apply(lambda pos_list: any(p.strip() in positions for p in pos_list))
        # ]
        filtered_df = filtered_df[
            filtered_df["Primary position"].notna()
            & filtered_df["Primary position"].apply(lambda x: isinstance(x, str))
        ]

        filtered_df = filtered_df[
            filtered_df["Primary position"]
            .str.split(",")
            .apply(lambda pos_list: any(p.strip() in positions for p in pos_list))
        ]

    # Apply league filter if specified
    if leagues and len(leagues) > 0:
        filtered_df = filtered_df[filtered_df["League"].isin(leagues)]

    return filtered_df


def prepare_data_global(data_folder: str, stat_categories: Dict) -> pd.DataFrame:
    """
    Load all league data and calculate GLOBAL percentiles across all players
    Also calculate composite attributes for all players

    Args:
        data_folder: Path to folder containing league CSV files
        stat_categories: Dictionary of stat categories

    Returns:
        DataFrame with all players, global percentile calculations, and composite attributes
    """
    from config.composite_attributes import COMPOSITE_ATTRIBUTES

    # Load all data
    df = load_all_league_data(data_folder)

    # Get all stat columns
    stat_columns = get_all_stat_columns(stat_categories)

    # Calculate GLOBAL percentiles (across ALL players from ALL leagues)
    df = calculate_percentiles(df, stat_columns)

    # Calculate composite attributes for all players
    df = calculate_composite_attributes_batch(df, stat_columns, COMPOSITE_ATTRIBUTES)

    return df


def calculate_percentiles(df: pd.DataFrame, stat_columns: List[str]) -> pd.DataFrame:
    """
    Calculate percentile ranks for specified statistics

    Args:
        df: DataFrame with player data
        stat_columns: List of column names to calculate percentiles for

    Returns:
        DataFrame with original data plus percentile columns
    """
    df_copy = df.copy()

    for col in stat_columns:
        if col in df_copy.columns:
            # Calculate percentile rank (0-100)
            percentile_col = f"{col}_percentile"
            df_copy[percentile_col] = df_copy[col].rank(pct=True) * 100
        else:
            print(f"Warning: Column '{col}' not found in data")

    return df_copy


def get_player_stats(
    df: pd.DataFrame, player_name: str, stat_columns: List[str]
) -> Dict:
    """
    Get statistics for a specific player

    Args:
        df: DataFrame with player data and percentiles
        player_name: Name of the player
        stat_columns: List of stat columns to retrieve

    Returns:
        Dictionary with player stats and percentiles
    """
    player_row = df[df["Player"] == player_name].iloc[0]

    stats = {}
    for col in stat_columns:
        # percentile_col = f"{col}_percentile"
        # stats[col] = {
        #     'value': player_row[col],
        #     'percentile': player_row.get(percentile_col, 0)
        # }
        percentile_col = f"{col}_percentile"
        percentile = player_row.get(percentile_col)

        if pd.notna(percentile):
            stats[col] = {"value": player_row[col], "percentile": percentile}

    return stats


def filter_midfielders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter dataframe to include only DM/CM players (no CAM)

    Args:
        df: DataFrame with player data

    Returns:
        Filtered DataFrame
    """
    # Filter for positions containing DMF, CMF, RCMF, LCMF, RDMF, LDMF but not AMF
    position_col = "Position"

    # Create mask for valid positions
    mask = df[position_col].str.contains("DMF|CMF", case=False, na=False) & ~df[
        position_col
    ].str.contains("AMF", case=False, na=False)

    return df[mask].copy()


def get_all_stat_columns(stat_categories: Dict) -> List[str]:
    """
    Extract all stat column names from the stat categories configuration

    Args:
        stat_categories: Dictionary of stat categories

    Returns:
        List of all stat column names, de-duplicated in first-seen order.
        Some stats (e.g. "Aerial duels per 90") are deliberately listed under
        more than one category; returning them twice makes callers that build
        one widget per stat collide on the widget key.
    """
    all_columns = []
    seen = set()
    for category in stat_categories.values():
        for stat in category["stats"]:
            column = stat["column"]
            if column not in seen:
                seen.add(column)
                all_columns.append(column)

    return all_columns


def prepare_data(csv_path: str, stat_categories: Dict) -> pd.DataFrame:
    """
    Main function to load and prepare data for the app

    Args:
        csv_path: Path to the CSV file
        stat_categories: Dictionary of stat categories

    Returns:
        Prepared DataFrame with filtered players and calculated percentiles
    """
    # Load data
    df = load_player_data(csv_path)

    # No position filtering needed - CSV files are already pre-filtered by position
    # CB CSV contains only CB positions (LCB, RCB, CB, etc.)
    # DM/CM CSV contains only DM/CM positions (DMF, CMF, etc.)

    # Get all stat columns
    stat_columns = get_all_stat_columns(stat_categories)

    # Calculate percentiles
    df = calculate_percentiles(df, stat_columns)

    return df


def get_player_info(df: pd.DataFrame, player_name: str, info_columns: Dict) -> Dict:
    """
    Get player information (name, age, team, country)

    Args:
        df: DataFrame with player data
        player_name: Name of the player
        info_columns: Dictionary mapping info types to column names

    Returns:
        Dictionary with player information
    """
    player_row = df[df[info_columns["name"]] == player_name].iloc[0]

    info = {
        "name": player_row[info_columns["name"]],
        "age": int(player_row[info_columns["age"]]),
        "minutes": int(player_row[info_columns["minutes"]]),
        "team": player_row[info_columns["team"]],
        "country": player_row[info_columns["country"]],
        "position": player_row[info_columns["position"]],
    }

    return info


def calculate_composite_attributes(
    player_stats: Dict, composite_attributes: Dict
) -> Dict:
    """
    Calculate composite attributes for a player based on weighted stat combinations

    Args:
        player_stats: Dictionary with player statistics (containing percentiles)
        composite_attributes: Dictionary defining composite attribute formulas

    Returns:
        Dictionary with calculated composite attribute scores
    """
    composite_scores = {}

    for attr_key, attr_config in composite_attributes.items():
        score = 0.0
        total_weight = 0.0

        for component in attr_config["components"]:
            stat_name = component["stat"]
            weight = component["weight"]
            use_percentile = component.get("use_percentile", True)

            # Get the stat data
            stat_data = player_stats.get(stat_name, {})

            if use_percentile:
                # Use percentile value (0-100)
                value = stat_data.get(
                    "percentile", 50
                )  # Default to 50th percentile if missing
            else:
                # Use raw value
                value = stat_data.get("value", 0)

            # Add weighted contribution
            score += weight * value
            total_weight += abs(weight)

        # Normalize score to 0-100 range if using percentiles
        # Since percentiles are 0-100, weighted sum preserves this range
        composite_scores[attr_key] = {
            "score": score,
            "display_name": attr_config["display_name"],
            "icon": attr_config.get("icon", ""),
            "description": attr_config.get("description", ""),
        }

    return composite_scores


def calculate_composite_attributes_batch(
    df: pd.DataFrame, stat_columns: List[str], composite_attributes: Dict
) -> pd.DataFrame:
    """
    Calculate composite attributes for all players in DataFrame

    Args:
        df: DataFrame with player data and percentile columns
        stat_columns: List of all stat column names
        composite_attributes: Dictionary defining composite attribute formulas

    Returns:
        DataFrame with added composite attribute columns (prefixed with COMP_)
    """
    df_copy = df.copy()

    # For each composite attribute
    for attr_key, attr_config in composite_attributes.items():
        scores = []

        # Calculate for each player
        for idx, row in df_copy.iterrows():
            score = 0.0
            total_weight = 0.0

            for component in attr_config["components"]:
                stat_name = component["stat"]
                weight = component["weight"]
                use_percentile = component.get("use_percentile", True)

                # Skip if stat not available
                if stat_name not in df_copy.columns:
                    continue

                if use_percentile:
                    # Use percentile column
                    percentile_col = f"{stat_name}_percentile"
                    if percentile_col in df_copy.columns:
                        value = row.get(percentile_col, 50)
                    else:
                        value = 50
                else:
                    # Use raw value
                    value = row.get(stat_name, 0)

                # Handle NaN
                if pd.isna(value):
                    value = 50 if use_percentile else 0

                score += weight * value
                total_weight += abs(weight)

            scores.append(score)

        # Add composite attribute column to DataFrame
        df_copy[f"COMP_{attr_key}"] = scores

    return df_copy


def calculate_grade_attributes_batch(
    df: pd.DataFrame, grade_attributes: Dict
) -> pd.DataFrame:
    """
    Calculate grade attributes for all players in DataFrame
    Similar to calculate_composite_attributes_batch but for grade-based skill profiles

    Args:
        df: DataFrame with player data and percentile columns
        grade_attributes: Dictionary defining grade attribute formulas (from GRADE_ATTRIBUTES)

    Returns:
        DataFrame with added grade attribute columns (prefixed with GRADE_)
    """
    df_copy = df.copy()

    # For each grade attribute
    for grade_key, grade_config in grade_attributes.items():
        scores = []

        # Calculate for each player
        for idx, row in df_copy.iterrows():
            score = 0.0
            total_weight = 0.0

            for component in grade_config["components"]:
                stat_name = component["stat"]
                weight = component["weight"]
                use_percentile = component.get("use_percentile", True)

                # Skip if stat not available
                if stat_name not in df_copy.columns:
                    continue

                if use_percentile:
                    # Use percentile column
                    percentile_col = f"{stat_name}_percentile"
                    if percentile_col in df_copy.columns:
                        value = row.get(percentile_col, 50)
                    else:
                        value = 50
                else:
                    # Use raw value
                    value = row.get(stat_name, 0)

                # Handle NaN
                if pd.isna(value):
                    value = 50 if use_percentile else 0

                score += weight * value
                total_weight += abs(weight)

            scores.append(score)

        # Add grade attribute column to DataFrame
        df_copy[f"GRADE_{grade_key}"] = scores

    return df_copy


def get_player_composite_attrs(
    df: pd.DataFrame, player_name: str, composite_attributes: Dict
) -> Dict:
    """
    Extract composite attributes for a specific player from pre-calculated dataframe

    Args:
        df: DataFrame with COMP_* columns already calculated
        player_name: Name of the player
        composite_attributes: COMPOSITE_ATTRIBUTES config dictionary

    Returns:
        Dictionary with same structure as calculate_composite_attributes()
        Example: {'Tackling': {'score': 85.2, 'display_name': 'Tackling', 'icon': '🛡️', 'description': '...'}}

    Raises:
        ValueError: If player not found in dataframe
    """
    # Get player row
    player_row = df[df["Player"] == player_name]

    if len(player_row) == 0:
        raise ValueError(f"Player '{player_name}' not found in dataframe")

    player_row = player_row.iloc[0]

    # Extract all composite attributes
    composite_attrs = {}

    for attr_key, attr_config in composite_attributes.items():
        comp_col = f"COMP_{attr_key}"

        if comp_col in df.columns:
            score = player_row[comp_col]

            # Handle NaN values
            if pd.isna(score):
                score = 50.0

            composite_attrs[attr_key] = {
                "score": score,
                "display_name": attr_config["display_name"],
                "icon": attr_config.get("icon", ""),
                "description": attr_config.get("description", ""),
            }

    return composite_attrs
