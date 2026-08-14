"""
Visualization utilities for player comparison charts
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from typing import List, Dict
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import math

from styles.design_system import (
    CANVAS, SOFT_CLOUD, INK, MUTE, HAIRLINE,
    SUCCESS, ALERT, INFO, ACCENT_TEAL,
    apply_nike_style, get_percentile_color,
)


def create_combined_player_chart(
    player_data: Dict,
    stat_categories: Dict,
    player_color: str
):
    """
    Create combined player performance chart with all categories

    Args:
        player_data: Dictionary containing player stats
        stat_categories: Dictionary of all stat categories
        player_color: Primary color for the player

    Returns:
        matplotlib figure
    """
    # Collect all stats from all categories
    all_percentiles = []
    all_colors = []
    all_labels = []
    category_positions = []
    category_names = []

    current_position = 0

    # Process each category in order: Defensive, Progressive, Offensive, General
    for category_key in ['Defensive', 'Progressive', 'Offensive', 'General']:
        if category_key not in stat_categories:
            continue

        category_config = stat_categories[category_key]
        category_stats = category_config['stats']

        # Mark the start position and name of this category
        category_positions.append(current_position + len(category_stats) / 2)
        category_names.append(category_key.upper())

        # Add stats from this category
        for stat in category_stats:
            stat_col = stat['column']
            percentile = player_data['stats'].get(stat_col, {}).get('percentile', 0)
            all_percentiles.append(percentile)
            all_colors.append(get_percentile_color(percentile))
            all_labels.append(stat['display'])
            current_position += 1

    total_stats = len(all_percentiles)

    # Create figure with extra space on left for category labels
    fig, ax = plt.subplots(figsize=(8, total_stats * 0.35 + 1))
    apply_nike_style(fig, ax)

    # Create horizontal bars
    y_positions = range(total_stats)
    bars = ax.barh(
        y_positions,
        all_percentiles,
        color=all_colors,
        alpha=0.85,
        edgecolor='white',
        linewidth=1.5
    )

    # Add percentile text on bars
    for i, (bar, percentile) in enumerate(zip(bars, all_percentiles)):
        width = bar.get_width()
        ax.text(
            width + 2,
            bar.get_y() + bar.get_height() / 2,
            f'{percentile:.0f}',
            va='center',
            fontsize=8,
            fontweight='bold',
            color=INK
        )

    # Add separator lines between categories
    separator_positions = []
    current_pos = 0
    for category_key in ['Defensive', 'Progressive', 'Offensive', 'General']:
        if category_key not in stat_categories:
            continue
        num_stats = len(stat_categories[category_key]['stats'])
        current_pos += num_stats
        if current_pos < total_stats:  # Don't add line after last category
            separator_positions.append(current_pos - 0.5)

    for sep_pos in separator_positions:
        ax.axhline(y=sep_pos, color=HAIRLINE, linestyle='--', linewidth=1.5, alpha=0.5)

    # Customize axes
    ax.set_yticks(y_positions)
    ax.set_yticklabels(all_labels, fontsize=9)
    ax.set_xlabel('Percentile Rank', fontsize=10, fontweight='bold', color=INK)
    ax.set_xlim(0, 105)
    ax.set_xticks([0, 25, 50, 75, 100])

    # Invert y-axis to have first stat on top
    ax.invert_yaxis()

    # Add vertical category labels on the left
    # Adjust the position to be in the left margin
    fig.subplots_adjust(left=0.35)

    for cat_pos, cat_name in zip(category_positions, category_names):
        ax.text(
            110,  # Position in the left margin
            cat_pos,
            cat_name,
            rotation=90,
            va='center',
            ha='center',
            fontsize=11,
            fontweight='bold',
            color=INK,
            bbox=dict(boxstyle='round,pad=0.5', facecolor=SOFT_CLOUD, edgecolor=HAIRLINE, linewidth=1)
        )

    # Adjust layout
    plt.tight_layout()

    return fig


def create_player_header(player_info: Dict, color: str):
    """
    Create a styled player information header

    Args:
        player_info: Dictionary with player information
        color: Color for the header accent

    Returns:
        HTML string for player header
    """
    header_html = f"""
    <div style="
        background: {SOFT_CLOUD};
        border: 1px solid {HAIRLINE};
        border-radius: 0;
        padding: 20px 15px;
        margin: 10px 0 20px 0;
    ">
        <h2 style="margin: 0 0 8px 0; color: {INK}; font-size: 22px; font-weight: 700;
                   border-bottom: 2px solid {color}; padding-bottom: 8px;">
            {player_info['name']}
        </h2>
        <div style="margin: 0; color: {MUTE}; font-size: 13px; line-height: 1.6;">
            <strong>Age:</strong> {player_info['age']} |
            <strong>Position:</strong> {player_info['position']}<br>
            <strong>Team:</strong> {player_info['team']} |
            <strong>Country:</strong> {player_info['country']} | <strong>Min Played:</strong> {player_info['minutes']}
        </div>
    </div>
    """
    return header_html


def display_player_comparison(
    players_data: List[Dict],
    stat_categories: Dict,
    player_colors: List[str]
):
    """
    Display complete player comparison with side-by-side column layout

    Args:
        players_data: List of player data dictionaries
        stat_categories: Dictionary of stat categories
        player_colors: List of colors for players
    """
    num_players = len(players_data)

    # Create columns for each player
    st.markdown("### Player Comparison")

    # Create columns for player headers and combined charts
    cols = st.columns(num_players)

    for idx, (col, player_data) in enumerate(zip(cols, players_data)):
        with col:
            # Display player header
            st.markdown(
                create_player_header(player_data['info'], player_colors[idx]),
                unsafe_allow_html=True
            )

            # Display combined chart with all categories
            fig = create_combined_player_chart(
                player_data,
                stat_categories,
                player_colors[idx]
            )

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)


def create_stats_table(players_data: List[Dict], stat_categories: Dict, df_filtered=None):
    """
    Create a detailed statistics table for selected players

    Args:
        players_data: List of player data dictionaries
        stat_categories: Dictionary of stat categories
        df_filtered: Optional filtered DataFrame to compute rank out of total players
    """
    import pandas as pd

    total_players = len(df_filtered) if df_filtered is not None else None

    for category_key, category_config in stat_categories.items():
        st.markdown(f"#### {category_config['display_name']} - Detailed Stats")

        # Prepare data for table
        table_data = []
        for stat in category_config['stats']:
            row = {'Statistic': stat['display']}
            for player_data in players_data:
                stat_col = stat['column']
                value = player_data['stats'].get(stat_col, {}).get('value', 0)
                percentile = player_data['stats'].get(stat_col, {}).get('percentile', 0)
                if df_filtered is not None and stat_col in df_filtered.columns:
                    series = df_filtered[stat_col].dropna()
                    rank = int((series > value).sum()) + 1
                    row[player_data['info']['name']] = f"{value:.2f} ({percentile:.0f}% | #{rank}/{total_players})"
                else:
                    row[player_data['info']['name']] = f"{value:.2f} ({percentile:.0f}%)"
            table_data.append(row)

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def display_composite_attributes(
    players_data: List[Dict],
    player_colors: List[str]
):
    """
    Display composite attributes comparison for selected players

    Args:
        players_data: List of player data dictionaries (with 'composite_attributes' key)
        player_colors: List of colors for players
    """
    import pandas as pd
    import numpy as np

    st.markdown("---")
    st.markdown("### 📊 Attributes Analysis")
    st.markdown("*Calculated from weighted combinations of key statistics*")

    # Get all attribute names from the first player
    if not players_data or 'composite_attributes' not in players_data[0]:
        st.warning("Composite attributes not calculated for players.")
        return

    attribute_names = list(players_data[0]['composite_attributes'].keys())

    # Create a chart for each attribute showing all players
    for attr_key in attribute_names:
        attr_data = players_data[0]['composite_attributes'][attr_key]
        attr_name = attr_data['display_name']
        attr_icon = attr_data.get('icon', '')
        attr_desc = attr_data.get('description', '')

        # Collect scores for all players
        player_scores = []
        for player_data in players_data:
            score = player_data['composite_attributes'][attr_key]['score']
            player_scores.append({
                'name': player_data['info']['name'],
                'score': score
            })

        # Sort by score descending
        player_scores.sort(key=lambda x: x['score'], reverse=True)

        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, max(2, len(players_data) * 0.6)))
        fig.patch.set_facecolor(CANVAS)
        ax.set_facecolor(SOFT_CLOUD)

        # Prepare data
        names = [p['name'] for p in player_scores]
        scores = [p['score'] for p in player_scores]

        # Assign colors based on original player order
        bar_colors = []
        for player_score in player_scores:
            # Find this player's index in original players_data
            for idx, player_data in enumerate(players_data):
                if player_data['info']['name'] == player_score['name']:
                    bar_colors.append(player_colors[idx])
                    break

        y_positions = range(len(names))
        bars = ax.barh(
            y_positions,
            scores,
            color=bar_colors,
            alpha=0.85,
            edgecolor='white',
            linewidth=2
        )

        # Add score labels on bars
        for i, (bar, score) in enumerate(zip(bars, scores)):
            width = bar.get_width()
            ax.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2,
                f'{score:.1f}',
                va='center',
                fontsize=11,
                fontweight='bold',
                color=INK
            )

        # Add rank numbers
        for i, (bar, rank) in enumerate(zip(bars, range(1, len(names) + 1))):
            ax.text(
                -2,
                bar.get_y() + bar.get_height() / 2,
                f'#{rank}',
                va='center',
                ha='right',
                fontsize=10,
                fontweight='bold',
                color=MUTE
            )

        # Customize axes
        ax.set_yticks(y_positions)
        ax.set_yticklabels(names, fontsize=11, fontweight='bold')
        ax.set_xlabel('Score', fontsize=10, fontweight='bold', color=INK)
        ax.set_title(
            f'{attr_name}\n{attr_desc}',
            fontsize=10,
            fontweight='bold',
            color=INK,
            pad=0
        )

        # Set x-axis limits
        max_score = max(scores) if scores else 100
        ax.set_xlim(0, max_score)

        # Add grid
        ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)

        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color(MUTE)

        # Invert y-axis to show highest score on top
        ax.invert_yaxis()

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)


def display_position_based_rankings(
    players_data: List[Dict],
    position_type: str,
    player_colors: List[str],
    df_filtered: pd.DataFrame = None
):
    """
    Display position-specific rankings for key composite attributes

    Args:
        players_data: List of player data dictionaries (with 'composite_attributes' key)
        position_type: Position type ("DM/CM" or "CB")
        player_colors: List of colors for players
    """
    from config.position_rankings import POSITION_RANKINGS

    if position_type not in POSITION_RANKINGS:
        return

    position_config = POSITION_RANKINGS[position_type]
    key_attributes = position_config['key_attributes']

    st.markdown("---")
    st.markdown("### 🏆 Position-Based Rankings")
    st.markdown(f"*Key attributes for {position_config['display_name']}*")

    # Medal icons for top 3
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    # Create ranking data for each key attribute
    ranking_data = []

    for attr_key in key_attributes:
        # Collect scores for all players for this attribute
        player_scores = []
        for idx, player_data in enumerate(players_data):
            if 'composite_attributes' not in player_data:
                continue

            if attr_key not in player_data['composite_attributes']:
                continue

            score = player_data['composite_attributes'][attr_key]['score']
            player_scores.append({
                'name': player_data['info']['name'],
                'score': score,
                'color': player_colors[idx]
            })

        # Sort by score descending
        player_scores.sort(key=lambda x: x['score'], reverse=True)

        # Build ranking string
        ranking_parts = []
        for rank, player in enumerate(player_scores[:3], 1):  # Top 3 only
            medal = medals.get(rank, "")
            ranking_parts.append(f"{medal} #{rank} {player['name']} ({player['score']:.1f})")

        ranking_string = " • ".join(ranking_parts) if ranking_parts else "N/A"

        # Get attribute display info
        attr_info = players_data[0]['composite_attributes'].get(attr_key, {})
        attr_icon = attr_info.get('icon', '')
        attr_display = attr_info.get('display_name', attr_key)

        ranking_data.append({
            'Attribute': f"{attr_display}",
            'Rankings': ranking_string
        })

    # Display as a styled dataframe
    import pandas as pd
    df_rankings = pd.DataFrame(ranking_data)

    # Custom CSS for the table
    st.markdown("""
    <style>
    .rankings-table {
        font-size: 14px;
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

    st.dataframe(
        df_rankings,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Attribute": st.column_config.TextColumn(
                "Attribute",
                width="medium",
            ),
            "Rankings": st.column_config.TextColumn(
                "Top Players",
                width="large",
            )
        }
    )

    # --- Top 10 Individual Stats section ---
    if df_filtered is not None and len(players_data) > 0:
        SKIP_STATS = {
            'Minutes played', 'Matches played', 'Yellow cards', 'Red cards',
            'Yellow cards per 90', 'Red cards per 90'
        }
        total_players = len(df_filtered)

        st.markdown("---")
        st.markdown("#### Top 10 Individual Stats")
        st.markdown("*Highest-ranked raw statistics vs all players in filtered dataset*")

        cols = st.columns(len(players_data))

        for idx, (col, player_data) in enumerate(zip(cols, players_data)):
            with col:
                player_name = player_data['info']['name']
                color = player_colors[idx] if idx < len(player_colors) else "#ffffff"
                st.markdown(
                    f"<span style='color:{color}; font-weight:bold'>{player_name}</span>",
                    unsafe_allow_html=True,
                )

                stat_rows = []
                for stat_name, stat_vals in player_data.get('stats', {}).items():
                    if stat_name in SKIP_STATS:
                        continue
                    pct = stat_vals.get('percentile', 0) if isinstance(stat_vals, dict) else 0
                    val = stat_vals.get('value', 0) if isinstance(stat_vals, dict) else 0
                    if val == 0 and pct == 0:
                        continue
                    rank = None
                    if stat_name in df_filtered.columns:
                        series = df_filtered[stat_name].dropna()
                        rank = int((series > val).sum()) + 1
                    stat_rows.append({
                        'Stat': stat_name,
                        'Value': round(float(val), 2),
                        'Percentile': float(pct),
                        'Rank': f"#{rank} / {total_players}" if rank is not None else "N/A",
                    })

                stat_rows.sort(key=lambda x: x['Percentile'], reverse=True)
                top10 = stat_rows[:10]

                # Format percentile for display after sorting
                for row in top10:
                    row['Percentile'] = f"{row['Percentile']:.0f}"

                df_top = pd.DataFrame(top10)
                if not df_top.empty:
                    st.dataframe(df_top, use_container_width=True, hide_index=True)
                else:
                    st.info("No stat data available.")


