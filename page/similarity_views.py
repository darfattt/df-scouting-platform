import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from config.position_groups import POSITION_GROUPS


def display_similarity_results_table(
    results_df, reference_player, weights, composite_display_names, relevant_composites
):
    """Display top 50 similar players table with all composite attributes"""
    st.markdown("#### Most Similar Players")

    display_df = results_df.copy()

    # Deduplicate by Wyscout id (or Player name as fallback) in case duplicates survived upstream
    if "Wyscout id" in display_df.columns:
        display_df = display_df.drop_duplicates(subset=["Wyscout id"], keep="first")
    else:
        display_df = display_df.drop_duplicates(subset=["Player"], keep="first")

    display_df["Similarity_Score"] = display_df["Similarity_Score"].round(3)
    display_df["Similarity_Percentile"] = display_df["Similarity_Percentile"].round(1)

    display_cols = [
        "Rank",
        "Player",
        "Full name",
        "Team",
        "Position",
        "Age",
        "Passport country",
        "Foot",
        "Height",
        "Contract expires",
        "Market value",
        "Minutes played",
        "Similarity_Score",
        "Similarity_Percentile",
    ]

    for metric in weights.keys():
        if metric in display_df.columns and metric not in display_cols:
            display_cols.append(metric)

    # commented by darfat to prevent duplication
    # all_comp_cols = [col for col in display_df.columns if col.startswith('COMP_')]
    # for comp_col in all_comp_cols:
    #     if comp_col not in display_cols:
    #         display_cols.append(comp_col)

    # display_cols = [col for col in display_cols if col in display_df.columns]
    # display_df = display_df[display_cols]

    # rename_dict = {}
    # for col in display_df.columns:
    #     if col.startswith('COMP_'):
    #         rename_dict[col] = composite_display_names.get(col, col)
    # display_df = display_df.rename(columns=rename_dict)
    # end duplication

    # Column configuration
    column_config = {
        "Rank": st.column_config.NumberColumn("#", width="small"),
        "Player": st.column_config.TextColumn("Player", width="medium"),
        "Full name": st.column_config.TextColumn("Full Name", width="large"),
        "Team": st.column_config.TextColumn("Team", width="medium"),
        "Position": st.column_config.TextColumn("Position", width="small"),
        "Age": st.column_config.NumberColumn("Age", width="small"),
        "Passport country": st.column_config.TextColumn(
            "Passport country", width="medium"
        ),
        "Foot": st.column_config.TextColumn("Foot", width="small"),
        "Height": st.column_config.NumberColumn("Height (cm)", width="small"),
        "Weight": st.column_config.NumberColumn("Weight (kg)", width="small"),
        "Contract expires": st.column_config.TextColumn(
            "Contract expires", width="medium"
        ),
        "Market value": st.column_config.TextColumn("Market value", width="small"),
        "Matches played": st.column_config.NumberColumn("Matches", width="small"),
        "Similarity_Score": st.column_config.NumberColumn(
            "Similarity Score",
            format="%.3f",
            width="medium",
            help="Cosine similarity score (higher = more similar)",
        ),
        "Similarity_Percentile": st.column_config.ProgressColumn(
            "Similarity %", min_value=0, max_value=100, format="%.0f%%", width="medium"
        ),
    }

    for metric in weights.keys():
        if metric in display_df.columns:
            column_config[metric] = st.column_config.NumberColumn(
                metric, format="%.1f", width="small"
            )

    # still have duplicate columns darfat
    all_comp_cols = [col for col in display_df.columns if col.startswith("COMP_")]
    for comp_col in all_comp_cols:
        if comp_col in display_df.columns:
            display_name = composite_display_names.get(comp_col, comp_col)
            column_config[display_name] = st.column_config.NumberColumn(
                display_name, format="%.1f", width="medium"
            )

    st.dataframe(
        display_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        height=600,
    )

    # Summary stats
    st.markdown("##### 📊 Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Similar Players Found", len(display_df))
    with col2:
        st.metric("Highest Similarity", f"{display_df['Similarity_Score'].max():.3f}")
    with col3:
        st.metric("Average Similarity", f"{display_df['Similarity_Score'].mean():.3f}")
    with col4:
        st.metric("Teams Represented", display_df["Team"].nunique())

    st.markdown("##### ⚖️ Individual Statistics Weights Used")
    weights_df = pd.DataFrame(
        [
            {"Metric": metric, "Weight": f"{weight:.3f}"}
            for metric, weight in weights.items()
        ]
    )
    st.dataframe(weights_df, use_container_width=True, hide_index=True)


