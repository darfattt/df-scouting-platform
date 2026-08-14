import streamlit as st
from config.stat_categories import STAT_CATEGORIES, PLAYER_INFO_COLUMNS, PLAYER_COLORS
from config.composite_attributes import COMPOSITE_ATTRIBUTES
from utils.data_loader import get_all_stat_columns, get_player_info, get_player_stats, get_player_composite_attrs
from utils.player_comparison import (
    display_player_comparison,
    create_stats_table,
    display_position_based_rankings,
    display_attribute_rankings_1d_dot,
    display_role_preset_match,
    display_player_info,
)

def render_player_comparison_page(df_filtered, selected_position_group):
    """
    Render Player Comparison page content

    Args:
        df_filtered: Filtered player dataframe
    """
    st.header("Player Comparison")

    if len(df_filtered) == 0:
        st.warning(
            "⚠️ No players match the selected filters. Adjust global filters in sidebar."
        )
        return

    # ========== PAGE OPTIONS SECTION ==========
    col1, col2 = st.columns([2, 1])
    with col1:
        if len(df_filtered) > 0:
            player_names = sorted(df_filtered["Player"].tolist())
            selected_players = st.multiselect(
                "Choose players (2-3):",
                options=player_names,
                max_selections=3,
                help="Select 2-3 players to compare",
                key="selected_players",
            )
        else:
            selected_players = []
            st.warning("No players available")

    with col2:
        st.info(f"📊 {len(df_filtered)} players available")

    st.markdown("---")

    # Show instructions if no players selected
    if len(selected_players) == 0:
        st.info("☝️ Please select at least 2 players from above to begin comparison.")

        # Show stats about the FILTERED dataset
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filtered Players", len(df_filtered))
        with col2:
            avg_age = df_filtered[PLAYER_INFO_COLUMNS["age"]].mean()
            st.metric("Average Age", f"{avg_age:.1f}")
        with col3:
            num_teams = df_filtered[PLAYER_INFO_COLUMNS["team"]].nunique()
            st.metric("Teams", num_teams)

        st.markdown("---")
        st.markdown("#### Available Players")
        st.dataframe(
            df_filtered[
                [
                    PLAYER_INFO_COLUMNS["name"],
                    PLAYER_INFO_COLUMNS["age"],
                    PLAYER_INFO_COLUMNS["team"],
                    PLAYER_INFO_COLUMNS["position"],
                    PLAYER_INFO_COLUMNS["country"],
                    PLAYER_INFO_COLUMNS["minutes"],
                ]
            ].sort_values(PLAYER_INFO_COLUMNS["name"]),
            use_container_width=True,
            hide_index=True,
        )
    elif len(selected_players) < 2:
        st.warning("⚠️ Please select at least 2 players to compare.")
    else:
        # Prepare player data
        players_data = []
        stat_columns = get_all_stat_columns(STAT_CATEGORIES)

        for player_name in selected_players:
            player_info = get_player_info(df_filtered, player_name, PLAYER_INFO_COLUMNS)
            player_stats = get_player_stats(df_filtered, player_name, stat_columns)

            # Get pre-calculated composite attributes from dataframe (already calculated in batch)
            composite_attrs = get_player_composite_attrs(
                df_filtered, player_name, COMPOSITE_ATTRIBUTES
            )

            players_data.append(
                {
                    "info": player_info,
                    "stats": player_stats,
                    "composite_attributes": composite_attrs,
                }
            )

        inferred_position_type = selected_position_group

        # Display comparison
        display_player_comparison(
            players_data, STAT_CATEGORIES, PLAYER_COLORS[: len(selected_players)]
        )

        # Display attribute rankings with 1D dot chart
        # display_attribute_rankings_1d_dot(
        #     players_data,
        #     df_filtered,
        #     inferred_position_type,
        #     PLAYER_COLORS[: len(selected_players)],
        # )

        # Display role/preset match analysis
        # with st.expander("View Role/Preset Match"):
        #     display_role_preset_match(
        #         players_data,
        #         df_filtered,
        #         selected_position_group,
        #         PLAYER_COLORS[: len(selected_players)],
        #     )

        # # Display player info section (always visible)
        # display_player_info(
        #     players_data,
        #     df_filtered,
        #     selected_position_group,
        #     PLAYER_COLORS[: len(selected_players)],
        # )

        # # Display position-based rankings
        # with st.expander("View Position Based Ranking"):
        #     display_position_based_rankings(
        #         players_data,
        #         inferred_position_type,
        #         PLAYER_COLORS[: len(selected_players)],
        #         df_filtered,
        #     )

        # Optional: Show detailed statistics table
        with st.expander("View Detailed Statistics Table"):
            create_stats_table(players_data, STAT_CATEGORIES, df_filtered)