def display_attribute_rankings_1d_dot(
    players_data: List[Dict],
    df_filtered: pd.DataFrame,
    position_type: str,
    player_colors: List[str]
):
    """
    Display attribute rankings for selected players using 1D dot chart

    Shows all players as background gray dots with selected players highlighted
    in their respective colors with labels. Shows rank for relevant composite attributes
    based on position type.

    Args:
        players_data: List of selected player data dictionaries (with 'composite_attributes' key)
        df_filtered: Filtered DataFrame with all players
        position_type: Position type ("CB", "DM/CM", "FB/WB", "CF", "Winger", "AM")
        player_colors: List of colors for selected players
    """
    from config.position_rankings import POSITION_RANKINGS
    from config.composite_attributes import COMPOSITE_ATTRIBUTES

    st.markdown("---")
    st.markdown("### Responsibility Rankings - Distribution")
    st.markdown("*Shows where selected players rank among all players in filtered dataset*")

    if position_type not in POSITION_RANKINGS:
        st.warning(f"Position type '{position_type}' not found in rankings configuration.")
        return

    position_config = POSITION_RANKINGS[position_type]
    print(f"Position Config : {position_config}")
    relevant_attributes = position_config['key_attributes']
    print(f"relevant_attributes : {relevant_attributes}")

    selected_player_names = [p['info']['name'] for p in players_data]

    fig, ax = plt.subplots(figsize=(14, len(relevant_attributes) * 1.2 + 1))
    fig.patch.set_facecolor(CANVAS)
    ax.set_facecolor(SOFT_CLOUD)

    y_positions = []
    attribute_names = []
    attr_display_info = []
    df_attr = None
    max_rank = 100

    for attr_key in relevant_attributes:
        if attr_key not in COMPOSITE_ATTRIBUTES:
            continue

        attr_config = COMPOSITE_ATTRIBUTES[attr_key]
        attr_display = f"{attr_config['display_name']}"
        attribute_names.append(attr_display)
        attr_display_info.append(attr_key)

        comp_col = f"COMP_{attr_key}"

        if comp_col not in df_filtered.columns:
            continue

        y_pos = len(y_positions)
        y_positions.append(y_pos)

        if comp_col not in df_filtered.columns:
            continue

        df_attr = df_filtered[[comp_col, 'Player']].copy()
        df_attr = df_attr.dropna()

        df_attr['rank'] = df_attr[comp_col].rank(method='min', ascending=False)
        max_rank = max(max_rank, df_attr['rank'].max())

        for _, row in df_attr.iterrows():
            player_name = row['Player']
            rank = row['rank']

            jitter = np.random.uniform(-0.15, 0.15)

            if player_name in selected_player_names:
                player_idx = selected_player_names.index(player_name)
                color = player_colors[player_idx]

                ax.scatter(
                    rank,
                    y_pos + jitter,
                    color=color,
                    s=150,
                    alpha=1.0,
                    edgecolor='white',
                    linewidth=2,
                    zorder=10
                )

                ax.annotate(
                    player_name,
                    (rank, y_pos + jitter),
                    xytext=(5, 0),
                    textcoords='offset points',
                    fontsize=5,
                    fontweight='bold',
                    color=INK,
                    va='center',
                    ha='left',
                    # bbox=dict(
                    #     boxstyle='round,pad=0.3',
                    #     facecolor=color + '40',
                    #     edgecolor=color,
                    #     linewidth=1
                    # )
                )
            else:
                ax.scatter(
                    rank,
                    y_pos + jitter,
                    color=MUTE,
                    s=20,
                    alpha=0.3,
                    edgecolor='none',
                    zorder=1
                )

    if not y_positions:
        st.warning("No composite attributes found for the selected position type.")
        plt.close(fig)
        return

    ax.set_yticks(y_positions)
    ax.set_yticklabels(attribute_names, fontsize=11, fontweight='bold')
    ax.set_xlabel('Rank Position', fontsize=12, fontweight='bold', color=INK)

    ax.set_xlim(max_rank, 0)

    ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color(MUTE)

    percentile_positions = [
        {'pct': 0.90, 'color': SUCCESS, 'label': 'Top 10%'},
        {'pct': 0.75, 'color': INFO, 'label': 'Top 25%'},
        {'pct': 0.50, 'color': ACCENT_TEAL, 'label': 'Top 50%'}
    ]

    for pct_info in percentile_positions:
        x_pos = max_rank * (1 - pct_info['pct'])
        ax.axvline(x=x_pos, color=pct_info['color'], linestyle='--', linewidth=1.5, alpha=0.5)
        ax.text(
            x_pos,
            len(y_positions) - 0.5,
            pct_info['label'],
            fontsize=8,
            color=pct_info['color'],
            rotation=0,
            ha='center',
            va='bottom',
            alpha=0.7
        )

    legend_elements = []
    for idx, name in enumerate(selected_player_names):
        legend_elements.append(
            Line2D(
                [0], [0],
                marker='o',
                color='w',
                markerfacecolor=player_colors[idx],
                markersize=10,
                label=name,
                markeredgecolor='white',
                markeredgewidth=2
            )
        )

    legend_elements.append(
        Line2D(
            [0], [0],
            marker='o',
            color='w',
            markerfacecolor=MUTE,
            markersize=6,
            label='Other Players',
            alpha=0.5
        )
    )

    ax.legend(
        handles=legend_elements,
        loc='lower left',
        fontsize=8,
        framealpha=0.85,
        edgecolor=MUTE,
        facecolor='#ffffff'
    )

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def display_role_preset_match(
    players_data: List[Dict],
    df_filtered: pd.DataFrame,
    position_group: str,
    player_colors: List[str]
):
    """
    Display role/preset match ratings for selected players using circle rating system

    Shows how well each player matches different role/preset profiles using
    5-circle rating system (filled = good match, empty = poor match).
    Presets are sorted by score (highest first). Only shows roles relevant to
    each player's position.

    Args:
        players_data: List of selected player data dictionaries (with 'composite_attributes' and 'stats' keys)
        df_filtered: Filtered DataFrame with all players
        position_group: Position group (not used, preserved for compatibility)
        player_colors: List of colors for selected players
    """
    from config.role_definitions import (
        DEFENDER_ROLES as DEFENDER_PRESETS,
        FULLBACK_ROLES as FULLBACK_PRESETS,
        MIDFIELDER_ROLES as MIDFIELDER_PRESETS,
        FORWARD_ROLES as FORWARD_PRESETS,
        ATTACKING_MIDFIELDER_ROLES as ATTACKING_MIDFIELDER_PRESETS
    )
    from utils.data_loader import get_player_stats
    from config.stat_categories import STAT_CATEGORIES
    from config.composite_attributes import COMPOSITE_ATTRIBUTES

    st.markdown("---")
    st.markdown("### Role Analysis")
    st.markdown(f"*Shows how well each player matches different tactical roles for {position_group}*")

    # Map individual positions to relevant preset categories
    position_preset_mapping = {
        # Defender positions
        'CB': DEFENDER_PRESETS,
        'Fullback': FULLBACK_PRESETS,
        'Defender': {**DEFENDER_PRESETS, **FULLBACK_PRESETS},
        'DM': MIDFIELDER_PRESETS,
        'AM': ATTACKING_MIDFIELDER_PRESETS,
        'Midfielder': {**MIDFIELDER_PRESETS, **ATTACKING_MIDFIELDER_PRESETS},

        'Winger': ATTACKING_MIDFIELDER_PRESETS,
        # Centre Forward positions
        'CF': FORWARD_PRESETS,
        'Forward': {**ATTACKING_MIDFIELDER_PRESETS, **FORWARD_PRESETS},
        'default': {**DEFENDER_PRESETS, **FORWARD_PRESETS, **ATTACKING_MIDFIELDER_PRESETS}
    }

    num_players = len(players_data)

    # Create columns for each player
    cols = st.columns(num_players)

    for idx, (col, player_data) in enumerate(zip(cols, players_data)):
        with col:
            player_name = player_data['info']['name']
            player_position = player_data['info']['position']

            st.markdown(f"#### {player_name}")
            st.caption(f"**Position:** {player_position}")

            # Get relevant presets based on this player's actual position
            relevant_presets = position_preset_mapping.get(
                position_group,
                position_preset_mapping['default']
            )

            # Calculate scores for all relevant presets
            preset_scores = []

            for preset_key, preset_config in relevant_presets.items():
                preset_icon = ''#preset_config.get('icon', '')
                preset_display = preset_config['display_name']

                # Calculate weighted score for this player
                components = preset_config.get('components', [])
                total_weight = 0
                weighted_sum = 0

                for component in components:
                    stat_name = component['stat']
                    weight = component['weight']

                    if stat_name in player_data['stats']:
                        stat_value = player_data['stats'][stat_name].get('percentile', 50.0)
                        weighted_sum += abs(weight) * stat_value
                        total_weight += abs(weight)

                # Normalize to 0-100 scale
                if total_weight > 0:
                    normalized_score = weighted_sum / total_weight
                else:
                    normalized_score = 50.0

                preset_scores.append({
                    'key': preset_key,
                    'icon': preset_icon,
                    'display': preset_display,
                    'score': normalized_score
                })

            # Sort by score descending (highest first)
            preset_scores.sort(key=lambda x: x['score'])

            # Create visualization
            fig, ax = plt.subplots(figsize=(9, len(preset_scores) * 0.7 + 1.5))
            fig.patch.set_facecolor(CANVAS)
            ax.set_facecolor(SOFT_CLOUD)

            y_positions = range(len(preset_scores))
            preset_labels = [f"{ps['icon']} {ps['display']}" for ps in preset_scores]

            for y_pos, preset_score in enumerate(preset_scores):
                score = preset_score['score']
                color = player_colors[idx]

                

                # Draw 5 circles based on score
                circle_spacing = 1
                num_circles = 8
                last_circle_x = (num_circles - 1) * circle_spacing + 0.5
                score_x = last_circle_x + 0.6

                # Calculate number of filled circles (0-num_circles scale)
                circle_scale = 100/num_circles
                num_filled = int(score / circle_scale)
                partial_fill = (score % circle_scale) / circle_scale

                circle_size = 1600
                empty_color = HAIRLINE

                for circle_idx in range(num_circles):
                    x_pos = circle_idx * circle_spacing + 0.5
                    #x_pos = (num_circles - 1) * circle_spacing + 0.5

                    if circle_idx < num_filled:
                        fill_color = color
                        alpha = 1.0
                        edgecolor = 'white'
                        linewidth = 2
                    elif circle_idx == num_filled and partial_fill > 0:
                        fill_color = color
                        alpha = 0.4
                        edgecolor = 'white'
                        linewidth = 1
                    else:
                        fill_color = empty_color
                        alpha = 0.8
                        edgecolor = MUTE
                        linewidth = 0.5

                    ax.scatter(
                        x_pos,
                        y_pos,
                        s=circle_size,
                        c=fill_color,
                        alpha=alpha,
                        edgecolor=edgecolor,
                        linewidth=linewidth,
                        zorder=10
                    )

                # Add score label
                ax.text(
                    score_x,
                    y_pos,
                    f'{score:.0f}',
                    va='center',
                    ha='left',
                    fontsize=11,
                    fontweight='bold',
                    color=INK
                )

            ax.set_yticks(y_positions)
            ax.set_yticklabels(preset_labels, fontsize=10, fontweight='bold')
            ax.set_xlabel('Role Rating', fontsize=10, fontweight='bold', color=INK)

            #ax.set_xlim(-0.5, 12.5)
            #ax.set_xlim(-0.2, 5 * circle_spacing + 2.5)
            ax.set_xlim(-0.3, score_x + 0.8)
            ax.set_ylim(-0.5, len(preset_scores) - 0.5)

            ax.grid(axis='y', alpha=0.2, linestyle='-', linewidth=0.5)
            ax.set_axisbelow(True)

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(MUTE)
            ax.spines['bottom'].set_color(MUTE)
            ax.set_xticks([])

            # Add legend for circles
            #legend_text = "●●●●● = Excellent Match | ●●●○○ = Good Match | ○○○○○ = Poor Match"
            legend_text = None
            ax.text(
                0,
                len(preset_scores) + 0.2,
                legend_text,
                fontsize=8,
                color=MUTE,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffffff', edgecolor=MUTE, linewidth=1)
            )

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)


