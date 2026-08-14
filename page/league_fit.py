"""
League Fit Analysis Page
Scores shortlisted players against a user-selected target league
using 11 event-based physical proxy metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from config.league_fit_config import (
    METRIC_COLUMNS,
    METRIC_DISPLAY,
    POSITION_WEIGHTS,
    POSITION_WEIGHTS_UNIFORM,
    POSITION_GROUP_TO_WEIGHT_KEY,
    RISK_READY_MIN,
    RISK_MONITOR_MIN,
    RISK_COLORS,
    RISK_BG_COLORS,
)
from config.position_groups import POSITION_GROUPS
from utils.league_fit import (
    compute_target_benchmarks,
    create_benchmark_comparison_chart,
    create_fit_leaderboard_figure,
    create_player_deep_dive_figure,
)

BG_COLOR = "#ffffff"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_weight_vector(position_group: str) -> pd.Series:
    key = POSITION_GROUP_TO_WEIGHT_KEY.get(position_group)
    raw = POSITION_WEIGHTS.get(key, POSITION_WEIGHTS_UNIFORM) if key else POSITION_WEIGHTS_UNIFORM
    return pd.Series({col: raw.get(col, 1.0) for col in METRIC_COLUMNS})


def _classify_risk(score: float) -> str:
    if score >= RISK_READY_MIN:
        return "Ready"
    if score >= RISK_MONITOR_MIN:
        return "Monitor"
    return "Risk"


def _score_players(
    df_all: pd.DataFrame,
    player_names: list,
    position_group: str,
    target_benchmarks: pd.DataFrame,
) -> pd.DataFrame:
    """Score a specific list of players against target benchmarks."""
    mask = df_all["Player"].isin(player_names)
    candidates = df_all.loc[mask].copy()

    if candidates.empty:
        return pd.DataFrame()

    weights = _get_weight_vector(position_group)
    active_metrics = []

    for col in METRIC_COLUMNS:
        bm = target_benchmarks.loc[col]
        if bm["missing"]:
            candidates[f"z_{col}"] = np.nan
            continue
        active_metrics.append(col)
        mean_val = bm["mean"]
        std_val = bm["std"]
        raw = pd.to_numeric(candidates[col], errors="coerce")
        if std_val == 0:
            candidates[f"z_{col}"] = 0.0
        else:
            candidates[f"z_{col}"] = (raw - mean_val) / std_val
        candidates[f"z_{col}"] = candidates[f"z_{col}"].fillna(-1.0)

    if not active_metrics:
        return pd.DataFrame()

    z_cols = [f"z_{col}" for col in active_metrics]
    w_active = weights[active_metrics]
    clipped = candidates[z_cols].clip(-2, 2)
    normalised = (clipped + 2) / 4

    weight_sum = w_active.values.sum()
    score_vector = np.zeros(len(candidates))
    for col in active_metrics:
        score_vector += normalised[f"z_{col}"].values * w_active[col]

    candidates["fit_score"] = (score_vector / weight_sum * 100).round(1)
    candidates["risk"] = candidates["fit_score"].apply(_classify_risk)

    info_cols = ["Player", "Team", "Age", "League", "Position", "Minutes played"]
    z_out = [f"z_{col}" for col in METRIC_COLUMNS if f"z_{col}" in candidates.columns]
    available = [c for c in info_cols + METRIC_COLUMNS + ["fit_score", "risk"] + z_out if c in candidates.columns]
    out = candidates[available].copy()
    out = out.sort_values("fit_score", ascending=False).reset_index(drop=True)
    out.index = out.index + 1
    out.index.name = "Rank"
    return out


def _build_metric_details(player_row: pd.Series, target_benchmarks: pd.DataFrame, weights: pd.Series) -> list:
    """Build a list of metric dicts for the AI prompt."""
    details = []
    for col in METRIC_COLUMNS:
        bm = target_benchmarks.loc[col]
        if bm["missing"]:
            continue
        player_val = pd.to_numeric(player_row.get(col, np.nan), errors="coerce")
        if np.isnan(player_val):
            player_val = 0.0
        std_val = bm["std"] if bm["std"] != 0 else 1.0
        z = (player_val - bm["mean"]) / std_val
        details.append({
            "metric_display": METRIC_DISPLAY[col],
            "player_val": float(player_val),
            "league_mean": float(bm["mean"]),
            "league_std": float(bm["std"]),
            "z_score": float(z),
            "weight": float(weights.get(col, 1.0)),
        })
    return details


# ---------------------------------------------------------------------------
# Risk summary cards
# ---------------------------------------------------------------------------

def _render_risk_summary(scored_df: pd.DataFrame):
    counts = scored_df["risk"].value_counts()
    ready = counts.get("Ready", 0)
    monitor = counts.get("Monitor", 0)
    risk = counts.get("Risk", 0)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div style='background:#e6f4ed;border:1px solid #007d48;border-radius:0;padding:16px;text-align:center'>"
            f"<h2 style='color:#007d48;margin:0'>{ready}</h2>"
            f"<b>Ready</b><br><small style='color:#707072'>Fit score ≥ {RISK_READY_MIN}</small></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div style='background:#e6f1f2;border:1px solid #0a7281;border-radius:0;padding:16px;text-align:center'>"
            f"<h2 style='color:#0a7281;margin:0'>{monitor}</h2>"
            f"<b>Monitor</b><br><small style='color:#707072'>Fit score {RISK_MONITOR_MIN}–{RISK_READY_MIN - 1}</small></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div style='background:#fce6e6;border:1px solid #d30005;border-radius:0;padding:16px;text-align:center'>"
            f"<h2 style='color:#d30005;margin:0'>{risk}</h2>"
            f"<b>Risk</b><br><small style='color:#707072'>Fit score &lt; {RISK_MONITOR_MIN}</small></div>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Styled results table
# ---------------------------------------------------------------------------

def _render_results_table(scored_df: pd.DataFrame, target_league: str):
    st.markdown("#### 📋 Fit Score Results")

    display_cols = ["Player", "Team", "Age", "League", "Position", "Minutes played", "fit_score", "risk"]
    available = [c for c in display_cols if c in scored_df.columns]
    table_df = scored_df.reset_index()[["Rank"] + available].copy()

    def _style_risk(val):
        colors = {"Ready": "background-color:#e6f4ed;color:#007d48;font-weight:bold",
                  "Monitor": "background-color:#e6f1f2;color:#0a7281;font-weight:bold",
                  "Risk": "background-color:#fce6e6;color:#d30005;font-weight:bold"}
        return colors.get(val, "")

    def _style_score(val):
        try:
            v = float(val)
            if v >= RISK_READY_MIN:
                return "color:#27ae60;font-weight:bold"
            if v >= RISK_MONITOR_MIN:
                return "color:#d68910;font-weight:bold"
            return "color:#d30005;font-weight:bold"
        except Exception:
            return ""

    styled = (
        table_df.style
        .applymap(_style_risk, subset=["risk"])
        .applymap(_style_score, subset=["fit_score"])
        .format({"fit_score": "{:.1f}", "Age": "{:.0f}"})
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# AI Report Section
# ---------------------------------------------------------------------------

def _render_ai_section(
    scored_df: pd.DataFrame,
    df_all: pd.DataFrame,
    target_benchmarks: pd.DataFrame,
    target_league: str,
    position_group: str,
):
    st.markdown("---")
    st.markdown("### 🧠 AI League Adaptation Report")
    st.caption(
        "Select a player to generate a professional AI-written adaptation report, "
        "based on their physical metrics vs the target league benchmarks."
    )

    try:
        from enrichment.ai_client import generate_scouting_report, is_configured
        from enrichment.prompt_templates import build_league_fit_prompt
    except ImportError as e:
        st.error(f"❌ Import error: {e}")
        return

    if not is_configured():
        st.warning(
            "⚠️ **No AI API key configured.** Add `GROQ_API_KEY` or `GEMINI_API_KEY` to your `.env` file."
        )
        return

    player_options = scored_df.reset_index()["Player"].tolist()
    selected_player = st.selectbox(
        "Select player for AI report:",
        options=player_options,
        key="league_fit_ai_player_select",
    )

    if st.button("📝 Generate League Adaptation Report", type="primary", key="league_fit_ai_btn"):
        # Get player row from scored_df
        player_scored = scored_df.reset_index()
        player_scored = player_scored[player_scored["Player"] == selected_player]
        if player_scored.empty:
            st.error("Player not found in results.")
            return
        player_scored_row = player_scored.iloc[0]

        # Get full player row from df_all for metric values
        player_full = df_all[df_all["Player"] == selected_player]
        player_row = player_full.iloc[0] if not player_full.empty else player_scored_row

        # Build metric details
        weights = _get_weight_vector(position_group)
        metric_details = _build_metric_details(player_row, target_benchmarks, weights)

        above_avg = sum(1 for m in metric_details if m["z_score"] >= 0)
        below_avg = sum(1 for m in metric_details if m["z_score"] < 0)

        prompt = build_league_fit_prompt(
            player_name=selected_player,
            position=str(player_row.get("Position", "Unknown")),
            team=str(player_row.get("Team", "Unknown")),
            source_league=str(player_row.get("League", "Unknown")),
            target_league=target_league,
            fit_score=float(player_scored_row.get("fit_score", 0)),
            risk_label=str(player_scored_row.get("risk", "Risk")),
            position_group=position_group,
            metric_details=metric_details,
            above_avg_count=above_avg,
            below_avg_count=below_avg,
        )

        with st.spinner(f"🧠 Generating adaptation report for {selected_player}..."):
            try:
                report = generate_scouting_report(prompt)
                st.session_state["league_fit_ai_report"] = report
                st.session_state["league_fit_ai_player"] = selected_player
            except Exception as e:
                st.error(f"❌ AI error: {e}")
                return

    # Display report
    if (
        st.session_state.get("league_fit_ai_report")
        and st.session_state.get("league_fit_ai_player") == selected_player
    ):
        fit_score = 0.0
        risk = "Risk"
        try:
            row = scored_df.reset_index()
            row = row[row["Player"] == selected_player].iloc[0]
            fit_score = float(row["fit_score"])
            risk = str(row["risk"])
        except Exception:
            pass

        risk_color = RISK_COLORS.get(risk, "#333")
        risk_bg = RISK_BG_COLORS.get(risk, "#fff")

        st.markdown(
            f"<div style='background:{risk_bg};border:1px solid {risk_color};"
            f"border-radius:0;padding:10px 16px;margin-bottom:12px'>"
            f"<b style='color:{risk_color}'>{risk} — Fit Score: {fit_score:.1f}/100</b>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='background:#f5f5f5;border:1px solid #cacacb;border-radius:0;padding:20px'>",
            unsafe_allow_html=True,
        )
        st.markdown(st.session_state["league_fit_ai_report"])
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("📋 Copy raw text"):
            st.text_area(
                "Report text:",
                value=st.session_state["league_fit_ai_report"],
                height=300,
                key="league_fit_report_copy",
            )

        st.caption(
            "⚠️ **Disclosure:** Generated by AI based on statistical data only. "
            "Validate with video analysis before making transfer decisions."
        )


# ---------------------------------------------------------------------------
# Main page renderer
# ---------------------------------------------------------------------------

def render_league_fit_page(df_filtered: pd.DataFrame, df_raw: pd.DataFrame = None):
    """
    Render the League Fit Analysis page.

    Args:
        df_filtered: Position/league-filtered player data (used for player selection)
        df_raw: Full unfiltered dataset (used to compute target league benchmarks)
    """
    st.header("League Fit Analysis")
    st.markdown(
        "Evaluate how shortlisted players would physically adapt to a **target league** "
        "using 11 event-based proxy metrics — no GPS data required."
    )

    if df_filtered is None or df_filtered.empty:
        st.warning("⚠️ No players match current filters. Adjust the sidebar filters.")
        return

    # Fall back to df_filtered if df_raw not provided
    df_all = df_raw if df_raw is not None and not df_raw.empty else df_filtered

    # Check required columns
    if "League" not in df_all.columns:
        st.error("❌ 'League' column missing from data.")
        return

    # ── Configuration panel ─────────────────────────────────────────────────
    st.markdown("### ⚙️ Configuration")
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        all_leagues = sorted([l for l in df_all["League"].dropna().unique() if isinstance(l, str)])
        # Default to Liga 1 if present
        default_idx = all_leagues.index("Liga 1") if "Liga 1" in all_leagues else 0
        target_league = st.selectbox(
            "🎯 Target League:",
            options=all_leagues,
            index=default_idx,
            key="lf_target_league",
            help="The league you want to evaluate fit against.",
        )

    with col2:
        pos_options = [k for k in POSITION_GROUPS.keys() if k != "All"]
        position_group = st.selectbox(
            "📍 Position Group (for weighting):",
            options=pos_options,
            key="lf_position_group",
            help="Determines which metrics are weighted most heavily for this position.",
        )

    with col3:
        min_minutes = st.number_input(
            "⏱ Min Minutes:",
            min_value=100,
            max_value=2000,
            value=500,
            step=100,
            key="lf_min_minutes",
            help="Minimum minutes played to be included in benchmarks.",
        )

    # ── Player selection ────────────────────────────────────────────────────
    st.markdown("### 👥 Select Shortlisted Players")

    player_options = sorted(df_filtered["Player"].dropna().unique().tolist())
    if not player_options:
        st.warning("No players available to select.")
        return

    selected_players = st.multiselect(
        "Choose players to evaluate:",
        options=player_options,
        default=[],
        key="lf_player_multiselect",
        help="Select up to 20 players from your current filtered pool.",
        max_selections=20,
    )

    if not selected_players:
        st.info("👆 Select at least one player above, then click **Analyze**.")
        return

    # ── Analyze button ──────────────────────────────────────────────────────
    # Use lf_run_* keys (not widget keys) to store the snapshot of config at analysis time
    if st.button("▶ Analyze League Fit", type="primary", key="lf_analyze_btn", use_container_width=True):
        st.session_state["lf_run"] = True
        st.session_state["lf_run_target_league"] = target_league
        st.session_state["lf_run_position_group"] = position_group
        st.session_state["lf_run_min_minutes"] = min_minutes
        st.session_state["lf_run_selected_players"] = selected_players
        # Clear previous AI report when re-running
        st.session_state.pop("league_fit_ai_report", None)
        st.session_state.pop("league_fit_ai_player", None)

    if not st.session_state.get("lf_run"):
        return

    # Read back from lf_run_* (separate from widget keys to avoid Streamlit conflict)
    target_league = st.session_state.get("lf_run_target_league", target_league)
    position_group = st.session_state.get("lf_run_position_group", position_group)
    min_minutes = st.session_state.get("lf_run_min_minutes", min_minutes)
    selected_players = st.session_state.get("lf_run_selected_players", selected_players)

    st.markdown("---")

    # ── Compute benchmarks ──────────────────────────────────────────────────
    with st.spinner(f"Computing {target_league} benchmarks for {position_group}..."):
        try:
            target_benchmarks = compute_target_benchmarks(
                df_all,
                position_group,
                min_minutes=min_minutes,
                target_club=None,
            )
            # Override the hardcoded TARGET_LEAGUE by filtering df_all ourselves
            from config.league_fit_config import TARGET_LEAGUE
            if target_league != TARGET_LEAGUE:
                # Recompute with the user-selected league
                from utils.league_fit import _position_filter_mask
                mask = (
                    (df_all["League"] == target_league)
                    & _position_filter_mask(df_all, position_group)
                    & (df_all["Minutes played"] >= min_minutes)
                )
                subset = df_all.loc[mask, METRIC_COLUMNS]
                rows = []
                for col in METRIC_COLUMNS:
                    series = pd.to_numeric(subset[col], errors="coerce").dropna()
                    count = len(series)
                    rows.append({
                        "metric": col,
                        "mean": series.mean() if count > 0 else np.nan,
                        "std": series.std(ddof=1) if count > 1 else 0.0,
                        "count": count,
                        "low_sample": count < 5,
                        "missing": count == 0,
                    })
                target_benchmarks = pd.DataFrame(rows).set_index("metric")
        except Exception as e:
            st.error(f"❌ Failed to compute benchmarks: {e}")
            return

    # Check for low sample warnings
    missing_metrics = target_benchmarks[target_benchmarks["missing"]].index.tolist()
    low_sample_metrics = target_benchmarks[target_benchmarks["low_sample"] & ~target_benchmarks["missing"]].index.tolist()

    if missing_metrics:
        st.warning(
            f"⚠️ **{len(missing_metrics)} metrics have no data** for {target_league} "
            f"({position_group}, ≥{min_minutes} min). They will be excluded from scoring. "
            f"Try reducing min minutes or selecting 'All' position group."
        )
    if low_sample_metrics:
        st.info(
            f"ℹ️ Low sample size (< 5 players) for {len(low_sample_metrics)} metrics — "
            f"benchmarks may be imprecise."
        )

    # ── Score players ───────────────────────────────────────────────────────
    with st.spinner("Scoring players..."):
        scored_df = _score_players(df_all, selected_players, position_group, target_benchmarks)

    if scored_df.empty:
        st.error("❌ Could not score players. Check that selected players exist in the dataset.")
        return

    # ── Summary cards ────────────────────────────────────────────────────────
    st.markdown(f"### 📊 Results — {target_league} Fit ({position_group})")
    _render_risk_summary(scored_df)
    st.markdown("")

    # ── Results table ────────────────────────────────────────────────────────
    _render_results_table(scored_df, target_league)

    # ── Benchmark info ───────────────────────────────────────────────────────
    with st.expander(f"📐 {target_league} Benchmark Details ({position_group})", expanded=False):
        bm_display = target_benchmarks.copy()
        bm_display.index = [METRIC_DISPLAY.get(i, i) for i in bm_display.index]
        bm_display = bm_display[["mean", "std", "count", "low_sample", "missing"]]
        bm_display.columns = ["Mean", "Std Dev", "Players", "Low Sample?", "Missing?"]
        bm_display["Mean"] = bm_display["Mean"].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "—")
        bm_display["Std Dev"] = bm_display["Std Dev"].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "—")
        st.dataframe(bm_display, use_container_width=True)

    # ── Charts ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📈 Visualizations")

    tab_bench, tab_board, tab_dive = st.tabs([
        "📊 Benchmark Comparison",
        "🏆 Fit Leaderboard",
        "🔍 Player Deep Dive",
    ])

    with tab_bench:
        st.markdown(
            f"Compares **{target_league}** average metrics against the source leagues "
            f"of your shortlisted players."
        )
        source_leagues = scored_df["League"].dropna().unique().tolist()

        # Build source benchmarks manually (same pattern as compute_source_benchmarks)
        source_benchmarks = {}
        for league in source_leagues:
            from utils.league_fit import _position_filter_mask
            mask = (
                (df_all["League"] == league)
                & _position_filter_mask(df_all, position_group)
                & (df_all["Minutes played"] >= min_minutes)
            )
            subset = df_all.loc[mask, METRIC_COLUMNS]
            rows = []
            for col in METRIC_COLUMNS:
                series = pd.to_numeric(subset[col], errors="coerce").dropna()
                count = len(series)
                rows.append({
                    "metric": col,
                    "mean": series.mean() if count > 0 else np.nan,
                    "std": series.std(ddof=1) if count > 1 else 0.0,
                    "count": count,
                })
            source_benchmarks[league] = pd.DataFrame(rows).set_index("metric")

        try:
            fig_bench = create_benchmark_comparison_chart(
                target_benchmarks,
                source_benchmarks,
                target_label=target_league,
            )
            st.pyplot(fig_bench)
            plt.close(fig_bench)
        except Exception as e:
            st.error(f"Chart error: {e}")

    with tab_board:
        st.markdown("Horizontal bar chart ranked by fit score.")
        try:
            fig_board = create_fit_leaderboard_figure(
                scored_df,
                position_group=position_group,
                top_n=min(len(scored_df), 20),
                target_label=target_league,
            )
            st.pyplot(fig_board)
            plt.close(fig_board)
        except Exception as e:
            st.error(f"Chart error: {e}")

    with tab_dive:
        st.markdown("Detailed per-metric comparison: player value vs target league average.")
        dive_players = scored_df.reset_index()["Player"].tolist()
        selected_dive = st.selectbox(
            "Select player:",
            options=dive_players,
            key="lf_dive_player_select",
        )
        try:
            player_full = df_all[df_all["Player"] == selected_dive]
            if player_full.empty:
                player_full = scored_df.reset_index()
                player_full = player_full[player_full["Player"] == selected_dive]

            player_row = player_full.iloc[0]
            # Merge fit_score + risk into player_row
            scored_row = scored_df.reset_index()
            scored_row = scored_row[scored_row["Player"] == selected_dive].iloc[0]
            player_row = player_row.copy()
            player_row["fit_score"] = scored_row["fit_score"]
            player_row["risk"] = scored_row["risk"]

            fig_dive = create_player_deep_dive_figure(
                player_row,
                target_benchmarks,
                df_all,
                position_group=position_group,
                target_label=target_league,
            )
            st.pyplot(fig_dive)
            plt.close(fig_dive)
        except Exception as e:
            st.error(f"Deep dive chart error: {e}")

    # ── AI Analysis ─────────────────────────────────────────────────────────
    _render_ai_section(
        scored_df=scored_df,
        df_all=df_all,
        target_benchmarks=target_benchmarks,
        target_league=target_league,
        position_group=position_group,
    )
