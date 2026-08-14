"""
Team Aggregator

Functions for aggregating player-level statistics to team-level metrics.
Uses minutes-weighted averages to create team playing style profiles.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from config.team_analysis_config import TEAM_METRICS, MIN_MINUTES_DEFAULT


def calculate_weighted_average(
    df: pd.DataFrame, metric_col: str, weight_col: str = "Minutes played"
) -> float:
    """
    Calculate weighted average of a metric using minutes played as weights.

    Args:
        df: DataFrame with player data
        metric_col: Column name of the metric
        weight_col: Column name of the weights (default: Minutes played)

    Returns:
        Weighted average value
    """
    if metric_col not in df.columns:
        return np.nan

    if weight_col not in df.columns:
        # Fall back to simple average if no weights
        return df[metric_col].mean()

    # Filter out rows with missing values
    valid_data = df[[metric_col, weight_col]].dropna()

    if len(valid_data) == 0:
        return np.nan

    # Calculate weighted average
    weighted_sum = (valid_data[metric_col] * valid_data[weight_col]).sum()
    total_weight = valid_data[weight_col].sum()

    if total_weight == 0:
        return np.nan

    return weighted_sum / total_weight


def aggregate_team_metrics(
    df: pd.DataFrame, team_name: str, metrics_config: Dict = None
) -> Dict[str, float]:
    """
    Aggregate all metrics for a single team.

    Args:
        df: League DataFrame
        team_name: Name of the team
        metrics_config: Configuration dict with metrics to aggregate (default: TEAM_METRICS)

    Returns:
        Dictionary with aggregated team metrics
    """
    if metrics_config is None:
        metrics_config = TEAM_METRICS

    # Filter for team
    team_df = df[df["Team"] == team_name].copy()

    if len(team_df) == 0:
        return {}

    team_metrics = {}

    # Aggregate metrics by category
    for category, metrics in metrics_config.items():
        for metric_name in metrics.keys():
            if metric_name in team_df.columns:
                value = calculate_weighted_average(team_df, metric_name)
                team_metrics[metric_name] = value

    return team_metrics


def aggregate_all_teams(df: pd.DataFrame, metrics_config: Dict = None) -> pd.DataFrame:
    """
    Aggregate metrics for all teams in the league.

    Args:
        df: League DataFrame
        metrics_config: Configuration dict with metrics

    Returns:
        DataFrame with teams as rows and metrics as columns
    """
    if metrics_config is None:
        metrics_config = TEAM_METRICS

    teams = df["Team"].unique()
    all_teams_data = []

    for team in teams:
        if pd.isna(team):
            continue

        team_metrics = aggregate_team_metrics(df, team, metrics_config)

        if team_metrics:  # Only add if we got data
            team_metrics["Team"] = team
            all_teams_data.append(team_metrics)

    # Convert to DataFrame
    if not all_teams_data:
        return pd.DataFrame()

    teams_df = pd.DataFrame(all_teams_data)

    # Reorder columns to have Team first
    cols = ["Team"] + [col for col in teams_df.columns if col != "Team"]
    teams_df = teams_df[cols]

    return teams_df


def calculate_league_averages(teams_df: pd.DataFrame) -> pd.Series:
    """
    Calculate league-wide averages for all metrics.

    Args:
        teams_df: DataFrame with team aggregated data

    Returns:
        Series with league averages
    """
    # Exclude Team column
    metric_cols = [col for col in teams_df.columns if col != "Team"]

    return teams_df[metric_cols].mean()


def calculate_league_percentiles(
    teams_df: pd.DataFrame, team_name: str
) -> Dict[str, float]:
    """
    Calculate percentile ranks for a team across all metrics.

    Args:
        teams_df: DataFrame with all teams
        team_name: Name of the team to calculate percentiles for

    Returns:
        Dictionary with percentile values (0-100)
    """
    if team_name not in teams_df["Team"].values:
        return {}

    team_row = teams_df[teams_df["Team"] == team_name].iloc[0]

    percentiles = {}
    metric_cols = [col for col in teams_df.columns if col != "Team"]

    for metric in metric_cols:
        if pd.notna(team_row[metric]):
            # Calculate percentile (0-100)
            percentile = (teams_df[metric] < team_row[metric]).mean() * 100
            percentiles[metric] = percentile
        else:
            percentiles[metric] = np.nan

    return percentiles


def get_team_strengths_weaknesses(
    teams_df: pd.DataFrame, team_name: str, top_n: int = 5
) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
    """
    Get top strengths and weaknesses for a team.

    Args:
        teams_df: DataFrame with all teams
        team_name: Name of the team
        top_n: Number of top/bottom metrics to return

    Returns:
        Tuple of (strengths, weaknesses) - each is list of (metric, percentile) tuples
    """
    percentiles = calculate_league_percentiles(teams_df, team_name)

    if not percentiles:
        return [], []

    # Sort by percentile
    sorted_metrics = sorted(percentiles.items(), key=lambda x: x[1], reverse=True)

    # Filter out NaN values
    sorted_metrics = [(m, p) for m, p in sorted_metrics if not np.isnan(p)]

    # Top strengths and weaknesses
    strengths = sorted_metrics[:top_n]
    weaknesses = sorted_metrics[-top_n:][::-1]  # Reverse to show lowest first

    return strengths, weaknesses


def compare_teams_metrics(
    teams_df: pd.DataFrame, team_names: List[str]
) -> pd.DataFrame:
    """
    Create comparison table for multiple teams.

    Args:
        teams_df: DataFrame with all teams
        team_names: List of team names to compare

    Returns:
        DataFrame with teams as rows for easy comparison
    """
    comparison_df = teams_df[teams_df["Team"].isin(team_names)].copy()

    return comparison_df


def get_extreme_teams(
    teams_df: pd.DataFrame, metric: str, top_n: int = 3, highest: bool = True
) -> pd.DataFrame:
    """
    Get teams with highest or lowest values for a specific metric.

    Args:
        teams_df: DataFrame with all teams
        metric: Metric column name
        top_n: Number of teams to return
        highest: If True, return highest values; else lowest

    Returns:
        DataFrame with top/bottom teams
    """
    if metric not in teams_df.columns:
        return pd.DataFrame()

    sorted_df = teams_df.sort_values(metric, ascending=not highest)

    return sorted_df.head(top_n)[["Team", metric]]


def normalize_metrics(teams_df: pd.DataFrame, method: str = "minmax") -> pd.DataFrame:
    """
    Normalize metrics to 0-100 scale for easier comparison.

    Args:
        teams_df: DataFrame with team metrics
        method: Normalization method ('minmax' or 'zscore')

    Returns:
        DataFrame with normalized values
    """
    normalized_df = teams_df.copy()
    metric_cols = [col for col in teams_df.columns if col != "Team"]

    for col in metric_cols:
        if method == "minmax":
            min_val = teams_df[col].min()
            max_val = teams_df[col].max()

            if max_val > min_val:
                normalized_df[col] = (
                    (teams_df[col] - min_val) / (max_val - min_val)
                ) * 100
            else:
                normalized_df[col] = 50  # Default if all values same

        elif method == "zscore":
            mean_val = teams_df[col].mean()
            std_val = teams_df[col].std()

            if std_val > 0:
                normalized_df[col] = ((teams_df[col] - mean_val) / std_val) * 100
            else:
                normalized_df[col] = 50

    return normalized_df
