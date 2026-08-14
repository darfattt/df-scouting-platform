"""
Team Data Loader

Functions for loading and filtering team data from CSV files.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import os


def load_league_data(league_file_path: str) -> pd.DataFrame:
    """
    Load league data from CSV file.

    Args:
        league_file_path: Path to CSV file (relative or absolute)

    Returns:
        DataFrame with league data
    """
    # Handle both relative and absolute paths
    if not os.path.isabs(league_file_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, league_file_path)
    else:
        file_path = league_file_path

    # Load CSV with proper encoding
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    # Remove unnamed column if exists
    if "Unnamed: 0" in df.columns:
        df = df.drop("Unnamed: 0", axis=1)

    # Clean column names
    df.columns = df.columns.str.strip()

    return df


def get_available_leagues(base_data_dir: str = "data") -> Dict[str, str]:
    """
    Get list of available league files.

    Args:
        base_data_dir: Base directory for data

    Returns:
        Dictionary mapping league names to file paths
    """
    leagues = {}

    # Check main data directory
    data_2025_dir = os.path.join(base_data_dir, "2025")

    if os.path.exists(data_2025_dir):
        for file in os.listdir(data_2025_dir):
            if file.endswith(".csv"):
                league_name = file.replace(".csv", "")
                leagues[league_name] = os.path.join(data_2025_dir, file)

    # Check root data directory
    if os.path.exists(base_data_dir):
        for file in os.listdir(base_data_dir):
            if file.endswith(".csv"):
                league_name = file.replace(".csv", "")
                if league_name not in leagues:
                    leagues[league_name] = os.path.join(base_data_dir, file)

    return leagues


def get_available_teams(df: pd.DataFrame) -> List[str]:
    """
    Get list of unique teams in the dataset.

    Args:
        df: League DataFrame

    Returns:
        Sorted list of team names
    """
    if "Team" not in df.columns:
        raise ValueError("DataFrame does not contain 'Team' column")

    teams = df["Team"].dropna().unique().tolist()
    return sorted(teams)


def filter_by_team(df: pd.DataFrame, team_names: List[str]) -> pd.DataFrame:
    """
    Filter DataFrame by team(s).

    Args:
        df: League DataFrame
        team_names: List of team names to filter

    Returns:
        Filtered DataFrame
    """
    return df[df["Team"].isin(team_names)].copy()


def filter_by_minutes(df: pd.DataFrame, min_minutes: int = 500) -> pd.DataFrame:
    """
    Filter players by minimum minutes played.

    Args:
        df: League DataFrame
        min_minutes: Minimum minutes threshold

    Returns:
        Filtered DataFrame
    """
    if "Minutes played" not in df.columns:
        return df.copy()

    return df[df["Minutes played"] >= min_minutes].copy()


def get_team_summary_info(df: pd.DataFrame, team_name: str) -> Dict:
    """
    Get summary information about a team.

    Args:
        df: League DataFrame
        team_name: Name of the team

    Returns:
        Dictionary with team summary info
    """
    team_df = df[df["Team"] == team_name]

    if len(team_df) == 0:
        return {}

    summary = {
        "team_name": team_name,
        "competition": team_df["Competition"].iloc[0]
        if "Competition" in team_df.columns
        else "N/A",
        "players_count": len(team_df),
        "avg_age": team_df["Age"].mean() if "Age" in team_df.columns else None,
        "total_minutes": team_df["Minutes played"].sum()
        if "Minutes played" in team_df.columns
        else None,
        "matches_played": team_df["Matches played"].iloc[0]
        if "Matches played" in team_df.columns
        else None,
    }

    return summary


def get_league_summary(df: pd.DataFrame) -> Dict:
    """
    Get summary information about the entire league.

    Args:
        df: League DataFrame

    Returns:
        Dictionary with league summary info
    """
    summary = {
        "total_teams": df["Team"].nunique() if "Team" in df.columns else 0,
        "total_players": len(df),
        "competition": df["Competition"].iloc[0]
        if "Competition" in df.columns
        else "N/A",
        "avg_age": df["Age"].mean() if "Age" in df.columns else None,
        "teams": get_available_teams(df),
    }

    return summary


def validate_data_quality(df: pd.DataFrame) -> Dict[str, bool]:
    """
    Validate data quality and required columns.

    Args:
        df: League DataFrame

    Returns:
        Dictionary with validation results
    """
    required_columns = ["Team", "Minutes played", "Player"]

    validation = {
        "has_required_columns": all(col in df.columns for col in required_columns),
        "has_team_data": "Team" in df.columns and df["Team"].notna().sum() > 0,
        "has_minutes_data": "Minutes played" in df.columns
        and df["Minutes played"].notna().sum() > 0,
        "total_rows": len(df),
        "missing_team_values": df["Team"].isna().sum() if "Team" in df.columns else 0,
    }

    return validation


def prepare_team_analysis_data(
    df: pd.DataFrame, min_minutes: int = 500
) -> pd.DataFrame:
    """
    Prepare data for team analysis by filtering and cleaning.

    Args:
        df: Raw league DataFrame
        min_minutes: Minimum minutes threshold

    Returns:
        Cleaned and filtered DataFrame
    """
    # Make a copy to avoid modifying original
    df_clean = df.copy()

    # Filter by minimum minutes
    df_clean = filter_by_minutes(df_clean, min_minutes)

    # Remove rows with missing team
    df_clean = df_clean[df_clean["Team"].notna()]

    # Ensure Minutes played is numeric
    if "Minutes played" in df_clean.columns:
        df_clean["Minutes played"] = pd.to_numeric(
            df_clean["Minutes played"], errors="coerce"
        )

    return df_clean