def display_similarity_scatter_plot(
    results_df, full_df, reference_player, stat_columns, weights
):
    """Display scatter plot of similar players"""
    import plotly.graph_objects as go

    st.markdown("#### Scatter Plot Analysis")

    # Metric selection for X/Y axes
    col1, col2 = st.columns(2)
    with col1:
        x_metric = st.selectbox(
            "X-Axis Metric:",
            options=stat_columns,
            index=0 if len(stat_columns) > 0 else None,
            key="scatter_x_metric",
        )
    with col2:
        y_metric = st.selectbox(
            "Y-Axis Metric:",
            options=stat_columns,
            index=1 if len(stat_columns) > 1 else 0,
            key="scatter_y_metric",
        )

    if not x_metric or not y_metric:
        st.warning("Please select both X and Y metrics")
        return

    # Create scatter plot
    fig = go.Figure()

    # Background players (not in results, not reference)
    similar_names = set(results_df["Player"].tolist())
    similar_names.add(reference_player)
    background_df = full_df[~full_df["Player"].isin(similar_names)]

    if (
        len(background_df) > 0
        and x_metric in background_df.columns
        and y_metric in background_df.columns
    ):
        fig.add_trace(
            go.Scatter(
                x=background_df[x_metric],
                y=background_df[y_metric],
                mode="markers",
                marker=dict(color="#9E9E9E", size=10, opacity=0.3),
                name="Other Players",
                text=background_df["Player"],
                hovertemplate="<b>%{text}</b><br>"
                + f"{x_metric}: %{{x:.1f}}<br>"
                + f"{y_metric}: %{{y:.1f}}<extra></extra>",
            )
        )

    # Similar players
    if x_metric in results_df.columns and y_metric in results_df.columns:
        # Create hover text with similarity scores
        hover_texts = []
        for idx, row in results_df.iterrows():
            hover_texts.append(
                f"<b>{row['Player']}</b><br>"
                + f"{x_metric}: {row[x_metric]:.1f}<br>"
                + f"{y_metric}: {row[y_metric]:.1f}<br>"
                + f"Similarity: {row['Similarity_Score']:.3f}"
            )

        fig.add_trace(
            go.Scatter(
                x=results_df[x_metric],
                y=results_df[y_metric],
                mode="markers+text",
                marker=dict(color="#007d48", size=12, opacity=0.8),
                name="Similar Players",
                text=results_df["Player"],
                textposition="top center",
                textfont=dict(size=9),
                hovertemplate="%{hovertext}<extra></extra>",
                hovertext=hover_texts,
            )
        )

    # Reference player
    ref_player_row = full_df[full_df["Player"] == reference_player].iloc[0]
    if x_metric in ref_player_row and y_metric in ref_player_row:
        fig.add_trace(
            go.Scatter(
                x=[ref_player_row[x_metric]],
                y=[ref_player_row[y_metric]],
                mode="markers+text",
                marker=dict(
                    color="#d30005",
                    size=15,
                    symbol="star",
                    line=dict(width=2, color="white"),
                ),
                name="Reference Player",
                text=[reference_player],
                textposition="top center",
                textfont=dict(size=11, color="#d30005"),
                hovertemplate=f"<b>{reference_player}</b><br>"
                + f"{x_metric}: {ref_player_row[x_metric]:.1f}<br>"
                + f"{y_metric}: {ref_player_row[y_metric]:.1f}<extra></extra>",
            )
        )

    # Update layout
    fig.update_layout(
        title=f"{x_metric} vs {y_metric} - Similarity Analysis",
        xaxis_title=x_metric,
        yaxis_title=y_metric,
        height=600,
        plot_bgcolor="#f5f5f5",
        paper_bgcolor="#ffffff",
        hovermode="closest",
    )

    st.plotly_chart(fig, use_container_width=True)