def get_extended_player_info(df_filtered: pd.DataFrame, player_name: str) -> Dict:
    """
    Extract extended player metadata including team logo, height, foot

    Args:
        df_filtered: Filtered DataFrame with all players
        player_name: Name of the player

    Returns:
        Dictionary with extended player metadata
    """
    player_row = df_filtered[df_filtered['Player'] == player_name].iloc[0]

    # Get age and round it
    age = player_row.get('Age', 0)
    age_rounded = int(round(age)) if pd.notna(age) else 0

    # Get foot and capitalize
    foot = player_row.get('Foot', 'Unknown')
    if pd.isna(foot) or foot == '':
        foot_formatted = 'Unknown'
    else:
        foot_formatted = str(foot).capitalize()  # Left -> Left, right -> Right, etc.

    # Use 'Matches played' instead of 'Matches'
    matches = player_row.get('Matches played', player_row.get('Matches', 0))

    return {
        'name': player_row.get('Full name', 'Unknown'),
        'age': age_rounded,  # CHANGED: Now rounded
        'team': player_row.get('Team', 'Unknown'),
        'team_logo': player_row.get('Team logo', None),  # URL or None
        'country': player_row.get('Birth country', 'Unknown'),
        'position': player_row.get('Position', 'Unknown'),
        'minutes': player_row.get('Minutes played', 0),
        'matches': matches,  # CHANGED: Now uses 'Matches played'
        'height': player_row.get('Height', None),  # May be NaN
        'foot': foot_formatted  # CHANGED: Now capitalized
    }


