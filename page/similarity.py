import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config.stat_categories import STAT_CATEGORIES
from config.position_groups import POSITION_GROUPS
from config.composite_attributes import COMPOSITE_ATTRIBUTES
from utils.data_loader import get_all_stat_columns, get_player_stats, get_player_composite_attrs
from ui_components import sanitize_key
from utils.player_similarity import SimilarityScorer, create_similarity_table_figure
from utils.similarity_helpers import (
    get_position_similarity_weights,
    get_presets_for_position,
    map_position_to_group,
)
from page.similarity_views import (
    display_similarity_results_table, 
    display_similarity_scatter_plot, 
    display_similarity_scatter_plot_composite, 
    display_similarity_player_detail
)

def get_top_stats_with_weights(
    df_filtered: pd.DataFrame,
    selected_player: str,
    player_position: str,
    top_n: int = 10,
) -> dict:
    """
    Get top individual stats for a position with weights based on player's actual stat values
    """
    from config.position_rankings import POSITION_RANKINGS
    from config.position_groups import POSITION_GROUPS
    from utils.data_loader import get_player_stats
    from config.stat_categories import STAT_CATEGORIES
    from config.composite_attributes import COMPOSITE_ATTRIBUTES

    stat_columns = get_all_stat_columns(STAT_CATEGORIES)

    position_group = None
    for pos_group, pos_list in POSITION_GROUPS.items():
        if pos_list and player_position in pos_list:
            for rank_group in POSITION_RANKINGS.keys():
                if rank_group in pos_group or pos_group in rank_group:
                    position_group = rank_group
                    break
        if position_group:
            break

    if not position_group:
        position_group = list(POSITION_RANKINGS.keys())[0]

    key_composites = POSITION_RANKINGS[position_group]["key_attributes"]

    all_candidate_stats = set()
    for comp_attr in key_composites:
        if comp_attr not in COMPOSITE_ATTRIBUTES:
            continue
        components = COMPOSITE_ATTRIBUTES[comp_attr].get("components", [])
        for comp in components:
            stat_name = comp["stat"]
            if stat_name in stat_columns:
                all_candidate_stats.add(stat_name)

    player_stats = get_player_stats(
        df_filtered, selected_player, list(all_candidate_stats)
    )
    
    stat_percentiles = {}
    for stat_name in all_candidate_stats:
        if stat_name in player_stats:
            stat_percentiles[stat_name] = player_stats[stat_name].get(
                "percentile", 50.0
            )
        else:
            stat_percentiles[stat_name] = 50.0

    sorted_stats = sorted(stat_percentiles.items(), key=lambda x: x[1], reverse=True)
    top_stats = sorted_stats[:top_n]

    total_percentile = sum(stat[1] for stat in top_stats)

    if total_percentile > 0:
        weights = {stat[0]: stat[1] / total_percentile for stat in top_stats}
    else:
        weights = {stat[0]: 1.0 / len(top_stats) for stat in top_stats}

    return weights

