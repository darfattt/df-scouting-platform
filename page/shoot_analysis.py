"""
Shoot Analysis Page
Analyzes shooting metrics to identify players who should shoot more.
Shows shots attempted, % of team's shots, gradient shooting grade, and better option %.
"""

import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from io import BytesIO
import requests
from datetime import datetime

from config.grade_attributes import GRADE_ATTRIBUTES
from utils.data_loader import calculate_grade_attributes_batch


def create_shoot_analysis_table_figure(
    df_analysis: pd.DataFrame,
    df_filtered: pd.DataFrame,
    top_n: int = 20,
) -> plt.Figure:
    """Create matplotlib figure displaying shoot analysis in table format"""
    merged_df = df_analysis.head(top_n).copy()
    if "Team logo" in df_filtered.columns and "Team logo" not in merged_df.columns:
        team_logo_df = df_filtered[["Player", "Team logo"]].copy()
        merged_df = merged_df.merge(team_logo_df, on="Player", how="left")
        
    merged_df = merged_df.drop_duplicates(subset=["Player", "Team"], keep="first")
    merged_df = merged_df.head(top_n)

    n_rows = len(merged_df)
    row_height = 0.5
    fig_height = max(8, n_rows * row_height + 3)

    fig, ax = plt.subplots(figsize=(10, fig_height))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f5f5f5")

    ax.set_xlim(0, 18)
    ax.set_ylim(-n_rows - 1, 1)
    ax.axis("off")

    title_text = "Shot Analysis"
    ax.text(9, 0.5, title_text, fontsize=16, fontweight="bold", ha="center")

    subtitle_text = f"Top {n_rows} Performers"
    ax.text(9, 0, subtitle_text, fontsize=10, ha="center", style="italic", color="#666")

    header_y = -0.8
    ax.text(0.5, header_y, "Rank", fontsize=11, fontweight="bold", ha="center", va="bottom")
    ax.text(1.3, header_y, "Player", fontsize=11, fontweight="bold", ha="left", va="bottom")
    ax.text(5.5, header_y, "Club", fontsize=11, fontweight="bold", ha="center", va="bottom")
    ax.text(9.0, header_y, "Shots", fontsize=11, fontweight="bold", ha="center", va="bottom")
    ax.text(11.5, header_y, "% Team", fontsize=11, fontweight="bold", ha="center", va="bottom")
    ax.text(14.0, header_y, "Option %", fontsize=11, fontweight="bold", ha="center", va="bottom")
    ax.text(16.5, header_y, "Grade", fontsize=11, fontweight="bold", ha="center", va="bottom")

    ax.plot([0.3, 17.7], [header_y - 0.1, header_y - 0.1], "k-", linewidth=1.5)

    for idx, (_, row) in enumerate(merged_df.iterrows()):
        y_pos = header_y - 0.5 - (idx * row_height)

        ax.text(0.5, y_pos, str(idx + 1), fontsize=10, ha="center", va="center")
        
        player_name = row["Player"][:25] if len(row["Player"]) > 25 else row["Player"]
        ax.text(1.3, y_pos, player_name, fontsize=10, ha="left", va="center")

        if pd.notna(row.get("Team logo")):
            try:
                response = requests.get(row["Team logo"], timeout=3)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    imagebox = OffsetImage(img, zoom=0.15)
                    ab = AnnotationBbox(imagebox, (5.0, y_pos), frameon=False)
                    ax.add_artist(ab)
            except:
                pass

        team_name = row["Team"] if pd.notna(row["Team"]) else "Unknown"
        team_display = team_name[:15] + "..." if len(team_name) > 15 else team_name
        ax.text(5.8, y_pos, team_display, fontsize=10, ha="left", va="center")

        shots = int(row["Shots Attempted"]) if pd.notna(row["Shots Attempted"]) else 0
        ax.text(9.0, y_pos, str(shots), fontsize=10, ha="center", va="center")

        pct_team = row["% of Team's Shots"] if pd.notna(row["% of Team's Shots"]) else 0
        ax.text(11.5, y_pos, f"{pct_team:.1f}%", fontsize=10, ha="center", va="center")

        option_pct = row["Better Option %"] if pd.notna(row["Better Option %"]) else 0
        ax.text(14.0, y_pos, f"{option_pct:.1f}%", fontsize=10, ha="center", va="center")

        grade = row["GRADE_Shooting"] if pd.notna(row.get("GRADE_Shooting")) else 0
        ax.text(16.5, y_pos, f"{grade:.1f}", fontsize=10, ha="center", va="center", fontweight="bold")

    bottom_y = header_y - 0.5 - (n_rows * row_height) + 0.25
    ax.plot([0.3, 17.7], [bottom_y, bottom_y], "k-", linewidth=1.5)

    footer_y = bottom_y - 0.5
    today_date = datetime.now().strftime("%d/%m/%Y")
    footer_text = f"Generated: {today_date} | Data: Wyscout via Best11Scouting"
    ax.text(0.5, footer_y, footer_text, fontsize=8, ha="left", va="top", color="#666")

    plt.tight_layout()
    return fig