def calculate_top_roles(df_filtered: pd.DataFrame, player_name: str, position_group: str, top_n: int = 5) -> List[Dict]:
    """
    Calculate role match scores for player, return top N

    Args:
        df_filtered: Filtered DataFrame with all players
        player_name: Name of the player
        position_group: Position group (CB, DM, AM, etc.)
        top_n: Number of top roles to return

    Returns:
        List of top N roles with scores
    """
    from config.role_definitions import (
        DEFENDER_ROLES,
        FULLBACK_ROLES,
        MIDFIELDER_ROLES,
        FORWARD_ROLES,
        ATTACKING_MIDFIELDER_ROLES
    )

    # Map position_group to role config
    position_role_mapping = {
        'CB': DEFENDER_ROLES,
        'Fullback': FULLBACK_ROLES,
        'DM': MIDFIELDER_ROLES,
        'CM': MIDFIELDER_ROLES,
        'AM': ATTACKING_MIDFIELDER_ROLES,
        'Winger': ATTACKING_MIDFIELDER_ROLES,
        'Forward': FORWARD_ROLES,
        'Striker': FORWARD_ROLES
    }

    role_config = position_role_mapping.get(position_group, MIDFIELDER_ROLES)
    player_row = df_filtered[df_filtered['Player'] == player_name].iloc[0]

    role_scores = []
    for role_name, role_def in role_config.items():
        total_weight = 0
        weighted_sum = 0

        for component in role_def['components']:
            stat_name = component['stat']
            weight = component['weight']

            # Use percentile if use_percentile=True, else raw value
            if component.get('use_percentile', True):
                stat_value = player_row.get(stat_name, 50.0)  # Default 50th percentile
            else:
                stat_value = player_row.get(stat_name, 0)

            weighted_sum += abs(weight) * stat_value
            total_weight += abs(weight)

        # Normalize to 0-100 scale
        if total_weight > 0:
            normalized_score = weighted_sum / total_weight
        else:
            normalized_score = 50.0

        role_scores.append({
            'role_name': role_def['display_name'],
            'score': normalized_score,
            'icon': role_def.get('icon', '⚽')
        })

    # Sort and return top N
    role_scores.sort(key=lambda x: x['score'], reverse=True)
    return role_scores[:top_n]


