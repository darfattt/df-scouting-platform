import streamlit as st
from config.stat_categories import STAT_CATEGORIES
from utils.data_loader import get_all_stat_columns
from ui_components import get_relevant_presets, sanitize_key
from config.composite_attributes import COMPOSITE_ATTRIBUTES
from datetime import date

def render_player_finder_page(df_filtered):
    """
    Render Player Finder page content with interactive weight adjustment

    Args:
        df_filtered: Filtered player dataframe
    """
    st.header("Player Finder")

    if len(df_filtered) == 0:
        st.warning(
            "⚠️ No players match the selected filters. Adjust global filters in sidebar."
        )
        return

    # ========== SEARCH MODE SELECTION ==========
    st.markdown("---")
    st.subheader("Search Mode")

    search_mode = st.radio(
        "Find players by:",
        options=["Role", "Responsibility"],
        help="Role = tactical presets (Ball Playing, Poacher, etc.)\nResponsibility = composite attributes (Security, Finishing, etc.)",
        horizontal=True,
        key="player_finder_search_mode",
    )

    st.markdown("---")

    # ========== PAGE OPTIONS SECTION ==========
    st.markdown("### ⚙️ Select Profile")

    col1, col2 = st.columns([3, 1])

    # Get relevant options based on search mode
    if search_mode == "Role":
        # Get relevant role presets based on position data
        relevant_presets = get_relevant_presets(df_filtered)

        with col1:
            selected_preset = st.selectbox(
                "Choose a player profile:",
                options=list(relevant_presets.keys()),
                help="Select a preset to start with. You can adjust weights below.",
                key="preset_selection",
            )

        with col2:
            st.info(f"📊 {len(df_filtered)} players available")

        # Show preset info
        preset_info = relevant_presets[selected_preset]
        st.info(
            f"{preset_info['icon']} **{preset_info['display_name']}** - {preset_info['description']}"
        )

    else:  # Responsibility mode
        # Get all responsibilities
        all_responsibilities = list(COMPOSITE_ATTRIBUTES.keys())

        with col1:
            selected_responsibility = st.selectbox(
                "Select Responsibility:",
                options=all_responsibilities,
                format_func=lambda x: f"{COMPOSITE_ATTRIBUTES[x]['icon']} {COMPOSITE_ATTRIBUTES[x]['display_name']}",
                help="Select a composite attribute to find players who excel in this responsibility",
                key="player_finder_responsibility",
            )

        with col2:
            st.info(f"📊 {len(df_filtered)} players available")

        # Show responsibility info
        responsibility_info = COMPOSITE_ATTRIBUTES[selected_responsibility]
        st.info(
            f"{responsibility_info['icon']} **{responsibility_info['display_name']}** - {responsibility_info['description']}"
        )

        # Show archetypes
        archetypes = responsibility_info.get("archetypes", [])
        if archetypes:
            st.caption(f"**Archetypes:** {', '.join(archetypes)}")

        # Use responsibility_info as preset_info for consistency
        preset_info = responsibility_info

    st.markdown("---")

    # ========== ADVANCED FILTERS SECTION ==========
    st.markdown("### 🎚️ Advanced Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Age Range - PATTERN from Player Similarity
        if "Age" in df_filtered.columns:
            min_age = int(df_filtered["Age"].min())
            max_age = int(df_filtered["Age"].max())
            age_range = st.slider(
                "Age Range:",
                min_value=min_age,
                max_value=max_age,
                value=(min_age, max_age),
                help="Filter by player age range",
                key="player_finder_age_range",
            )
        else:
            age_range = None

    with col2:
        # Minutes Played - DEFAULT: 500 minutes (user preference)
        if "Minutes" in df_filtered.columns:
            min_minutes = st.number_input(
                "Minimum Minutes Played:",
                min_value=0,
                max_value=int(df_filtered["Minutes"].max()),
                value=500,  # DEFAULT: 500 minutes
                step=100,
                help="Filter out players with fewer minutes",
                key="player_finder_min_minutes",
            )
        else:
            min_minutes = 0

    with col3:
        # Contract Expires
        if "Contract expires" in df_filtered.columns:
            contract_date = st.date_input(
                "Contract Expires Before:",
                value=date(2027, 6, 30),
                help="Show only players with contract expiring on or before this date",
                key="player_finder_contract_expires",
            )

            exclude_null_contract = st.checkbox(
                "Exclude players with no contract info",
                value=False,  # Default to including nulls for Player Finder
                help="Hide players who have None/Null contract expiration dates",
                key="player_finder_exclude_null_contract",
            )

            contract_expires_before = contract_date.strftime("%Y-%m-%d")
        else:
            contract_expires_before = None
            exclude_null_contract = False

    st.markdown("---")

    # ========== WEIGHT ADJUSTMENT SECTION ==========
    st.markdown("### ⚖️ Adjust Metric Weights")

    # Get preset metrics and all available stats
    preset_metrics = {
        comp["stat"]: comp["weight"] for comp in preset_info["components"]
    }
    all_stats = get_all_stat_columns(STAT_CATEGORIES)

    # Two-column layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Preset Metrics")
        adjusted_weights = {}

        for metric, default_weight in preset_metrics.items():
            if metric in df_filtered.columns:
                adjusted_weights[metric] = st.slider(
                    metric,
                    min_value=-1.0,
                    max_value=1.0,
                    value=default_weight,
                    step=0.05,
                    help=f"Weight for {metric} (default: {default_weight})",
                    key=sanitize_key(metric, "preset"),
                )
            else:
                st.warning(f"⚠️ {metric} not available in dataset")

    with col2:
        st.markdown("#### ➕ Other Metrics")
        with st.expander("Customize with additional metrics"):
            other_metrics = [
                m
                for m in all_stats
                if m not in preset_metrics.keys() and m in df_filtered.columns
            ]

            if other_metrics:
                additional_weights = {}

                # Group in columns
                metric_cols = st.columns(2)
                for i, metric in enumerate(other_metrics):
                    with metric_cols[i % 2]:
                        include = st.checkbox(
                            metric, key=sanitize_key(metric, "include")
                        )
                        if include:
                            weight = st.slider(
                                "Weight",
                                min_value=-1.0,
                                max_value=1.0,
                                value=0.1,
                                step=0.05,
                                key=sanitize_key(metric, "weight"),
                            )
                            additional_weights[metric] = weight
            else:
                st.info("All metrics already included in preset")
                additional_weights = {}

    # Weight summary
    total_weight = sum(abs(w) for w in adjusted_weights.values())
    if additional_weights:
        total_weight += sum(abs(w) for w in additional_weights.values())

    st.info(f"**Total Weight**: {total_weight:.2f} (will be normalized)")

    st.markdown("---")

    # ========== CALCULATE BUTTON ==========
    if st.button("Calculate Profile Scores", type="primary", use_container_width=True):
        if total_weight == 0:
            st.error("❌ Please set at least one metric weight greater than 0")
        else:
            # Combine weights
            all_weights = adjusted_weights.copy()
            if additional_weights:
                all_weights.update(additional_weights)

            # Create temp preset/responsibility for calculation
            temp_config = {
                "display_name": preset_info["display_name"],
                "description": preset_info["description"],
                "components": [
                    {"stat": k, "weight": v} for k, v in all_weights.items()
                ],
                "icon": preset_info.get("icon", ""),
            }

            # Calculate scores based on search mode
            from utils.player_finder import DefenderScorer

            scorer = DefenderScorer({})  # Initialize with empty presets

            try:
                if search_mode == "Role":
                    # Use calculate_preset_score with temporary preset
                    scorer.presets = {selected_preset: temp_config}
                    results_df, used_weights = scorer.calculate_preset_score(
                        df_filtered,
                        selected_preset,
                        top_n_limit=100,
                        min_minutes=min_minutes,
                        age_range=age_range,
                        contract_expires_before=contract_expires_before,
                        exclude_null_contract=exclude_null_contract,
                    )
                    profile_name = selected_preset
                else:  # Responsibility mode
                    # Use calculate_preset_score with temporary responsibility config
                    scorer.presets = {selected_responsibility: temp_config}
                    results_df, used_weights = scorer.calculate_preset_score(
                        df_filtered,
                        selected_responsibility,
                        top_n_limit=100,
                        min_minutes=min_minutes,
                        age_range=age_range,
                        contract_expires_before=contract_expires_before,
                        exclude_null_contract=exclude_null_contract,
                    )
                    profile_name = selected_responsibility  # Use the key, not display name, to match score column

                if len(results_df) == 0:
                    st.warning("⚠️ No players found with these weights and filters.")
                else:
                    display_label = preset_info.get("display_name", profile_name)
                    st.subheader(f"Top 100 players matching: {display_label}")

                    # Display metrics used
                    with st.expander("Show Metrics & Weights Used", expanded=False):
                        st.write(used_weights)

                    # Display results using the display functions from player_finder
                    from utils.player_finder import display_results_table, display_score_distribution, display_player_detail

                    tab1, tab2, tab3 = st.tabs(["Results Table", "Score Distribution", "Player Detail"])

                    with tab1:
                        display_results_table(results_df, profile_name, used_weights)

                    with tab2:
                        display_score_distribution(results_df, profile_name)

                    with tab3:
                        display_player_detail(results_df, df_filtered, profile_name, used_weights, scorer)

            except Exception as e:
                st.error(f"❌ Error calculating scores: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

