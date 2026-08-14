"""
Outlier Detection Module for Player Analysis

Provides statistical outlier detection using Z-score and IQR methods
to identify exceptional players in specific metrics.
"""

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from io import BytesIO
import requests
from styles.design_system import CANVAS, SOFT_CLOUD, apply_nike_style
from datetime import datetime
from typing import Literal, Tuple, Optional


def detect_outliers_zscore(
    df: pd.DataFrame, metric: str, threshold: float = 3.0, higher_is_good: bool = True
) -> pd.DataFrame:
    """
    Detect outliers using Z-score method

    Args:
        df: Filtered DataFrame with percentile values
        metric: Column name to analyze
        threshold: Z-score threshold (default 3.0 = 99.7%)
        higher_is_good: If False, inverts outlier logic for LOWER_IS_GOOD metrics

    Returns:
        DataFrame with outliers, sorted by absolute Z-score
        Adds columns: 'z_score', 'outlier_type' ('high' or 'low')
    """
    # Validate metric exists
    if metric not in df.columns:
        return pd.DataFrame()

    # Calculate Z-scores
    mean = df[metric].mean()
    std = df[metric].std()
    print(f"mean : {mean}")
    print(f"std : {std}")

    # Handle zero standard deviation (all values identical)
    if std == 0 or pd.isna(std):
        return pd.DataFrame()

    df_copy = df.copy()
    df_copy["z_score"] = (df_copy[metric] - mean) / std

    # USER PREFERENCE: HIGH PERFORMERS ONLY (positive outliers)
    # Identify outliers based on threshold
    if higher_is_good:
        # For HIGHER_IS_GOOD: High positive Z-scores are outliers
        outliers = df_copy[df_copy["z_score"] >= threshold].copy()
        outliers["outlier_type"] = "high"
        # Sort by Z-score descending (highest first)
        outliers = outliers.sort_values("z_score", ascending=False)
    else:
        # For LOWER_IS_GOOD: High negative Z-scores are outliers (inverted)
        # Players with LOW fouls/cards (good behavior) = negative Z-scores
        outliers = df_copy[df_copy["z_score"] <= -threshold].copy()
        outliers["outlier_type"] = "low"
        # Sort by Z-score ascending (most negative first)
        outliers = outliers.sort_values("z_score", ascending=True)

    return outliers


def detect_outliers_iqr(
    df: pd.DataFrame, metric: str, multiplier: float = 1.5, higher_is_good: bool = True
) -> pd.DataFrame:
    """
    Detect outliers using IQR method

    Args:
        df: Filtered DataFrame with percentile values
        metric: Column name to analyze
        multiplier: IQR multiplier (default 1.5 = moderate outliers)
        higher_is_good: If False, focuses on lower outliers

    Returns:
        DataFrame with outliers, sorted by distance from quartiles
        Adds columns: 'iqr_distance', 'outlier_type' ('high' or 'low')
    """
    # Validate metric exists
    if metric not in df.columns:
        return pd.DataFrame()

    # Calculate quartiles and IQR
    Q1 = df[metric].quantile(0.25)
    Q3 = df[metric].quantile(0.75)
    IQR = Q3 - Q1

    # Handle zero IQR (all values in narrow range)
    if IQR == 0 or pd.isna(IQR):
        return pd.DataFrame()

    lower_bound = Q1 - (multiplier * IQR)
    upper_bound = Q3 + (multiplier * IQR)

    df_copy = df.copy()

    # USER PREFERENCE: HIGH PERFORMERS ONLY
    # Identify outliers based on bounds
    if higher_is_good:
        # Focus on upper outliers
        outliers = df_copy[df_copy[metric] > upper_bound].copy()
        outliers["iqr_distance"] = outliers[metric] - upper_bound
        outliers["outlier_type"] = "high"
    else:
        # Focus on lower outliers (for LOWER_IS_GOOD metrics)
        outliers = df_copy[df_copy[metric] < lower_bound].copy()
        outliers["iqr_distance"] = lower_bound - outliers[metric]
        outliers["outlier_type"] = "low"

    # Sort by distance from boundary
    outliers = outliers.sort_values("iqr_distance", ascending=False)

    return outliers