def render_shoot_analysis_page(df_filtered):
    """
    Render Shoot Analysis page — "Players who should shoot more?"

    Args:
        df_filtered: Filtered player dataframe with percentile columns
    """
    st.header("Shoot Analysis")
    st.markdown(
        "_Players who should shoot more? "
        "Players with the lowest Better Option % when shooting AND good/elite Shooting Grades._"
    )

    if len(df_filtered) == 0:
        st.warning(
            "⚠️ No players match the selected filters. Adjust global filters in sidebar."
        )
        return

    # ========== FILTERS ==========
    st.markdown("---")
    st.markdown("### ⚙️ Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        max_shots = int(df_filtered["Shots"].max()) if "Shots" in df_filtered.columns and df_filtered["Shots"].max() > 0 else 100
        min_shots = st.slider(
            "Min Shots Attempted:",
            min_value=0,
            max_value=max_shots,
            value=min(5, max_shots),
            step=1,
            key="shoot_min_shots",
            help="Filter out players with fewer total shots",
        )

    with col2:
        max_minutes = int(df_filtered["Minutes played"].max()) if "Minutes played" in df_filtered.columns else 3000
        min_minutes = st.slider(
            "Min Minutes Played:",
            min_value=0,
            max_value=max_minutes,
            value=min(300, max_minutes),
            step=50,
            key="shoot_min_minutes",
            help="Filter out players with insufficient playing time",
        )

    with col3:
        sort_options = [
            "Shooting Grade (High → Low)",
            "Better Option % (Low → High)",
            "Shots Attempted (High → Low)",
            "% of Team's Shots (High → Low)",
        ]
        sort_by = st.selectbox(
            "Sort By:",
            options=sort_options,
            index=0,
            key="shoot_sort_by",
        )

    st.markdown("---")

    # ========== DATA PROCESSING ==========
    df_work = df_filtered.copy()

    # Validate required columns
    required_cols = ["Shots", "Shots per 90", "Team", "Player", "Minutes played"]
    missing = [c for c in required_cols if c not in df_work.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        return

    # Apply filters
    df_work = df_work[
        (df_work["Shots"] >= min_shots) & (df_work["Minutes played"] >= min_minutes)
    ].copy()

    if len(df_work) == 0:
        st.warning("⚠️ No players match the filter criteria. Try lowering the thresholds.")
        return

    # 1. Shots Attempted — raw total Shots column
    df_work["Shots Attempted"] = df_work["Shots"].astype(int)

    # 2. % of Team's Shots — player shots / team total shots
    team_total_shots = df_work.groupby("Team")["Shots"].transform("sum")
    df_work["% of Team's Shots"] = np.where(
        team_total_shots > 0,
        (df_work["Shots"] / team_total_shots) * 100,
        0,
    )

    # 3. Gradient Shooting Grade — use existing grade calculation
    shooting_only = {"Shooting": GRADE_ATTRIBUTES["Shooting"]}
    df_work = calculate_grade_attributes_batch(df_work, shooting_only)
    grade_col = "GRADE_Shooting"

    # 4. Better Option % = Shot assists / (Shot assists + Shots per 90) × 100
    shot_assists_col = "Shot assists per 90"
    shots_p90_col = "Shots per 90"

    if shot_assists_col in df_work.columns and shots_p90_col in df_work.columns:
        denominator = df_work[shot_assists_col] + df_work[shots_p90_col]
        df_work["Better Option %"] = np.where(
            denominator > 0,
            (df_work[shot_assists_col] / denominator) * 100,
            0,
        )
    else:
        df_work["Better Option %"] = 0.0

    # ========== SORTING ==========
    if sort_by == "Shooting Grade (High → Low)":
        df_work = df_work.sort_values(grade_col, ascending=False)
    elif sort_by == "Better Option % (Low → High)":
        df_work = df_work.sort_values("Better Option %", ascending=True)
    elif sort_by == "Shots Attempted (High → Low)":
        df_work = df_work.sort_values("Shots Attempted", ascending=False)
    elif sort_by == "% of Team's Shots (High → Low)":
        df_work = df_work.sort_values("% of Team's Shots", ascending=False)

    df_work = df_work.reset_index(drop=True)
    df_work.index = df_work.index + 1  # 1-based rank

    # ========== RESULTS DISPLAY ==========
    st.markdown("---")
    st.markdown(f"### 📊 Analysis Results ({len(df_work)} players)")

    tab1, tab2 = st.tabs(["Data Table", "Export Figure"])
    
    with tab1:
        # Build display DataFrame
        display_cols = {
            "Player": "Player",
            "Team": "Team",
        }

        # Add League if available
        for league_col_name in ["League", "Competition"]:
            if league_col_name in df_work.columns:
                display_cols[league_col_name] = "League"
                break

        if "Position" in df_work.columns:
            display_cols["Position"] = "Position"

        display_cols.update(
            {
                "Shots Attempted": "Shots Attempted",
                "% of Team's Shots": "% of Team's Shots",
                grade_col: "Shooting Grade",
                "Better Option %": "Better Option %",
            }
        )

        df_display = df_work[list(display_cols.keys())].rename(columns=display_cols)

        # Configure column display
        column_config = {
            "Shots Attempted": st.column_config.NumberColumn(
                "Shots Attempted",
                format="%d",
            ),
            "% of Team's Shots": st.column_config.NumberColumn(
                "% of Team's Shots",
                format="%.1f%%",
            ),
            "Shooting Grade": st.column_config.ProgressColumn(
                "Shooting Grade",
                min_value=0,
                max_value=100,
                format="%.1f",
            ),
            "Better Option %": st.column_config.NumberColumn(
                "Better Option %",
                format="%.1f%%",
            ),
        }

        st.dataframe(
            df_display,
            use_container_width=True,
            height=min(700, 40 + len(df_display) * 35),
            column_config=column_config,
        )

    with tab2:
        st.markdown("#### Export Analysis Figure")
        st.markdown(
            "Generate a publication-ready figure for reports and presentations"
        )
        
        top_n = len(df_work) if len(df_work) <= 20 else 20
        fig = create_shoot_analysis_table_figure(
            df_work,
            df_filtered,
            top_n=st.number_input("Number of players in figure (Top N):", min_value=5, max_value=40, value=top_n, step=5)
        )
        
        st.pyplot(fig)
        
        st.info("💡 Right-click on the figure above to save as image, or use Streamlit's camera icon")

    # ========== SUMMARY METRICS ==========
    st.markdown("---")
    st.markdown("### 📈 Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_grade = df_work[grade_col].mean()
        st.metric("Avg Shooting Grade", f"{avg_grade:.1f}")

    with col2:
        avg_better = df_work["Better Option %"].mean()
        st.metric("Avg Better Option %", f"{avg_better:.1f}%")

    with col3:
        total_shots = df_work["Shots Attempted"].sum()
        st.metric("Total Shots", f"{total_shots:,}")

    with col4:
        top_grade_player = df_work.loc[df_work[grade_col].idxmax(), "Player"]
        st.metric("Best Shooter", top_grade_player)

    # ========== INSIGHT: SHOULD SHOOT MORE ==========
    st.markdown("---")
    st.markdown("### 🎯 Players Who Should Shoot More")
    st.markdown(
        "_Players with **low** Better Option % (they pass instead of shoot) "
        "AND **high** Shooting Grade (they're efficient when they do shoot)._"
    )

    # Filter: Shooting Grade >= 70 (good/elite) and Better Option % in bottom 50%
    grade_threshold = 60
    better_option_median = df_work["Better Option %"].median()

    df_should_shoot = df_work[
        (df_work[grade_col] >= grade_threshold)
        & (df_work["Better Option %"] <= better_option_median)
    ].sort_values("Better Option %", ascending=True)

    if len(df_should_shoot) > 0:
        df_should_shoot_display = df_should_shoot[list(display_cols.keys())].rename(
            columns=display_cols
        )
        st.dataframe(
            df_should_shoot_display,
            use_container_width=True,
            height=min(400, 40 + len(df_should_shoot_display) * 35),
            column_config=column_config,
        )
    else:
        st.info("No players match the 'should shoot more' criteria with current filters.")
