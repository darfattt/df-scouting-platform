"""
Team Visualizations

Matplotlib visualizations for team analysis with cream theme.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List, Tuple, Optional
from config.team_analysis_config import COLORS, PLAYING_STYLE_DIMENSIONS


def setup_cream_theme():
    """Set up matplotlib with cream theme."""
    plt.rcParams["figure.facecolor"] = COLORS["background"]
    plt.rcParams["axes.facecolor"] = COLORS["background"]
    plt.rcParams["axes.edgecolor"] = COLORS["primary"]
    plt.rcParams["axes.labelcolor"] = COLORS["primary"]
    plt.rcParams["text.color"] = COLORS["primary"]
    plt.rcParams["xtick.color"] = COLORS["primary"]
    plt.rcParams["ytick.color"] = COLORS["primary"]
    plt.rcParams["grid.color"] = COLORS["grid"]
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.alpha"] = 0.3


def create_playing_style_radar(
    style_dimensions: Dict[str, float],
    team_name: str,
    comparison_dimensions: Optional[Dict[str, float]] = None,
    comparison_name: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 10),
):
    """Create radar chart for playing style dimensions."""
    setup_cream_theme()

    dimensions = list(style_dimensions.keys())
    values = list(style_dimensions.values())
    num_vars = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection="polar"))
    fig.patch.set_facecolor(COLORS["background"])

    ax.plot(
        angles, values, "o-", linewidth=2.5, color=COLORS["accent2"], label=team_name
    )
    ax.fill(angles, values, alpha=0.25, color=COLORS["accent2"])

    if comparison_dimensions is not None:
        comp_values = [comparison_dimensions.get(dim, 50) for dim in dimensions]
        comp_values += comp_values[:1]
        ax.plot(
            angles,
            comp_values,
            "o-",
            linewidth=2.5,
            color=COLORS["accent1"],
            label=comparison_name,
        )
        ax.fill(angles, comp_values, alpha=0.15, color=COLORS["accent1"])

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        [d[:15] + "..." if len(d) > 15 else d for d in dimensions], size=10
    )
    ax.set_rlabel_position(30)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], size=8)
    ax.set_ylim(0, 100)

    if comparison_dimensions is not None:
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)

    title = f"{team_name} - Playing Style Profile"
    if comparison_name:
        title += f" vs {comparison_name}"
    plt.title(title, size=14, fontweight="bold", pad=20, color=COLORS["primary"])

    plt.tight_layout()
    return fig


def create_team_comparison_bar(
    teams_df: pd.DataFrame,
    metrics: List[str],
    team_names: Optional[List[str]] = None,
    show_league_avg: bool = True,
    figsize: Tuple[int, int] = (14, 8),
    top_n: Optional[int] = None,
):
    """Create horizontal bar chart comparing teams across metrics."""
    setup_cream_theme()

    if team_names is not None:
        plot_df = teams_df[teams_df["Team"].isin(team_names)].copy()
    else:
        plot_df = teams_df.copy()

    league_avg = teams_df[metrics].mean()
    n_metrics = len(metrics)

    fig, axes = plt.subplots(1, n_metrics, figsize=figsize, sharey=True)
    fig.patch.set_facecolor(COLORS["background"])

    if n_metrics == 1:
        axes = [axes]

    colors = [
        COLORS["accent2"],
        COLORS["accent1"],
        COLORS["accent3"],
        COLORS["accent4"],
        COLORS["accent5"],
    ]

    for idx, (metric, ax) in enumerate(zip(metrics, axes)):
        ax.set_facecolor(COLORS["background"])
        sorted_df = plot_df.sort_values(metric, ascending=True)

        # If top_n is specified, filter to top N teams
        if top_n is not None and len(sorted_df) > top_n:
            sorted_df = sorted_df.tail(top_n)

        y_pos = np.arange(len(sorted_df))
        bars = ax.barh(
            y_pos,
            sorted_df[metric].values,
            color=colors[idx % len(colors)],
            alpha=0.7,
            edgecolor="white",
        )

        if show_league_avg:
            ax.axvline(
                x=league_avg[metric],
                color=COLORS["accent1"],
                linestyle="--",
                linewidth=2,
                alpha=0.8,
            )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(sorted_df["Team"].values, fontsize=9)
        ax.set_xlabel(
            metric[:20] + "..." if len(metric) > 20 else metric,
            fontsize=10,
            fontweight="bold",
        )
        ax.set_title(metric[:25], fontsize=11, fontweight="bold", pad=10)

        for i, (bar, val) in enumerate(zip(bars, sorted_df[metric].values)):
            if not np.isnan(val):
                ax.text(val, i, f" {val:.1f}", va="center", fontsize=8)

    fig.suptitle(
        "Team Comparison Across Metrics", fontsize=14, fontweight="bold", y=0.98
    )
    plt.tight_layout()
    return fig


def create_style_scatter_plot(
    teams_df: pd.DataFrame,
    style_dimensions: Dict[str, Dict[str, float]],
    x_dim: str,
    y_dim: str,
    highlight_teams: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (12, 8),
):
    """Create scatter plot of teams across two playing style dimensions."""
    setup_cream_theme()

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(COLORS["background"])
    ax.set_facecolor(COLORS["background"])

    teams = list(style_dimensions.keys())
    x_vals = [style_dimensions[t].get(x_dim, 50) for t in teams]
    y_vals = [style_dimensions[t].get(y_dim, 50) for t in teams]

    ax.scatter(
        x_vals,
        y_vals,
        alpha=0.6,
        s=100,
        c=COLORS["accent2"],
        edgecolors="white",
        linewidth=1,
    )

    if highlight_teams:
        for team in highlight_teams:
            if team in style_dimensions:
                x = style_dimensions[team].get(x_dim, 50)
                y = style_dimensions[team].get(y_dim, 50)
                ax.scatter(
                    x,
                    y,
                    alpha=0.9,
                    s=200,
                    c=COLORS["accent1"],
                    edgecolors="white",
                    linewidth=2,
                )
                ax.annotate(
                    team,
                    (x, y),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=9,
                    fontweight="bold",
                )

    ax.set_xlabel(x_dim, fontsize=12, fontweight="bold")
    ax.set_ylabel(y_dim, fontsize=12, fontweight="bold")
    ax.set_title(f"{y_dim} vs {x_dim}", fontsize=14, fontweight="bold", pad=15)
    ax.axhline(y=50, color=COLORS["grid"], linestyle="-", alpha=0.5)
    ax.axvline(x=50, color=COLORS["grid"], linestyle="-", alpha=0.5)

    plt.tight_layout()
    return fig


def create_metrics_heatmap(
    teams_df: pd.DataFrame,
    metrics: List[str],
    team_names: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (14, 10),
):
    """Create heatmap of team metrics (normalized 0-100)."""
    setup_cream_theme()

    if team_names is not None:
        plot_df = teams_df[teams_df["Team"].isin(team_names)].copy()
    else:
        plot_df = teams_df.copy()

    normalized_data = []
    for metric in metrics:
        if metric in plot_df.columns:
            min_val = plot_df[metric].min()
            max_val = plot_df[metric].max()
            if max_val > min_val:
                normalized = ((plot_df[metric] - min_val) / (max_val - min_val)) * 100
            else:
                normalized = pd.Series([50] * len(plot_df))
            normalized_data.append(normalized.values)

    heatmap_data = np.array(normalized_data).T

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(COLORS["background"])
    ax.set_facecolor(COLORS["background"])

    im = ax.imshow(heatmap_data, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_yticks(np.arange(len(plot_df)))
    ax.set_xticklabels(
        [m[:20] + "..." if len(m) > 20 else m for m in metrics], rotation=45, ha="right"
    )
    ax.set_yticklabels(plot_df["Team"].values)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Relative Strength (0-100)", fontsize=10)

    for i in range(len(plot_df)):
        for j in range(len(metrics)):
            val = heatmap_data[i, j]
            text_color = "white" if val < 30 or val > 70 else "black"
            ax.text(
                j,
                i,
                f"{val:.0f}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=8,
            )

    plt.title(
        "Team Metrics Heatmap (Normalized)", fontsize=14, fontweight="bold", pad=15
    )
    plt.tight_layout()
    return fig


def create_style_distribution_chart(
    style_distribution: Dict[str, int], figsize: Tuple[int, int] = (10, 6)
):
    """Create bar chart showing distribution of playing styles in the league."""
    setup_cream_theme()

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(COLORS["background"])
    ax.set_facecolor(COLORS["background"])

    styles = list(style_distribution.keys())
    counts = list(style_distribution.values())
    colors = [
        COLORS["accent2"],
        COLORS["accent1"],
        COLORS["accent3"],
        COLORS["accent4"],
        COLORS["accent5"],
    ]

    bars = ax.bar(styles, counts, color=colors, alpha=0.7, edgecolor="white")

    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{int(count)}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_xlabel("Playing Style", fontsize=12, fontweight="bold")
    ax.set_ylabel("Number of Teams", fontsize=12, fontweight="bold")
    ax.set_title(
        "Playing Style Distribution in League", fontsize=14, fontweight="bold", pad=15
    )
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig
