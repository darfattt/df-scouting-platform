"""
Team Styles

Functions for calculating playing style dimensions and classifying team styles.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from config.team_analysis_config import (
    PLAYING_STYLE_DIMENSIONS,
    STYLE_THRESHOLDS,
)


def calculate_dimension_score(
    team_metrics: Dict[str, float], dimension_config: Dict
) -> float:
    """
    Calculate score for a single playing style dimension.

    Args:
        team_metrics: Dictionary of team metric values
        dimension_config: Configuration for the dimension

    Returns:
        Score (0-100 scale)
    """
    metrics = dimension_config["metrics"]
    weights = dimension_config["weights"]

    weighted_sum = 0
    total_weight = 0

    for metric, weight in zip(metrics, weights):
        if metric in team_metrics and not np.isnan(team_metrics[metric]):
            # Normalize individual metrics to 0-100 scale
            # For now, assume metrics are roughly on similar scales
            value = team_metrics[metric]

            # Handle different metric scales
            if metric.endswith("per 90"):
                # Scale per 90 metrics (typically 0-50 range)
                normalized_value = min(100, (value / 20) * 100)
            elif metric.endswith("%"):
                # Percentages are already 0-100
                normalized_value = value
            elif "length" in metric.lower():
                # Pass length in meters (typically 10-40m)
                normalized_value = min(100, (value / 40) * 100)
            else:
                # Default normalization
                normalized_value = min(100, max(0, value))

            weighted_sum += normalized_value * weight
            total_weight += weight

    if total_weight == 0:
        return 50  # Default neutral value

    raw_score = weighted_sum / total_weight

    # Ensure score is between 0-100
    return min(100, max(0, raw_score))


def calculate_all_style_dimensions(team_metrics: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate all playing style dimensions for a team.

    Args:
        team_metrics: Dictionary of team metric values

    Returns:
        Dictionary with dimension names and scores
    """
    dimensions = {}

    for dim_name, dim_config in PLAYING_STYLE_DIMENSIONS.items():
        score = calculate_dimension_score(team_metrics, dim_config)
        dimensions[dim_name] = score

    return dimensions


def classify_playing_style(
    style_dimensions: Dict[str, float], return_confidence: bool = False
) -> Tuple[str, float]:
    """
    Classify team playing style based on dimension scores.

    Args:
        style_dimensions: Dictionary of playing style dimensions
        return_confidence: If True, return confidence score

    Returns:
        Tuple of (style_name, confidence_score)
    """
    best_style = "Balanced"
    best_score = 0

    # Check each style definition
    for style_name, style_config in STYLE_THRESHOLDS.items():
        if style_name == "Balanced":
            continue

        conditions = style_config["conditions"]
        score = 0
        total_conditions = len(conditions)

        if total_conditions == 0:
            continue

        for dim_name, (min_val, max_val) in conditions.items():
            if dim_name in style_dimensions:
                dim_value = style_dimensions[dim_name]
                if min_val <= dim_value <= max_val:
                    # Calculate how well it fits (center of range = best fit)
                    center = (min_val + max_val) / 2
                    distance = abs(dim_value - center)
                    max_distance = (max_val - min_val) / 2
                    fit_score = 1 - (distance / max_distance) if max_distance > 0 else 1
                    score += fit_score

        # Calculate average fit score
        avg_score = score / total_conditions

        if avg_score > best_score:
            best_score = avg_score
            best_style = style_name

    # Set confidence threshold
    confidence = best_score

    # If confidence is too low, return Balanced
    if confidence < 0.4:
        best_style = "Balanced"
        confidence = 1 - confidence  # Invert for balanced

    if return_confidence:
        return best_style, confidence
    return best_style


def get_style_description(style_name: str) -> str:
    """
    Get description for a playing style.

    Args:
        style_name: Name of the playing style

    Returns:
        Description string
    """
    if style_name in STYLE_THRESHOLDS:
        return STYLE_THRESHOLDS[style_name]["description"]
    return "Unknown style"


def get_style_icon(style_name: str) -> str:
    """
    Get icon for a playing style.

    Args:
        style_name: Name of the playing style

    Returns:
        Icon emoji
    """
    if style_name in STYLE_THRESHOLDS:
        return STYLE_THRESHOLDS[style_name].get("icon", "⚽")
    return "⚽"