def get_metric_indicator(metric: str, stat_categories: dict) -> bool:
    """
    Check if metric is HIGHER_IS_GOOD or LOWER_IS_GOOD

    Args:
        metric: Column name (can be raw stat, COMP_*, or GRADE_* attribute)
        stat_categories: STAT_CATEGORIES dict from config

    Returns:
        True if HIGHER_IS_GOOD, False if LOWER_IS_GOOD
    """
    # USER PREFERENCE: Handle composite attributes
    # Composite attributes are always HIGHER_IS_GOOD (calculated from percentiles)
    if metric.startswith("COMP_"):
        return True

    # USER PREFERENCE: Handle grade attributes
    # Grade attributes are always HIGHER_IS_GOOD (calculated from percentiles)
    if metric.startswith("GRADE_"):
        return True

    # Search through all categories for raw stats
    for category_data in stat_categories.values():
        for stat in category_data.get("stats", []):
            if stat["column"] == metric:
                indicator = stat.get("indicator", "HIGHER_IS_GOOD")
                return indicator == "HIGHER_IS_GOOD"

    # Default to HIGHER_IS_GOOD if not found
    return True


def create_outliers_table_figure(
    outliers_df: pd.DataFrame,
    metric: str,
    method: str,
    position_group: str,
    df_filtered: pd.DataFrame,
    top_n: int = 20,
) -> plt.Figure:
    """
    Create matplotlib figure displaying outliers in table format

    Displays: Rank | Player | Club | Age | Metric Value | Outlier Score

    Args:
        outliers_df: DataFrame with outlier players (from detect_outliers_*)
        metric: Metric name being analyzed
        method: "Z-Score" or "IQR"
        position_group: Position group name (e.g., "Forward", "CB")
        df_filtered: Full DataFrame for merging team logos
        top_n: Number of players to display

    Returns:
        matplotlib Figure object
    """
    # PATTERN: Mirror create_similarity_table_figure structure

    # Use outliers_df directly (already has all columns from df_filtered)
    # Only add 'Team logo' if it exists and isn't already present
    merged_df = outliers_df.head(top_n).copy()

    # Conditionally add Team logo if available and not already present
    if "Team logo" in df_filtered.columns and "Team logo" not in merged_df.columns:
        team_logo_df = df_filtered[["Player", "Team logo"]].copy()
        merged_df = merged_df.merge(team_logo_df, on="Player", how="left")

    # Remove duplicates using existing Team column
    merged_df = merged_df.drop_duplicates(subset=["Player", "Team"], keep="first")
    merged_df = merged_df.head(top_n)

    # Calculate figure dimensions
    n_rows = len(merged_df)
    row_height = 0.5
    fig_height = n_rows * row_height + 3.0
    fig_height = max(5, fig_height)
    
    # Create figure with cream background
    fig, ax = plt.subplots(figsize=(8, fig_height))
    apply_nike_style(fig, ax)

    # Set coordinate system
    ax.set_xlim(0, 16)
    ax.set_ylim(-(n_rows * row_height) - 2.5, 1)
    ax.axis("off")

    # Title section
    metric_title_display = metric.replace("COMP_", "")
    metric_title_display = metric_title_display.replace("DM_", "")
    metric_title_display = metric_title_display.replace("FB_", "")

    title_text = f"{position_group} Outliers - {metric_title_display}"
    ax.text(8, 0.5, title_text, fontsize=16, fontweight="bold", ha="center")

    subtitle_text = f"Method: {method} | Top {n_rows} exceptional performers"
    ax.text(8, 0, subtitle_text, fontsize=10, ha="center", style="italic", color="#666")

    # Column headers: Rank | Player | Club | Age | Metric | Score
    header_y = -0.8
    ax.text(
        0.5, header_y, "Rank", fontsize=11, fontweight="bold", ha="center", va="bottom"
    )
    ax.text(
        2.0, header_y, "Player", fontsize=11, fontweight="bold", ha="left", va="bottom"
    )
    ax.text(
        5.5, header_y, "Club", fontsize=11, fontweight="bold", ha="center", va="bottom"
    )
    ax.text(
        9.0, header_y, "Age", fontsize=11, fontweight="bold", ha="center", va="bottom"
    )

    # Truncate metric name if too long
    metric_display = (
        metric_title_display[:13] + "..."
        if len(metric_title_display) > 13
        else metric_title_display
    )
    ax.text(
        11.0,
        header_y,
        metric_display,
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="bottom",
    )

    if method == "Z-Score":
        ax.text(
            14.0,
            header_y,
            "Z-Score",
            fontsize=11,
            fontweight="bold",
            ha="center",
            va="bottom",
        )
    else:
        ax.text(
            14.0,
            header_y,
            "IQR Dist",
            fontsize=11,
            fontweight="bold",
            ha="center",
            va="bottom",
        )

    # Header line
    ax.plot([0.3, 15.7], [header_y - 0.1, header_y - 0.1], "k-", linewidth=1.5)

    # Data rows
    for idx, (_, row) in enumerate(merged_df.iterrows()):
        y_pos = header_y - 0.5 - (idx * row_height)

        # Rank
        ax.text(0.5, y_pos, str(idx + 1), fontsize=10, ha="center", va="center")

        # Player name
        player_name = row["Player"][:30] if len(row["Player"]) > 30 else row["Player"]
        ax.text(1.3, y_pos, player_name, fontsize=10, ha="left", va="center")

        # Team logo (with error handling)
        if pd.notna(row.get("Team logo")):
            try:
                response = requests.get(row["Team logo"], timeout=3)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    imagebox = OffsetImage(img, zoom=0.15)
                    ab = AnnotationBbox(imagebox, (5.0, y_pos), frameon=False)
                    ax.add_artist(ab)
            except:
                pass  # Skip logo on failure

        # Team name
        team_name = row["Team"] if pd.notna(row["Team"]) else "Unknown"
        team_display = team_name[:20] + "..." if len(team_name) > 20 else team_name
        ax.text(5.3, y_pos, team_display, fontsize=10, ha="left", va="center")

        # Age
        age = int(row["Age"]) if pd.notna(row["Age"]) else "-"
        ax.text(9.0, y_pos, str(age), fontsize=10, ha="center", va="center")

        # Metric value
        metric_val = row[metric] if pd.notna(row[metric]) else 0
        ax.text(11.0, y_pos, f"{metric_val:.2f}", fontsize=10, ha="center", va="center")

        # Outlier score
        if method == "Z-Score":
            score = row.get("z_score", 0)
        else:
            score = row.get("iqr_distance", 0)
        ax.text(
            14.0,
            y_pos,
            f"{score:.2f}",
            fontsize=10,
            ha="center",
            va="center",
            fontweight="bold",
        )

    # Bottom border
    bottom_y = header_y - 0.5 - (n_rows * row_height) + 0.25
    ax.plot([0.3, 15.7], [bottom_y, bottom_y], "k-", linewidth=1.5)

    # Footer
    footer_y = bottom_y - 0.5
    today_date = datetime.now().strftime("%d/%m/%Y")
    footer_text = (
        f"Generated: {today_date} | Data: Wyscout via Best11Scouting\n"
        f"Position Group: {position_group} | Method: {method}"
    )
    ax.text(0.5, footer_y, footer_text, fontsize=8, ha="left", va="top", color="#666")

    plt.tight_layout()
    return fig


