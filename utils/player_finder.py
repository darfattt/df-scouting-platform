"""
Player Finder visualization with defender preset scoring
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple
from config.stat_categories import is_lower_better


class DefenderScorer:
    """Calculate weighted scores for defender presets"""

    def __init__(self, presets: Dict):
        """
        Args:
            presets: DEFENDER_PRESETS dictionary
        """
        self.presets = presets

    def calculate_preset_score(
        self,
        df: pd.DataFrame,
        preset_name: str,
        top_n_limit: int = 30,
        min_minutes: int = 0,
        age_range: tuple = None,
        contract_expires_before: str = None,
        exclude_null_contract: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Calculate weighted score for all players using preset

        Args:
            df: DataFrame with player data
            preset_name: Key from DEFENDER_PRESETS
            top_n_limit: Return only top N players
            min_minutes: Minimum minutes played filter
            age_range: (min_age, max_age) tuple for age filtering
            contract_expires_before: Contract expiry date filter (YYYY-MM-DD format)
            exclude_null_contract: If True, exclude players with null contract dates

        Returns:
            (result_df, normalized_weights)
        """
        preset = self.presets[preset_name]
        components = preset['components']

        # Extract weights and validate metrics exist
        weights = {}
        for comp in components:
            metric = comp['stat']
            if metric not in df.columns:
                raise ValueError(f"Metric '{metric}' not found in dataframe")
            weights[metric] = comp['weight']

        # Normalize weights to sum to 1.0
        total_weight = sum(abs(w) for w in weights.values())
        normalized_weights = {k: v/total_weight for k, v in weights.items()}

        # Apply filters BEFORE scoring calculation
        df_copy = df.copy()

        # Minutes filter
        if 'Minutes' in df_copy.columns:
            df_copy = df_copy[df_copy['Minutes'] >= min_minutes]

        # Age filter
        if age_range and 'Age' in df_copy.columns:
            min_age, max_age = age_range
            df_copy = df_copy[(df_copy['Age'] >= min_age) & (df_copy['Age'] <= max_age)]

        # Contract filter with exclude_null_contract logic
        if contract_expires_before and 'Contract expires' in df_copy.columns:
            from datetime import datetime
            try:
                cutoff_date = datetime.strptime(contract_expires_before, '%Y-%m-%d')
                df_copy['contract_date'] = df_copy['Contract expires'].apply(
                    lambda x: datetime.strptime(str(x), '%Y-%m-%d') if pd.notna(x) and str(x) != 'nan' else None
                )

                if exclude_null_contract:
                    df_copy = df_copy[(df_copy['contract_date'].notna()) &
                                     (df_copy['contract_date'] <= cutoff_date)]
                else:
                    df_copy = df_copy[(df_copy['contract_date'].isna()) |
                                     (df_copy['contract_date'] <= cutoff_date)]

                df_copy = df_copy.drop('contract_date', axis=1)
            except Exception:
                pass  # Skip contract filter if date parsing fails

        # Calculate normalized scores (0-100 scale)
        result_df = df_copy.copy()
        weighted_scores = pd.Series(0.0, index=df_copy.index)

        for metric, weight in normalized_weights.items():
            col_values = df_copy[metric]
            col_min = col_values.min()
            col_max = col_values.max()

            if col_max == col_min:
                normalized_values = pd.Series(50.0, index=df_copy.index)
            else:
                # Normalize to 0-100 scale
                if is_lower_better(metric) and weight < 0:
                    # Negative metric with negative weight: invert normalization
                    normalized_values = 100 - ((col_values - col_min) / (col_max - col_min) * 100)
                else:
                    normalized_values = (col_values - col_min) / (col_max - col_min) * 100

            # Add weighted contribution
            weighted_scores += normalized_values * abs(weight)

        # Add score to result
        score_column = f'{preset_name.replace(" ", "_")}_Score'
        result_df[score_column] = weighted_scores

        # Sort by score (descending)
        result_df = result_df.sort_values(score_column, ascending=False).reset_index(drop=True)
        result_df['Rank'] = range(1, len(result_df) + 1)

        # Calculate percentile rank
        percentile_column = f'{score_column}_Percentile'
        result_df[percentile_column] = result_df[score_column].rank(pct=True) * 100

        # Return top N players only
        top_players = result_df.head(top_n_limit)

        # Select relevant columns (including new player info columns)
        display_cols = [
            'Rank', 'Player', 'Team', 'Position', 'Age',
            'Birth country', 'Height', 'Contract expires', 'Market value',  # New columns
            score_column, percentile_column
        ] + list(normalized_weights.keys())

        # Filter to only include columns that exist
        display_cols = [col for col in display_cols if col in top_players.columns]

        return top_players[display_cols], normalized_weights

    def calculate_responsibility_score(
        self,
        df: pd.DataFrame,
        responsibility_name: str,
        composite_attributes: Dict,
        top_n_limit: int = 30,
        min_minutes: int = 0,
        age_range: tuple = None,
        contract_expires_before: str = None,
        exclude_null_contract: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Calculate weighted score for all players using composite attribute (responsibility)

        Args:
            df: DataFrame with player data
            responsibility_name: Key from COMPOSITE_ATTRIBUTES
            composite_attributes: COMPOSITE_ATTRIBUTES dictionary
            top_n_limit: Return only top N players
            min_minutes: Minimum minutes played filter
            age_range: (min_age, max_age) tuple for age filtering
            contract_expires_before: Contract expiry date filter (YYYY-MM-DD format)
            exclude_null_contract: If True, exclude players with null contract dates

        Returns:
            (result_df, normalized_weights)
        """
        responsibility = composite_attributes[responsibility_name]
        components = responsibility['components']

        # Extract weights and validate metrics exist
        weights = {}
        for comp in components:
            metric = comp['stat']
            if metric not in df.columns:
                raise ValueError(f"Metric '{metric}' not found in dataframe")
            weights[metric] = comp['weight']

        # Normalize weights to sum to 1.0
        total_weight = sum(abs(w) for w in weights.values())
        normalized_weights = {k: v/total_weight for k, v in weights.items()}

        # Apply filters BEFORE scoring calculation
        df_copy = df.copy()

        # Minutes filter
        if 'Minutes' in df_copy.columns:
            df_copy = df_copy[df_copy['Minutes'] >= min_minutes]

        # Age filter
        if age_range and 'Age' in df_copy.columns:
            min_age, max_age = age_range
            df_copy = df_copy[(df_copy['Age'] >= min_age) & (df_copy['Age'] <= max_age)]

        # Contract filter with exclude_null_contract logic
        if contract_expires_before and 'Contract expires' in df_copy.columns:
            from datetime import datetime
            try:
                cutoff_date = datetime.strptime(contract_expires_before, '%Y-%m-%d')
                df_copy['contract_date'] = df_copy['Contract expires'].apply(
                    lambda x: datetime.strptime(str(x), '%Y-%m-%d') if pd.notna(x) and str(x) != 'nan' else None
                )

                if exclude_null_contract:
                    df_copy = df_copy[(df_copy['contract_date'].notna()) &
                                     (df_copy['contract_date'] <= cutoff_date)]
                else:
                    df_copy = df_copy[(df_copy['contract_date'].isna()) |
                                     (df_copy['contract_date'] <= cutoff_date)]

                df_copy = df_copy.drop('contract_date', axis=1)
            except Exception:
                pass  # Skip contract filter if date parsing fails

        # Calculate normalized scores (0-100 scale)
        result_df = df_copy.copy()
        weighted_scores = pd.Series(0.0, index=df_copy.index)

        for metric, weight in normalized_weights.items():
            col_values = df_copy[metric]
            col_min = col_values.min()
            col_max = col_values.max()

            if col_max == col_min:
                normalized_values = pd.Series(50.0, index=df_copy.index)
            else:
                # Normalize to 0-100 scale
                if is_lower_better(metric) and weight < 0:
                    # Negative metric with negative weight: invert normalization
                    normalized_values = 100 - ((col_values - col_min) / (col_max - col_min) * 100)
                else:
                    normalized_values = (col_values - col_min) / (col_max - col_min) * 100

            # Add weighted contribution
            weighted_scores += normalized_values * abs(weight)

        # Add score to result
        score_column = f'{responsibility_name.replace(" ", "_")}_Score'
        result_df[score_column] = weighted_scores

        # Sort by score (descending)
        result_df = result_df.sort_values(score_column, ascending=False).reset_index(drop=True)
        result_df['Rank'] = range(1, len(result_df) + 1)

        # Calculate percentile rank
        percentile_column = f'{score_column}_Percentile'
        result_df[percentile_column] = result_df[score_column].rank(pct=True) * 100

        # Return top N players only
        top_players = result_df.head(top_n_limit)

        # Select relevant columns (including new player info columns)
        display_cols = [
            'Rank', 'Player', 'Team', 'Position', 'Age',
            'Birth country', 'Height', 'Contract expires', 'Market value',  # New columns
            score_column, percentile_column
        ] + list(normalized_weights.keys())

        # Filter to only include columns that exist
        display_cols = [col for col in display_cols if col in top_players.columns]

        return top_players[display_cols], normalized_weights

    def get_metric_contributions(
        self,
        df: pd.DataFrame,
        player_idx: int,
        preset_name: str
    ) -> Dict[str, Dict]:
        """
        Get individual metric contributions to a player's total score

        Args:
            df: DataFrame with player data
            player_idx: Index of player in dataframe
            preset_name: Key from DEFENDER_PRESETS

        Returns:
            Dictionary of metric contributions
        """
        print(f"presets : {self.presets}")
        preset = self.presets[preset_name]
        components = preset['components']

        # Extract weights
        weights = {}
        for comp in components:
            metric = comp['stat']
            weights[metric] = comp['weight']

        # Normalize weights
        total_weight = sum(abs(w) for w in weights.values())
        normalized_weights = {k: v/total_weight for k, v in weights.items()}

        contributions = {}
        for metric, weight in normalized_weights.items():
            if metric in df.columns:
                col_values = df[metric]
                col_min = col_values.min()
                col_max = col_values.max()
                player_value = df.loc[player_idx, metric]

                if col_max == col_min:
                    normalized_value = 50.0
                else:
                    if is_lower_better(metric) and weight < 0:
                        normalized_value = 100 - ((player_value - col_min) / (col_max - col_min) * 100)
                    else:
                        normalized_value = (player_value - col_min) / (col_max - col_min) * 100

                    # Clamp to 0-100
                    normalized_value = max(0, min(100, normalized_value))

                contributions[metric] = {
                    'raw_value': player_value,
                    'normalized_score': normalized_value,
                    'weight': weight,
                    'weighted_contribution': normalized_value * abs(weight)
                }

        return contributions


def get_percentile_color(percentile_rank):
    """Return color code based on percentile range"""
    if percentile_rank >= 90:
        return '#1a5f27'  # Elite dark green
    elif percentile_rank >= 80:
        return '#1a9641'  # Excellent green
    elif percentile_rank >= 70:
        return '#4caf50'  # Very good green
    elif percentile_rank >= 60:
        return '#73c378'  # Good medium green
    elif percentile_rank >= 50:
        return '#a4d65e'  # Above average light green
    elif percentile_rank >= 40:
        return '#f9d057'  # Average yellow
    elif percentile_rank >= 30:
        return '#ffa726'  # Below average orange
    elif percentile_rank >= 20:
        return '#fc8d59'  # Poor light orange
    elif percentile_rank >= 10:
        return '#e57373'  # Bad light red
    else:
        return '#d73027'  # Very bad red


def style_weighted_score(val, percentile_rank):
    """Style function for weighted score column"""
    color = get_percentile_color(percentile_rank)
    return f'background-color: {color}; color: white; font-weight: bold'


def show_player_finder(filtered_df: pd.DataFrame, presets: Dict, selected_preset: str):
    """
    Main Player Finder visualization

    Args:
        filtered_df: Player dataframe already filtered by global filters (league + position)
        presets: Dictionary of preset configurations (DEFENDER_PRESETS or custom)
        selected_preset: Name of the preset to use (key from presets dict)
    """
    st.header("🎯 Player Finder - Defender Profiles")

    # Check for empty dataframe
    if len(filtered_df) == 0:
        st.warning("⚠️ No players match the selected filters. Adjust filters in sidebar.")
        return

    # Initialize scorer
    print(f"presets : {presets}")
    print(f"selected_preset : {selected_preset}")
    scorer = DefenderScorer(presets)

    # Show summary
    preset_info = presets[selected_preset]
    num_metrics = len(preset_info.get('components', []))

    st.info(
        f"🔍 **Profile: {preset_info['display_name']}** {preset_info.get('icon', '')}  \n"
        f"**Available Players**: {len(filtered_df)} players from {filtered_df['Team'].nunique()} teams  \n"
        f"**Description**: {preset_info['description']}  \n"
        f"**Metrics**: {num_metrics} metrics with custom weights"
    )

    # Calculate scores
    with st.spinner("Calculating profile scores..."):
        try:
            results_df, used_weights = scorer.calculate_preset_score(
                filtered_df,
                selected_preset,
                top_n_limit=30
            )
        except ValueError as e:
            st.error(f"❌ Error calculating scores: {str(e)}")
            st.info("Some metrics may be missing from the dataset.")
            return

    # Display results in tabs
    st.subheader("📊 Profile Scoring Results")

    tab1, tab2, tab3 = st.tabs(["📋 Results Table", "📊 Score Distribution", "🔍 Player Detail"])

    with tab1:
        # Results table with styling
        display_results_table(results_df, selected_preset, used_weights)

    with tab2:
        # Score distribution visualizations
        display_score_distribution(results_df, selected_preset)

    with tab3:
        # Individual player analysis
        display_player_detail(results_df, filtered_df, selected_preset, used_weights, scorer)


def display_results_table(results_df, preset_name, used_weights):
    """Display top 30 results table with color coding"""
    st.markdown("#### Top 30 Performers")

    score_col = f'{preset_name.replace(" ", "_")}_Score'
    percentile_col = f'{score_col}_Percentile'

    # Format scores
    display_df = results_df.copy()
    display_df[score_col] = display_df[score_col].round(2)
    display_df[percentile_col] = display_df[percentile_col].round(1)

    # Rename Birth country to Passport Country if it exists
    if 'Birth country' in display_df.columns:
        display_df = display_df.rename(columns={'Birth country': 'Passport Country'})

    # Column configuration with new player info columns
    column_config = {
        'Rank': st.column_config.NumberColumn("#", width="small"),
        'Player': st.column_config.TextColumn("Player", width="medium"),
        'Team': st.column_config.TextColumn("Team", width="medium"),
        'Position': st.column_config.TextColumn("Position", width="small"),
        'Age': st.column_config.NumberColumn("Age", width="small"),
        'Passport Country': st.column_config.TextColumn("Passport Country", width="small"),
        'Height': st.column_config.NumberColumn("Height (cm)", width="small", format="%.0f"),
        'Contract expires': st.column_config.TextColumn("Contract", width="small"),
        'Market value': st.column_config.TextColumn("Market Value", width="small"),
        score_col: st.column_config.NumberColumn(
            "Weighted Score",
            format="%.1f",
            width="medium"
        ),
        percentile_col: st.column_config.ProgressColumn(
            "Percentile Rank",
            min_value=0,
            max_value=100,
            format="%.0f%%",
            width="medium"
        )
    }

    # Add metric column configs
    for metric in used_weights.keys():
        if metric in display_df.columns:
            column_config[metric] = st.column_config.NumberColumn(
                metric,
                format="%.1f",
                width="small"
            )

    # Apply styling (color-code the score column)
    styled_df = display_df.style.apply(
        lambda row: [
            style_weighted_score(row[score_col], row[percentile_col])
            if col == score_col else ''
            for col in display_df.columns
        ],
        axis=1
    )

    # Display table
    st.dataframe(
        styled_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True
    )

    # Summary stats
    st.markdown("##### 📊 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Top 30 Players", len(display_df))
    with col2:
        st.metric("Top Score", f"{display_df[score_col].max():.1f}")
    with col3:
        st.metric("Average Score", f"{display_df[score_col].mean():.1f}")
    with col4:
        st.metric("Median Score", f"{display_df[score_col].median():.1f}")

    # Weights used
    st.markdown("##### ⚖️ Weights Used")
    weights_df = pd.DataFrame([
        {'Metric': metric, 'Weight': f"{weight:.2f}", 'Percentage': f"{abs(weight)*100:.1f}%"}
        for metric, weight in used_weights.items()
    ])
    st.dataframe(weights_df, use_container_width=True, hide_index=True)


def display_score_distribution(results_df, preset_name):
    """Display score distribution visualizations"""
    st.markdown("#### Score Distribution Analysis")

    score_col = f'{preset_name.replace(" ", "_")}_Score'

    # Score distribution histogram
    fig_hist = px.histogram(
        results_df,
        x=score_col,
        nbins=15,
        title=f"{preset_name} Score Distribution (Top 30 Players)",
        color_discrete_sequence=['#1151ff'],
        labels={score_col: f"{preset_name} Score", 'count': 'Number of Players'}
    )
    fig_hist.update_layout(
        height=400,
        showlegend=False,
        plot_bgcolor='#f5f5f5',
        paper_bgcolor='#ffffff'
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # Top 10 vs Bottom 10 comparison (if we have enough players)
    if len(results_df) >= 20:
        st.markdown("#### Top 10 vs Bottom 10 Comparison")
        top_10 = results_df.head(10)
        bottom_10 = results_df.tail(10)

        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(
            y=top_10['Player'][::-1],  # Reverse for better display
            x=top_10[score_col][::-1],
            orientation='h',
            name='Top 10',
            marker_color='#007d48'
        ))

        fig_compare.add_trace(go.Bar(
            y=bottom_10['Player'],
            x=bottom_10[score_col],
            orientation='h',
            name='Bottom 10 (of Top 30)',
            marker_color='#d30005'
        ))

        fig_compare.update_layout(
            title=f"{preset_name} - Top vs Bottom Performers",
            xaxis_title=f"{preset_name} Score",
            height=600,
            barmode='group',
            plot_bgcolor='#f5f5f5',
            paper_bgcolor='#ffffff'
        )
        st.plotly_chart(fig_compare, use_container_width=True)


def display_player_detail(results_df, df_to_score, preset_name, used_weights, scorer):
    """Display individual player analysis"""
    st.markdown("#### Individual Player Analysis")

    # Player selection for detailed view
    selected_player = st.selectbox(
        "Select a player for detailed breakdown:",
        options=results_df['Player'].tolist(),
        key="player_detail_select"
    )

    if selected_player:
        player_data = results_df[results_df['Player'] == selected_player].iloc[0]
        player_idx = df_to_score[df_to_score['Player'] == selected_player].index[0]

        score_col = f'{preset_name.replace(" ", "_")}_Score'
        percentile_col = f'{score_col}_Percentile'

        # Player overview
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Rank", f"#{int(player_data['Rank'])}")
        with col2:
            st.metric("Player", selected_player)
        with col3:
            st.metric("Team", player_data['Team'])
        with col4:
            st.metric("Score", f"{player_data[score_col]:.1f}")
        with col5:
            st.metric("Percentile", f"{player_data[percentile_col]:.1f}%")

        # Metric breakdown
        st.markdown("##### Metric Contributions")
        contributions = scorer.get_metric_contributions(
            df_to_score, player_idx, preset_name
        )

        if contributions:
            # Create enhanced breakdown dataframe
            breakdown_data = []
            for metric, data in contributions.items():
                breakdown_data.append({
                    'Metric': metric,
                    'Raw Value': f"{data['raw_value']:.1f}",
                    'Normalized Score': f"{data['normalized_score']:.1f}",
                    'Weight': f"{data['weight']:.2f}",
                    'Weighted Contribution': f"{data['weighted_contribution']:.1f}"
                })

            breakdown_df = pd.DataFrame(breakdown_data)
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

            # Enhanced contribution chart
            fig_contrib = px.bar(
                breakdown_df,
                x='Metric',
                y=[float(x) for x in breakdown_df['Weighted Contribution']],
                title=f"Weighted Metric Contributions for {selected_player}",
                color=[float(x) for x in breakdown_df['Normalized Score']],
                color_continuous_scale=[
                    [0.0, '#d73027'],   # Very bad red
                    [0.1, '#e57373'],   # Bad light red
                    [0.2, '#fc8d59'],   # Poor light orange
                    [0.3, '#ffa726'],   # Below average orange
                    [0.4, '#f9d057'],   # Average yellow
                    [0.5, '#a4d65e'],   # Above average light green
                    [0.6, '#73c378'],   # Good medium green
                    [0.7, '#4caf50'],   # Very good green
                    [0.8, '#1a9641'],   # Excellent green
                    [1.0, '#1a5f27']    # Elite dark green
                ],
                labels={'color': 'Normalized Score', 'y': 'Weighted Contribution'}
            )
            fig_contrib.update_layout(
                height=400,
                showlegend=True,
                xaxis_title="Metrics",
                yaxis_title="Weighted Contribution to Total Score",
                plot_bgcolor='#f5f5f5',
                paper_bgcolor='#ffffff'
            )
            fig_contrib.update_traces(
                texttemplate='%{y:.1f}',
                textposition='outside'
            )
            st.plotly_chart(fig_contrib, use_container_width=True)


def calculate_all_role_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate scores for all available roles for all players

    Args:
        df: DataFrame with player data

    Returns:
        DataFrame with original data + ROLE_{name} columns for each role
    """
    from config.defender_presets import DEFENDER_PRESETS
    from config.forward_presets import FORWARD_PRESETS
    from config.attacking_midfielder_presets import ATTACKING_MIDFIELDER_PRESETS

    # Combine all presets
    all_presets = {}
    all_presets.update(DEFENDER_PRESETS)
    all_presets.update(FORWARD_PRESETS)
    all_presets.update(ATTACKING_MIDFIELDER_PRESETS)

    result_df = df.copy()
    scorer = DefenderScorer(all_presets)

    for role_name, role_config in all_presets.items():
        try:
            # Calculate score for this role
            components = role_config['components']
            weights = {comp['stat']: comp['weight'] for comp in components}

            # Check if all metrics available
            if not all(metric in df.columns for metric in weights.keys()):
                continue

            # Normalize weights
            total_weight = sum(abs(w) for w in weights.values())
            normalized_weights = {k: v/total_weight for k, v in weights.items()}

            # Calculate normalized scores (0-100)
            weighted_scores = pd.Series(0.0, index=df.index)

            for metric, weight in normalized_weights.items():
                col_values = df[metric]
                col_min = col_values.min()
                col_max = col_values.max()

                if col_max == col_min:
                    normalized_values = pd.Series(50.0, index=df.index)
                else:
                    if is_lower_better(metric) and weight < 0:
                        normalized_values = 100 - ((col_values - col_min) / (col_max - col_min) * 100)
                    else:
                        normalized_values = (col_values - col_min) / (col_max - col_min) * 100

                weighted_scores += normalized_values * abs(weight)

            # Add to result dataframe
            score_col = f"ROLE_{role_name.replace(' ', '_')}"
            result_df[score_col] = weighted_scores

        except Exception as e:
            # Skip roles that fail
            continue

    return result_df


def display_player_finder_scatter_plot(
    results_df: pd.DataFrame,
    df_filtered: pd.DataFrame,
    search_mode: str
) -> None:
    """
    Display scatter plot with Role scores on X-axis and Composite attributes on Y-axis

    Args:
        results_df: Top N results to highlight
        df_filtered: Full filtered dataset
        search_mode: Kept for compatibility but not used (always shows role vs responsibility)
    """
    st.subheader("📊 Scatter Plot Analysis - Role vs Responsibility")

    # STEP 1: Calculate all role scores (with caching)
    player_list_hash = hash(tuple(sorted(df_filtered['Player'].tolist())))

    if 'player_finder_role_scores_df' not in st.session_state or \
       st.session_state.get('player_finder_role_scores_hash') != player_list_hash:

        with st.spinner("Calculating role scores for all players..."):
            role_scores_df = calculate_all_role_scores(df_filtered)
            st.session_state.player_finder_role_scores_df = role_scores_df
            st.session_state.player_finder_role_scores_hash = player_list_hash
    else:
        role_scores_df = st.session_state.player_finder_role_scores_df

    # STEP 2: Build X-axis options (Roles)
    from config.defender_presets import DEFENDER_PRESETS
    from config.forward_presets import FORWARD_PRESETS
    from config.attacking_midfielder_presets import ATTACKING_MIDFIELDER_PRESETS

    all_role_presets = {}
    all_role_presets.update(DEFENDER_PRESETS)
    all_role_presets.update(FORWARD_PRESETS)
    all_role_presets.update(ATTACKING_MIDFIELDER_PRESETS)

    # Get role columns that were successfully calculated
    role_columns = [col for col in role_scores_df.columns if col.startswith('ROLE_')]
    role_options = []
    role_mapping = {}

    for col in role_columns:
        # Extract role name from column (ROLE_Ball_Playing -> Ball Playing)
        role_name = col.replace('ROLE_', '').replace('_', ' ')
        if role_name in all_role_presets:
            display_name = f"{all_role_presets[role_name].get('icon', '')} {role_name}"
            role_options.append(display_name)
            role_mapping[display_name] = col

    # STEP 3: Build Y-axis options (Composite Attributes)
    from config.composite_attributes import COMPOSITE_ATTRIBUTES

    composite_columns = [f"COMP_{attr}" for attr in COMPOSITE_ATTRIBUTES.keys()
                        if f"COMP_{attr}" in df_filtered.columns]

    composite_options = []
    composite_mapping = {}

    for col in composite_columns:
        # Extract attribute name from column (COMP_Security -> Security)
        attr_name = col.replace('COMP_', '')
        if attr_name in COMPOSITE_ATTRIBUTES:
            display_name = f"{COMPOSITE_ATTRIBUTES[attr_name]['icon']} {COMPOSITE_ATTRIBUTES[attr_name]['display_name']}"
            composite_options.append(display_name)
            composite_mapping[display_name] = col

    # Validate we have options
    if len(role_options) == 0:
        st.warning("⚠️ No role scores available. Some metrics may be missing from dataset.")
        return

    if len(composite_options) == 0:
        st.warning("⚠️ No composite attributes available. Composite attributes may not be calculated.")
        return

    # STEP 4: Create selectboxes
    col1, col2 = st.columns(2)

    with col1:
        x_role_display = st.selectbox(
            "X-Axis (Role):",
            options=role_options,
            index=0,
            key="player_finder_scatter_x_role"
        )

    with col2:
        y_comp_display = st.selectbox(
            "Y-Axis (Responsibility):",
            options=composite_options,
            index=0,
            key="player_finder_scatter_y_comp"
        )

    x_metric = role_mapping[x_role_display]
    y_metric = composite_mapping[y_comp_display]

    # Merge role scores with original data
    # Use Player as key to merge
    merged_df = df_filtered.merge(
        role_scores_df[['Player'] + role_columns],
        on='Player',
        how='left'
    )

    # Validate metrics exist
    if x_metric not in merged_df.columns or y_metric not in merged_df.columns:
        st.error(f"Selected metrics not found in dataset")
        return

    # STEP 5: Prepare data layers
    result_player_names = results_df['Player'].tolist()
    background_df = merged_df[~merged_df['Player'].isin(result_player_names)]

    # Merge both role scores AND composite attributes into results_df for highlighting
    results_with_scores = results_df.merge(
        merged_df[['Player'] + role_columns + composite_columns],
        on='Player',
        how='left'
    )

    # STEP 6: Create figure
    fig = go.Figure()

    # Layer 1: Background players (gray)
    fig.add_trace(go.Scatter(
        x=background_df[x_metric],
        y=background_df[y_metric],
        mode='markers',
        marker=dict(color='#9E9E9E', size=10, opacity=0.3),
        name='Other Players',
        hoverinfo='skip'
    ))

    # Layer 2: Top results (green)
    hover_texts = []
    for idx, row in results_with_scores.iterrows():
        hover_text = (
            f"<b>{row['Player']}</b><br>{row['Team']}<br>"
            f"{x_role_display}: {row[x_metric]:.1f}<br>"
            f"{y_comp_display}: {row[y_metric]:.1f}<br>"
        )
        # Add score column if it exists
        score_cols = [col for col in row.index if col.endswith('_Score')]
        if score_cols:
            hover_text += f"Search Score: {row[score_cols[0]]:.2f}"
        hover_texts.append(hover_text)

    fig.add_trace(go.Scatter(
        x=results_with_scores[x_metric],
        y=results_with_scores[y_metric],
        mode='markers+text',
        marker=dict(color='#007d48', size=12, opacity=0.8),
        text=results_with_scores['Player'],
        textposition='top center',
        textfont=dict(size=9),
        name='Top Results',
        hovertext=hover_texts,
        hoverinfo='text'
    ))

    # Layout
    fig.update_layout(
        title=f"{x_role_display} vs {y_comp_display}",
        xaxis_title=x_role_display,
        yaxis_title=y_comp_display,
        plot_bgcolor='#f5f5f5',
        paper_bgcolor='#ffffff',
        height=600,
        hovermode='closest'
    )

    st.plotly_chart(fig, use_container_width=True)
