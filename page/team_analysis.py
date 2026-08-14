import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

# Import custom configurations
from config.stat_categories import STAT_CATEGORIES
from config.position_groups import (
    POSITION_GROUPS, 
    POSITION_GROUP_ORDER, 
    POSITION_GROUP_ICONS, 
    get_group_for_position
)
from config.composite_attributes import COMPOSITE_ATTRIBUTES, get_display_name
from config.role_definitions import get_all_roles
from config.registry import get_roles_for_position, get_responsibilities_for_position

# Import utilities
from utils.team_aggregator import aggregate_team_metrics
from utils.team_styles import analyze_team_style
from enrichment.ai_client import generate_scouting_report, is_configured
from enrichment.prompt_templates import build_team_gap_prompt

def _calculate_player_tactical_profile(row: pd.Series, all_roles: Dict) -> Tuple[str, List[str]]:
    """
    Calculate the best role and top archetypes for a player row.
    """
    # 1. Determine per-player position group
    player_pos = row.get("Primary position", "Unknown")
    player_group = get_group_for_position(player_pos)
    
    # Roles for this specific position group
    if player_group == "All":
        relevant_role_names = list(all_roles.keys())
    else:
        relevant_role_names = get_roles_for_position(player_group)
    
    # 2. Calculate Role Score
    row_role_scores = {}
    for role_name in relevant_role_names:
        if role_name in all_roles:
            role_info = all_roles[role_name]
            score = 0.0
            for comp in role_info.get("components", []):
                stat = comp["stat"]
                weight = comp["weight"]
                val = row.get(f"{stat}_percentile", row.get(stat, 50.0))
                if pd.isna(val): val = 50.0
                score += val * weight
            row_role_scores[role_name] = score
    
    best_role = max(row_role_scores, key=row_role_scores.get) if row_role_scores else "N/A"
    
    # 3. Identify Archetypes
    if player_group == "All":
        comp_cols = [c for c in row.index if c.startswith("COMP_")]
    else:
        relevant_comp_keys = get_responsibilities_for_position(player_group)
        comp_cols = [f"COMP_{k}" for k in relevant_comp_keys if f"COMP_{k}" in row.index]
        if not comp_cols:
            comp_cols = [c for c in row.index if c.startswith("COMP_")]
    
    if not comp_cols:
        return best_role, ["N/A"]
        
    top_3 = row[comp_cols].sort_values(ascending=False).head(3)
    archetypes = [c.replace("COMP_", "") for c in top_3.index]
    
    return best_role, archetypes

