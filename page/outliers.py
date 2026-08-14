import streamlit as st
import pandas as pd
from config.stat_categories import STAT_CATEGORIES
from config.composite_attributes import COMPOSITE_ATTRIBUTES
from config.grade_attributes import GRADE_ATTRIBUTES
from config.position_groups import (
    POSITION_GROUPS, 
    filter_by_position_group, 
    get_group_for_position
)
from config.role_definitions import get_all_roles
from config.registry import get_roles_for_position, get_responsibilities_for_position
from utils.data_loader import calculate_grade_attributes_batch
from utils.outlier_detection import (
    detect_outliers_zscore,
    detect_outliers_iqr,
    create_outliers_table_figure,
    display_outliers_analysis,
    get_metric_indicator,
)


def render_outliers_analysis_page(df_filtered, selected_position_group):
    """
    Render Outliers Analysis page
    Identifies statistically exceptional players using Z-score and IQR methods

    Args:
        df_filtered: Filtered player dataframe (with percentiles)
        selected_position_group: Currently selected position group
    """
    st.header("Outliers Analysis")

    # Empty data check
    if len(df_filtered) == 0:
        st.warning(
            "⚠️ No players match the selected filters. Adjust global filters in sidebar."
        )
        return

    st.markdown(
        "Identify exceptional players who significantly outperform their position group"
    )

    # ========== METHOD SELECTION ==========
    st.markdown("### 🔬 Detection Method")

    col_method, col_threshold = st.columns([2, 1])

    with col_method:
        method = st.radio(
            "Statistical Method:",
            options=["Z-Score", "IQR"],
            horizontal=True,
            help="Z-Score: Standard deviations from mean | IQR: Interquartile range method",
            key="outliers_method",
        )

    with col_threshold:
        if method == "Z-Score":
            threshold = st.number_input(
                "Z-Score Threshold:",
                min_value=1.0,
                max_value=4.0,
                value=2.5,
                step=0.1,
                help="Lenient: 2.0 (top 2.3%), Standard: 2.5 (top 0.6%), Strict: 3.0 (top 0.13%)",
                key="outliers_zscore_threshold",
            )
        else:
            threshold = st.number_input(
                "IQR Multiplier:",
                min_value=1.0,
                max_value=3.0,
                value=1.5,
                step=0.1,
                help="Standard: 1.5, Strict: 2.0, Lenient: 1.0",
                key="outliers_iqr_multiplier",
            )

    st.markdown("---")

    # ========== METRIC SELECTION ==========
    st.markdown("### 📊 Metric Selection")

    # Collect raw stats
    all_stats = []
    for category_name, category_data in STAT_CATEGORIES.items():
        for stat in category_data.get("stats", []):
            col = stat["column"]
            if col in df_filtered.columns:
                all_stats.append(col)

    # Collect composite attributes (COMP_*)
    composite_attrs = []
    all_comp_cols = [col for col in df_filtered.columns if col.startswith("COMP_")]

    if len(all_comp_cols) > 0:
        for col in sorted(all_comp_cols):
            composite_attrs.append(col)
    else:
        for comp_name in COMPOSITE_ATTRIBUTES.keys():
            col = f"COMP_{comp_name}"
            if col in df_filtered.columns:
                composite_attrs.append(col)

    if not all_stats and not composite_attrs:
        st.error("No statistical columns available in filtered data")
        return

    # Debug info (collapsible)
    with st.expander("ℹ️ Available Metrics Info", expanded=False):
        st.write(f"**Raw Stats Available:** {len(all_stats)}")
        st.write(f"**Composite Attributes Available:** {len(composite_attrs)}")
        st.write(f"**Total Players in Filtered Data:** {len(df_filtered)}")
        if len(composite_attrs) > 0:
            st.write("Sample composite attributes:", composite_attrs[:5])

    # Metric selector with source type grouping
    col_metric, col_source = st.columns([3, 1])

    with col_source:
        metric_source = st.radio(
            "Metric Type:",
            options=["Raw Stats", "Composite Attributes", "Grades"],
            key="outliers_metric_source",
            help="Raw Stats: Individual statistics | Composite: Weighted combinations | Grades: Skill-based grading",
        )

    grade_display_names = {}

    if metric_source == "Raw Stats":
        # Category filter for raw stats
        col_category, _ = st.columns([1, 2])
        with col_category:
            category_filter = st.selectbox(
                "Category:",
                options=["All"] + list(STAT_CATEGORIES.keys()),
                key="outliers_category_filter",
            )

        # Filter stats by category
        if category_filter != "All":
            filtered_stats = [
                stat["column"]
                for stat in STAT_CATEGORIES[category_filter].get("stats", [])
                if stat["column"] in df_filtered.columns
            ]
        else:
            filtered_stats = all_stats

        available_metrics = sorted(filtered_stats)
    elif metric_source == "Grades":
        # Calculate grades on-demand
        grade_cols = [f"GRADE_{name}" for name in GRADE_ATTRIBUTES.keys()]
        missing_grades = [col for col in grade_cols if col not in df_filtered.columns]

        if missing_grades:
            with st.spinner("Calculating grades..."):
                df_filtered = calculate_grade_attributes_batch(
                    df_filtered, GRADE_ATTRIBUTES
                )

        # Create display names mapping
        grade_display_names = {
            f"GRADE_{key}": f"{config['display_name']} ({config['icon']})"
            for key, config in GRADE_ATTRIBUTES.items()
        }

        available_metrics = sorted(grade_cols)
    else:
        # Use composite attributes
        available_metrics = sorted(composite_attrs)

    with col_metric:
        if len(available_metrics) > 0:
            if metric_source == "Grades":
                selected_metric = st.selectbox(
                    "Select Metric:",
                    options=available_metrics,
                    index=0,
                    format_func=lambda x: grade_display_names.get(x, x),
                    help="Choose which statistic to analyze for outliers (single metric only)",
                    key="outliers_selected_metric",
                )
            else:
                selected_metric = st.selectbox(
                    "Select Metric:",
                    options=available_metrics,
                    index=0,
                    help="Choose which statistic to analyze for outliers (single metric only)",
                    key="outliers_selected_metric",
                )
        else:
            st.error("No metrics available for selected category")
            return

    st.markdown("---")

    # ========== INITIAL FILTERS ==========
    st.markdown("### 🎛️ 1. Define Initial Context")

    col_min, col_info = st.columns([1, 2])

    with col_min:
        min_minutes = st.number_input(
            "Minimum Minutes Played:",
            min_value=0,
            max_value=5000,
            value=300,
            step=100,
            help="Lower values = more players, but less reliable stats",
            key="outliers_min_minutes",
        )
    with col_info:
        st.info("💡 Detection will be performed on players meeting this threshold. Advanced filters appear after detection.")

    # Apply initial filter for detection
    df_analysis_base = df_filtered.copy()
    if "Minutes played" in df_analysis_base.columns:
        df_analysis_base = df_analysis_base[df_analysis_base["Minutes played"] >= min_minutes]

    if len(df_analysis_base) == 0:
        st.warning("⚠️ No players match the minimum minutes criteria. Try a lower value.")
        return

    st.markdown("---")

    # ========== ANALYSIS BUTTON ==========
    if st.button("🔍 Detect Outliers", type="primary", use_container_width=True):
        with st.spinner("Analyzing outliers..."):
            if selected_metric not in df_analysis_base.columns:
                st.error(f"❌ Metric '{selected_metric}' not found in filtered data.")
                return

            metric_values = df_analysis_base[selected_metric].dropna()
            if len(metric_values) == 0:
                st.error(f"❌ No valid data for metric '{selected_metric}' (all values are NaN)")
                return

            if metric_values.std() == 0:
                st.warning(f"⚠️ No variation in '{selected_metric}' - all players have similar values")
                return

            # Get metric indicator
            higher_is_good = get_metric_indicator(selected_metric, STAT_CATEGORIES)

            # Detect outliers based on method
            if method == "Z-Score":
                outliers_df = detect_outliers_zscore(
                    df_analysis_base,
                    selected_metric,
                    threshold=threshold,
                    higher_is_good=higher_is_good,
                )
            else:
                outliers_df = detect_outliers_iqr(
                    df_analysis_base,
                    selected_metric,
                    multiplier=threshold,
                    higher_is_good=higher_is_good,
                )

            # Check if outliers were found
            if len(outliers_df) == 0:
                st.warning(f"⚠️ No outliers detected for '{selected_metric}' using {method} method with threshold {threshold}")
                if "outliers_results" in st.session_state:
                    del st.session_state["outliers_results"]
                return

            # Store in session state for persistence
            st.session_state["outliers_results"] = outliers_df
            st.session_state["outliers_metric_result"] = selected_metric
            st.session_state["outliers_method_result"] = method
            st.session_state["outliers_position_result"] = selected_position_group

            st.success(f"✅ Found {len(outliers_df)} potential outliers!")

    # ========== RESULTS DISPLAY ==========
    if (
        "outliers_results" in st.session_state
        and len(st.session_state["outliers_results"]) > 0
    ):
        st.markdown("---")
        st.markdown("### 📈 Analysis Results")

        raw_outliers_df = st.session_state["outliers_results"]
        metric = st.session_state["outliers_metric_result"]
        method = st.session_state["outliers_method_result"]
        # Note: position used for export figure context
        position = st.session_state["outliers_position_result"]

        # --- Advanced Secondary Filters (Post-detection) ---
        exp = st.expander("🛠️ Refine Results (Filters)", expanded=True)
        with exp:
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                age_range = st.slider("Age Range:", 16, 40, (18, 35), key="outliers_age_slider")
            with f_col2:
                top_n = st.number_input("Top N Outliers:", 1, 500, 20, key="outliers_top_n_refined")
            with f_col3:
                # Use standard POSITION_GROUPS for filtering
                pos_group = st.selectbox("Position Group:", options=["All"] + list(POSITION_GROUPS.keys())[1:], key="outliers_pos_group_refined")
            
            f_col4, f_col5 = st.columns(2)
            with f_col4:
                use_expiry = st.checkbox("Filter by Contract Expiry", value=False, key="outliers_use_expiry")
                expiry_date = st.date_input("Expires Before:", value=pd.Timestamp.now().date(), disabled=not use_expiry, key="outliers_expiry_date")
            with f_col5:
                include_no_contract = st.checkbox("Include players with no contract info", value=True, key="outliers_no_contract")

        # Apply secondary filters to results
        df_display = raw_outliers_df.copy()
        
        if "Age" in df_display.columns:
            df_display = df_display[(df_display["Age"] >= age_range[0]) & (df_display["Age"] <= age_range[1])]
            
        if pos_group != "All":
            df_display = filter_by_position_group(df_display, pos_group)
            
        if use_expiry and "Contract expires" in df_display.columns:
            # Robust date parsing
            df_display["exp_temp"] = pd.to_datetime(df_display["Contract expires"], errors='coerce')
            if include_no_contract:
                df_display = df_display[df_display["exp_temp"].isnull() | (df_display["exp_temp"] <= pd.Timestamp(expiry_date))]
            else:
                df_display = df_display[df_display["exp_temp"].notnull() & (df_display["exp_temp"] <= pd.Timestamp(expiry_date))]
            df_display = df_display.drop(columns=["exp_temp"])

        # Limit to top N after all filters
        df_display = df_display.head(top_n)

        if df_display.empty:
            st.warning("⚠️ No outliers match the refined filter criteria. Adjust the settings above.")
            return

        # --- Calculate Tactical Columns for Display ---
        all_roles = get_all_roles()
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
            
            # Identify Archetypes
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

    # ========== RESULTS DISPLAY ==========
    if (
        "outliers_results" in st.session_state
        and len(st.session_state["outliers_results"]) > 0
    ):
        st.markdown("---")
        st.markdown("### 📈 Analysis Results")

        outliers_df = st.session_state["outliers_results"]
        metric = st.session_state["outliers_metric_result"]
        method = st.session_state["outliers_method_result"]
        position = st.session_state["outliers_position_result"]

        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(
            ["📊 Outliers Table", "📄 Export Figure", "📖 Interpretation"]
        )

        with tab1:
            # Prepare the requested player info columns (excluding score/metric/outlier_type as display_outliers_analysis adds them)
            requested_info_cols = [
                "Player", "Full name", "Primary position", "Position", "Best Role", "Top Archetypes", "Age",
                "Passport country", "Foot", "Height", "Weight", 
                "Contract expires", "Market value",
                "Team", "League", "Matches played", "Minutes played"
            ]
            
            display_outliers_analysis(
                df_display,
                metric,
                method,
                player_info_cols=requested_info_cols,
            )

        with tab2:
            st.markdown("#### Export Analysis Figure")
            st.markdown(
                "Generate a publication-ready figure for reports and presentations"
            )

            fig = create_outliers_table_figure(
                df_display,
                metric,
                method,
                position,
                df_filtered,
                top_n=min(top_n, len(df_display)),
            )

            st.pyplot(fig)

            st.info(
                "💡 Right-click on the figure above to save as image, or use Streamlit's camera icon"
            )

        with tab3:
            st.markdown("#### 📖 How to Interpret Results")

            method_explanation = ""
            if method == "Z-Score":
                method_explanation = """
            - **Z-Score Method**: Measures how many standard deviations a player's stat is from the mean
              - Z-Score > 3.0: Player is in top 0.3% (exceptional outlier)
              - Z-Score > 2.5: Player is in top 1.2% (strong outlier)
              - Higher Z-score = more exceptional performance
            """
            else:
                method_explanation = """
            - **IQR Method**: Uses interquartile range to identify outliers
              - Values beyond Q3 + 1.5×IQR are outliers (top ~7% in normal distribution)
              - More robust to extreme values than Z-score
              - IQR Distance = how far beyond the threshold
            """

            higher_text = (
                "higher is better"
                if get_metric_indicator(metric, STAT_CATEGORIES)
                else "lower is better"
            )

            st.markdown(f"""
            **Method:** {method}

            {method_explanation}

            **Context:**
            - Analysis is relative to **{position}** position group only
            - Based on percentile ranks within filtered dataset
            - Metric: **{metric}** ({higher_text})
            - **Focus: HIGH PERFORMERS ONLY** - identifying exceptional positive talent

            **Scouting Application:**
            - Outliers represent exceptional talent in specific attributes
            - Single metric analysis provides clear, interpretable results
            - Cross-reference with other metrics for complete player profile
            - Consider league context (different competitive levels)
            - Use for initial screening, validate with video analysis
            """)

            # Statistical summary
            if method == "Z-Score":
                mean_z = df_display["z_score"].mean()
                max_z = df_display["z_score"].max()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average Z-Score", f"{mean_z:.2f}")
                with col2:
                    st.metric("Max Z-Score", f"{max_z:.2f}")
            else:
                mean_dist = df_display["iqr_distance"].mean()
                max_dist = df_display["iqr_distance"].max()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average IQR Distance", f"{mean_dist:.2f}")
                with col2:
                    st.metric("Max IQR Distance", f"{max_dist:.2f}")