def calculate_top_responsibilities(player_data: Dict, position_group: str, top_n: int = 5) -> List[Dict]:
    """
    Calculate top responsibilities (composite attributes) for a player

    Args:
        player_data: Player data dictionary with composite_attributes
        position_group: Position group (CB, DM, AM, etc.)
        top_n: Number of top responsibilities to return

    Returns:
        List of top N responsibilities with scores and components
    """
    from config.position_rankings import POSITION_RANKINGS
    from config.composite_attributes import COMPOSITE_ATTRIBUTES

    if position_group not in POSITION_RANKINGS:
        # Default to all attributes if position not in rankings
        relevant_attributes = list(player_data.get('composite_attributes', {}).keys())
    else:
        position_config = POSITION_RANKINGS[position_group]
        relevant_attributes = position_config.get('key_attributes', [])

    responsibilities = []
    for attr_key in relevant_attributes:
        if attr_key not in player_data.get('composite_attributes', {}):
            continue

        attr_data = player_data['composite_attributes'][attr_key]

        # Get components from COMPOSITE_ATTRIBUTES
        components = []
        if attr_key in COMPOSITE_ATTRIBUTES:
            components = COMPOSITE_ATTRIBUTES[attr_key].get('components', [])

        responsibilities.append({
            'attr_key': attr_key,
            'display_name': attr_data.get('display_name', attr_key),
            'score': attr_data.get('score', 0),
            'icon': attr_data.get('icon', ''),
            'components': components
        })

    # Sort by score descending
    responsibilities.sort(key=lambda x: x['score'], reverse=True)
    return responsibilities[:top_n]


def calculate_league_rankings(df_filtered: pd.DataFrame, player_name: str, top_role_name: str, top_resp_attr_key: str, position_group: str) -> Dict:
    """
    Calculate player's rank within filtered leagues for top role and responsibility

    Args:
        df_filtered: Filtered DataFrame with all players
        player_name: Name of the player
        top_role_name: Top role name
        top_resp_attr_key: Top responsibility attribute key
        position_group: Position group for role calculation

    Returns:
        Dictionary with rankings for role and responsibility
    """
    from config.role_definitions import (
        DEFENDER_ROLES,
        FULLBACK_ROLES,
        MIDFIELDER_ROLES,
        FORWARD_ROLES,
        ATTACKING_MIDFIELDER_ROLES
    )

    # Map position_group to role config
    position_role_mapping = {
        'CB': DEFENDER_ROLES,
        'Fullback': FULLBACK_ROLES,
        'DM': MIDFIELDER_ROLES,
        'CM': MIDFIELDER_ROLES,
        'AM': ATTACKING_MIDFIELDER_ROLES,
        'Winger': ATTACKING_MIDFIELDER_ROLES,
        'Forward': FORWARD_ROLES,
        'Striker': FORWARD_ROLES
    }

    role_config = position_role_mapping.get(position_group, MIDFIELDER_ROLES)

    # Find the role definition
    role_def = None
    for role_key, role_data in role_config.items():
        if role_data['display_name'] == top_role_name:
            role_def = role_data
            break

    # Calculate role scores for all players
    if role_def:
        role_scores = []
        for _, player_row in df_filtered.iterrows():
            total_weight = 0
            weighted_sum = 0

            for component in role_def['components']:
                stat_name = component['stat']
                weight = component['weight']

                if component.get('use_percentile', True):
                    stat_value = player_row.get(stat_name, 50.0)
                else:
                    stat_value = player_row.get(stat_name, 0)

                weighted_sum += abs(weight) * stat_value
                total_weight += abs(weight)

            if total_weight > 0:
                normalized_score = weighted_sum / total_weight
            else:
                normalized_score = 50.0

            role_scores.append(normalized_score)

        df_filtered = df_filtered.copy()
        df_filtered['_role_score'] = role_scores
        df_filtered['_role_rank'] = df_filtered['_role_score'].rank(method='min', ascending=False)

        player_role_rank = df_filtered[df_filtered['Player'] == player_name]['_role_rank'].iloc[0]
        role_total = len(df_filtered)
    else:
        player_role_rank = 0
        role_total = len(df_filtered)

    # Responsibility ranking (use pre-calculated COMP_ column)
    comp_col = f'COMP_{top_resp_attr_key}'
    if comp_col in df_filtered.columns:
        df_filtered = df_filtered.copy()
        df_filtered['_resp_rank'] = df_filtered[comp_col].rank(method='min', ascending=False)
        player_resp_rank = df_filtered[df_filtered['Player'] == player_name]['_resp_rank'].iloc[0]
        resp_total = len(df_filtered)
    else:
        player_resp_rank = 0
        resp_total = len(df_filtered)

    from config.composite_attributes import COMPOSITE_ATTRIBUTES
    resp_display_name = COMPOSITE_ATTRIBUTES.get(top_resp_attr_key, {}).get('display_name', top_resp_attr_key)

    return {
        'role': {
            'name': top_role_name,
            'rank': int(player_role_rank),
            'total': role_total
        },
        'responsibility': {
            'name': resp_display_name,
            'rank': int(player_resp_rank),
            'total': resp_total
        }
    }


