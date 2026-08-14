def render_outliers_analysis_page(df_filtered, selected_position_group):
    """
    Render Outliers Analysis page
    Identifies statistically exceptional players using Z-score and IQR methods

    Args:
        df_filtered: Filtered player dataframe (with percentiles)
        selected_position_group: Currently selected position group
    """
    st.header("📌 Outliers Analysis")

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

    # USER PREFERENCE: Include both raw stats AND composite attributes
    from config.stat_categories import STAT_CATEGORIES
    from config.composite_attributes import COMPOSITE_ATTRIBUTES

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

    # Debug: Show available composite attributes
    if len(all_comp_cols) > 0:
        for col in sorted(all_comp_cols):
            composite_attrs.append(col)
    else:
        # Fallback: Try collecting from COMPOSITE_ATTRIBUTES dict
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
            # Create format function for display names
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

    # ========== ADDITIONAL FILTERS ==========
    st.markdown("### 🎛️ Additional Filters")

    col_min, col_age, col_top = st.columns(3)

    with col_min:
        min_minutes = st.number_input(
            "Minimum Minutes:",
            min_value=0,
            max_value=5000,
            value=300,
            step=100,
            help="Lower values = more players, but less reliable stats",
            key="outliers_min_minutes",
        )

    with col_age:
        age_range = st.slider(
            "Age Range:",
            min_value=16,
            max_value=40,
            value=(18, 35),
            key="outliers_age_range",
        )

    with col_top:
        top_n = st.number_input(
            "Top N Outliers:",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
            help="Number of top outliers to display",
            key="outliers_top_n",
        )

    # Contract expires filter
    contract_expires_before = None
    exclude_null_contract = False
    if "Contract expires" in df_filtered.columns:
        from datetime import date

        col_contract, col_null = st.columns(2)

        with col_contract:
            contract_date = st.date_input(
                "Contract Expires Before:",
                value=date.today(),
                help="Show only players with contract expiring on or before this date",
                key="outliers_contract_expires",
            )
            contract_expires_before = contract_date.strftime("%Y-%m-%d")

        with col_null:
            exclude_null_contract = st.checkbox(
                "Exclude players with no contract info",
                value=False,
                help="Hide players who have None/Null contract expiration dates",
                key="outliers_exclude_null_contract",
            )

    # Apply filters
    df_analysis = df_filtered.copy()

    if "Minutes played" in df_analysis.columns:
        df_analysis = df_analysis[df_analysis["Minutes played"] >= min_minutes]

    if "Age" in df_analysis.columns:
        df_analysis = df_analysis[
            (df_analysis["Age"] >= age_range[0]) & (df_analysis["Age"] <= age_range[1])
        ]

    # Apply contract filter
    if contract_expires_before and "Contract expires" in df_analysis.columns:
        from datetime import datetime

        try:
            cutoff_date = datetime.strptime(contract_expires_before, "%Y-%m-%d")
            df_analysis["contract_date"] = df_analysis["Contract expires"].apply(
                lambda x: datetime.strptime(str(x), "%Y-%m-%d")
                if pd.notna(x) and str(x) != "nan"
                else None
            )

            if exclude_null_contract:
                df_analysis = df_analysis[
                    (df_analysis["contract_date"].notna())
                    & (df_analysis["contract_date"] <= cutoff_date)
                ]
            else:
                df_analysis = df_analysis[
                    (df_analysis["contract_date"].isna())
                    | (df_analysis["contract_date"] <= cutoff_date)
                ]

            df_analysis = df_analysis.drop("contract_date", axis=1)
        except Exception:
            pass  # Skip contract filter if date parsing fails

    if len(df_analysis) == 0:
        st.warning("⚠️ No players match the filter criteria. Try adjusting filters.")
        return

    st.markdown("---")

    # ========== ANALYSIS BUTTON ==========
    if st.button("🔍 Detect Outliers", type="primary", use_container_width=True):
        with st.spinner("Analyzing outliers..."):
            # Debug: Check if metric exists in dataframe
            if selected_metric not in df_analysis.columns:
                st.error(
                    f"❌ Metric '{selected_metric}' not found in filtered data. Available columns: {df_analysis.columns.tolist()[:10]}..."
                )
                return

            # Debug: Check for data variation
            metric_values = df_analysis[selected_metric].dropna()
            if len(metric_values) == 0:
                st.error(
                    f"❌ No valid data for metric '{selected_metric}' (all values are NaN)"
                )
                return

            if metric_values.std() == 0:
                st.warning(
                    f"⚠️ No variation in '{selected_metric}' - all players have similar values (std={metric_values.std():.4f})"
                )
                st.info(f"📊 All values: ~{metric_values.mean():.2f}")
                return

            # Get metric indicator (HIGHER_IS_GOOD or LOWER_IS_GOOD)
            higher_is_good = get_metric_indicator(selected_metric, STAT_CATEGORIES)
            # print(f"metric_values :{metric_values}")
            # Detect outliers based on method
            if method == "Z-Score":
                outliers_df = detect_outliers_zscore(
                    df_analysis,
                    selected_metric,
                    threshold=threshold,
                    higher_is_good=higher_is_good,
                )
            else:
                outliers_df = detect_outliers_iqr(
                    df_analysis,
                    selected_metric,
                    multiplier=threshold,
                    higher_is_good=higher_is_good,
                )

            # Check if outliers were found
            if len(outliers_df) == 0:
                st.warning(
                    f"⚠️ No outliers detected for '{selected_metric}' using {method} method with threshold {threshold}"
                )
                st.info(f"""
                **Suggestions:**
                - Try lowering the threshold (current: {threshold})
                - Check if the metric has enough variation in your filtered dataset
                - Try a different detection method ({("IQR" if method == "Z-Score" else "Z-Score")})
                - Adjust age range or minimum minutes filters to include more players

                **Data Summary:**
                - Players analyzed: {len(df_analysis)}
                - Metric mean: {metric_values.mean():.2f}
                - Metric std: {metric_values.std():.2f}
                - Metric range: {metric_values.min():.2f} - {metric_values.max():.2f}
                """)
                # Clear previous results
                if "outliers_results" in st.session_state:
                    del st.session_state["outliers_results"]
                return

            # Limit to top N
            outliers_df = outliers_df.head(top_n)

            # Store in session state for persistence
            st.session_state["outliers_results"] = outliers_df
            st.session_state["outliers_metric_result"] = selected_metric
            st.session_state["outliers_method_result"] = method
            st.session_state["outliers_position_result"] = selected_position_group

            st.success(f"✅ Found {len(outliers_df)} outliers!")

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
            # Interactive table display
            display_outliers_analysis(
                outliers_df,
                metric,
                method,
                player_info_cols=["Player", "Team", "Position","Age","Passport country","Foot","Height","Weight","Contract expires","Market value"],
            )

        with tab2:
            st.markdown("#### Export Analysis Figure")
            st.markdown(
                "Generate a publication-ready figure for reports and presentations"
            )

            # Generate matplotlib figure
            fig = create_outliers_table_figure(
                outliers_df,
                metric,
                method,
                position,
                df_filtered,
                top_n=min(top_n, len(outliers_df)),
            )

            # Display figure
            st.pyplot(fig)

            # Note about saving
            st.info(
                "💡 Right-click on the figure above to save as image, or use Streamlit's camera icon"
            )

        with tab3:
            st.markdown("#### 📖 How to Interpret Results")

            # USER PREFERENCE: Focus on high performers interpretation
            st.markdown(f"""
            **Method:** {method}

            {
                '''
            - **Z-Score Method**: Measures how many standard deviations a player's stat is from the mean
              - Z-Score > 3.0: Player is in top 0.3% (exceptional outlier)
              - Z-Score > 2.5: Player is in top 1.2% (strong outlier)
              - Higher Z-score = more exceptional performance
            '''
                if method == "Z-Score"
                else '''
            - **IQR Method**: Uses interquartile range to identify outliers
              - Values beyond Q3 + 1.5×IQR are outliers (top ~7% in normal distribution)
              - More robust to extreme values than Z-score
              - IQR Distance = how far beyond the threshold
            '''
            }

            **Context:**
            - Analysis is relative to **{position}** position group only
            - Based on percentile ranks within filtered dataset
            - Metric: **{metric}** ({
                "higher is better"
                if get_metric_indicator(metric, STAT_CATEGORIES)
                else "lower is better"
            })
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
                mean_z = outliers_df["z_score"].mean()
                max_z = outliers_df["z_score"].max()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average Z-Score", f"{mean_z:.2f}")
                with col2:
                    st.metric("Max Z-Score", f"{max_z:.2f}")
            else:
                mean_dist = outliers_df["iqr_distance"].mean()
                max_dist = outliers_df["iqr_distance"].max()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average IQR Distance", f"{mean_dist:.2f}")
                with col2:
                    st.metric("Max IQR Distance", f"{max_dist:.2f}")