def analyze_team_style(
    team_metrics: Dict[str, float],
    league_avg_metrics: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Complete playing style analysis for a team.

    Args:
        team_metrics: Team metrics dictionary
        league_avg_metrics: League average metrics (optional, for comparison)

    Returns:
        Dictionary with complete style analysis
    """
    # Calculate dimensions
    dimensions = calculate_all_style_dimensions(team_metrics)

    # Classify style
    style_name, confidence = classify_playing_style(dimensions, return_confidence=True)

    # Find top dimensions (strengths)
    sorted_dims = sorted(dimensions.items(), key=lambda x: x[1], reverse=True)
    top_strengths = sorted_dims[:3]
    bottom_weaknesses = sorted_dims[-3:][::-1]

    analysis = {
        "style_name": style_name,
        "style_icon": get_style_icon(style_name),
        "style_description": get_style_description(style_name),
        "confidence": confidence,
        "dimensions": dimensions,
        "top_strengths": top_strengths,
        "bottom_weaknesses": bottom_weaknesses,
    }

    # Add comparison to league average if provided
    if league_avg_metrics is not None:
        league_dimensions = calculate_all_style_dimensions(league_avg_metrics)
        diff_from_avg = {}
        for dim in dimensions:
            diff_from_avg[dim] = dimensions[dim] - league_dimensions[dim]
        analysis["diff_from_avg"] = diff_from_avg

    return analysis


def calculate_style_similarity(
    style1: Dict[str, float], style2: Dict[str, float]
) -> float:
    """
    Calculate similarity between two teams' playing styles.

    Args:
        style1: First team's style dimensions
        style2: Second team's style dimensions

    Returns:
        Similarity score (0-100, higher = more similar)
    """
    common_dims = set(style1.keys()) & set(style2.keys())

    if not common_dims:
        return 0

    # Calculate Euclidean distance
    squared_diffs = []
    for dim in common_dims:
        diff = style1[dim] - style2[dim]
        squared_diffs.append(diff**2)

    distance = np.sqrt(sum(squared_diffs) / len(common_dims))

    # Convert distance to similarity (0-100)
    # Max possible distance is ~141 (sqrt(100^2 + 100^2))
    similarity = max(0, 100 - distance)

    return similarity


def find_similar_teams(
    target_team: str,
    all_teams_styles: Dict[str, Dict[str, float]],
    top_n: int = 5,
    exclude_same: bool = True,
) -> List[Tuple[str, float]]:
    """
    Find teams with similar playing styles.

    Args:
        target_team: Name of the target team
        all_teams_styles: Dictionary mapping team names to their style dimensions
        top_n: Number of similar teams to return
        exclude_same: If True, exclude the target team itself

    Returns:
        List of (team_name, similarity_score) tuples
    """
    if target_team not in all_teams_styles:
        return []

    target_style = all_teams_styles[target_team]

    similarities = []
    for team_name, team_style in all_teams_styles.items():
        if exclude_same and team_name == target_team:
            continue

        similarity = calculate_style_similarity(target_style, team_style)
        similarities.append((team_name, similarity))

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:top_n]


def get_style_distribution(teams_styles: Dict[str, str]) -> Dict[str, int]:
    """
    Get distribution of playing styles across the league.

    Args:
        teams_styles: Dictionary mapping team names to style names

    Returns:
        Dictionary with style counts
    """
    distribution = {}

    for style_name in teams_styles.values():
        distribution[style_name] = distribution.get(style_name, 0) + 1

    return distribution


def calculate_league_style_stats(
    all_teams_data: pd.DataFrame,
) -> Dict[str, Dict[str, float]]:
    """
    Calculate style statistics for all teams in the league.

    Args:
        all_teams_data: DataFrame with all teams' metrics

    Returns:
        Dictionary mapping team names to their style analyses
    """
    team_styles = {}

    # Calculate league averages
    metric_cols = [col for col in all_teams_data.columns if col != "Team"]
    league_avg = all_teams_data[metric_cols].mean().to_dict()

    # Analyze each team
    for _, row in all_teams_data.iterrows():
        team_name = row["Team"]
        team_metrics = row[metric_cols].to_dict()

        analysis = analyze_team_style(team_metrics, league_avg)
        team_styles[team_name] = analysis

    return team_styles