def create_player_info_card(player_info_extended: Dict, player_color: str, fig_width: int = 6) -> plt.Figure:
    """
    Create player metadata card with 2-column label-on-top format

    Args:
        player_info_extended: Extended player metadata
        player_color: Color for the player
        fig_width: Width of the figure

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(fig_width, 5))
    fig.patch.set_facecolor(CANVAS)
    ax.set_facecolor(SOFT_CLOUD)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Accent border on left
    ax.plot([0.2, 0.2], [0.5, 9.5], color=player_color, linewidth=8, solid_capstyle='round')

    # Player name at top (centered, large)
    ax.text(5, 8.5, player_info_extended['name'], fontsize=22, fontweight='bold',
            ha='center', va='center', color=INK)

    # 2-column grid with labels on top
    y_start = 6.5
    row_spacing = 2.0
    col1_x_label = 1.5
    col1_x_value = 1.5
    col2_x_label = 6
    col2_x_value = 6
    label_offset = 0.6  # Offset for value below label

    # Row 1: Position | Pref. Foot
    ax.text(col1_x_label, y_start, 'Position:', fontsize=10, fontweight='bold', ha='left', color=MUTE)
    ax.text(col1_x_value, y_start - label_offset, player_info_extended['position'],
            fontsize=13, ha='left', color=INK, fontweight='bold')

    ax.text(col2_x_label, y_start, 'Pref. Foot:', fontsize=10, fontweight='bold', ha='left', color=MUTE)
    ax.text(col2_x_value, y_start - label_offset, player_info_extended['foot'],
            fontsize=13, ha='left', color=INK, fontweight='bold')

    # Row 2: Nationality | Height
    y_row2 = y_start - row_spacing
    ax.text(col1_x_label, y_row2, 'Nationality:', fontsize=10, fontweight='bold', ha='left', color=MUTE)
    ax.text(col1_x_value, y_row2 - label_offset, player_info_extended['country'],
            fontsize=13, ha='left', color=INK, fontweight='bold')

    height_display = f"{int(player_info_extended['height'])} cm" if pd.notna(player_info_extended['height']) else 'N/A'
    ax.text(col2_x_label, y_row2, 'Height:', fontsize=10, fontweight='bold', ha='left', color=MUTE)
    ax.text(col2_x_value, y_row2 - label_offset, height_display,
            fontsize=13, ha='left', color=INK, fontweight='bold')

    # Row 3: Match/Minutes | Age
    y_row3 = y_row2 - row_spacing
    matches_minutes = f"{player_info_extended['matches']} / {player_info_extended['minutes']} min"
    ax.text(col1_x_label, y_row3, 'Match/Minutes:', fontsize=10, fontweight='bold', ha='left', color=MUTE)
    ax.text(col1_x_value, y_row3 - label_offset, matches_minutes,
            fontsize=13, ha='left', color=INK, fontweight='bold')

    ax.text(col2_x_label, y_row3, 'Age:', fontsize=10, fontweight='bold', ha='left', color=MUTE)
    ax.text(col2_x_value, y_row3 - label_offset, str(player_info_extended['age']),
            fontsize=13, ha='left', color=INK, fontweight='bold')

    # Team name at bottom
    ax.text(5, 0.8, player_info_extended['team'], fontsize=14, fontweight='bold',
            ha='center', va='center', color=MUTE)

    plt.tight_layout()
    return fig


def create_top_roles_circles(top_roles: List[Dict], player_color: str) -> plt.Figure:
    """
    Create top 5 roles visualization using multi-circle rating pattern

    Follows the pattern from display_role_preset_match() where each role
    is shown with 8 circles (filled/partial/empty) representing the score.

    Args:
        top_roles: List of top roles with scores (0-100)
        player_color: Color for the player's filled circles

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(CANVAS)
    ax.set_facecolor(SOFT_CLOUD)

    # Constants (from display_role_preset_match)
    num_circles = 8
    circle_spacing = 1.0
    circle_size = 1600
    empty_color = HAIRLINE

    # Process top 5 roles
    for y_pos, role in enumerate(top_roles[:5]):
        score = role['score']
        role_name = role['role_name']

        # Calculate filled circles from 0-100 score
        circle_scale = 100 / num_circles
        num_filled = int(score / circle_scale)
        partial_fill = (score % circle_scale) / circle_scale

        # Draw 8 circles for this role
        for circle_idx in range(num_circles):
            x_pos = circle_idx * circle_spacing + 0.5

            # Determine fill state (3 states)
            if circle_idx < num_filled:
                # FULLY FILLED
                fill_color = player_color
                alpha = 1.0
                edgecolor = 'white'
                linewidth = 2

            elif circle_idx == num_filled and partial_fill > 0:
                # PARTIALLY FILLED
                fill_color = player_color
                alpha = 0.4
                edgecolor = 'white'
                linewidth = 1

            else:
                # EMPTY
                fill_color = empty_color
                alpha = 0.8
                edgecolor = MUTE
                linewidth = 0.5

            # Render circle
            ax.scatter(
                x_pos,
                y_pos,
                s=circle_size,
                c=fill_color,
                alpha=alpha,
                edgecolor=edgecolor,
                linewidth=linewidth,
                zorder=10
            )

        # Add role name label (left side)
        ax.text(
            -0.5,
            y_pos,
            role_name,
            ha='right',
            va='center',
            fontsize=10,
            fontweight='bold',
            color=INK
        )

        # Add score label (right side)
        last_circle_x = (num_circles - 1) * circle_spacing + 0.5  # 7.5
        score_x = last_circle_x + 0.6  # 8.1

        ax.text(
            score_x,
            y_pos,
            f'{score:.0f}',
            ha='left',
            va='center',
            fontsize=11,
            fontweight='bold',
            color=INK
        )

    # Configure axes (hide everything except labels)
    ax.set_xlim(-3, 9.5)  # Space for role names and scores
    ax.set_ylim(-0.5, len(top_roles[:5]) - 0.5)
    ax.set_xticks([])
    ax.set_yticks([])

    # Remove all spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Add subtle grid (optional)
    ax.grid(axis='y', alpha=0.2, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    return fig


def create_top_responsibilities_dots(
    top_responsibilities: List[Dict],
    player_name: str,
    player_color: str,
    df_filtered: pd.DataFrame,
    fig_width: int = 14
) -> plt.Figure:
    """
    Create responsibilities visualization showing all players as gray, highlighting selected

    Args:
        top_responsibilities: List of top responsibilities with scores
        player_name: Name of the player
        player_color: Color for the player
        df_filtered: Filtered DataFrame with all players
        fig_width: Width of the figure

    Returns:
        Matplotlib figure
    """
    # PATTERN: Follow display_attribute_rankings_1d_dot() logic
    top_responsibilities = sorted(
        top_responsibilities,
        key=lambda r: r.get("value", 0),
        reverse=True
    )

    fig, ax = plt.subplots(figsize=(fig_width, len(top_responsibilities) * 0.2 + 1))
    fig.patch.set_facecolor(CANVAS)
    ax.set_facecolor(SOFT_CLOUD)

    y_positions = []
    attribute_names = []
    max_rank = 100
    n_resp = len(top_responsibilities)

    for idx, resp in enumerate(top_responsibilities):
        attr_key = resp['attr_key']
        comp_col = f"COMP_{attr_key}"

        if comp_col not in df_filtered.columns:
            continue

        y_pos = n_resp - 1 - idx   # invert Y so best is on top
        y_positions.append(y_pos)
        attribute_names.append(f"{resp['display_name']}")

        # Calculate ranks for all players
        df_attr = df_filtered[[comp_col, 'Player']].copy().dropna()
        df_attr['rank'] = df_attr[comp_col].rank(method='min', ascending=False)
        max_rank = max(max_rank, df_attr['rank'].max())

        # Draw all players as gray dots with jitter
        for _, row in df_attr.iterrows():
            p_name = row['Player']
            rank = row['rank']
            jitter = np.random.uniform(-0.01, 0.05)

            if p_name == player_name:
                # Highlighted player (selected)
                ax.scatter(rank, y_pos + jitter, color=player_color, s=150, alpha=1.0,
                           edgecolor='white', linewidth=2, zorder=10)
                ax.annotate(p_name, (rank, y_pos + jitter), xytext=(5, 0),
                            textcoords='offset points', fontsize=3, fontweight='bold',
                            color=INK, va='center', ha='left')
            else:
                # Gray background dots
                ax.scatter(rank, y_pos + jitter, color=MUTE, s=20, alpha=0.3,
                           edgecolor='none', zorder=1)

    # Configure axes
    print(f"y_positions {y_positions}")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(attribute_names, fontsize=11, fontweight='bold')
    #ax.set_xlabel('Rank Position', fontsize=12, fontweight='bold', color=INK)
    ax.set_xlim(max_rank, 0)  # Inverted: rank 1 on right
    #ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color(MUTE)

    # Add percentile reference lines
    for pct_info in [{'pct': 0.90, 'color': SUCCESS, 'label': 'Top 10%'},
                     {'pct': 0.75, 'color': INFO, 'label': 'Top 25%'},
                     {'pct': 0.50, 'color': ACCENT_TEAL, 'label': 'Top 50%'}]:
        x_pos = max_rank * (1 - pct_info['pct'])
        ax.axvline(x=x_pos, color=pct_info['color'], linestyle='--', linewidth=1.5, alpha=0.5)

    plt.tight_layout()
    return fig


def create_responsibility_spider_chart(responsibility_dict: Dict, player_stats: Dict, player_color: str, fig_width: int = 5) -> plt.Figure:
    """
    Create spider/radar chart for responsibility components

    Args:
        responsibility_dict: Responsibility data with components
        player_stats: Player statistics
        player_color: Color for the player
        fig_width: Width of the figure

    Returns:
        Matplotlib figure
    """
    from math import pi

    components = responsibility_dict['components']
    N = len(components)

    if N == 0:
        # Empty chart if no components
        fig, ax = plt.subplots(figsize=(fig_width, fig_width))
        fig.patch.set_facecolor(CANVAS)
        ax.set_facecolor(SOFT_CLOUD)
        ax.text(0.5, 0.5, 'No components', ha='center', va='center', transform=ax.transAxes)
        ax.axis('off')
        return fig

    # Extract component values
    values = []
    labels = []
    for comp in components:
        stat_name = comp['stat']
        # Use percentile values
        if comp.get('use_percentile', True):
            value = player_stats.get(stat_name, {}).get('percentile', 50.0)
        else:
            # If raw value, we need to convert to percentile-like scale
            value = player_stats.get(stat_name, {}).get('percentile', 50.0)

        values.append(value)
        # Shorten label for readability
        label_short = stat_name[:20] + '...' if len(stat_name) > 20 else stat_name
        labels.append(label_short)

    # Close the polygon (first value repeated at end)
    values += values[:1]

    # Calculate angles
    theta = [2 * pi * i / N for i in range(N)]
    theta += theta[:1]

    # Create polar plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_width), subplot_kw=dict(projection='polar'))
    fig.patch.set_facecolor(CANVAS)
    ax.set_facecolor(SOFT_CLOUD)

    # Plot data
    ax.plot(theta, values, 'o-', linewidth=2, color=player_color)
    ax.fill(theta, values, alpha=0.25, color=player_color)

    # Configure radial axis (0-100 for percentiles)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(['25', '50', '75', '100'], fontsize=7, color=MUTE)

    # Set theta labels
    ax.set_xticks(theta[:-1])
    ax.set_xticklabels(labels, fontsize=7, color=INK)

    # Grid
    ax.grid(True, linestyle='--', alpha=0.3)

    plt.tight_layout()
    return fig


def create_empty_altair_chart(message: str) -> alt.Chart:
    """
    Create empty Altair chart with message

    Args:
        message: Message to display

    Returns:
        Altair chart object
    """
    df_empty = pd.DataFrame({'x': [0], 'y': [0], 'message': [message]})
    return alt.Chart(df_empty).mark_text(
        fontSize=14,
        color=MUTE
    ).encode(
        x=alt.value(200),
        y=alt.value(200),
        text='message:N'
    ).properties(
        width=400,
        height=400,
        background=CANVAS
    )


def create_responsibility_radar_chart_altair(
    responsibility_dict: Dict,
    player_stats: Dict,
    player_color: str,
    fig_width: int = 5
) -> alt.Chart:
    """
    Create radar/spider chart for responsibility components using Altair

    Args:
        responsibility_dict: Responsibility data with components
        player_stats: Player statistics
        player_color: Color for the player
        fig_width: Width of the figure (used for sizing)

    Returns:
        Altair chart object
    """
    components = responsibility_dict['components']
    N = len(components)

    if N == 0:
        # Return empty chart with message
        return create_empty_altair_chart("No components")

    # Extract component values and labels
    values = []
    labels = []
    for comp in components:
        stat_name = comp['stat']
        # Use percentile values
        if comp.get('use_percentile', True):
            value = player_stats.get(stat_name, {}).get('percentile', 50.0)
        else:
            value = player_stats.get(stat_name, {}).get('percentile', 50.0)

        values.append(value)
        # Shorten label for readability
        label_short = stat_name[:20] + '...' if len(stat_name) > 20 else stat_name
        labels.append(label_short)

    # Calculate angles (in radians)
    angles = [2 * math.pi * i / N for i in range(N)]

    # Close the polygon
    values_closed = values + [values[0]]
    labels_closed = labels + [labels[0]]
    angles_closed = angles + [angles[0]]

    # Convert to Cartesian coordinates for Altair
    x_coords = []
    y_coords = []
    for angle, value in zip(angles_closed, values_closed):
        # Normalize value to 0-1 range for radius
        radius = value / 100.0
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        x_coords.append(x)
        y_coords.append(y)

    # Create DataFrame for radar data
    df_radar = pd.DataFrame({
        'x': x_coords,
        'y': y_coords,
        'value': values_closed,
        'label': labels_closed
    })

    # Layer 1: Grid circles (background)
    grid_data = []
    for pct in [25, 50, 75, 100]:
        circle_points = 100
        for i in range(circle_points + 1):
            angle = 2 * math.pi * i / circle_points
            radius = pct / 100.0
            grid_data.append({
                'x': radius * math.cos(angle),
                'y': radius * math.sin(angle),
                'percentile': pct
            })

    df_grid = pd.DataFrame(grid_data)

    grid_layer = alt.Chart(df_grid).mark_line(
        strokeDash=[3, 3],
        opacity=0.3,
        color=MUTE
    ).encode(
        x=alt.X('x:Q', scale=alt.Scale(domain=[-1.2, 1.2]), axis=None),
        y=alt.Y('y:Q', scale=alt.Scale(domain=[-1.2, 1.2]), axis=None),
        detail='percentile:N'
    )

    # Layer 2: Axis lines (spokes)
    axis_data = []
    for i, angle in enumerate(angles):
        axis_data.append({'x': 0, 'y': 0, 'axis_id': i})
        axis_data.append({
            'x': math.cos(angle),
            'y': math.sin(angle),
            'axis_id': i
        })

    df_axes = pd.DataFrame(axis_data)

    axes_layer = alt.Chart(df_axes).mark_line(
        color=MUTE,
        opacity=0.5
    ).encode(
        x='x:Q',
        y='y:Q',
        detail='axis_id:N'
    )

    # Layer 3: Data area (filled polygon)
    area_layer = alt.Chart(df_radar).mark_area(
        opacity=0.25,
        color=player_color
    ).encode(
        x='x:Q',
        y='y:Q',
        order=alt.Order('label:N', sort='ascending')
    )

    # Layer 4: Data line (polygon outline)
    line_layer = alt.Chart(df_radar).mark_line(
        color=player_color,
        size=2
    ).encode(
        x='x:Q',
        y='y:Q',
        order=alt.Order('label:N', sort='ascending'),
        tooltip=[
            alt.Tooltip('label:N', title='Metric'),
            alt.Tooltip('value:Q', title='Percentile', format='.1f')
        ]
    )

    # Layer 5: Data points
    points_layer = alt.Chart(df_radar).mark_point(
        filled=True,
        size=100,
        color=player_color
    ).encode(
        x='x:Q',
        y='y:Q',
        tooltip=[
            alt.Tooltip('label:N', title='Metric'),
            alt.Tooltip('value:Q', title='Percentile', format='.1f')
        ]
    )

    # Layer 6: Axis labels
    label_data = []
    for angle, label in zip(angles, labels):
        label_radius = 1.15  # Just outside the 100% circle
        label_data.append({
            'x': label_radius * math.cos(angle),
            'y': label_radius * math.sin(angle),
            'label': label,
            'angle': angle
        })

    df_labels = pd.DataFrame(label_data)

    labels_layer = alt.Chart(df_labels).mark_text(
        fontSize=8,
        fontWeight='bold',
        color=INK,
        align='center'
    ).encode(
        x='x:Q',
        y='y:Q',
        text='label:N'
    )

    # Combine all layers
    chart = (
        grid_layer + axes_layer + area_layer + line_layer + points_layer + labels_layer
    ).properties(
        width=fig_width * 100,  # Convert to pixels
        height=fig_width * 100,
        background=CANVAS  # Match matplotlib styling
    ).configure_view(
        strokeWidth=0
    )

    return chart


def display_player_info(
    players_data: List[Dict],
    df_filtered: pd.DataFrame,
    position_group: str,
    player_colors: List[str]
):
    """
    Display player profiles vertically stacked (not horizontal columns)

    Args:
        players_data: List of player data dictionaries
        df_filtered: Filtered DataFrame with all players
        position_group: Position group (CB, DM, AM, etc.)
        player_colors: List of colors for players
    """
    st.markdown("---")
    st.markdown("### 📋 Player Profiles")
    st.markdown("*Comprehensive player information with roles, responsibilities, and rankings*")

    # Loop through each player vertically (NOT using columns)
    for idx, (player_data, color) in enumerate(zip(players_data, player_colors)):
        player_name = player_data['info']['name']

        # Player section header
        st.markdown(f"### {player_name}")

        # Section 1: Player Info Card (full width)
        player_info_ext = get_extended_player_info(df_filtered, player_name)
        fig = create_player_info_card(player_info_ext, color)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        # Section 2: Top 5 Roles (5 columns circles)
        # st.markdown("#### Top 5 Roles")
        # top_roles = calculate_top_roles(df_filtered, player_name, position_group)
        # fig = create_top_roles_circles(top_roles, color)
        # st.pyplot(fig, use_container_width=True)
        # plt.close(fig)

        # Section 3: Top 5 Responsibilities (with all players context)
        st.markdown("#### Top 5 Responsibilities")
        top_responsibilities = calculate_top_responsibilities(player_data, position_group)
        fig = create_top_responsibilities_dots(top_responsibilities, player_name, color, df_filtered)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        # Section 4: Spider Charts (5 columns)
        st.markdown("#### Responsibility Breakdown")
        if len(top_responsibilities) > 0:
            spider_cols = st.columns(min(len(top_responsibilities), 5))
            for spider_col, resp in zip(spider_cols, top_responsibilities[:5]):
                with spider_col:
                    st.caption(resp['display_name'])
                    fig = create_responsibility_spider_chart(resp, player_data['stats'], color, fig_width=3)
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)

        # Section 5: League Rankings
        # st.markdown("#### League Rankings")
        # if len(top_roles) > 0 and len(top_responsibilities) > 0:
        #     rankings = calculate_league_rankings(
        #         df_filtered, player_name, top_roles[0]['role_name'],
        #         top_responsibilities[0]['attr_key'], position_group
        #     )
        #     st.markdown(f"**#{rankings['role']['rank']}** in {rankings['role']['name']} out of **{rankings['role']['total']}** players")
        #     st.markdown(f"**#{rankings['responsibility']['rank']}** in {rankings['responsibility']['name']} out of **{rankings['responsibility']['total']}** players")

        # Separator between players (except for last player)
        if idx < len(players_data) - 1:
            st.markdown("---")