def display_outliers_analysis(
    outliers_df: pd.DataFrame,
    metric: str,
    method: str,
    player_info_cols: list = ["Player", "Age", "Team", "Position"],
) -> None:
    """
    Display outliers analysis results in Streamlit with interactive table

    Args:
        outliers_df: DataFrame with outlier players
        metric: Metric being analyzed
        method: "Z-Score" or "IQR"
        player_info_cols: Columns to display alongside metrics
    """
    if len(outliers_df) == 0:
        st.warning("⚠️ No outliers detected with current threshold settings.")
        return

    st.success(
        f"✅ Found {len(outliers_df)} outliers for **{metric}** using **{method}** method"
    )

    # Prepare display columns
    score_col = "z_score" if method == "Z-Score" else "iqr_distance"
    display_cols = player_info_cols + [metric, score_col, "outlier_type"]

    # Filter to available columns
    display_cols = [col for col in display_cols if col in outliers_df.columns]

    # Round numeric columns for display
    display_df = outliers_df[display_cols].copy()
    for col in display_df.columns:
        if pd.api.types.is_numeric_dtype(display_df[col]):
            display_df[col] = display_df[col].round(2)

    # Display dataframe with styling
    st.dataframe(
        display_df,
        use_container_width=True,
        height=min(600, len(display_df) * 35 + 38),  # Dynamic height
    )

    # Download button for CSV export
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Outliers CSV",
        data=csv,
        file_name=f"outliers_{metric.replace(' ', '_')}_{method}.csv",
        mime="text/csv",
    )
