import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from config.composite_attributes import COMPOSITE_ATTRIBUTES
from config.grade_attributes import GRADE_ATTRIBUTES
from utils.data_loader import calculate_grade_attributes_batch

def render_player_details_page(df_filtered):
    st.header("Player Details")

    if len(df_filtered) == 0:
        st.warning("⚠️ No players match the selected global filters.")
        return

    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        # Player Selection
        all_players = sorted(df_filtered["Player"].unique())
        selected_player = st.selectbox(
            "Search and Select Player:",
            options=all_players,
            index=0,
            key="details_player_select"
        )
        
        # Player Info
        player_data = df_filtered[df_filtered["Player"] == selected_player].iloc[0]
        
        st.markdown(f"### {selected_player}")
        st.markdown(f"**Team:** {player_data.get('Team', 'N/A')}")
        st.markdown(f"**League:** {player_data.get('League', 'N/A')}")
        st.markdown(f"**Age:** {player_data.get('Age', 'N/A')}")
        st.markdown(f"**Position:** {player_data.get('Position', 'N/A')}")
        st.markdown(f"**Minutes played:** {player_data.get('Minutes played', 'N/A')}")
        
    with col2:
        # Profile Analysis Selection
        st.markdown("### Profile Analysis")
        
        metric_source = st.radio(
            "Select Metric Type:",
            options=["Composite Attributes", "Evaluation Grades"],
            horizontal=True,
            key="details_metric_source"
        )
        
        if metric_source == "Composite Attributes":
            source_dict = COMPOSITE_ATTRIBUTES
            prefix = "COMP_"
        else:
            source_dict = GRADE_ATTRIBUTES
            prefix = "GRADE_"
            # Check if grades are calculated
            grade_cols = [f"GRADE_{name}" for name in GRADE_ATTRIBUTES.keys()]
            missing_grades = [col for col in grade_cols if col not in df_filtered.columns]
            if missing_grades:
                with st.spinner("Calculating grades..."):
                    df_filtered = calculate_grade_attributes_batch(df_filtered, GRADE_ATTRIBUTES)
        
        options = list(source_dict.keys())
        selected_metrics = st.multiselect(
            f"Select {metric_source}:",
            options=options,
            default=[options[0]] if options else [],
            format_func=lambda x: source_dict[x]["display_name"],
            key="details_metric_select"
        )
        
        for sm in selected_metrics:
            info = source_dict[sm]
            st.info(f"{info.get('icon', '')} **{info['display_name']}**: {info['description']}")

    st.markdown("---")
    st.markdown("### Profile Metrics vs. Filtered Cohort")
    st.caption("Compare the selected player against all players in the currently filtered data.")

    if not selected_metrics:
        st.warning(f"Please select at least one {metric_source}.")
        return

    # Add custom CSS for the ranking bars — Nike design system
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #ffffff; }
    [data-testid="stHeader"] { background-color: rgba(255,255,255,0.95); border-bottom: 1px solid #cacacb; }
    .ranking-container {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        font-family: 'Inter', sans-serif;
    }
    .metric-name {
        width: 250px;
        font-weight: 600;
        font-size: 1rem;
        color: #111111;
    }
    .value-box {
        border: 1px solid #cacacb;
        border-radius: 0;
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.4rem;
        margin-right: 12px;
        color: #111111;
        background-color: #f5f5f5;
    }
    .progress-wrapper {
        flex-grow: 1;
        background-color: #f5f5f5;
        border-radius: 0;
        height: 32px;
        position: relative;
        overflow: hidden;
        border: 1px solid #cacacb;
    }
    .progress-bar {
        height: 100%;
        border-radius: 0;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 15px;
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
        transition: width 0.4s ease-in-out;
    }
    .rank-text {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        color: #111111;
        font-weight: 600;
        font-size: 0.85rem;
        pointer-events: none;
    }
    .tab-content-container {
        background-color: #ffffff;
        padding: 20px;
        border: 1px solid #cacacb;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    tab_dist, tab_rank = st.tabs(["Distribution", "Rankings"])

    # Pre-calculate data for both tabs to avoid redundancy
    chart_data_list = []
    
    for m_name in selected_metrics:
        metric_col = f"{prefix}{m_name}"
        if metric_col not in df_filtered.columns:
            continue
            
        valid_data = df_filtered.dropna(subset=[metric_col]).copy()
        valid_cohort_size = len(valid_data)
        if valid_cohort_size == 0:
            continue
            
        if selected_player not in valid_data["Player"].values:
            continue
            
        ascending_rank = False
        valid_data["Rank"] = valid_data[metric_col].rank(ascending=ascending_rank, method="min")
        valid_data["jitter"] = np.random.uniform(-0.4, 0.4, valid_cohort_size)
        
        player_row = valid_data[valid_data["Player"] == selected_player].iloc[0]
        player_val = player_row[metric_col]
        player_rank = int(player_row["Rank"])
        
        # Percentile for the bar width and color (0 to 100)
        percentile = (valid_cohort_size - player_rank + 1) / valid_cohort_size * 100
        
        # 3-band semantic color — Nike design system
        if percentile < 33:
            bar_color = "#d30005"   # ALERT
        elif percentile < 67:
            bar_color = "#0a7281"   # ACCENT_TEAL
        else:
            bar_color = "#007d48"   # SUCCESS

        # Ordinal suffix for rank
        def get_ordinal(n):
            if 11 <= (n % 100) <= 13:
                suffix = 'th'
            else:
                suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
            return f"{n}{suffix}"

        chart_data_list.append({
            "m_name": m_name,
            "display_name": source_dict[m_name]['display_name'],
            "metric_col": metric_col,
            "player_val": player_val,
            "player_rank": player_rank,
            "rank_display": get_ordinal(player_rank),
            "cohort_size": valid_cohort_size,
            "percentile": percentile,
            "bar_color": bar_color,
            "valid_data": valid_data,
            "player_row": player_row
        })

    with tab_dist:
        st.markdown('<div class="tab-content-container">', unsafe_allow_html=True)
        st.caption("Dots represent all players in the currently filtered data. The selected player is highlighted in blue.")
        for data in chart_data_list:
            player_val_formatted = f"{data['player_val']:.1f}"
            
            # Score for coloring (0 to 100, where 100 is best)
            data["valid_data"]["Score"] = data["valid_data"]["Rank"].rank(ascending=False, pct=True) * 100
            
            # Base dots
            base_points = alt.Chart(data["valid_data"]).mark_circle(size=60, opacity=0.8).encode(
                x=alt.X(f"{data['metric_col']}:Q", title=None, scale=alt.Scale(zero=False)),
                y=alt.Y("jitter:Q", axis=None, title=None, scale=alt.Scale(domain=[-1, 1])),
                color=alt.Color("Score:Q", scale=alt.Scale(scheme="redyellowgreen", domain=[0, 100]), legend=None),
                tooltip=["Player", "Team", f"{data['metric_col']}:Q", "Rank:Q"]
            )
            
            # Highlight player dot
            highlight_df = pd.DataFrame([data["player_row"]])
            highlight_point = alt.Chart(highlight_df).mark_circle(
                size=400, opacity=1, color="#2f66e0", stroke="white", strokeWidth=2
            ).encode(
                x=alt.X(f"{data['metric_col']}:Q"),
                y=alt.Y("jitter:Q"),
                tooltip=["Player", "Team", f"{data['metric_col']}:Q", "Rank:Q"],
                order=alt.value(1)
            )
            
            # Text labels
            highlight_df["label_line1"] = f"{selected_player}"
            highlight_df["label_line2"] = f"{player_val_formatted} - #{data['player_rank']} out of {data['cohort_size']}"
            
            text_line1 = alt.Chart(highlight_df).mark_text(
                align="center", baseline="bottom", dy=-18, fontSize=12, fontWeight="bold", color="#707072"
            ).encode(
                x=alt.X(f"{data['metric_col']}:Q"),
                y=alt.Y("jitter:Q"),
                text="label_line1:N"
            )
            
            text_line2 = alt.Chart(highlight_df).mark_text(
                align="center", baseline="bottom", dy=20, fontSize=11, color="gray"
            ).encode(
                x=alt.X(f"{data['metric_col']}:Q"),
                y=alt.Y("jitter:Q"),
                text="label_line2:N"
            )
            
            chart = alt.layer(base_points, highlight_point, text_line1, text_line2).properties(
                height=160,
                width="container",
                background="#ffffff",
                title=alt.TitleParams(text=data["display_name"], font="sans-serif", fontSize=14, anchor="start", offset=10)
            ).configure_view(strokeWidth=0).configure_axis(grid=False)
            
            st.altair_chart(chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_rank:
        st.markdown('<div class="tab-content-container">', unsafe_allow_html=True)
        st.markdown(f"#### {selected_player} — Position Rank")
        st.write("")
        
        for data in chart_data_list:
            player_val_rounded = int(round(data['player_val']))
            
            html_bar = f"""
            <div class="ranking-container">
                <div class="metric-name">{data['display_name']}</div>
                <div class="value-box">{player_val_rounded}</div>
                <div class="progress-wrapper">
                    <div class="progress-bar" style="width: {data['percentile']:.1f}%; background-color: {data['bar_color']};">
                    </div>
                    <div class="rank-text">{data['rank_display']} / {data['cohort_size']}</div>
                </div>
            </div>
            """
            st.markdown(html_bar, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
