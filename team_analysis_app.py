"""
Team Analysis Dashboard

Streamlit app for analyzing team playing styles in football leagues.
Aggregates player-level data to create team-level insights.

Usage:
    streamlit run team_analysis_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# Import team analysis modules
from config.team_analysis_config import (
    AVAILABLE_LEAGUES,
    TEAM_METRICS,
    PLAYING_STYLE_DIMENSIONS,
    COLORS,
    MIN_MINUTES_DEFAULT,
    MAX_TEAMS_COMPARE,
    EXPORT_SETTINGS,
)
from utils.team_data_loader import (
    load_league_data,
    get_available_teams,
    get_league_summary,
    prepare_team_analysis_data,
)
from utils.team_aggregator import (
    aggregate_all_teams,
    calculate_league_averages,
    calculate_league_percentiles,
    get_team_strengths_weaknesses,
)
from utils.team_styles import (
    calculate_all_style_dimensions,
    classify_playing_style,
    get_style_description,
    get_style_icon,
    analyze_team_style,
    calculate_league_style_stats,
    find_similar_teams,
)
from utils.team_visualizations import (
    create_playing_style_radar,
    create_team_comparison_bar,
    create_style_scatter_plot,
    create_metrics_heatmap,
    create_style_distribution_chart,
    setup_cream_theme,
)

# Page configuration
st.set_page_config(
    page_title="Team Analysis Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for cream theme
custom_css = """
<style>
    .main {
        background-color: #ffffff;
    }
    .stApp {
        background-color: #ffffff;
    }
    .stSelectbox, .stMultiSelect {
        background-color: white;
    }
    h1 {
        color: #111111;
        font-weight: 700;
    }
    h2, h3 {
        color: #111111;
    }
    .stMetric {
        background-color: white;
        border-radius: 5px;
        padding: 10px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


def load_and_process_data(league_file: str, min_minutes: int = MIN_MINUTES_DEFAULT):
    """Load and process league data."""
    # Load raw data
    df_raw = load_league_data(league_file)

    # Clean and prepare
    df_clean = prepare_team_analysis_data(df_raw, min_minutes)

    # Aggregate to team level
    teams_df = aggregate_all_teams(df_clean)

    # Calculate style dimensions for all teams
    style_stats = calculate_league_style_stats(teams_df)

    return df_clean, teams_df, style_stats


def render_sidebar():
    """Render sidebar with global filters."""
    st.sidebar.markdown("### 📍 Team Analysis Hub")
    st.sidebar.markdown("---")

    # League selection
    st.sidebar.markdown("**🔍 Global Filter**")
    selected_league = st.sidebar.selectbox(
        "Select League:",
        options=list(AVAILABLE_LEAGUES.keys()),
        index=0,
        key="league_selector",
    )

    # Load data summary
    league_file = AVAILABLE_LEAGUES[selected_league]
    df_raw = load_league_data(league_file)
    league_summary = get_league_summary(df_raw)

    st.sidebar.info(
        f"📊 {selected_league}\n"
        f"   {league_summary['total_teams']} Teams | "
        f"{league_summary['total_players']} Players"
    )

    st.sidebar.markdown("---")

    return selected_league, league_file


def render_team_selector(teams: list, max_selections: int = MAX_TEAMS_COMPARE):
    """Render team selection section."""
    st.markdown("---")
    st.markdown("### 🎯 Select Team(s) for Analysis")

    col1, col2 = st.columns([3, 1])

    with col1:
        # Analysis mode
        analysis_mode = st.radio(
            "Analysis Mode:",
            options=["Single Team", "Compare Teams (2-3)", "League Overview"],
            horizontal=True,
            key="analysis_mode",
        )

    with col2:
        st.write("")
        st.write("")
        if analysis_mode == "Single Team":
            max_sel = 1
        elif analysis_mode == "Compare Teams (2-3)":
            max_sel = MAX_TEAMS_COMPARE
        else:
            max_sel = len(teams)

        st.markdown(f"**Max: {max_sel} team(s)**")

    # Team selection
    if analysis_mode == "League Overview":
        selected_teams = teams
        st.success(f"✅ Analyzing all {len(teams)} teams in league")
    else:
        selected_teams = st.multiselect(
            f"Select Team{'s' if max_sel > 1 else ''}:",
            options=teams,
            default=teams[: min(max_sel, len(teams))] if max_sel <= 3 else [],
            max_selections=max_sel,
            key="team_selector",
        )

        if not selected_teams:
            st.warning(
                f"⚠️ Please select at least {1 if analysis_mode == 'Single Team' else 2} team(s)"
            )
            return None, analysis_mode

        st.success(f"✅ Selected: {', '.join(selected_teams)}")

    return selected_teams, analysis_mode


def render_single_team_analysis(
    team_name: str, teams_df: pd.DataFrame, style_stats: dict
):
    """Render analysis for a single team."""
    st.markdown("---")

    # Header
    team_data = style_stats[team_name]
    style_name = team_data["style_name"]
    style_icon = team_data["style_icon"]

    col_header1, col_header2, col_header3 = st.columns([2, 2, 1])

    with col_header1:
        st.markdown(f"## {team_name}")

    with col_header2:
        st.markdown(f"### {style_icon} {style_name}")
        st.caption(team_data["style_description"])

    with col_header3:
        confidence = team_data["confidence"]
        st.metric("Style Confidence", f"{confidence:.0%}")

    # Playing style radar
    st.markdown("---")
    st.markdown("#### 🎨 Playing Style Profile")

    col_radar, col_breakdown = st.columns([2, 1])

    with col_radar:
        fig_radar = create_playing_style_radar(team_data["dimensions"], team_name)
        st.pyplot(fig_radar)
        plt.close(fig_radar)

    with col_breakdown:
        st.markdown("**📊 Dimension Scores:**")
        for dim, score in sorted(
            team_data["dimensions"].items(), key=lambda x: x[1], reverse=True
        ):
            bar_length = int(score / 5)  # Scale to 20 chars max
            bar = "█" * bar_length + "░" * (20 - bar_length)
            st.text(f"{dim[:18]:<18} {bar} {score:.0f}")

    # Strengths and Weaknesses
    st.markdown("---")
    col_strengths, col_weaknesses = st.columns(2)

    with col_strengths:
        st.markdown("#### 💪 Top Strengths")
        for metric, percentile in team_data["top_strengths"]:
            st.markdown(f"- **{metric}**: {percentile:.0f}th percentile")

    with col_weaknesses:
        st.markdown("#### ⚠️ Areas for Improvement")
        for metric, percentile in team_data["bottom_weaknesses"]:
            st.markdown(f"- **{metric}**: {percentile:.0f}th percentile")

    # Similar teams
    st.markdown("---")
    st.markdown("#### 🔍 Similar Playing Styles")

    # Get all team dimensions
    all_dimensions = {t: s["dimensions"] for t, s in style_stats.items()}
    similar_teams = find_similar_teams(team_name, all_dimensions, top_n=5)

    if similar_teams:
        sim_cols = st.columns(min(len(similar_teams), 5))
        for idx, (sim_team, similarity) in enumerate(similar_teams):
            with sim_cols[idx]:
                st.metric(sim_team, f"{similarity:.0f}% similar")

    # Detailed metrics tabs
    st.markdown("---")
    st.markdown("#### 📋 Detailed Tactical Breakdown")

    tabs = st.tabs(["⚽ Attack", "🔄 Build-up", "⚡ Defense", "🎯 Set Pieces"])

    # Attack metrics
    with tabs[0]:
        attack_metrics = [
            "Goals per 90",
            "xG per 90",
            "Shots per 90",
            "Shots on target, %",
            "Goal conversion, %",
            "Touches in box per 90",
            "Dribbles per 90",
        ]
        available_attack = [m for m in attack_metrics if m in teams_df.columns]
        if available_attack:
            team_row = teams_df[teams_df["Team"] == team_name].iloc[0]
            cols = st.columns(len(available_attack))
            for idx, metric in enumerate(available_attack):
                with cols[idx]:
                    value = team_row[metric]
                    st.metric(
                        metric[:15], f"{value:.2f}" if not pd.isna(value) else "N/A"
                    )

    # Build-up metrics
    with tabs[1]:
        buildup_metrics = [
            "Passes per 90",
            "Accurate passes, %",
            "Progressive passes per 90",
            "Forward passes per 90",
            "Short / medium passes per 90",
        ]
        available_buildup = [m for m in buildup_metrics if m in teams_df.columns]
        if available_buildup:
            team_row = teams_df[teams_df["Team"] == team_name].iloc[0]
            cols = st.columns(len(available_buildup))
            for idx, metric in enumerate(available_buildup):
                with cols[idx]:
                    value = team_row[metric]
                    st.metric(
                        metric[:15], f"{value:.2f}" if not pd.isna(value) else "N/A"
                    )

    # Defense metrics
    with tabs[2]:
        defense_metrics = [
            "Successful defensive actions per 90",
            "Defensive duels per 90",
            "PAdj Interceptions",
            "Aerial duels per 90",
        ]
        available_def = [m for m in defense_metrics if m in teams_df.columns]
        if available_def:
            team_row = teams_df[teams_df["Team"] == team_name].iloc[0]
            cols = st.columns(len(available_def))
            for idx, metric in enumerate(available_def):
                with cols[idx]:
                    value = team_row[metric]
                    st.metric(
                        metric[:15], f"{value:.2f}" if not pd.isna(value) else "N/A"
                    )

    # Set pieces
    with tabs[3]:
        setpiece_metrics = ["Corners per 90", "Free kicks per 90", "Crosses per 90"]
        available_sp = [m for m in setpiece_metrics if m in teams_df.columns]
        if available_sp:
            team_row = teams_df[teams_df["Team"] == team_name].iloc[0]
            cols = st.columns(len(available_sp))
            for idx, metric in enumerate(available_sp):
                with cols[idx]:
                    value = team_row[metric]
                    st.metric(
                        metric[:15], f"{value:.2f}" if not pd.isna(value) else "N/A"
                    )


def render_team_comparison(team_names: list, teams_df: pd.DataFrame, style_stats: dict):
    """Render comparison between multiple teams."""
    st.markdown("---")
    st.markdown(f"### 📊 Team Comparison: {', '.join(team_names)}")

    # Side-by-side style classification
    st.markdown("#### 🎨 Playing Style Comparison")

    cols = st.columns(len(team_names))
    for idx, team in enumerate(team_names):
        with cols[idx]:
            team_data = style_stats[team]
            st.markdown(f"##### {team}")
            st.markdown(f"**{team_data['style_icon']} {team_data['style_name']}**")
            st.caption(team_data["style_description"])
            st.progress(team_data["confidence"])
            st.caption(f"Confidence: {team_data['confidence']:.0%}")

    # Dual/Triple radar comparison
    st.markdown("---")
    st.markdown("#### 📈 Playing Style Radar Comparison")

    # Create comparison radar
    if len(team_names) == 2:
        team1, team2 = team_names
        fig_compare = create_playing_style_radar(
            style_stats[team1]["dimensions"],
            team1,
            style_stats[team2]["dimensions"],
            team2,
        )
        st.pyplot(fig_compare)
        plt.close(fig_compare)
    else:
        # For 3 teams, show individual radars side by side
        radar_cols = st.columns(len(team_names))
        for idx, team in enumerate(team_names):
            with radar_cols[idx]:
                fig_radar = create_playing_style_radar(
                    style_stats[team]["dimensions"], team
                )
                st.pyplot(fig_radar)
                plt.close(fig_radar)

    # Comparison table
    st.markdown("---")
    st.markdown("#### 📋 Detailed Metrics Comparison")

    comparison_df = teams_df[teams_df["Team"].isin(team_names)].copy()
    comparison_df = comparison_df.set_index("Team").T
    comparison_df = comparison_df.reset_index()
    comparison_df.columns = ["Metric"] + list(comparison_df.columns[1:])

    st.dataframe(comparison_df, use_container_width=True)

    # Key differences
    st.markdown("---")
    st.markdown("#### 🎯 Key Differences")

    # Find biggest differences between first two teams
    if len(team_names) >= 2:
        team1, team2 = team_names[:2]
        differences = []

        for metric in teams_df.columns:
            if metric != "Team":
                val1 = teams_df[teams_df["Team"] == team1][metric].iloc[0]
                val2 = teams_df[teams_df["Team"] == team2][metric].iloc[0]
                if not pd.isna(val1) and not pd.isna(val2):
                    diff = abs(val1 - val2)
                    differences.append((metric, diff, val1, val2))

        # Sort by difference
        differences.sort(key=lambda x: x[1], reverse=True)

        col_diff1, col_diff2 = st.columns(2)

        with col_diff1:
            st.markdown(f"**📊 Biggest Metric Differences ({team1} vs {team2})**")
            for metric, diff, val1, val2 in differences[:5]:
                st.markdown(
                    f"- **{metric}**: {val1:.2f} vs {val2:.2f} (diff: {diff:.2f})"
                )

        with col_diff2:
            st.markdown(f"**🎨 Style Dimension Differences**")
            dims1 = style_stats[team1]["dimensions"]
            dims2 = style_stats[team2]["dimensions"]

            dim_differences = []
            for dim in dims1:
                diff = abs(dims1[dim] - dims2[dim])
                dim_differences.append((dim, diff, dims1[dim], dims2[dim]))

            dim_differences.sort(key=lambda x: x[1], reverse=True)

            for dim, diff, d1, d2 in dim_differences[:5]:
                st.markdown(f"- **{dim}**: {d1:.0f} vs {d2:.0f}")


def render_league_overview(teams_df: pd.DataFrame, style_stats: dict):
    """Render league-wide overview."""
    st.markdown("---")
    st.markdown("### 🏆 League Overview")

    # Style distribution
    st.markdown("#### 🎨 Playing Style Distribution")

    style_counts = {}
    for team_data in style_stats.values():
        style = team_data["style_name"]
        style_counts[style] = style_counts.get(style, 0) + 1

    col_dist, col_table = st.columns([2, 1])

    with col_dist:
        fig_dist = create_style_distribution_chart(style_counts)
        st.pyplot(fig_dist)
        plt.close(fig_dist)

    with col_table:
        st.markdown("**Style Counts:**")
        for style, count in sorted(
            style_counts.items(), key=lambda x: x[1], reverse=True
        ):
            st.markdown(f"- {style}: {count} teams")

    # Scatter plot
    st.markdown("---")
    st.markdown("#### 📍 Team Positioning Map")

    col_x, col_y = st.columns(2)

    with col_x:
        x_dim = st.selectbox(
            "X-Axis:",
            options=list(PLAYING_STYLE_DIMENSIONS.keys()),
            index=0,
            key="scatter_x",
        )

    with col_y:
        y_dim = st.selectbox(
            "Y-Axis:",
            options=list(PLAYING_STYLE_DIMENSIONS.keys()),
            index=2,
            key="scatter_y",
        )

    all_dimensions = {t: s["dimensions"] for t, s in style_stats.items()}

    fig_scatter = create_style_scatter_plot(teams_df, all_dimensions, x_dim, y_dim)
    st.pyplot(fig_scatter)
    plt.close(fig_scatter)

    # Top teams by metric
    st.markdown("---")
    st.markdown("#### 🏅 League Leaders by Category")

    leader_tabs = st.tabs(["⚽ Attack", "🔄 Build-up", "⚡ Defense", "🎯 Creativity"])

    # Attack leaders
    with leader_tabs[0]:
        attack_metrics = ["Goals per 90", "xG per 90", "Shots per 90"]
        available = [m for m in attack_metrics if m in teams_df.columns][:3]
        if available:
            fig_leaders = create_team_comparison_bar(teams_df, available, top_n=5)
            st.pyplot(fig_leaders)
            plt.close(fig_leaders)

    # Build-up leaders
    with leader_tabs[1]:
        buildup_metrics = [
            "Passes per 90",
            "Progressive passes per 90",
            "Accurate passes, %",
        ]
        available = [m for m in buildup_metrics if m in teams_df.columns][:3]
        if available:
            fig_buildup = create_team_comparison_bar(teams_df, available, top_n=5)
            st.pyplot(fig_buildup)
            plt.close(fig_buildup)

    # Defense leaders
    with leader_tabs[2]:
        defense_metrics = ["Successful defensive actions per 90", "PAdj Interceptions"]
        available = [m for m in defense_metrics if m in teams_df.columns][:3]
        if available:
            fig_def = create_team_comparison_bar(teams_df, available, top_n=5)
            st.pyplot(fig_def)
            plt.close(fig_def)

    # Creativity leaders
    with leader_tabs[3]:
        creative_metrics = ["Key passes per 90", "xA per 90", "Shot assists per 90"]
        available = [m for m in creative_metrics if m in teams_df.columns][:3]
        if available:
            fig_creative = create_team_comparison_bar(teams_df, available, top_n=5)
            st.pyplot(fig_creative)
            plt.close(fig_creative)

    # Full league heatmap
    st.markdown("---")
    st.markdown("#### 🔥 Full League Metrics Heatmap")

    # Select key metrics for heatmap
    key_metrics = [
        "Goals per 90",
        "xG per 90",
        "Passes per 90",
        "Progressive passes per 90",
        "Defensive duels per 90",
        "Key passes per 90",
        "Shots per 90",
    ]
    available_metrics = [m for m in key_metrics if m in teams_df.columns]

    if available_metrics:
        fig_heatmap = create_metrics_heatmap(teams_df, available_metrics)
        st.pyplot(fig_heatmap)
        plt.close(fig_heatmap)


def main():
    """Main function to run the team analysis app."""
    # Header
    st.title("⚽ Team Analysis Dashboard")
    st.markdown("Analyze team playing styles, compare tactics, and identify strengths.")

    # Sidebar
    selected_league, league_file = render_sidebar()

    # Load and process data
    with st.spinner("Loading and processing team data..."):
        try:
            df_clean, teams_df, style_stats = load_and_process_data(league_file)
            teams_list = get_available_teams(df_clean)

            if not teams_list:
                st.error("❌ No teams found in the selected league.")
                return

        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            return

    # Team selection
    selected_teams, analysis_mode = render_team_selector(teams_list)

    if not selected_teams:
        return

    # Run analysis
    with st.spinner("Analyzing team data..."):
        if analysis_mode == "Single Team":
            render_single_team_analysis(selected_teams[0], teams_df, style_stats)
        elif analysis_mode == "Compare Teams (2-3)":
            render_team_comparison(selected_teams, teams_df, style_stats)
        else:  # League Overview
            render_league_overview(teams_df, style_stats)

    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: #7f8c8d; font-size: 12px;">
            Data source: Wyscout | {selected_league}<br>
            Analysis based on aggregated player statistics (min {MIN_MINUTES_DEFAULT} minutes played)
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
