import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import custom configurations
from config.stat_categories import STAT_CATEGORIES
from config.position_groups import POSITION_GROUPS
from config.composite_attributes import COMPOSITE_ATTRIBUTES

# Import modular components
from data_manager import load_data_by_continents, get_available_continents, prepare_filtered_data
from ui_components import (
    build_custom_preset_ui, 
    get_relevant_presets, 
    sanitize_key
)

# Import page renderers
from page.comparison import render_player_comparison_page
from page.finder import render_player_finder_page
from page.similarity import render_player_similarity_page
from page.scatter import render_scatter_analysis_page
from page.outliers import render_outliers_analysis_page
from page.clustering import render_clustering_analysis_page
from page.regression import render_regression_analysis_page
from page.league_fit import render_league_fit_page
from page.shoot_analysis import render_shoot_analysis_page
from page.player_details import render_player_details_page
from page.ai_intelligence import render_ai_intelligence_page
from page.team_analysis import render_team_analysis_page

# App Setup - Wide Mode & Sidebar State
st.set_page_config(
    page_title="df-scouting platform",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_nike_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
        color: #111111;
    }
    [data-testid="stHeader"] {
        background-color: #ffffff;
        border-bottom: 1px solid #cacacb;
    }
    [data-testid="stSidebar"] {
        background-color: #f5f5f5;
        border-right: 1px solid #cacacb;
    }
    /* Don't hit Material Symbols spans: they render their icon via a font
       ligature, so overriding font-family prints the raw name
       (e.g. "keyboard_double_arrow_left") instead of the glyph. */
    [data-testid="stSidebar"] *:not([data-testid="stIconMaterial"]) {
        font-family: 'Inter', sans-serif;
        color: #111111;
    }
    [data-testid="stIconMaterial"],
    span.material-icons,
    span.material-icons-outlined,
    span.material-symbols-rounded,
    span.material-symbols-outlined {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }
    [data-testid="stMetric"] {
        background-color: #f5f5f5;
        border: 1px solid #cacacb;
        border-radius: 0;
        padding: 16px;
    }
    [data-testid="stMetricValue"] { color: #111111; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #707072; font-size: 0.85rem; }
    [data-testid="stExpander"] { border: 1px solid #cacacb; border-radius: 0; }
    button[kind="primary"] {
        background-color: #111111 !important;
        color: #ffffff !important;
        border-radius: 9999px !important;
        border: none !important;
        font-weight: 600;
    }
    button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #111111 !important;
        border-radius: 9999px !important;
        font-weight: 600;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 2px solid #111111;
        color: #111111;
        font-weight: 700;
    }
    [data-testid="stTabs"] button { color: #707072; border-radius: 0; }
    hr { border-color: #cacacb; }
    [data-testid="stDataFrame"] { border: 1px solid #cacacb; }

    /* ── Radio buttons ──────────────────────────────────────────── */
    [data-testid="stRadio"] label {
        gap: 8px;
        cursor: pointer;
    }
    [data-testid="stRadio"] label span:first-child {
        border: 1.5px solid #cacacb !important;
        background-color: #ffffff !important;
        box-shadow: none !important;
    }
    [data-testid="stRadio"] label[data-selected="true"] span:first-child,
    [data-testid="stRadio"] input[type="radio"]:checked + span {
        border-color: #111111 !important;
        background-color: #111111 !important;
        box-shadow: inset 0 0 0 3px #ffffff !important;
    }
    [data-testid="stRadio"] label:hover span:first-child {
        border-color: #111111 !important;
    }

    /* ── Checkboxes ─────────────────────────────────────────────── */
    [data-testid="stCheckbox"] label span:first-child {
        border: 1.5px solid #cacacb !important;
        border-radius: 0px !important;
        background-color: #ffffff !important;
        box-shadow: none !important;
    }
    [data-testid="stCheckbox"] input[type="checkbox"]:checked + span,
    [data-testid="stCheckbox"] label[data-checked="true"] span:first-child {
        background-color: #111111 !important;
        border-color: #111111 !important;
    }
    [data-testid="stCheckbox"] label:hover span:first-child {
        border-color: #111111 !important;
    }

    /* ── Selectbox ──────────────────────────────────────────────── */
    [data-testid="stSelectbox"] > div > div {
        border: 1px solid #cacacb !important;
        border-radius: 0px !important;
        background-color: #ffffff !important;
        color: #111111 !important;
        box-shadow: none !important;
    }
    [data-testid="stSelectbox"] > div > div:focus-within {
        border-color: #111111 !important;
        box-shadow: none !important;
    }
    [data-testid="stSelectbox"] svg { color: #111111 !important; }

    /* ── Multiselect ────────────────────────────────────────────── */
    [data-testid="stMultiSelect"] > div > div {
        border: 1px solid #cacacb !important;
        border-radius: 0px !important;
        background-color: #ffffff !important;
        box-shadow: none !important;
    }
    [data-testid="stMultiSelect"] > div > div:focus-within {
        border-color: #111111 !important;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: #111111 !important;
        border-radius: 9999px !important;
    }
    /* The tag label sits in a nested div, not a span, so the sidebar's
       blanket `color: #111111` used to paint it black on the black pill.
       Cover every descendant, and keep the tag's own ✕ light. */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"],
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
        color: #ffffff !important;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] svg {
        color: #ffffff !important;
        fill: currentColor !important;
    }
    /* Chevron / clear-all icons outside the tags stay dark. */
    [data-testid="stMultiSelect"] svg { color: #111111; }

    /* ── Slider ─────────────────────────────────────────────────── */
    [data-testid="stSlider"] [role="slider"] {
        background-color: #111111 !important;
        border: 2px solid #111111 !important;
        box-shadow: none !important;
    }
    [data-testid="stSlider"] [data-testid="stSliderTrackFill"] {
        background-color: #111111 !important;
    }

    /* ── Toggle ─────────────────────────────────────────────────── */
    [data-testid="stToggle"] input:checked + div {
        background-color: #111111 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    inject_nike_css()
    # Sidebar: Logo and Title
    st.sidebar.title("DF Scouting")
    st.sidebar.markdown("---")

    # Sidebar: Global Filters
    st.sidebar.header("Global Filters")

    # 0. Continent Filter (folder-based)
    available_continents = get_available_continents()
    if not available_continents:
        st.error("No continent folders found in data/2025/. Please add data.")
        return

    select_all_continents = st.sidebar.checkbox("Select All Continents", value=False, key="select_all_continents")
    if select_all_continents:
        selected_continents = available_continents
    else:
        selected_continents = st.sidebar.multiselect(
            "Continents:",
            options=available_continents,
            default=available_continents,
            help="Select continent folders to load data from",
            key="continent_multiselect",
        )

    if not selected_continents:
        st.warning("Please select at least one continent to load data.")
        return

    # Load Data from selected continents
    with st.spinner(f"Loading data from {len(selected_continents)} continent(s)..."):
        df_raw = load_data_by_continents(tuple(selected_continents))

    if df_raw is None or df_raw.empty:
        st.error("Failed to load data. Please check if CSV files exist in the selected continent folders.")
        return

    st.sidebar.caption(f"{len(df_raw)} players loaded from {len(selected_continents)} continent(s)")

    # 1. League Filter
    leagues = sorted([l for l in df_raw["League"].unique().tolist() if isinstance(l, str)])
    select_all_leagues = st.sidebar.checkbox("Select All Leagues", value=True, key="select_all_leagues")
    if select_all_leagues:
        selected_leagues = leagues
    else:
        selected_leagues = st.sidebar.multiselect("Leagues:", options=leagues, default=[], key="league_multiselect")
    
    # 2. Position Filter
    position_group_names = list(POSITION_GROUPS.keys())
    selected_position_group = st.sidebar.selectbox("Position Group:", options=position_group_names)
    
    # Apply filters via Data Manager
    df_filtered = prepare_filtered_data(
        df_raw, 
        tuple(selected_leagues), 
        selected_position_group,
        is_calculate_percentile=True,
        is_calculate_composite=True
    )

    # Sidebar: Navigation
    st.sidebar.markdown("---")
    st.sidebar.header("Navigation")
    
    page = st.sidebar.radio(
        "Select Feature:",
        options=[
            "Player Details",
            "Player Comparison",
            "Player Finder",
            "Player Similarity",
            "Scatter Analysis",
            "Outliers Analysis",
            "Clustering Analysis",
            "Regression Analysis",
            "League Fit Analysis",
            "Shoot Analysis",
            "Team Analysis",
            "AI Intelligence",
            "Outlier Intelligence",
        ]
    )

    # Render selected page
    if page == "Player Details":
        render_player_details_page(df_filtered)
    elif page == "Player Comparison":
        render_player_comparison_page(df_filtered, selected_position_group)
    elif page == "Player Finder":
        render_player_finder_page(df_filtered)
    elif page == "Player Similarity":
        render_player_similarity_page(df_filtered, selected_position_group)
    elif page == "Scatter Analysis":
        render_scatter_analysis_page(df_filtered)
    elif page == "Outliers Analysis":
        render_outliers_analysis_page(df_filtered, selected_position_group)
    elif page == "Clustering Analysis":
        render_clustering_analysis_page(df_filtered, selected_position_group)
    elif page == "Regression Analysis":
        render_regression_analysis_page(df_filtered)
    elif page == "League Fit Analysis":
        render_league_fit_page(df_filtered, df_raw)
    elif page == "Shoot Analysis":
        render_shoot_analysis_page(df_filtered)
    elif page == "Team Analysis":
        # For Team Analysis, we want the full squad (ignore global position filter)
        df_team_squad = prepare_filtered_data(
            df_raw, 
            tuple(selected_leagues), 
            "All",
            is_calculate_percentile=True,
            is_calculate_composite=True
        )
        render_team_analysis_page(df_team_squad, selected_position_group)
    elif page == "AI Intelligence":
        render_ai_intelligence_page(df_filtered, selected_position_group)
    elif page == "Outlier Intelligence":
        from page.outlier_intelligence import render_outlier_intelligence_page
        render_outlier_intelligence_page(df_filtered, selected_position_group)

    # Sidebar: Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("v2.0 | DF Scouting")

if __name__ == "__main__":
    main()
