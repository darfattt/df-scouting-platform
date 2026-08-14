"""
Outlier Intelligence Page - Automated Scout Pipeline
Merges Data Engineering, ML Prediction, and AI Analysis into one workflow.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from typing import Optional

# ── Import Shared Logic from AI Intelligence ────────────────────────────────
from page.ai_intelligence import (
    import_pipeline,
    import_models,
    import_enrichment,
)

from config.stat_categories import STAT_CATEGORIES
from config.composite_attributes import COMPOSITE_ATTRIBUTES
from config.grade_attributes import GRADE_ATTRIBUTES
from config.position_groups import POSITION_GROUPS, filter_by_position_group, get_group_for_position
from config.role_definitions import get_all_roles
from config.registry import get_roles_for_position, get_responsibilities_for_position
from utils.data_loader import calculate_grade_attributes_batch
from utils.outlier_detection import get_metric_indicator

BG_COLOR = "#ffffff"
ACCENT_COLORS = {"Elite": "#007d48", "Good": "#1151ff", "Average": "#0a7281", "Below Average": "#d30005"}

GLOBAL_LEAGUE_SENTINEL = "Global (all leagues in filter)"
DEFAULT_TARGET_LEAGUE_HINT = "Liga 1"  # BRI Liga 1 Indonesia (League column value after Competition→League alias)


def _pick_default_target_league(league_options: list) -> int:
    """Return the index of the default target league within league_options."""
    for i, lg in enumerate(league_options):
        if isinstance(lg, str) and DEFAULT_TARGET_LEAGUE_HINT.lower() in lg.lower():
            return i
    return 0  # falls back to GLOBAL_LEAGUE_SENTINEL which is index 0


def _recalibrate_against_target_league(df_results: pd.DataFrame, target_league: str):
    """
    Re-baseline tier verdict and z-score against a specific league's composite_score distribution.

    Keeps the model's original tier in `predicted_tier_label_global` and overrides
    `predicted_tier_label` with the league-relative verdict. Recomputes `composite_zscore`
    relative to the target league's mean/std.

    Returns:
        (df_results, baseline) — baseline dict with target_league, n, mean, std, p30, p70, p90,
        or {'warning': '...'} if the target league has too few rows.
    """
    df = df_results.copy()

    # Preserve the model's global-trained tier verdict before any override
    if "predicted_tier_label" in df.columns and "predicted_tier_label_global" not in df.columns:
        df["predicted_tier_label_global"] = df["predicted_tier_label"]

    cs = df["composite_score"] if "composite_score" in df.columns else None

    if target_league == GLOBAL_LEAGUE_SENTINEL or "League" not in df.columns:
        if cs is not None:
            mean_g, std_g = cs.mean(), cs.std()
            df["composite_zscore"] = (cs - mean_g) / std_g if std_g and std_g > 0 else 0.0
        return df, {"target_league": GLOBAL_LEAGUE_SENTINEL}

    df_target = df[df["League"] == target_league]
    if len(df_target) < 10 or cs is None:
        if cs is not None:
            mean_g, std_g = cs.mean(), cs.std()
            df["composite_zscore"] = (cs - mean_g) / std_g if std_g and std_g > 0 else 0.0
        return df, {
            "target_league": target_league,
            "warning": f"Only {len(df_target)} players from '{target_league}' in the result set "
                       f"(min 10 required). Falling back to global tiers and z-score.",
        }

    cs_t = df_target["composite_score"]
    mean_t = float(cs_t.mean())
    std_t = float(cs_t.std())
    p30_t = float(np.quantile(cs_t, 0.30))
    p70_t = float(np.quantile(cs_t, 0.70))
    p90_t = float(np.quantile(cs_t, 0.90))

    df["composite_zscore"] = (cs - mean_t) / std_t if std_t > 0 else 0.0

    def _assign(score):
        if pd.isna(score):
            return "Average"
        if score >= p90_t:
            return "Elite"
        if score >= p70_t:
            return "Good"
        if score >= p30_t:
            return "Average"
        return "Below Average"

    df["predicted_tier_label"] = cs.apply(_assign)

    return df, {
        "target_league": target_league,
        "n": int(len(df_target)),
        "mean": mean_t,
        "std": std_t,
        "p30": p30_t,
        "p70": p70_t,
        "p90": p90_t,
    }

def render_outlier_intelligence_page(df_filtered: pd.DataFrame, selected_position_group: str):
    st.header("Outlier Intelligence — Automated Scout")
    st.caption(
        "This tool automates the **Bronze → Silver → Gold** pipeline, trains a position-aware "
        "ML model, and identifies elite outliers with AI scouting reports."
    )

    # ── Sidebar / Initial Filters ─────────────────────────────────────────────
    # We simplify the UI: only 'Minimum Minutes' is required to start.
    # Other filters (Age, etc) can be applied to the results later.
    st.markdown("### 1. Define Initial Context")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        min_mins = st.number_input(
            "Minimum Minutes Played:",
            min_value=0,
            max_value=5000,
            value=300,
            step=100,
            key="oi_min_mins"
        )
    with col2:
        available_leagues = (
            sorted(df_filtered["League"].dropna().unique().tolist())
            if "League" in df_filtered.columns else []
        )
        league_options = [GLOBAL_LEAGUE_SENTINEL] + available_leagues
        default_idx = _pick_default_target_league(league_options)
        st.selectbox(
            "Target League (benchmark):",
            options=league_options,
            index=default_idx,
            key="oi_target_league",
            help=(
                "Tier verdict and composite_zscore will be benchmarked against this league's "
                "composite_score distribution. Choose 'Global' to keep dataset-wide tiers."
            ),
        )

    # ── Metric Selection ─────────────────────────────────────────────────────
    st.markdown("### 2. Metric Selection (Analysis Context)")
    st.caption("Define which metrics the AI should prioritize for scouting insights.")

    col_source, col_metric = st.columns([1, 2])
    
    with col_source:
        metric_source = st.radio(
            "Metric Type:",
            options=["Raw Stats", "Composite Attributes", "Grades"],
            key="oi_metric_source",
            help="Raw Stats: Individual statistics | Composite: Weighted combinations | Grades: Skill-based grading",
        )

    all_stats = []
    for category_name, category_data in STAT_CATEGORIES.items():
        for stat in category_data.get("stats", []):
            col = stat["column"]
            if col in df_filtered.columns:
                all_stats.append(col)

    composite_attrs = [f"COMP_{name}" for name in COMPOSITE_ATTRIBUTES.keys()]
    grade_display_names = {}
    
    # Pre-populate display names for all possible metrics
    for key, config in GRADE_ATTRIBUTES.items():
        grade_display_names[f"GRADE_{key}"] = config['display_name']
    for key, config in COMPOSITE_ATTRIBUTES.items():
        grade_display_names[f"COMP_{key}"] = config['display_name']

    available_metrics = []

    if metric_source == "Raw Stats":
        col_cat, _ = st.columns([1, 2])
        with col_cat:
            category_filter = st.selectbox("Category:", options=["All"] + list(STAT_CATEGORIES.keys()), key="oi_category_filter")
        
        if category_filter != "All":
            available_metrics = sorted([
                stat["column"] for stat in STAT_CATEGORIES[category_filter].get("stats", [])
                if stat["column"] in df_filtered.columns or stat["column"] in all_stats
            ])
        else:
            available_metrics = sorted(all_stats)
            
    elif metric_source == "Grades":
        available_metrics = sorted([f"GRADE_{name}" for name in GRADE_ATTRIBUTES.keys()])
    else:
        available_metrics = sorted(composite_attrs)

    with col_metric:
        if available_metrics:
            selected_metric = st.selectbox(
                "Select Metric:",
                options=available_metrics,
                index=0,
                format_func=lambda x: grade_display_names.get(x, x),
                key="oi_selected_metric",
            )
        else:
            st.warning("No metrics available for this type.")
            selected_metric = None

    # ── Auto-sync ML Features ────────────────────────────────────────────────
    # If the selected metric changed, update the pre-selected ML features
    if "oi_prev_metric" not in st.session_state:
        st.session_state["oi_prev_metric"] = None

    if selected_metric != st.session_state["oi_prev_metric"]:
        # Identify constituent metrics
        constituents = []
        if metric_source == "Raw Stats":
            constituents = [selected_metric] if selected_metric else []
        elif metric_source == "Grades" and selected_metric:
            # Extract key from GRADE_ATTRIBUTES (e.g. GRADE_Crossing -> Crossing)
            grade_key = selected_metric.replace("GRADE_", "")
            if grade_key in GRADE_ATTRIBUTES:
                constituents = [c["stat"] for c in GRADE_ATTRIBUTES[grade_key].get("components", [])]
        elif metric_source == "Composite Attributes" and selected_metric:
            # Extract key from COMPOSITE_ATTRIBUTES (e.g. COMP_Security -> Security)
            comp_key = selected_metric.replace("COMP_", "")
            if comp_key in COMPOSITE_ATTRIBUTES:
                constituents = [c["stat"] for c in COMPOSITE_ATTRIBUTES[comp_key].get("components", [])]
        
        # Add supplementary features by default
        from models.feature_engineering import SUPPLEMENTARY_FEATURES
        new_features = list(set(constituents + SUPPLEMENTARY_FEATURES))
        
        # Update session state for the multiselect
        st.session_state["oi_ml_features"] = [f for f in new_features if f in df_filtered.columns or f in all_stats]
        st.session_state["oi_prev_metric"] = selected_metric

    # ── ML Feature Selection ─────────────────────────────────────────────────
    st.markdown("### 3. ML Model Features")
    from models.feature_engineering import ML_FEATURES, SUPPLEMENTARY_FEATURES
    all_possible_features = sorted(list(set(ML_FEATURES + SUPPLEMENTARY_FEATURES + all_stats)))
    
    selected_ml_features = st.multiselect(
        "Define ML Features for Tier Prediction:",
        options=all_possible_features,
        key="oi_ml_features", # This uses the session state initialized above
        help="These features will be used to train/predict the performance tier. Auto-updated based on your selection above."
    )

    # ── Action Button ──────────────────────────────────────────────────────────
    st.markdown("---")
    run_btn = st.button("Run Outlier Intelligence Pipeline", type="primary", use_container_width=True)

    if run_btn:
        if not selected_metric:
            st.error("Please select a metric context first.")
        elif not selected_ml_features:
            st.error("Please select at least one ML feature.")
        else:
            _execute_pipeline(df_filtered, min_mins, selected_position_group, selected_metric, selected_ml_features)

    # ── Results Display (if exists in session state) ──────────────────────────
    if "oi_results" in st.session_state:
        _render_results_section(selected_position_group)

def _execute_pipeline(df_filtered: pd.DataFrame, min_mins: int, selected_position_group: str, context_metric: str, ml_features: list):
    """Run the end-to-end automation."""
    run_pipeline, _, load_gold, _, _, _ = import_pipeline()
    train_model, get_model_status, predict_dataframe, _, _, _, _ = import_models()

    # 1. Filter locally first
    df_to_process = df_filtered[df_filtered["Minutes played"] >= min_mins]
    if len(df_to_process) < 20:
        st.error(f"Too few players ({len(df_to_process)}) match the filters. Lower the minute threshold.")
        return

    # 2. Run Pipeline (Bronze -> Silver -> Gold)
    progress_bar = st.progress(0, text="Running Data Pipeline...")
    
    def on_progress(step: int, total: int, msg: str):
        progress_bar.progress(step / total, text=msg)

    with st.spinner("Processing data layers..."):
        result = run_pipeline(df_to_process, progress_callback=on_progress)
    
    if result["overall"] != "success":
        st.error("Data Pipeline failed. Check 'AI Intelligence' page logs.")
        return

    # 3. Load Gold & Predict Tiers
    progress_bar.progress(0.7, text="Training/Predicting Performance Tiers...")
    try:
        df_gold = load_gold()
        
        # We ALWAYS retrain if the user explicitly defined features to ensure sync
        # Or we can check if model exists and has same features. 
        # For simplicity and to satisfy "define ML_feature first", we retrain.
        with st.spinner("Training XGBoost model with selected features..."):
            print(f"Train model with this feature : {ml_features}")
            train_model(df_gold, feature_names=ml_features, nickname="dynamic")
        
        # Predict
        df_results = predict_dataframe(df_gold, nickname="dynamic")

        # Re-baseline tiers + z-score against the chosen target league
        target_league = st.session_state.get("oi_target_league", GLOBAL_LEAGUE_SENTINEL)
        df_results, baseline = _recalibrate_against_target_league(df_results, target_league)

        # Store results and meta in session state
        st.session_state["oi_results"] = df_results
        st.session_state["oi_target_baseline"] = baseline
        # (oi_context_metric and oi_ml_features are already in session_state via widgets)
        st.session_state["oi_timestamp"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        
        progress_bar.progress(1.0, text="Complete!")
        st.success(f"Analysis complete at {st.session_state['oi_timestamp']}!")
        st.balloons()
        st.rerun()

    except Exception as e:
        st.error(f"Error during modeling: {e}")
        st.exception(e)

def _render_results_section(selected_position_group: str):
    """Render the results table and AI Analyst."""
    df_results = st.session_state["oi_results"]

    st.markdown("---")
    st.markdown("### 2. Analysis Results")

    # Benchmark banner — show which league tiers are relative to
    baseline = st.session_state.get("oi_target_baseline", {})
    if baseline.get("warning"):
        st.warning(baseline["warning"])
    elif baseline.get("target_league") and baseline["target_league"] != GLOBAL_LEAGUE_SENTINEL:
        st.info(
            f"Tiers benchmarked against **{baseline['target_league']}** "
            f"(n={baseline.get('n', '?')}, "
            f"mean={baseline.get('mean', 0):.1f}, "
            f"std={baseline.get('std', 0):.1f}, "
            f"P90={baseline.get('p90', 0):.1f})."
        )
    
    # Secondary Filters (Post-analysis)
    exp = st.expander("Refine Results (Filters)", expanded=False)
    with exp:
        c1, c2, c3 = st.columns(3)
        with c1:
            age_range = st.slider("Age Range:", 16, 40, (18, 35), key="oi_age_slider")
        with c2:
            top_n = st.number_input("Top N Results:", 5, 500, 20, key="oi_top_n")
        with c3:
            tiers = st.multiselect("Tiers:", ["Elite", "Good", "Average", "Below Average"], default=["Elite", "Good"], key="oi_tiers")
        
        c4, c5 = st.columns(2)
        with c4:
            pos_group = st.selectbox("Position Group:", options=["All"] + list(POSITION_GROUPS.keys())[1:], key="oi_pos_group")
        with c5:
            use_expiry = st.checkbox("Filter by Contract Expiry", value=False, key="oi_use_expiry")
            expiry_date = st.date_input("Expires Before:", value=pd.Timestamp("2026-08-31"), disabled=not use_expiry, key="oi_expiry_date")
            include_no_contract = st.checkbox("Include players with no contract info", value=True, disabled=not use_expiry, key="oi_no_contract")

    # Apply secondary filters
    df_display = df_results.copy()
    if "Age" in df_display.columns:
        df_display = df_display[(df_display["Age"] >= age_range[0]) & (df_display["Age"] <= age_range[1])]
    if "predicted_tier_label" in df_display.columns:
        df_display = df_display[df_display["predicted_tier_label"].isin(tiers)]
    
    # Apply Position Group Filter
    if pos_group != "All":
        df_display = filter_by_position_group(df_display, pos_group)
        
    # Apply Contract Expiration Filter
    if use_expiry and "Contract expires" in df_display.columns:
        # Robust date parsing
        df_display["exp_temp"] = pd.to_datetime(df_display["Contract expires"], errors='coerce')
        # Filter (keeping only those before specified date and optionally those without info)
        if include_no_contract:
            df_display = df_display[df_display["exp_temp"].isnull() | (df_display["exp_temp"] <= pd.Timestamp(expiry_date))]
        else:
            df_display = df_display[df_display["exp_temp"].notnull() & (df_display["exp_temp"] <= pd.Timestamp(expiry_date))]
        df_display = df_display.drop(columns=["exp_temp"])
    
    # Apply Sorting (based on selected metric)
    sort_col = st.session_state.get("oi_selected_metric", "composite_score")
    if sort_col not in df_display.columns:
        sort_col = "composite_score"
    
    if sort_col in df_display.columns:
        df_display = df_display.nlargest(top_n, sort_col)
    else:
        df_display = df_display.head(top_n)

    # 4. Calculate Tactical Columns for Display
    if not df_display.empty:
        all_roles = get_all_roles()
        
        # Prepare lists for new columns
        best_roles = []
        archetypes_list = []
        
        for _, row in df_display.iterrows():
            # Determine per-player position group
            player_pos = row.get("Position", "Unknown")
            player_group = get_group_for_position(player_pos)
            
            # Roles for this specific position group
            relevant_role_names = get_roles_for_position(player_group) if player_group != "All" else list(all_roles.keys())
            
            # Calculate Role Score
            row_role_scores = {}
            for role_name in relevant_role_names:
                if role_name in all_roles:
                    role_info = all_roles[role_name]
                    score = 0.0
                    for comp in role_info.get("components", []):
                        stat = comp["stat"]
                        weight = comp["weight"]
                        val = row.get(f"{stat}_percentile", row.get(stat, 50.0))
                        if pd.isna(val): val = 50.0
                        score += val * weight
                    row_role_scores[role_name] = score
            
            best_role = max(row_role_scores, key=row_role_scores.get) if row_role_scores else "N/A"
            best_roles.append(best_role)
            
            # Identify Archetypes (using per-player responsibilities)
            # if player_group == "All":
            #     comp_cols = [c for c in row.index if c.startswith("COMP_")]
            # else:
            relevant_comp_keys = get_responsibilities_for_position(player_group)
            comp_cols = [f"COMP_{k}" for k in relevant_comp_keys if f"COMP_{k}" in row.index]
            if not comp_cols:
                comp_cols = [c for c in row.index if c.startswith("COMP_")]
            
            top_3 = row[comp_cols].sort_values(ascending=False).head(3)
            archetypes_list.append(", ".join([
                COMPOSITE_ATTRIBUTES.get(c.replace("COMP_", ""), {}).get("display_name", c.replace("COMP_", "")) 
                for c in top_3.index
            ]))
            
        df_display["Best Role"] = best_roles
        df_display["Top Archetypes"] = archetypes_list

    # Ensure Age is integer for display (remove decimal)
    if "Age" in df_display.columns:
        df_display["Age"] = pd.to_numeric(df_display["Age"], errors='coerce').fillna(0).astype(int)

    # Display Table
    st.markdown(f"#### Detected Talent ({len(df_display)} players)")
    
    used_features = st.session_state.get("oi_ml_features", [])
    
    display_cols = [
        "Player", "Full name", "Position", "Best Role", "Top Archetypes", "Age",
        "predicted_tier_label", "predicted_tier_label_global",
        "Passport country", "Foot", "Height", "Weight",
        "composite_score", "composite_zscore", "Contract expires", "Market value",
        "Team", "League", "Matches played", "Minutes played"
    ]

    for feature in used_features:
        if feature not in display_cols:
            display_cols.append(feature)

    available_cols = [c for c in display_cols if c in df_display.columns]

    # Highlight Tiers
    def color_tiers(val):
        color = ACCENT_COLORS.get(val, "black")
        return f'color: {color}; font-weight: bold'

    if available_cols:
        tier_color_cols = [
            c for c in ("predicted_tier_label", "predicted_tier_label_global")
            if c in available_cols
        ]
        # Styler.map replaced Styler.applymap, which pandas 3.0 removed.
        styled_df = df_display[available_cols].style
        if tier_color_cols:
            styled_df = styled_df.map(color_tiers, subset=tier_color_cols)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # ── AI Analyst Section ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 3. AI Scout Deep-Dive")
    
    generate_scouting_report, is_configured, build_player_scouting_prompt = import_enrichment()
    
    if not is_configured():
        st.warning("GEMINI_API_KEY not configured. Scouting reports disabled.")
        return

    player_list = sorted(df_display["Player"].unique().tolist())
    if player_list:
        selected_player = st.selectbox("Select Player for AI Report:", options=player_list, key="oi_ai_select")
        
        if st.button("Generate AI Scouting Report", key="oi_ai_btn"):
            with st.spinner(f"AI is analyzing {selected_player} for {pos_group}..."):
                player_row = df_display[df_display["Player"] == selected_player].iloc[0]
                try:
                    # 1. Build stats dictionary using the features used during analysis
                    used_features = st.session_state.get("oi_ml_features", [])
                    if not used_features:
                        from models.feature_engineering import ML_FEATURES
                        used_features = ML_FEATURES
                    
                    stats_dict = {f: player_row.get(f, 0.0) for f in used_features if f in player_row.index}
                    
                    # 1b. Calculate Best Role (Tactical Fit) - Filtered by per-player position group
                    all_roles = get_all_roles()
                    player_pos = player_row.get("Position", "Unknown")
                    player_group = get_group_for_position(player_pos)
                    
                    # if player_group == "All":
                    #     relevant_role_names = list(all_roles.keys())
                    # else:
                    relevant_role_names = get_roles_for_position(player_group)
                    
                    role_scores = {}
                    # Only consider roles mapped to this specific player group
                    for role_name in relevant_role_names:
                        if role_name in all_roles:
                            role_info = all_roles[role_name]
                            score = 0.0
                            for comp in role_info.get("components", []):
                                stat = comp["stat"]
                                weight = comp["weight"]
                                val = player_row.get(f"{stat}_percentile", player_row.get(stat, 50.0))
                                if pd.isna(val): val = 50.0
                                score += val * weight
                            role_scores[role_name] = score
                    
                    best_role = "N/A"
                    if role_scores:
                        best_role = max(role_scores, key=role_scores.get)
                    
                    # 1c. Find Top 3 Archetypes (from COMP_ columns) - Filtered by per-player position group
                    # if player_group == "All":
                    #     comp_cols = [c for c in player_row.index if c.startswith("COMP_")]
                    # else:
                    relevant_comp_keys = get_responsibilities_for_position(player_group)
                    comp_cols = [f"COMP_{k}" for k in relevant_comp_keys if f"COMP_{k}" in player_row.index]
                    
                    # Fallback to all COMP_ if none found for group (to be safe)
                    if not comp_cols:
                        comp_cols = [c for c in player_row.index if c.startswith("COMP_")]
                        
                    top_comp_scores = player_row[comp_cols].sort_values(ascending=False).head(3)
                    top_archetypes = [
                        COMPOSITE_ATTRIBUTES.get(c.replace("COMP_", ""), {}).get("display_name", c.replace("COMP_", "")) 
                        for c in top_comp_scores.index
                    ]
                    
                    # 2. Build the structured prompt
                    # We need to extract common fields
                    # (Note: prompt builder uses position_group from context)
                    baseline = st.session_state.get("oi_target_baseline", {})
                    tgt_lg = baseline.get("target_league")
                    target_league_arg = tgt_lg if tgt_lg and tgt_lg != GLOBAL_LEAGUE_SENTINEL else None

                    prompt = build_player_scouting_prompt(
                        player_name=selected_player,
                        position=player_row.get("Position", "Unknown"),
                        team=player_row.get("Team", "Unknown"),
                        league=player_row.get("League", "Unknown"),
                        age=player_row.get("Age"),
                        performance_tier=player_row.get("predicted_tier_label", "Average"),
                        composite_score=player_row.get("composite_score", 50.0),
                        composite_percentile=player_row.get("composite_percentile", 50.0),
                        key_stats=stats_dict,
                        position_group=pos_group,
                        best_role=best_role,
                        top_archetypes=top_archetypes,
                        target_league=target_league_arg,
                    )
                    
                    # 3. Generate the report
                    report = generate_scouting_report(prompt)
                    
                    st.markdown(f"#### Scouting Report: {selected_player}")
                    st.write(report)
                except Exception as e:
                    st.error(f"AI Report failed: {e}")
    else:
        st.info("No players match the criteria for AI analysis.")

    # ── Graphical Stats Section ──────────────────────────────────────────────
    st.markdown("---")
    _render_graphical_stats_section(df_results, pos_group, df_display)

def _render_graphical_stats_section(df_results: pd.DataFrame, current_pos_group: str, df_display: pd.DataFrame = None):
    """Render the graphical statistics section with tabs."""
    st.markdown("### 4. Graphical Stats")
    
    if df_display is None:
        df_display = df_results
        
    tab1, tab2 = st.tabs(["Scatter", "Distribution"])
    
    with tab1:
        _render_scatter_tab(df_results, current_pos_group)
        
    with tab2:
        _render_distribution_tab(df_display)

def _render_distribution_tab(df: pd.DataFrame):
    """Render the Distribution plot tab."""
    st.markdown("#### Target Distributions")
    st.caption("Distribution of the filtered players currently shown in the table above.")
    
    if df.empty:
        st.info("No data available to distribute. Adjust your filters above.")
        return
        
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**Age Distribution**")
        if "Age" in df.columns:
            age_counts = df["Age"].value_counts().sort_index()
            st.bar_chart(age_counts)
        else:
            st.info("Age data not available")
            
        st.markdown("**Best Role Distribution**")
        if "Best Role" in df.columns:
            role_counts = df["Best Role"].value_counts()
            st.bar_chart(role_counts)
        else:
            st.info("Best Role data not available")
            
        st.markdown("**League/Competition Distribution**")
        if "League" in df.columns:
            league_counts = df["League"].value_counts()
            st.bar_chart(league_counts)
        else:
            st.info("League data not available")

    with c2:
        st.markdown("**Position Group Distribution**")
        if "Position" in df.columns:
            df_pos = df.copy()
            df_pos["Group"] = df_pos["Position"].apply(get_group_for_position)
            pos_counts = df_pos["Group"].value_counts()
            st.bar_chart(pos_counts)
        else:
            st.info("Position data not available")
            
        st.markdown("**Market Value Range Distribution**")
        if "Market value" in df.columns:
            def categorize_mv(val):
                try:
                    v = float(val)
                    if pd.isna(v):
                        return "Unknown"
                    if v >= 1000000:
                        return "> 1M"
                    elif v >= 500000:
                        return "500k - 1M"
                    elif v >= 300000:
                        return "300k - 500k"
                    else:
                        return "< 300k"
                except:
                    return "Unknown"

            mv_cats = df["Market value"].apply(categorize_mv)
            mv_counts = mv_cats.value_counts()
            cats_ordered = ["> 1M", "500k - 1M", "300k - 500k", "< 300k", "Unknown"]
            ordered_counts = pd.Series({c: mv_counts.get(c, 0) for c in cats_ordered})
            if ordered_counts["Unknown"] == 0:
                ordered_counts = ordered_counts.drop("Unknown")
            st.bar_chart(ordered_counts)
        else:
            st.info("Market value data not available")
            
        st.markdown("**Passport Country Distribution**")
        if "Passport country" in df.columns:
            country_counts = df["Passport country"].value_counts()
            st.bar_chart(country_counts.head(10)) 
        else:
            st.info("Passport country data not available")

def _render_scatter_tab(df_results: pd.DataFrame, current_pos_group: str):
    """Render the Scatter plot tab."""
    # 0. Load global context for background (Gold layer containing all tiers)
    try:
        from pipeline.gold_layer import load_gold
        df_global = load_gold()
        # Standardize column names for plot (Gold uses performance_tier, Results uses predicted_tier_label)
        if "performance_tier" in df_global.columns and "predicted_tier_label" not in df_global.columns:
            df_global["predicted_tier_label"] = df_global["performance_tier"]
    except Exception:
        df_global = df_results.copy()

    # 0b. Resolve the target league (Liga 1 benchmark) for league-relative fit
    from config.league_fit_config import TARGET_LEAGUE  # "Liga 1"
    global_leagues = (
        df_global["League"].dropna().unique().tolist()
        if "League" in df_global.columns else []
    )
    target_league = st.session_state.get("oi_target_league", GLOBAL_LEAGUE_SENTINEL)
    if target_league == GLOBAL_LEAGUE_SENTINEL or target_league not in global_leagues:
        target_league = TARGET_LEAGUE

    # 1. Main Monitor Player Selection
    all_players_search = sorted(df_results["Player"].unique().tolist())
    monitor_player = st.selectbox("Select Player to Monitor (Scatter):", options=all_players_search, key="oi_plot_monitor")

    # 2. Local filters for the context (other dots)
    c1, c2, c3 = st.columns(3)
    with c1:
        # Leagues filter - with "All" option
        available_leagues = sorted(df_global["League"].unique().tolist()) if "League" in df_global.columns else []
        league_options = ["All"] + available_leagues
        default_leagues = [target_league] if target_league in available_leagues else ["All"]
        selected_leagues = st.multiselect(
            "Filter Leagues (Plot):",
            options=league_options,
            default=default_leagues,
            key="oi_plot_leagues",
            help=f"The monitored player is benchmarked against this league's distribution (default: {target_league}).",
        )
    
    with c2:
        # Position Group filter (based on config/position_groups.py)
        available_groups = list(POSITION_GROUPS.keys())
        selected_groups = st.multiselect("Filter Position Group (Plot):", options=available_groups, default=[current_pos_group] if current_pos_group in available_groups else ["All"], key="oi_plot_pos_groups")

    with c3:
        # Performance Tier filter
        available_tiers = ["Elite", "Good", "Average", "Below Average"]
        if "predicted_tier_label" in df_global.columns:
            # Also include any that might exist outside the standard list
            existing_tiers = [t for t in df_global["predicted_tier_label"].unique() if pd.notna(t)]
            available_tiers = list(set(available_tiers + existing_tiers))
        
        selected_tiers = st.multiselect("Highlight by Tier:", options=sorted(available_tiers), default=[], key="oi_plot_tiers")

    # 3. Filter data for the "context" players (using global dataset)
    df_context = df_global.copy()
    if selected_leagues and "All" not in selected_leagues:
        df_context = df_context[df_context["League"].isin(selected_leagues)]

    # Combine all allowed positions from selected groups (used for context + z-ref)
    allowed_positions = []
    if selected_groups and "All" not in selected_groups:
        for g in selected_groups:
            pos_list = POSITION_GROUPS.get(g)
            if pos_list:
                allowed_positions.extend(pos_list)
        if allowed_positions:
            df_context = df_context[df_context["Position"].isin(allowed_positions)]

    # 3b. Compute the target-league (Liga 1) z-score reference from df_global,
    #     under the same position-group filter, so the y-axis anchors to Liga 1
    #     even when other leagues are added to the view.
    ref_df = df_global[df_global["League"] == target_league] if "League" in df_global.columns else df_global.iloc[0:0]
    if allowed_positions:
        ref_df = ref_df[ref_df["Position"].isin(allowed_positions)]
    ref_mean = ref_df["composite_score"].mean() if not ref_df.empty else np.nan
    ref_std = ref_df["composite_score"].std() if not ref_df.empty else np.nan
    ref_ok = pd.notna(ref_std) and ref_std > 0 and len(ref_df) >= 10

    # 4. Integrate Monitor Player
    monitor_row = df_results[df_results["Player"] == monitor_player]

    # Combine (remove monitor from context to avoid double plotting, then concatenate)
    df_context = df_context[df_context["Player"] != monitor_player]
    df_plot = pd.concat([monitor_row, df_context], ignore_index=True)

    if df_plot.empty:
        st.warning("No data matches the plot filters.")
        return

    # 4b. Derive composite_zscore (Liga 1-relative) on the plotted frames so the
    #     monitor and every cloud dot share one reference.
    if not ref_ok:
        st.info(
            f"Fewer than 10 {target_league} players match the position filter — "
            f"the y-axis z-score is relative to the shown cloud instead of {target_league}."
        )
        fb_mean = df_context["composite_score"].mean()
        fb_std = df_context["composite_score"].std()
        z_mean, z_std = fb_mean, (fb_std if fb_std and fb_std > 0 else 1.0)
    else:
        z_mean, z_std = ref_mean, ref_std

    def _z(series):
        return (series - z_mean) / z_std

    df_context = df_context.assign(composite_zscore=_z(df_context["composite_score"]))
    monitor_row = monitor_row.assign(composite_zscore=_z(monitor_row["composite_score"]))

    # 5. Additional Player Highlighting (Multi)
    remaining_players = sorted(df_context["Player"].tolist())
    highlight_players = st.multiselect("Highlight Additional Players:", options=remaining_players, key="oi_plot_highlight")

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # Color mapping for tiers
    tier_colors = {
        "Elite": "#007d48",
        "Good": "#1151ff",
        "Average": "#0a7281",
        "Below Average": "#d30005",
        "Unknown": "#707072"
    }

    # Plot context points by tier
    for tier, color in tier_colors.items():
        tier_df = df_context[df_context["predicted_tier_label"] == tier]
        if not tier_df.empty:
            ax.scatter(
                tier_df["Age"],
                tier_df["composite_zscore"],
                c=color,
                label=tier,
                alpha=0.5, 
                edgecolors='white', 
                s=60
            )

    # Plot Monitor Player (special styling)
    if not monitor_row.empty:
        ax.scatter(
            monitor_row["Age"],
            monitor_row["composite_zscore"],
            c='gray', # Distinct orange
            edgecolors='gold',
            s=200,
            linewidths=1,
            label="Monitor",
            zorder=5
        )
        # Always label monitor
        ax.annotate(
            monitor_row.iloc[0]["Player"],
            (monitor_row.iloc[0]["Age"], monitor_row.iloc[0]["composite_zscore"]),
            textcoords="offset points", 
            xytext=(0,12), 
            ha='center',
            fontsize=9,
            fontweight='bold',
            color='#d35400'
        )

    # Highlight additional selected players or tiers
    highlight_mask = pd.Series(False, index=df_context.index)
    if highlight_players:
        highlight_mask = highlight_mask | df_context["Player"].isin(highlight_players)
    if selected_tiers and "predicted_tier_label" in df_context.columns:
        highlight_mask = highlight_mask | df_context["predicted_tier_label"].isin(selected_tiers)
        
    highlight_df = df_context[highlight_mask]
    
    if not highlight_df.empty:
        ax.scatter(
            highlight_df["Age"],
            highlight_df["composite_zscore"],
            c='none',
            edgecolors='gray',
            s=69,
            linewidths=1,
            label="Highlighted",
            zorder=4
        )
        # Add labels for highlighted
        for _, row in highlight_df.iterrows():
            ax.annotate(
                row["Player"],
                (row["Age"], row["composite_zscore"]),
                textcoords="offset points", 
                xytext=(0,10), 
                ha='center',
                fontsize=8,
                fontweight='bold',
                color='gray'
            )

    # Add Liga 1-relative reference lines (z-scale)
    ref_label = target_league if ref_ok else "shown cloud"
    ax.axhline(0, color="#0a7281", linestyle='--', alpha=0.5)   # league average
    ax.axhline(1, color='gray', linestyle=':', alpha=0.4)       # +1 std
    ax.axhline(-1, color='gray', linestyle=':', alpha=0.4)      # -1 std
    ax.text(
        ax.get_xlim()[1], 0, f" {ref_label} avg",
        va='center', ha='left', fontsize=8, color="#0a7281",
    )

    # Formatting
    ax.set_title(f"League Fit: {monitor_player} vs {target_league}", fontsize=14, fontweight='bold', color='#111111')
    ax.set_xlabel("Age", fontsize=12)
    ax.set_ylabel(f"Performance vs {target_league} (Z-Score)", fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.legend(title="Performance Tier", bbox_to_anchor=(1.05, 1), loc='upper left')

    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        f"**Y-axis**: standard deviations vs {ref_label} average "
        f"(0 = {ref_label} average, +1 = one std above). "
        f"Monitoring **{monitor_player}** against {len(df_context)} peers. "
        f"Dot colours reflect global performance tiers, not {target_league}-relative tiers."
    )

if __name__ == "__main__":
    # If run directly as a script (unlikely)
    pass
