import streamlit as st
import pandas as pd
import altair as alt

from config.stat_categories import STAT_CATEGORIES
from config.composite_attributes import COMPOSITE_ATTRIBUTES
from config.grade_attributes import GRADE_ATTRIBUTES
from utils.data_loader import calculate_grade_attributes_batch

def render_scatter_analysis_page(df_filtered):
    """
    Render Scatter Analysis page with interactive Altair charts

    Args:
        df_filtered: Filtered player dataframe
    """
    st.header("Scatter Analysis")

    if len(df_filtered) == 0:
        st.warning(
            "⚠️ No players match the selected filters. Adjust global filters in sidebar."
        )
        return

    st.markdown("---")

    # ========== CHART CONFIGURATION SECTION ==========
    st.markdown("### ⚙️ Chart Configuration")

    st.write("**Metric Source**")
    metric_source = st.radio(
        "Metric Source",
        options=["Raw Stats", "Composite Attributes", "Grades"],
        horizontal=True,
        label_visibility="collapsed",
        key="scatter_metric_source",
    )

    if metric_source == "Raw Stats":
        all_numeric = df_filtered.select_dtypes(include=["number"]).columns.tolist()
        
        col_category, _ = st.columns([1, 2])
        with col_category:
            category_filter = st.selectbox(
                "Category:",
                options=["All"] + list(STAT_CATEGORIES.keys()),
                key="scatter_category_filter",
            )
            
        if category_filter != "All":
            filtered_stats = [
                stat["column"]
                for stat in STAT_CATEGORIES[category_filter].get("stats", [])
                if stat["column"] in df_filtered.columns
            ]
            available_metrics = sorted(filtered_stats)
        else:
            available_metrics = sorted(all_numeric)
    elif metric_source == "Composite Attributes":
        composite_attrs = [col for col in df_filtered.columns if col.startswith("COMP_")]
        if not composite_attrs:
            for comp_name in COMPOSITE_ATTRIBUTES.keys():
                col = f"COMP_{comp_name}"
                if col in df_filtered.columns:
                    composite_attrs.append(col)
        available_metrics = sorted(composite_attrs) if composite_attrs else ["No Composite Attributes Found"]
    else:
        grade_cols = [f"GRADE_{name}" for name in GRADE_ATTRIBUTES.keys()]
        missing_grades = [col for col in grade_cols if col not in df_filtered.columns]
        if missing_grades:
            with st.spinner("Calculating grades..."):
                df_filtered = calculate_grade_attributes_batch(df_filtered, GRADE_ATTRIBUTES)
        available_metrics = sorted(grade_cols)

    if not available_metrics:
        st.warning("No metrics available for selected type.")
        return

    # Default metrics based on position group if possible
    default_x = "Age" if "Age" in available_metrics else available_metrics[0]
    default_y = (
        "Minutes played" if "Minutes played" in available_metrics else (available_metrics[1] if len(available_metrics) > 1 else available_metrics[0])
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        x_axis = st.selectbox(
            "X-Axis Metric:",
            options=available_metrics,
            index=available_metrics.index(default_x) if default_x in available_metrics else 0,
            key="scatter_x_axis",
        )

    with col2:
        y_axis = st.selectbox(
            "Y-Axis Metric:",
            options=available_metrics,
            index=available_metrics.index(default_y) if default_y in available_metrics else (1 if len(available_metrics) > 1 else 0),
            key="scatter_y_axis",
        )

    with col3:
        color_by = st.selectbox(
            "Color By:",
            options=["League", "Position", "Team", "Age Group", "None"],
            index=0,
            key="scatter_color_by",
        )

    # Filtering for the chart specifically
    st.markdown("---")
    st.markdown("### 🎚️ Display Filters & Highlights")

    if "Minutes played" in df_filtered.columns:
        max_val = df_filtered["Minutes played"].max()
        max_mins = int(max_val) if pd.notna(max_val) else 1000
        # If max_mins is 0, slider will fail if max_value=0 and min_value=0.
        if max_mins <= 0:
            max_mins = 1
            
        min_minutes = st.slider(
            "Minimum Minutes Played:",
            min_value=0,
            max_value=max_mins,
            value=0,
            step=50 if max_mins >= 50 else 1,
            key="scatter_min_minutes"
        )
        if min_minutes > 0:
            df_filtered = df_filtered[df_filtered["Minutes played"] >= min_minutes]

    col1, col2 = st.columns(2)

    with col1:
        # Highlight specific teams
        all_teams = sorted(df_filtered["Team"].unique().tolist())
        highlight_teams = st.multiselect(
            "Highlight Teams:",
            options=all_teams,
            default=[],
            help="These teams will be highlighted in the chart",
            key="scatter_highlight_teams",
        )
        
        # Highlight Top X
        top_x = st.number_input(
            f"Highlight Top N in {x_axis}:",
            min_value=0,
            max_value=100,
            value=0,
            step=1,
            key="scatter_top_x",
            help=f"Highlight the top N players based on {x_axis}"
        )

    with col2:
        # Search for specific players
        all_players = sorted(df_filtered["Player"].unique().tolist())
        search_players = st.multiselect(
            "Highlight Players:",
            options=all_players,
            default=[],
            help="Search for and highlight specific players",
            key="scatter_search_players",
        )
        
        # Highlight Top Y
        top_y = st.number_input(
            f"Highlight Top N in {y_axis}:",
            min_value=0,
            max_value=100,
            value=0,
            step=1,
            key="scatter_top_y",
            help=f"Highlight the top N players based on {y_axis}"
        )

    st.markdown("---")

    # ========== CHART GENERATION ==========
    # Prepare data for Altair
    chart_df = df_filtered.copy()

    # Create Age Group if color_by is Age Group
    if color_by == "Age Group":
        if "Age" in chart_df.columns:
            chart_df["Age Group"] = pd.cut(
                chart_df["Age"],
                bins=[0, 21, 25, 30, 100],
                labels=["U21", "21-25", "26-30", "30+"],
            )
        else:
            st.warning("Age column not found to create age groups")
            color_by = "None"

    # Define tooltips
    tooltips = [
        alt.Tooltip("Player:N", title="Player"),
        alt.Tooltip("Team:N", title="Team"),
        alt.Tooltip("League:N", title="League"),
        alt.Tooltip("Position:N", title="Position"),
        alt.Tooltip("Age:Q", title="Age"),
        alt.Tooltip(f"{x_axis}:Q", title=x_axis, format=".2f"),
        alt.Tooltip(f"{y_axis}:Q", title=y_axis, format=".2f"),
    ]

    # Base chart
    base = alt.Chart(chart_df).encode(
        x=alt.X(f"{x_axis}:Q", title=x_axis, scale=alt.Scale(zero=False)),
        y=alt.Y(f"{y_axis}:Q", title=y_axis, scale=alt.Scale(zero=False)),
        tooltip=tooltips,
    )

    # Color encoding
    if color_by != "None":
        chart = base.mark_circle(size=60, opacity=0.6).encode(
            color=alt.Color(f"{color_by}:N", title=color_by)
        )
    else:
        chart = base.mark_circle(size=60, opacity=0.6, color="#1151ff")

    # Add highlighting for teams
    if highlight_teams:
        team_df = chart_df[chart_df["Team"].isin(highlight_teams)]
        highlight_layer = (
            alt.Chart(team_df)
            .mark_circle(size=120, opacity=1, stroke="gray", strokeWidth=1)
            .encode(
                x=f"{x_axis}:Q",
                y=f"{y_axis}:Q",
                color=alt.Color(f"{color_by}:N") if color_by != "None" else alt.value("#1151ff"),
                tooltip=tooltips,
            )
        )
        
        team_text_layer = (
            alt.Chart(team_df)
            .mark_text(align="left", dx=10, dy=-10, fontWeight="bold", color="gray")
            .encode(x=f"{x_axis}:Q", y=f"{y_axis}:Q", text="Player:N")
        )
        
        chart = chart + highlight_layer + team_text_layer

    # Determine players to highlight (searched + top x + top y)
    players_to_highlight = set(search_players) if search_players else set()
    
    if top_x > 0:
        top_x_players = chart_df.nlargest(top_x, x_axis)["Player"].tolist()
        players_to_highlight.update(top_x_players)
        
    if top_y > 0:
        top_y_players = chart_df.nlargest(top_y, y_axis)["Player"].tolist()
        players_to_highlight.update(top_y_players)

    # Add highlighting for specific players
    if players_to_highlight:
        highlighted_df = chart_df[chart_df["Player"].isin(players_to_highlight)]
        player_layer = (
            alt.Chart(highlighted_df)
            .mark_circle(size=200, opacity=1, stroke="gray", strokeWidth=1)
            .encode(
                x=f"{x_axis}:Q",
                y=f"{y_axis}:Q",
                tooltip=tooltips,
            )
        )

        # Add labels for highlighted players
        text_layer = (
            alt.Chart(highlighted_df)
            .mark_text(align="left", dx=10, dy=-10, color="gray")
            .encode(x=f"{x_axis}:Q", y=f"{y_axis}:Q", text="Player:N")
        )

        chart = chart + player_layer + text_layer

    # Add mean lines
    x_mean = chart_df[x_axis].mean()
    y_mean = chart_df[y_axis].mean()

    x_rule = alt.Chart(pd.DataFrame({x_axis: [x_mean]})).mark_rule(
        strokeDash=[5, 5], color="gray"
    ).encode(x=f"{x_axis}:Q")
    
    y_rule = alt.Chart(pd.DataFrame({y_axis: [y_mean]})).mark_rule(
        strokeDash=[5, 5], color="gray"
    ).encode(y=f"{y_axis}:Q")

    chart = (chart + x_rule + y_rule).properties(
        width="container", height=600, title=f"{y_axis} vs {x_axis}", background="#ffffff"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    # Summary Statistics
    st.markdown("---")
    st.markdown("### 📊 Quadrant Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Players in top-right quadrant
        top_right = chart_df[(chart_df[x_axis] > x_mean) & (chart_df[y_axis] > y_mean)]
        st.markdown(f"**High {x_axis} & High {y_axis}** ({len(top_right)} players)")
        st.dataframe(
            top_right[["Player", "Team", x_axis, y_axis]]
            .sort_values(by=y_axis, ascending=False)
            .head(10),
            use_container_width=True,
            hide_index=True,
        )

    with col2:
        # Correlation
        correlation = chart_df[x_axis].corr(chart_df[y_axis])
        st.metric("Correlation Coefficient", f"{correlation:.3f}")
        
        if correlation > 0.7:
            st.success("Strong positive correlation")
        elif correlation < -0.7:
            st.warning("Strong negative correlation")
        elif abs(correlation) < 0.3:
            st.info("Weak or no correlation")