def render_player_similarity_page(df_filtered, selected_position_group):
    """
    Render Player Similarity page content
    """
    st.header("Player Similarity")

    if len(df_filtered) == 0:
        st.warning(
            "⚠️ No players match the selected filters. Adjust global filters in sidebar."
        )
        return

    # ========== PAGE OPTIONS SECTION ==========
    col1, col2 = st.columns([3, 1])

    with col1:
        player_names = sorted(df_filtered["Player"].tolist())

        selected_player = st.selectbox(
            "Choose a reference player:",
            options=player_names,
            index=None,
            placeholder="Search for a player...",
            help="Find players similar to this reference player",
            key="similarity_reference_player",
        )

    if not selected_player:
        st.info("☝️ Please select a reference player to begin similarity analysis.")
        return

    # Show reference player info
    ref_player_info = df_filtered[df_filtered["Player"] == selected_player].iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Player", selected_player)
    with col2:
        st.metric("Team", ref_player_info["Team"])
    with col3:
        st.metric("Position", ref_player_info["Position"])
    with col4:
        st.metric("Age", ref_player_info["Age"])

    st.markdown("---")

    stat_columns = get_all_stat_columns(STAT_CATEGORIES)

    with st.expander("⚙️ Reference Player Attributes", expanded=False):
        ref_composite_attrs = get_player_composite_attrs(
            df_filtered, selected_player, COMPOSITE_ATTRIBUTES
        )

        if ref_composite_attrs:
            comp_cols = st.columns(4)
            for idx, (attr_key, attr_data) in enumerate(ref_composite_attrs.items()):
                with comp_cols[idx % 4]:
                    st.metric(
                        label=f"{attr_data['icon']} {attr_data['display_name']}",
                        value=f"{attr_data['score']:.1f}",
                        help=attr_data["description"],
                    )

    st.markdown("---")

    # ========== SIMILARITY METHOD SELECTOR ==========
    st.markdown("### 🎯 Similarity Method")

    col1, col2 = st.columns([3, 2])

    with col1:
        similarity_method = st.selectbox(
            "Choose similarity calculation method:",
            options=["cosine", "euclidean", "pearson"],
            format_func=lambda x: {
                "cosine": "🎨 Cosine Similarity (Style/Pattern Matching)",
                "euclidean": "📊 Euclidean Distance (Performance Matching)",
                "pearson": "🔬 Pearson Correlation (Statistical Fingerprint)",
            }[x],
            index=0,
            key="similarity_method_selector",
        )

    with col2:
        position_method_map = {
            "CB": "cosine", "Fullback": "cosine", "DM": "cosine", "CM": "pearson",
            "AM": "cosine", "Winger": "cosine", "Forward": "euclidean", "Striker": "euclidean",
        }
        recommended_method = position_method_map.get(selected_position_group, "cosine")
        if similarity_method != recommended_method:
            st.info(f"💡 For {selected_position_group}, we recommend **{recommended_method}**")

    st.markdown("---")

    # ========== PRESET SELECTOR SECTION ==========
    player_position = selected_position_group
    available_presets = get_presets_for_position(player_position)

    preset_options = ["Auto (Position-based)"]
    preset_display_map = {"Auto (Position-based)": "auto"}

    for preset in available_presets:
        display_name = preset["display_name"]
        preset_key = preset["key"]
        preset_options.append(display_name)
        preset_display_map[display_name] = preset_key

    with st.expander("🎯 Select Similarity Preset", expanded=False):
        selected_preset_display = st.selectbox(
            "Similarity Profile:",
            options=preset_options,
            index=0,
            key="similarity_preset_selector",
        )
        selected_preset_key = preset_display_map[selected_preset_display]

    # ========== METRIC WEIGHTS SECTION ==========
    st.markdown("### ⚖️ Adjust Metric Weights")

    from config.position_rankings import POSITION_RANKINGS
    player_position = ref_player_info["Position"]

    position_group = None
    for pos_group, pos_list in POSITION_GROUPS.items():
        if pos_list and player_position in pos_list:
            for rank_group in POSITION_RANKINGS.keys():
                if rank_group in pos_group or pos_group in rank_group:
                    position_group = rank_group
                    break
        if position_group:
            break

    if not position_group:
        position_group = list(POSITION_RANKINGS.keys())[0]

    relevant_composites = POSITION_RANKINGS[position_group]["key_attributes"]
    composite_columns = [f"COMP_{attr}" for attr in COMPOSITE_ATTRIBUTES.keys()]

    composite_display_names = {
        f"COMP_{key}": f"{config.get('icon', '')} {config['display_name']}"
        for key, config in COMPOSITE_ATTRIBUTES.items()
    }

    if (
        "selected_player" not in st.session_state
        or st.session_state.selected_player != selected_player
        or st.session_state.get("selected_preset") != selected_preset_key
    ):
        st.session_state.similarity_weights = get_position_similarity_weights(
            df_filtered, selected_player, player_position, preset_key=selected_preset_key,
        )
        st.session_state.selected_player = selected_player
        st.session_state.selected_preset = selected_preset_key

    if "similarity_weights" not in st.session_state:
        st.session_state.similarity_weights = get_position_similarity_weights(
            df_filtered, selected_player, player_position, preset_key="auto"
        )

    with st.expander("⚙️ Configure Metric Weights", expanded=True):
        adjusted_weights = {}
        metric_tab1, metric_tab2 = st.tabs(["Individual Stats", "Attributes"])

        with metric_tab1:
            st.markdown("#### Individual Statistics")
            current_individual_weights = {k: v for k, v in st.session_state.similarity_weights.items() if k in stat_columns}

            if current_individual_weights:
                for metric, default_weight in current_individual_weights.items():
                    weight = st.slider(metric, min_value=0.0, max_value=1.0, value=default_weight, step=0.05, key=sanitize_key(metric, "sim_weight_ind"))
                    adjusted_weights[metric] = weight

            GK_STATS = {"Save rate, %", "Clean sheets", "xG against per 90", "Prevented goals per 90", "Back passes received as GK per 90", "Exits per 90", "Conceded goals per 90"}
            available_stats = [s for s in stat_columns if s not in current_individual_weights and s not in GK_STATS]
            
            if available_stats:
                st.markdown("---")
                additional_stats = st.multiselect("Select additional individual stats to include:", options=available_stats, default=[])

                if additional_stats:
                    player_stats_for_additional = get_player_stats(df_filtered, selected_player, additional_stats)
                    for idx, metric in enumerate(additional_stats):
                        val = player_stats_for_additional[metric].get("percentile", 50.0) if metric in player_stats_for_additional else 50.0
                        default_weight = val / 100.0
                        weight = st.slider(metric, min_value=0.0, max_value=1.0, value=default_weight, step=0.05, key=sanitize_key(metric, "sim_weight_ind_add"))
                        adjusted_weights[metric] = weight

            min_age_df = int(df_filtered["Age"].min())
            max_age_df = int(df_filtered["Age"].max())
            age_range = st.slider("Age Range:", min_value=min_age_df, max_value=max_age_df, value=(22, 35), key="similarity_age_range")

        st.session_state.similarity_weights = adjusted_weights

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        min_minutes = st.number_input("Minimum Minutes Played:", min_value=0, max_value=int(df_filtered["Minutes"].max()), value=500, step=100, key="similarity_min_minutes")

    st.markdown("---")

    if st.button("Find Similar Players", type="primary", key="calculate_similarity"):
        if not adjusted_weights or sum(adjusted_weights.values()) == 0:
            st.error("❌ Please select at least one metric with weight > 0")
        else:
            with st.spinner("Calculating player similarity..."):
                individual_weights = {k: v for k, v in adjusted_weights.items() if k in stat_columns and k in df_filtered.columns}
                if not individual_weights:
                    st.error("❌ Please select at least one individual statistic with weight > 0")
                    return

                scorer = SimilarityScorer(df_filtered, stat_columns, composite_columns)
                try:
                    results_df = scorer.calculate_similarity(
                        reference_player_name=selected_player, weights=individual_weights, method=similarity_method,
                        min_minutes=int(min_minutes), age_range=age_range,
                        same_position_only=False,
                    )

                    if len(results_df) == 0:
                        st.warning("⚠️ No similar players found.")
                    else:
                        result_players = results_df["Player"].tolist() + [selected_player]
                        composite_data = df_filtered[df_filtered["Player"].isin(result_players)][["Player"] + composite_columns]
                        # Deduplicate by Player before merge to prevent fan-out from duplicate rows in df_filtered
                        composite_data = composite_data.drop_duplicates(subset=["Player"], keep="first")
                        common_cols = set(results_df.columns) & set(["Player"] + composite_columns)
                        common_cols.discard("Player")
                        if common_cols:
                            composite_data = composite_data.drop(columns=common_cols)
                        results_df = results_df.merge(composite_data, on="Player", how="left")

                        st.session_state.similarity_results = {
                            "results_df": results_df, "scorer": scorer, "reference_player": selected_player,
                            "weights": individual_weights, "composite_display_names": composite_display_names,
                            "df_filtered": df_filtered, "stat_columns": stat_columns, "composite_columns": composite_columns,
                            "relevant_composites": [f"COMP_{attr}" for attr in relevant_composites],
                        }
                        # Initialize display DataFrame with default top-10 (no post-filters applied yet)
                        st.session_state.similarity_df_display = results_df.head(10).copy()
                        # Drop the method comparison: it belongs to the previous reference player
                        st.session_state.pop("similarity_method_comparison", None)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    if "similarity_results" in st.session_state and st.session_state.similarity_results:
        results = st.session_state.similarity_results
        st.subheader("Similarity Results")

        # ── Post-Analysis Filters ─────────────────────────────────────────────
        exp = st.expander("Refine Results (Filters)", expanded=False)
        with exp:
            c1, c2, c3 = st.columns(3)
            with c1:
                sim_age_range = st.slider("Age Range:", 16, 40, (16, 40), key="sim_results_age_slider")
            with c2:
                sim_top_n = st.number_input("Top N Results:", 5, 500, 10, key="sim_results_top_n")
            with c3:
                sim_pos_group = st.selectbox(
                    "Position Group:",
                    options=["All"] + list(POSITION_GROUPS.keys())[1:],
                    key="sim_results_pos_group",
                )

            c4, c5 = st.columns(2)
            with c4:
                available_feet = ["All"]
                if "Foot" in results["results_df"].columns:
                    available_feet += sorted(results["results_df"]["Foot"].dropna().unique().tolist())
                sim_foot = st.selectbox("Preferred Foot:", options=available_feet, key="sim_results_foot")

                available_countries = sorted(results["results_df"]["Passport country"].dropna().unique().tolist()) if "Passport country" in results["results_df"].columns else []
                sim_passport = st.multiselect("Passport Country:", options=available_countries, key="sim_results_passport")

            with c5:
                sim_use_expiry = st.checkbox("Filter by Contract Expiry", value=False, key="sim_results_use_expiry")
                sim_expiry_date = st.date_input(
                    "Expires Before:",
                    value=pd.Timestamp("2026-08-31"),
                    disabled=not sim_use_expiry,
                    key="sim_results_expiry_date",
                )
                sim_include_no_contract = st.checkbox(
                    "Include players with no contract info",
                    value=True,
                    disabled=not sim_use_expiry,
                    key="sim_results_no_contract",
                )

            if st.button("Apply Filters", key="sim_apply_filters", type="primary"):
                df_temp = results["results_df"].copy()

                if "Age" in df_temp.columns:
                    df_temp = df_temp[(df_temp["Age"] >= sim_age_range[0]) & (df_temp["Age"] <= sim_age_range[1])]

                if sim_pos_group != "All":
                    allowed_positions = POSITION_GROUPS.get(sim_pos_group, [])
                    if allowed_positions:
                        df_temp = df_temp[df_temp["Position"].isin(allowed_positions)]

                if sim_foot != "All" and "Foot" in df_temp.columns:
                    df_temp = df_temp[df_temp["Foot"] == sim_foot]

                if sim_passport and "Passport country" in df_temp.columns:
                    df_temp = df_temp[df_temp["Passport country"].isin(sim_passport)]

                if sim_use_expiry and "Contract expires" in df_temp.columns:
                    df_temp["_exp_temp"] = pd.to_datetime(df_temp["Contract expires"], errors="coerce")
                    if sim_include_no_contract:
                        df_temp = df_temp[
                            df_temp["_exp_temp"].isnull()
                            | (df_temp["_exp_temp"] <= pd.Timestamp(sim_expiry_date))
                        ]
                    else:
                        df_temp = df_temp[
                            df_temp["_exp_temp"].notnull()
                            & (df_temp["_exp_temp"] <= pd.Timestamp(sim_expiry_date))
                        ]
                    df_temp = df_temp.drop(columns=["_exp_temp"])

                df_temp = df_temp.head(int(sim_top_n))
                st.session_state.similarity_df_display = df_temp

        # Ensure display DataFrame is initialized (fallback for first render after calculation)
        if "similarity_df_display" not in st.session_state:
            st.session_state.similarity_df_display = results["results_df"].head(10).copy()

        df_display = st.session_state.similarity_df_display

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Results Table", "Attributes Scatter", "Individual Stats Scatter", "Player Detail", "Method Comparison"])

        with tab1:
            display_similarity_results_table(df_display, results["reference_player"], results["weights"], results["composite_display_names"], results["relevant_composites"])
        with tab2:
            display_similarity_scatter_plot_composite(df_display, results["df_filtered"], results["reference_player"], results["composite_columns"], results["composite_display_names"], results["weights"])
        with tab3:
            display_similarity_scatter_plot(df_display, results["df_filtered"], results["reference_player"], results["stat_columns"], results["weights"])
        with tab4:
            display_similarity_player_detail(df_display, results["scorer"], results["reference_player"], results["weights"])
        with tab5:
            st.subheader("Method Comparison")
            st.caption(
                f"Ranks the top 15 matches for **{results['reference_player']}** under each "
                "similarity method (cosine, euclidean, pearson) using the weights above."
            )

            if st.button("Compare Methods", key="sim_compare_methods", type="primary"):
                try:
                    with st.spinner("Running all three similarity methods..."):
                        st.session_state.similarity_method_comparison = results["scorer"].compare_methods(
                            results["reference_player"],
                            results["weights"],
                            top_n=15,
                            min_minutes=int(min_minutes),
                            age_range=age_range,
                            same_position_only=False,
                        )
                except Exception as e:
                    st.session_state.pop("similarity_method_comparison", None)
                    st.error(f"❌ Method comparison failed: {type(e).__name__}: {e}")

            comparison_df = st.session_state.get("similarity_method_comparison")
            if comparison_df is None:
                st.info("Click **Compare Methods** to score the shortlist with all three methods.")
            elif len(comparison_df) == 0:
                st.warning("⚠️ No players matched the current minutes/age filters.")
            else:
                score_cols = [c for c in ["cosine_score", "euclidean_score", "pearson_score", "average_score"] if c in comparison_df.columns]
                styled = comparison_df.style.format({c: "{:.3f}" for c in score_cols})
                if "average_score" in comparison_df.columns:
                    styled = styled.background_gradient(subset=["average_score"], cmap="YlOrRd")
                st.dataframe(styled, use_container_width=True, hide_index=True)