def _ensure_composite_score(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure the 'composite_score' column exists in the dataframe."""
    if "composite_score" in df.columns:
        return df
    
    df_copy = df.copy()
    # Calculate as mean of all COMP_ columns if available
    comp_cols = [c for c in df_copy.columns if c.startswith("COMP_")]
    if comp_cols:
        df_copy["composite_score"] = df_copy[comp_cols].mean(axis=1).fillna(0)
    else:
        df_copy["composite_score"] = 50.0 # Default fallback
    
    return df_copy

def _get_squad_analysis(df: pd.DataFrame, all_roles: Dict, min_mins: int) -> pd.DataFrame:
    """Helper to process a dataframe and return categorized player list."""
    df_f = df[df["Minutes played"] >= min_mins].copy()
    if df_f.empty: return pd.DataFrame()
    
    roles_list = []
    primary_archetype_list = []
    position_group_list = []
    
    for idx, row in df_f.iterrows():
        best_role, archetypes = _calculate_player_tactical_profile(row, all_roles)
        roles_list.append(best_role)
        primary_archetype_list.append(archetypes[0] if archetypes else "N/A")
        position_group_list.append(get_group_for_position(row.get("Primary position", "Unknown")))
        
    df_f["Best Role"] = roles_list
    df_f["Primary Archetype"] = primary_archetype_list
    df_f["Position Group"] = position_group_list
    return df_f

def render_team_analysis_page(df_filtered: pd.DataFrame, selected_position_group: str):
    """
    Render the new Team Analysis page.
    """
    st.header("Team Analysis Dashboard")
    st.caption("Deep-dive into team playing style, squad archetype composition, and tactical gap analysis.")

    if df_filtered.empty:
        st.warning("⚠️ No data matches the current global filters. Please adjust your selection (Leagues/Continents) in the sidebar.")
        return

    # Ensure composite_score exists for sorting and selection
    df_filtered = _ensure_composite_score(df_filtered)

    # --- 0. Team Selection ---
    st.markdown("### 🏹 1. Team Selection")
    all_teams = sorted([t for t in df_filtered["Team"].unique().tolist() if isinstance(t, str)])
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        target_team = st.selectbox("Select Target Team (Analysis Goal):", options=all_teams, key="team_analysis_target")
    
    all_teams_avg_score = df_filtered.groupby("Team")["composite_score"].mean().sort_values(ascending=False)
    top_4_teams = ["Persib", "Persija", "Borneo FC", "Lion City Sailors FC","Buriram United","Svay Rieng","Johor Darul Ta'zim","Công An Hà Nội"]
    if target_team in top_4_teams: top_4_teams.remove(target_team)
    #else: top_4_teams = top_4_teams[:8]
    
    with col_t2:
        benchmark_teams = st.multiselect("Select Benchmark Teams (Comparison):", options=all_teams, default=top_4_teams, key="team_analysis_benchmark")

    if not target_team:
        st.info("Please select a target team to begin.")
        return

    min_mins = st.slider("Min Minutes Played (Squad Analysis):", 0, 1500, 300, 100, key="team_min_mins")
    all_roles = get_all_roles()

    # --- Section 1: Player List ---
    df_target = df_filtered[df_filtered["Team"] == target_team]
    df_target_processed = _get_squad_analysis(df_target, all_roles, min_mins)

    if df_target_processed.empty:
        st.warning(f"No players in {target_team} match the minimum minutes criteria ({min_mins}).")
        return

    st.markdown("---")
    with st.expander("🏃 2. Player Tactical Profile", expanded=False):
        display_cols = ["Player", "Age","Primary position" ,"Position", "Best Role", "Primary Archetype", "Minutes played", "composite_score"]
        
        # Get unique groups in the squad and sort them using the standardized order
        squad_groups = sorted(
            df_target_processed["Position Group"].unique().tolist(), 
            key=lambda x: POSITION_GROUP_ORDER.index(x) if x in POSITION_GROUP_ORDER else 99
        )
        
        for group in squad_groups:
            icon = POSITION_GROUP_ICONS.get(group, "⚙️")
            st.subheader(f"{icon} {group}")
            df_group = df_target_processed[df_target_processed["Position Group"] == group]
            st.dataframe(
                df_group[display_cols].sort_values("Minutes played", ascending=False),
                use_container_width=True,
                hide_index=True
            )

    # --- Section 2: Squad Composition ---
    st.markdown("---")
    st.markdown("### 📊 3. How team play? (Squad Archetypes)")
    target_comp = df_target_processed["Primary Archetype"].value_counts().reset_index()
    target_comp.columns = ["Archetype", "Selected Team"]
    
    st.bar_chart(target_comp.set_index("Archetype"), use_container_width=True)
    
    st.markdown("#### 🎭 Calculated Tactical Identity")
    team_metrics = aggregate_team_metrics(df_filtered, target_team)
    
    if team_metrics:
        team_style_analysis = analyze_team_style(team_metrics)
        st.markdown(f"**{team_style_analysis['style_icon']} {team_style_analysis['style_name']}** — {team_style_analysis['style_description']}")
        
        c_str, c_wk = st.columns(2)
        with c_str:
            st.markdown("**Top Stylistic Strengths**")
            for dim, score in team_style_analysis['top_strengths']:
                st.write(f"- {dim} ({score:.0f}/100)")
        with c_wk:
            st.markdown("**Stylistic Weaknesses**")
            for dim, score in team_style_analysis['bottom_weaknesses']:
                st.write(f"- {dim} ({score:.0f}/100)")

    # --- Section 3: Benchmarking ---
    st.markdown("---")
    st.markdown("### ⚖️ 4. What team missing? (Position Group Benchmark)")
    
    if not benchmark_teams:
        st.info("Select benchmark teams to see the comparison.")
    else:
        with st.spinner("Analyzing benchmark teams..."):
            df_bench = df_filtered[df_filtered["Team"].isin(benchmark_teams)]
            df_bench_processed = _get_squad_analysis(df_bench, all_roles, min_mins)

            # Determine which position groups to analyse (from config order)
            active_groups = [
                g for g in POSITION_GROUP_ORDER
                if g in df_target_processed["Position Group"].values
                or g in df_bench_processed["Position Group"].values
            ]

            all_archetype_gaps = []  # Collect gaps across all groups for session state

        with st.expander("View Position Group Benchmarks", expanded=False):
            for group in active_groups:
                icon = POSITION_GROUP_ICONS.get(group, "⚙️")
                st.markdown(f"#### {icon} {group}")

                target_group_df = df_target_processed[df_target_processed["Position Group"] == group]
                bench_group_df  = df_bench_processed[df_bench_processed["Position Group"] == group]

                # --- Player count delta ---
                target_count = len(target_group_df)
                # Average count across benchmark teams for this group
                bench_count_per_team = (
                    df_bench_processed[df_bench_processed["Position Group"] == group]
                    .groupby("Team").size().mean()
                ) if not bench_group_df.empty else 0.0
                bench_count_per_team = bench_count_per_team if pd.notna(bench_count_per_team) else 0.0

                count_delta = bench_count_per_team - target_count
                col_cnt1, col_cnt2, col_cnt3 = st.columns(3)
                col_cnt1.metric("Your squad", f"{target_count} players")
                col_cnt2.metric("Benchmark avg", f"{bench_count_per_team:.1f} players")
                col_cnt3.metric("Δ Gap", f"{count_delta:+.1f}", delta_color="inverse")

                if target_group_df.empty or bench_group_df.empty:
                    if target_group_df.empty:
                        st.warning(f"⚠️ Target team has **no {group}** players meeting criteria.")
                    if bench_group_df.empty:
                        st.info(f"Benchmark teams have no {group} players — skipping archetype comparison.")
                    st.markdown("---")
                    continue

                # --- Archetype comparison within this group ---
                target_arch = target_group_df["Primary Archetype"].value_counts().reset_index()
                target_arch.columns = ["Archetype", "Selected Team"]

                # Avg archetype count per benchmark team within this group
                bench_arch_counts = (
                    bench_group_df.groupby(["Team", "Primary Archetype"]).size().reset_index(name="Count")
                )
                bench_arch_avg = bench_arch_counts.groupby("Primary Archetype")["Count"].mean().reset_index()
                bench_arch_avg.columns = ["Archetype", "Benchmark Avg"]

                group_comp = pd.merge(target_arch, bench_arch_avg, on="Archetype", how="outer").fillna(0)
                group_comp = group_comp.sort_values("Benchmark Avg", ascending=False)

                st.bar_chart(group_comp.set_index("Archetype"), use_container_width=True)

                # Identify archetype gaps within this group
                group_gaps = group_comp[
                    group_comp["Selected Team"] < (group_comp["Benchmark Avg"] * 0.8)
                ].copy()
                group_gaps["Gap Size"] = group_gaps["Benchmark Avg"] - group_gaps["Selected Team"]

                if not group_gaps.empty:
                    # Enrich with quality scores
                    t_qual = target_group_df.groupby("Primary Archetype")["composite_score"].mean().reset_index()
                    t_qual.columns = ["Archetype", "Target Quality"]
                    b_qual = bench_group_df.groupby("Primary Archetype")["composite_score"].mean().reset_index()
                    b_qual.columns = ["Archetype", "Bench Quality"]

                    group_gaps = pd.merge(group_gaps, t_qual, on="Archetype", how="left").fillna(40)
                    group_gaps = pd.merge(group_gaps, b_qual, on="Archetype", how="left").fillna(50)
                    group_gaps["Priority"] = group_gaps["Gap Size"] * (
                        group_gaps["Bench Quality"] / (group_gaps["Target Quality"] + 1)
                    )
                    group_gaps = group_gaps.sort_values("Priority", ascending=False)
                    group_gaps["Position Group"] = group
                    all_archetype_gaps.append(group_gaps)

                    st.markdown("**🔻 Archetype Gaps in this group:**")
                    for _, gap_row in group_gaps.iterrows():
                        st.write(
                            f"- **{gap_row['Archetype']}**: benchmark ~{gap_row['Benchmark Avg']:.1f} "
                            f"vs yours {gap_row['Selected Team']:.0f} "
                            f"(quality: {gap_row['Target Quality']:.1f} vs {gap_row['Bench Quality']:.1f})"
                        )
                else:
                    st.success(f"✅ Archetype balance in **{group}** is on par with benchmarks.")

                # --- Attribute/responsibility gaps within this group ---
                resps = get_responsibilities_for_position(group)
                attr_gap_rows = []
                for resp in resps:
                    col = f"COMP_{resp}"
                    if col in target_group_df.columns and col in bench_group_df.columns:
                        t_avg = target_group_df[col].mean()
                        b_avg = bench_group_df[col].mean()
                        if pd.notna(t_avg) and pd.notna(b_avg):
                            gap_score = b_avg - t_avg
                            if gap_score > 5:  # Only show meaningful gaps
                                attr_gap_rows.append({
                                    "Responsibility": resp,
                                    "Your Avg": round(t_avg, 1),
                                    "Bench Avg": round(b_avg, 1),
                                    "Gap": round(gap_score, 1)
                                })

                if attr_gap_rows:
                    attr_gap_df = pd.DataFrame(attr_gap_rows).sort_values("Gap", ascending=False)
                    st.markdown("**📉 Attribute Gaps in this group:**")
                    st.dataframe(attr_gap_df, use_container_width=True, hide_index=True)

                st.markdown("---")

        # Aggregate gaps summary
        st.markdown("---")
        st.markdown("### 💰 5. What filling gap is worth? (Marginal Value Summary)")

        all_gaps_df = pd.concat(all_archetype_gaps) if all_archetype_gaps else pd.DataFrame()

        if all_gaps_df.empty:
            st.success("✅ Squad archetype balance is on par with benchmarks across all position groups!")
        else:
            all_gaps_df = all_gaps_df.sort_values("Priority", ascending=False)
            st.warning(f"🔍 {len(all_gaps_df)} archetype gap(s) identified across position groups.")

            # ── Build long-form data for a grouped + stacked bar chart ──
            # We need rows like:
            #   Position Group | Squad | Archetype | Count
            # "Squad" = "Yours" or "Benchmark Avg"

            chart_rows = []
            for _, row in all_gaps_df.iterrows():
                pg  = row["Position Group"]
                arc = row["Archetype"]
                disp = get_display_name(arc)
                chart_rows.append({"Position Group": pg, "Squad": "Yours",         "Archetype": disp, "Is Gap": True,  "Count": row["Selected Team"]})
                chart_rows.append({"Position Group": pg, "Squad": "Benchmark Avg", "Archetype": disp, "Is Gap": True,  "Count": row["Benchmark Avg"]})

            # Add non-gap archetypes so each bar shows full squad composition
            for group in active_groups:
                tg_df = df_target_processed[df_target_processed["Position Group"] == group]
                bg_df = df_bench_processed[df_bench_processed["Position Group"] == group]
                if tg_df.empty and bg_df.empty:
                    continue
                gap_archs_raw = all_gaps_df[all_gaps_df["Position Group"] == group]["Archetype"].tolist()
                gap_archs_disp = [get_display_name(a) for a in gap_archs_raw]

                t_arch = tg_df["Primary Archetype"].value_counts().reset_index()
                t_arch.columns = ["Archetype", "Count"]
                for _, ar in t_arch.iterrows():
                    d = get_display_name(ar["Archetype"])
                    if d not in gap_archs_disp:
                        chart_rows.append({"Position Group": group, "Squad": "Yours",         "Archetype": d, "Is Gap": False, "Count": ar["Count"]})

                b_arch_counts = bg_df.groupby(["Team", "Primary Archetype"]).size().reset_index(name="n")
                b_arch_avg   = b_arch_counts.groupby("Primary Archetype")["n"].mean().reset_index()
                b_arch_avg.columns = ["Archetype", "Count"]
                for _, ar in b_arch_avg.iterrows():
                    d = get_display_name(ar["Archetype"])
                    if d not in gap_archs_disp:
                        chart_rows.append({"Position Group": group, "Squad": "Benchmark Avg", "Archetype": d, "Is Gap": False, "Count": ar["Count"]})

            chart_df = pd.DataFrame(chart_rows)
            chart_df = chart_df.groupby(["Position Group", "Squad", "Archetype", "Is Gap"], as_index=False)["Count"].sum()

            # Prefix gap archetypes in the legend so they stand out
            chart_df["Legend"] = chart_df.apply(
                lambda r: f"⚠ {r['Archetype']}" if r["Is Gap"] else r["Archetype"], axis=1
            )

            import altair as alt

            pg_order = [g for g in POSITION_GROUP_ORDER if g in chart_df["Position Group"].unique()]

            chart = (
                alt.Chart(chart_df)
                .mark_bar(width={"band": 0.9})
                .encode(
                    x=alt.X(
                        "Position Group:N",
                        sort=pg_order,
                        axis=alt.Axis(labelAngle=0, labelFontSize=12),
                        title=None,
                    ),
                    xOffset=alt.XOffset(
                        "Squad:N",
                        sort=["Yours", "Benchmark Avg"],
                    ),
                    y=alt.Y("Count:Q", title="Players (count)", stack="zero"),
                    color=alt.Color(
                        "Legend:N",
                        legend=alt.Legend(
                            title="Archetype  (⚠ = gap)",
                            orient="right",
                            labelLimit=160,
                            symbolLimit=40,
                        ),
                        scale=alt.Scale(scheme="tableau20"),
                    ),
                    tooltip=[
                        alt.Tooltip("Position Group:N"),
                        alt.Tooltip("Squad:N"),
                        alt.Tooltip("Archetype:N"),
                        alt.Tooltip("Count:Q", format=".1f"),
                        alt.Tooltip("Is Gap:N"),
                    ],
                )
                .properties(height=300)
            )

            # Overlay text labels showing "Yours | Bench Avg" under each pair
            squad_label = (
                alt.Chart(
                    pd.DataFrame([
                        {"Position Group": pg, "Squad": sq, "label": sq}
                        for pg in chart_df["Position Group"].unique()
                        for sq in ["Yours", "Benchmark Avg"]
                    ])
                )
                .mark_text(dy=12, angle=0, fontSize=9, color="#555")
                .encode(
                    x=alt.X("Position Group:N", sort=pg_order),
                    xOffset=alt.XOffset("Squad:N", sort=["Yours", "Benchmark Avg"]),
                    text=alt.Text("label:N"),
                    y=alt.value(300),
                )
            )

            st.altair_chart(chart, use_container_width=True)

            # ── Gap priority table ──
            display_gaps = all_gaps_df[["Position Group", "Archetype", "Selected Team", "Benchmark Avg", "Gap Size", "Target Quality", "Bench Quality", "Priority"]].copy()
            display_gaps["Archetype"] = display_gaps["Archetype"].apply(get_display_name)
            display_gaps.columns = ["Position Group", "Archetype", "Yours", "Bench Avg", "Gap", "Your Quality", "Bench Quality", "Priority"]
            st.dataframe(display_gaps.round(1), use_container_width=True, hide_index=True)

        # Store top gaps in session state for shortlist / AI section
        st.session_state["team_analysis_gaps"] = (
            all_gaps_df["Archetype"].tolist() if not all_gaps_df.empty else []
        )
        # Also expose position_attribute_gaps_df for AI prompt
        # (re-compute a flat version for the AI section below)
        position_attribute_gaps = []
        for group in active_groups:
            resps = get_responsibilities_for_position(group)
            target_group_df = df_target_processed[df_target_processed["Position Group"] == group]
            bench_group_df  = df_bench_processed[df_bench_processed["Position Group"] == group]
            if target_group_df.empty or bench_group_df.empty:
                continue
            max_gap, worst_resp, t_worst, b_worst = 0, None, 0, 0
            for resp in resps:
                col = f"COMP_{resp}"
                if col in target_group_df.columns and col in bench_group_df.columns:
                    t_avg = target_group_df[col].mean()
                    b_avg = bench_group_df[col].mean()
                    if pd.notna(t_avg) and pd.notna(b_avg):
                        gap = b_avg - t_avg
                        if gap > max_gap:
                            max_gap, worst_resp, t_worst, b_worst = gap, resp, t_avg, b_avg
            if worst_resp and max_gap > 0:
                position_attribute_gaps.append({
                    "Position Group": group, "Responsibility Gap": worst_resp,
                    "Gap Score": max_gap, "Target Avg": t_worst, "Bench Avg": b_worst
                })
        pos_attr_gaps_df = pd.DataFrame(position_attribute_gaps)
        if not pos_attr_gaps_df.empty:
            pos_attr_gaps_df = pos_attr_gaps_df.sort_values("Gap Score", ascending=False)
        
        # --- AI Analyst Squad Gap Section ---
        st.markdown("---")
        st.markdown("### 🧠 AI Analyst — Gap Evaluation")
        st.caption("Ask the AI Director of Football to analyze these gaps and output a scouting recommendation.")
        
        if not is_configured():
            st.warning("⚠️ **GEMINI_API_KEY / GROQ_API_KEY not configured.** Add it to your `.env` file.")
        else:
            if st.button("🤖 Generate Scouting Recommendation Report"):
                with st.spinner("AI is analyzing squad gaps and predicting market values..."):
                    try:
                        # --- 1. Position Group Headcount context ---
                        pg_gaps_list = []
                        for group in active_groups:
                            tg_df = df_target_processed[df_target_processed["Position Group"] == group]
                            bg_df = df_bench_processed[df_bench_processed["Position Group"] == group]
                            your_count = len(tg_df)
                            bench_avg = (
                                bg_df.groupby("Team").size().mean()
                                if not bg_df.empty else 0.0
                            )
                            bench_avg = bench_avg if pd.notna(bench_avg) else 0.0
                            pg_gaps_list.append({
                                "position_group": group,
                                "your_count": your_count,
                                "bench_avg_count": bench_avg,
                                "delta": bench_avg - your_count,
                            })

                        # --- 2. Ranked archetype gaps (grouped by position group) ---
                        # Group same position group archetypes into one priority item
                        arch_gaps_list = []
                        if not all_gaps_df.empty:
                            seen_pg = {}  # position_group -> first entry index
                            for _, r in all_gaps_df.iterrows():
                                pg = r.get("Position Group", "")
                                raw_arch = r.get("Archetype", "")
                                disp_arch = get_display_name(raw_arch)
                                if pg in seen_pg:
                                    # Append archetype to existing entry
                                    idx = seen_pg[pg]
                                    existing = arch_gaps_list[idx]
                                    existing["archetypes"].append(disp_arch)
                                    # Keep worst yours/bench_avg/gap across group
                                    existing["yours"] = min(existing["yours"], r.get("Selected Team", 0))
                                    existing["bench_avg"] = max(existing["bench_avg"], r.get("Benchmark Avg", 0))
                                    existing["gap"] = max(existing["gap"], r.get("Gap Size", 0))
                                    existing["priority"] = max(existing["priority"], r.get("Priority", 0))
                                else:
                                    seen_pg[pg] = len(arch_gaps_list)
                                    arch_gaps_list.append({
                                        "position_group": pg,
                                        "archetypes": [disp_arch],
                                        "yours": r.get("Selected Team", 0),
                                        "bench_avg": r.get("Benchmark Avg", 0),
                                        "gap": r.get("Gap Size", 0),
                                        "your_quality": r.get("Target Quality", 40),
                                        "bench_quality": r.get("Bench Quality", 50),
                                        "priority": r.get("Priority", 0),
                                    })
                            # Re-sort by priority descending
                            arch_gaps_list.sort(key=lambda x: x["priority"], reverse=True)

                        # --- 3. Attribute responsibility gaps ---
                        attr_gaps_list = []
                        if not pos_attr_gaps_df.empty:
                            for _, r in pos_attr_gaps_df.iterrows():
                                attr_gaps_list.append({
                                    "position_group": r["Position Group"],
                                    "responsibility": get_display_name(r["Responsibility Gap"]),
                                    "your_avg": r["Target Avg"],
                                    "bench_avg": r["Bench Avg"],
                                    "gap": r["Gap Score"],
                                })

                        prompt = build_team_gap_prompt(
                            target_team=target_team,
                            benchmark_teams=benchmark_teams,
                            gaps_text="No major tactical gaps identified." if not attr_gaps_list else "",
                            position_group_gaps=pg_gaps_list,
                            archetype_gaps=arch_gaps_list,
                            attribute_gaps=attr_gaps_list,
                        )
                        print(f"prompt: {prompt}")
                        
                        report = generate_scouting_report(prompt)
                        st.markdown(
                            f"""<div style='background:#f5f5f5;border-left:4px solid #1151ff;padding:20px;border-radius:0;margin-top:16px;'>
                            {report}
                            </div>""",
                            unsafe_allow_html=True
                        )
                    except Exception as e:
                        st.error(f"Failed to generate report: {e}")

    # --- Section 5: The Shortlist ---
    st.markdown("---")
    st.markdown("### 📜 6. The Shortlist (Recommended Targets)")
    
    # if "team_analysis_gaps" not in st.session_state or not st.session_state["team_analysis_gaps"]:
    #     st.info("No tactical gaps identified or benchmarks not selected.")
    # else:
    #     top_gaps = st.session_state["team_analysis_gaps"][:3]
    #     st.caption(f"Finding top targets matching your gaps: {', '.join(top_gaps)}")
        
    #     # Recommendations from global dataset (excluding target team)
    #     df_rec = df_filtered[df_filtered["Team"] != target_team].copy()
        
    #     # We need to categorize them for filtering. To optimize, we focus on players with high composite scores.
    #     # But categorization takes time, so we'll just filter for top composite scores first.
    #     # Then categorize the top 100 for more precise match.
        
    #     df_rec_top = df_rec.nlargest(100, "composite_score")
    #     df_rec_processed = _get_squad_analysis(df_rec_top, all_roles, 300)
        
    #     # Match with gaps
    #     recommendations = df_rec_processed[df_rec_processed["Primary Archetype"].isin(top_gaps)]
        
    #     if recommendations.empty:
    #         st.info("No immediate elite matches found in current filters. Try broadening your League/Continent selection.")
    #     else:
    #         st.dataframe(
    #             recommendations[["Player", "Team", "Position", "Age", "Primary Archetype", "composite_score"]].sort_values("composite_score", ascending=False).head(10),
    #             use_container_width=True,
    #             hide_index=True
    #         )

if __name__ == "__main__":
    pass