def display_similarity_scatter_plot_composite(
    results_df,
    full_df,
    reference_player,
    composite_columns,
    composite_display_names,
    weights,
):
    """Display scatter plot with composite attributes on axes"""
    import plotly.graph_objects as go

    st.markdown("#### Attributes Scatter Plot")

    # Metric selection for X/Y axes - only composite attributes
    col1, col2 = st.columns(2)

    # Create friendly display options
    composite_options_display = [
        composite_display_names[col]
        for col in composite_columns
        if col in full_df.columns
    ]
    composite_options_mapping = {
        display: col
        for display, col in zip(
            composite_options_display,
            [col for col in composite_columns if col in full_df.columns],
        )
    }

    if len(composite_options_display) < 2:
        st.warning(
            "Not enough composite attributes available. Please ensure data is loaded correctly."
        )
        return

    with col1:
        x_metric_display = st.selectbox(
            "X-Axis Composite Attribute:",
            options=composite_options_display,
            index=0,
            key="scatter_comp_x_metric",
        )
        x_metric = composite_options_mapping.get(x_metric_display)

    with col2:
        y_metric_display = st.selectbox(
            "Y-Axis Composite Attribute:",
            options=composite_options_display,
            index=1 if len(composite_options_display) > 1 else 0,
            key="scatter_comp_y_metric",
        )
        y_metric = composite_options_mapping.get(y_metric_display)

    if not x_metric or not y_metric:
        st.warning("Please select both X and Y composite attributes")
        return

    # Create scatter plot
    fig = go.Figure()

    # Background players (not in results, not reference)
    similar_names = set(results_df["Player"].tolist())
    similar_names.add(reference_player)
    background_df = full_df[~full_df["Player"].isin(similar_names)]

    if (
        len(background_df) > 0
        and x_metric in background_df.columns
        and y_metric in background_df.columns
    ):
        fig.add_trace(
            go.Scatter(
                x=background_df[x_metric],
                y=background_df[y_metric],
                mode="markers",
                marker=dict(color="#9E9E9E", size=10, opacity=0.3),
                name="Other Players",
                text=background_df["Player"],
                hovertemplate="<b>%{text}</b><br>"
                + f"{x_metric_display}: %{{x:.1f}}<br>"
                + f"{y_metric_display}: %{{y:.1f}}<extra></extra>",
            )
        )

    # Similar players
    if x_metric in results_df.columns and y_metric in results_df.columns:
        hover_texts = []
        for idx, row in results_df.iterrows():
            hover_texts.append(
                f"<b>{row['Player']}</b><br>"
                + f"{x_metric_display}: {row[x_metric]:.1f}<br>"
                + f"{y_metric_display}: {row[y_metric]:.1f}<br>"
                + f"Similarity: {row['Similarity_Score']:.3f}"
            )

        fig.add_trace(
            go.Scatter(
                x=results_df[x_metric],
                y=results_df[y_metric],
                mode="markers+text",
                marker=dict(color="#007d48", size=12, opacity=0.8),
                name="Similar Players",
                text=results_df["Player"],
                textposition="top center",
                textfont=dict(size=9),
                hovertemplate="%{hovertext}<extra></extra>",
                hovertext=hover_texts,
            )
        )

    # Reference player
    ref_player_row = full_df[full_df["Player"] == reference_player]
    if len(ref_player_row) > 0:
        ref_player_row = ref_player_row.iloc[0]
        fig.add_trace(
            go.Scatter(
                x=[ref_player_row[x_metric]],
                y=[ref_player_row[y_metric]],
                mode="markers+text",
                marker=dict(
                    color="#d30005",
                    size=15,
                    symbol="star",
                    line=dict(width=2, color="white"),
                ),
                name="Reference Player",
                text=[reference_player],
                textposition="top center",
                textfont=dict(size=11, color="#d30005"),
                hovertemplate=f"<b>{reference_player}</b><br>"
                + f"{x_metric_display}: {ref_player_row[x_metric]:.1f}<br>"
                + f"{y_metric_display}: {ref_player_row[y_metric]:.1f}<extra></extra>",
            )
        )

    # Update layout
    fig.update_layout(
        title=f"{x_metric_display} vs {y_metric_display} - Attributes Analysis",
        xaxis_title=x_metric_display,
        yaxis_title=y_metric_display,
        height=600,
        plot_bgcolor="#f5f5f5",
        paper_bgcolor="#ffffff",
        hovermode="closest",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Add explanation
    from config.composite_attributes import COMPOSITE_ATTRIBUTES

    x_attr_key = x_metric.replace("COMP_", "")
    y_attr_key = y_metric.replace("COMP_", "")

    st.info(
        "💡 **How to interpret this chart:**\n\n"
        f"- **X-Axis ({x_metric_display})**: {COMPOSITE_ATTRIBUTES[x_attr_key]['description']}\n\n"
        f"- **Y-Axis ({y_metric_display})**: {COMPOSITE_ATTRIBUTES[y_attr_key]['description']}\n\n"
        "- Players closer to the reference player (red star) are more similar across these composite attributes"
    )


def display_similarity_player_detail(results_df, scorer, reference_player, weights):
    """Display detailed player comparison with both composite and individual contributions"""
    import plotly.graph_objects as go
    import plotly.express as px
    from config.composite_attributes import COMPOSITE_ATTRIBUTES

    st.markdown("#### Individual Player Comparison")

    # Player selection
    selected_similar_player = st.selectbox(
        "Select a similar player to compare:",
        options=results_df["Player"].tolist(),
        key="detail_similar_player",
    )

    if not selected_similar_player:
        st.info("Select a player to view detailed comparison")
        return

    individual_contributions = scorer.get_metric_contributions(
        reference_player, selected_similar_player, weights
    )

    st.markdown(
        f"##### Comparing: **{reference_player}** vs **{selected_similar_player}**"
    )

    # ========== Individual Metric Contributions ==========
    if individual_contributions:
        st.markdown("---")
        st.markdown("#### 📊 Individual Metric Contributions")
        st.caption("Raw statistical attributes used in similarity calculation")

        # Create comparison table
        comparison_data = []
        for metric, data in sorted(
            individual_contributions.items(),
            key=lambda x: x[1]["weighted_contribution"],
            reverse=True,
        ):
            comparison_data.append(
                {
                    "Metric": metric,
                    f"{reference_player}": f"{data['reference_value']:.1f}",
                    f"{selected_similar_player}": f"{data['similar_value']:.1f}",
                    "Difference": f"{data['difference']:.1f}",
                    "Similarity %": f"{data['metric_similarity']:.1f}%",
                    "Weight": f"{data['weight']:.2f}",
                    "Contribution": f"{data['weighted_contribution']:.1f}",
                }
            )

        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        # Visualization of contributions
        contribution_values = [
            float(row["Contribution"]) for _, row in comparison_df.iterrows()
        ]
        similarity_values = [
            float(row["Similarity %"].replace("%", ""))
            for _, row in comparison_df.iterrows()
        ]

        fig = px.bar(
            comparison_df,
            x="Metric",
            y=contribution_values,
            title=f"Individual Metric Contributions to Similarity Score",
            color=similarity_values,
            color_continuous_scale="RdYlGn",
            labels={"y": "Weighted Contribution", "color": "Similarity %"},
        )
        fig.update_layout(
            height=400,
            plot_bgcolor="#f5f5f5",
            paper_bgcolor="#ffffff",
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ========== ALL COMPOSITE ATTRIBUTES (Display Only) ==========
    st.markdown("---")
    st.markdown("#### 🎯 All Composite Attribute Contributions")
    st.caption(
        "Composite attributes for comparison (not used in similarity calculation)"
    )

    all_composite_contributions = scorer.get_all_composite_contributions(
        reference_player, selected_similar_player, COMPOSITE_ATTRIBUTES
    )

    if all_composite_contributions:
        comp_data = []
        for comp_col, data in sorted(
            all_composite_contributions.items(),
            key=lambda x: x[1]["metric_similarity"],
            reverse=True,
        ):
            comp_data.append(
                {
                    "Attribute": data["display_name"],
                    f"{reference_player}": f"{data['reference_value']:.1f}",
                    f"{selected_similar_player}": f"{data['similar_value']:.1f}",
                    "Difference": f"{data['difference']:.1f}",
                    "Similarity %": f"{data['metric_similarity']:.1f}%",
                }
            )

        comp_df = pd.DataFrame(comp_data)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

        # ========== 1D DISTRIBUTION CHARTS FOR RELEVANT COMPOSITES ==========
        st.markdown("---")
        st.markdown("#### 📊 Relevant Composite Attribute Distributions")
        st.caption(
            "Distribution of key attributes across all filtered players, highlighting selected players"
        )

        from config.position_rankings import POSITION_RANKINGS

        ref_player_row = scorer.df[scorer.df["Player"] == reference_player].iloc[0]
        player_position = ref_player_row["Position"]

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
            position_group = "CB"

        relevant_composite_names = POSITION_RANKINGS.get(position_group, {}).get(
            "key_attributes", []
        )

        col1, col2 = st.columns(2)
        for idx, comp_name in enumerate(relevant_composite_names):
            comp_col = f"COMP_{comp_name}"
            if (
                comp_col not in scorer.df.columns
                or comp_name not in COMPOSITE_ATTRIBUTES
            ):
                continue

            with col1 if idx % 2 == 0 else col2:
                fig = go.Figure()

                fig.add_trace(
                    go.Histogram(
                        x=scorer.df[comp_col],
                        name="All Players",
                        marker_color="#9E9E9E",
                        opacity=0.7,
                        nbinsx=30,
                    )
                )

                ref_val = scorer.df[scorer.df["Player"] == reference_player][
                    comp_col
                ].iloc[0]
                fig.add_vline(
                    x=ref_val,
                    line_width=3,
                    line_dash="dash",
                    line_color="#d30005",
                    annotation_text=f"{reference_player}",
                    annotation_position="top",
                )

                sim_val = scorer.df[scorer.df["Player"] == selected_similar_player][
                    comp_col
                ].iloc[0]
                fig.add_vline(
                    x=sim_val,
                    line_width=3,
                    line_dash="dash",
                    line_color="#007d48",
                    annotation_text=f"{selected_similar_player}",
                    annotation_position="bottom",
                )

                fig.update_layout(
                    title=COMPOSITE_ATTRIBUTES[comp_name]["display_name"],
                    xaxis_title="Score",
                    yaxis_title="Count",
                    height=300,
                    plot_bgcolor="#f5f5f5",
                    paper_bgcolor="#ffffff",
                    showlegend=False,
                )

                st.plotly_chart(fig, use_container_width=True)

        # ========== HORIZONTAL BAR CHART FOR COMPOSITE COMPARISON ==========
        st.markdown("---")
        st.markdown("#### 📊 Composite Attribute Comparison")
        st.caption("Side-by-side comparison of composite attribute scores")

        comp_chart_data = []
        for comp_col, data in all_composite_contributions.items():
            comp_chart_data.append(
                {
                    "Attribute": data["display_name"],
                    reference_player: data["reference_value"],
                    selected_similar_player: data["similar_value"],
                }
            )

        if comp_chart_data:
            bar_df = pd.DataFrame(comp_chart_data)

            bar_df_melted = bar_df.melt(
                id_vars=["Attribute"], var_name="Player", value_name="Score"
            )

            fig = px.bar(
                bar_df_melted,
                x="Score",
                y="Attribute",
                color="Player",
                orientation="h",
                barmode="group",
                color_discrete_map={
                    reference_player: "#d30005",
                    selected_similar_player: "#007d48",
                },
                height=400,
            )

            fig.update_layout(
                title="Composite Attribute Scores Comparison",
                xaxis_title="Score (0-100)",
                yaxis_title="Attribute",
                plot_bgcolor="#f5f5f5",
                paper_bgcolor="#ffffff",
                legend_title_text="",
            )

            st.plotly_chart(fig, use_container_width=True)

        # ========== DOT MATRIX CHART FOR ROLE/PRESET SCORES ==========
        st.markdown("---")
        st.markdown("#### 🎯 Role/Preset Scores Comparison")
        st.caption("Preset profile scores for both players")

        from config.defender_presets import DEFENDER_PRESETS
        from config.forward_presets import FORWARD_PRESETS
        from config.attacking_midfielder_presets import ATTACKING_MIDFIELDER_PRESETS
        from utils.similarity_helpers import get_presets_for_position
        from utils.player_finder import DefenderScorer

        available_presets = get_presets_for_position(player_position)

        preset_scores_data = []

        for preset in available_presets:
            preset_key = preset["key"]
            preset_type = preset["type"]

            preset_config = None
            if preset_type == "role":
                if preset["display_name"] in DEFENDER_PRESETS:
                    preset_config = DEFENDER_PRESETS[preset["display_name"]]
                elif preset["display_name"] in FORWARD_PRESETS:
                    preset_config = FORWARD_PRESETS[preset["display_name"]]
                elif preset["display_name"] in ATTACKING_MIDFIELDER_PRESETS:
                    preset_config = ATTACKING_MIDFIELDER_PRESETS[preset["display_name"]]

            if preset_config is None:
                continue

            components = preset_config["components"]
            ref_score = 0
            sim_score = 0
            total_weight = 0

            for comp in components:
                metric = comp["stat"]
                weight = comp["weight"]
                total_weight += abs(weight)

            if total_weight == 0:
                total_weight = 1

            for comp in components:
                metric = comp["stat"]
                weight = comp["weight"]

                if metric in scorer.df.columns:
                    ref_val = scorer.df[scorer.df["Player"] == reference_player][
                        metric
                    ].iloc[0]
                    sim_val = scorer.df[scorer.df["Player"] == selected_similar_player][
                        metric
                    ].iloc[0]
                else:
                    ref_val = 50
                    sim_val = 50

                ref_score += ref_val * weight
                sim_score += sim_val * weight

            ref_score_normalized = max(
                0, min(100, (ref_score / total_weight) * 10 + 50)
            )
            sim_score_normalized = max(
                0, min(100, (sim_score / total_weight) * 10 + 50)
            )

            preset_scores_data.append(
                {
                    "Preset": preset["display_name"],
                    "Type": preset_type,
                    "Player": reference_player,
                    "Score": ref_score_normalized,
                }
            )
            preset_scores_data.append(
                {
                    "Preset": preset["display_name"],
                    "Type": preset_type,
                    "Player": selected_similar_player,
                    "Score": sim_score_normalized,
                }
            )

        if preset_scores_data:
            preset_df = pd.DataFrame(preset_scores_data)

            fig = px.scatter(
                preset_df,
                x="Preset",
                y="Score",
                color="Player",
                symbol="Player",
                color_discrete_map={
                    reference_player: "#d30005",
                    selected_similar_player: "#007d48",
                },
                height=500,
                size_max=15,
            )

            fig.update_traces(
                marker=dict(size=12, line=dict(width=2, color="white")),
                marker_line_width=2,
            )

            fig.update_layout(
                title="Role/Preset Profile Scores",
                xaxis_title="Role/Preset",
                yaxis_title="Score (0-100)",
                plot_bgcolor="#f5f5f5",
                paper_bgcolor="#ffffff",
                xaxis_tickangle=-45,
                hovermode="closest",
            )

            st.plotly_chart(fig, use_container_width=True)

            st.info(
                "💡 **How to interpret:**\n\n"
                "- **Higher scores** indicate better fit for that role/preset\n"
                "- Compare both players' profiles to see which roles they excel in\n"
                "- Use this to identify potential positional versatility or specialization"
            )


