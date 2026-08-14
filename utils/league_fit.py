"""
League Fit Analysis — scoring logic and matplotlib figure factories.

Compares source-league players against BRI Liga 1 benchmarks on 11
event-based physical-proxy metrics.  No GPS / tracking data required.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
from styles.design_system import apply_nike_style

from config.league_fit_config import (
    TARGET_LEAGUE,
    TARGET_LEAGUE_DISPLAY,
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _position_filter_mask(df: pd.DataFrame, position_group: str) -> pd.Series:
    """Return a boolean mask filtering df by position group using the same
    split-and-match logic as the rest of the app."""
    tags = POSITION_GROUPS.get(position_group)
    if tags is None:                          # "All"
        return pd.Series(True, index=df.index)
    return (
        df["Position"].notna()
        & df["Position"].apply(lambda x: isinstance(x, str))
        & df["Position"].str.split(",").apply(
            lambda parts: any(p.strip() in tags for p in parts) if isinstance(parts, list) else False
        )
    )


def _get_weight_vector(position_group: str) -> pd.Series:
    """Return a Series of weights indexed by METRIC_COLUMNS for the given
    position group."""
    key = POSITION_GROUP_TO_WEIGHT_KEY.get(position_group)
    raw = POSITION_WEIGHTS.get(key, POSITION_WEIGHTS_UNIFORM) if key else POSITION_WEIGHTS_UNIFORM
    return pd.Series({col: raw.get(col, 1.0) for col in METRIC_COLUMNS})


def _classify_risk(score: float) -> str:
    if score >= RISK_READY_MIN:
        return "Ready"
    if score >= RISK_MONITOR_MIN:
        return "Monitor"
    return "Risk"


# ---------------------------------------------------------------------------
# Benchmark computation
# ---------------------------------------------------------------------------

def compute_target_benchmarks(
    df_all: pd.DataFrame,
    position_group: str,
    min_minutes: int = 500,
    target_club: str = None,
) -> pd.DataFrame:
    """Compute mean / std / count for each of the 11 metrics for Liga 1
    players that match *position_group* and *min_minutes*.

    When *target_club* is provided the benchmarks are restricted to that
    club's players only; otherwise the full league is used.

    Returns a DataFrame indexed by metric column name with columns
    ``mean``, ``std``, ``count``, ``low_sample`` (bool), ``missing`` (bool).
    """
    mask = (
        (df_all["League"] == TARGET_LEAGUE)
        & _position_filter_mask(df_all, position_group)
        & (df_all["Minutes played"] >= min_minutes)
    )
    if target_club is not None:
        mask = mask & (df_all["Team"] == target_club)
    subset = df_all.loc[mask, METRIC_COLUMNS]

    rows = []
    for col in METRIC_COLUMNS:
        series = pd.to_numeric(subset[col], errors="coerce").dropna()
        count = len(series)
        rows.append({
            "metric":      col,
            "mean":        series.mean() if count > 0 else np.nan,
            "std":         series.std(ddof=1) if count > 1 else 0.0,
            "count":       count,
            "low_sample":  count < 5,
            "missing":     count == 0,
        })
    return pd.DataFrame(rows).set_index("metric")


def compute_source_benchmarks(
    df_all: pd.DataFrame,
    position_group: str,
    source_leagues: list,
    min_minutes: int = 500,
) -> dict:
    """Return {league_name: benchmarks_df} for each source league."""
    result = {}
    for league in source_leagues:
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
                "mean":   series.mean() if count > 0 else np.nan,
                "std":    series.std(ddof=1) if count > 1 else 0.0,
                "count":  count,
            })
        result[league] = pd.DataFrame(rows).set_index("metric")
    return result


# ---------------------------------------------------------------------------
# Fit-score computation  (vectorised)
# ---------------------------------------------------------------------------

def compute_fit_scores(
    df_all: pd.DataFrame,
    position_group: str,
    source_leagues: list,
    min_minutes: int = 500,
    age_range: tuple = (18, 40),
    target_benchmarks: pd.DataFrame = None,
) -> pd.DataFrame:
    """Score every candidate player from *source_leagues* against Liga 1
    benchmarks.

    Returns a DataFrame with columns:
        Player, Team, Age, League, Position, Minutes played,
        fit_score, risk,
        z_<metric> … (raw z-scores for each metric)
    """
    if target_benchmarks is None:
        target_benchmarks = compute_target_benchmarks(df_all, position_group, min_minutes)

    # ── candidate pool ──────────────────────────────────────────────────────
    mask = (
        df_all["League"].isin(source_leagues)
        & _position_filter_mask(df_all, position_group)
        & (df_all["Minutes played"] >= min_minutes)
        & (df_all["Age"] >= age_range[0])
        & (df_all["Age"] <= age_range[1])
    )
    candidates = df_all.loc[mask].copy()

    if candidates.empty:
        return pd.DataFrame(columns=[
            "Player", "Team", "Age", "League", "Position",
            "Minutes played", "fit_score", "risk",
        ])

    weights = _get_weight_vector(position_group)

    # ── per-metric z-scores (vectorised) ────────────────────────────────────
    active_metrics = []          # metrics that contribute to the score
    for col in METRIC_COLUMNS:
        bm = target_benchmarks.loc[col]
        if bm["missing"]:
            candidates[f"z_{col}"] = np.nan
            continue
        active_metrics.append(col)
        mean_val = bm["mean"]
        std_val  = bm["std"]
        raw      = pd.to_numeric(candidates[col], errors="coerce")
        if std_val == 0:
            candidates[f"z_{col}"] = 0.0
        else:
            candidates[f"z_{col}"] = (raw - mean_val) / std_val
        # NaN player values → mild penalty
        candidates[f"z_{col}"] = candidates[f"z_{col}"].fillna(-1.0)

    # ── z → normalised [0, 1] ───────────────────────────────────────────────
    z_cols   = [f"z_{col}" for col in active_metrics]
    w_active = weights[active_metrics]

    clipped   = candidates[z_cols].clip(-2, 2)
    normalised = (clipped + 2) / 4                  # [-2,+2] → [0,1]

    # ── weighted fit score ──────────────────────────────────────────────────
    # dot product of each row with weight vector, divided by sum of weights
    weight_sum = w_active.values.sum()
    # align column names: normalised has z_<col>, weight vector indexed by <col>
    score_vector = np.zeros(len(candidates))
    for i, col in enumerate(active_metrics):
        score_vector += normalised[f"z_{col}"].values * w_active[col]
    candidates["fit_score"] = (score_vector / weight_sum * 100).round(1)

    # ── risk label ──────────────────────────────────────────────────────────
    candidates["risk"] = candidates["fit_score"].apply(_classify_risk)

    # ── output columns ──────────────────────────────────────────────────────
    info_cols = ["Player", "Team", "Age", "League", "Position", "Minutes played"]
    z_out     = [f"z_{col}" for col in METRIC_COLUMNS]
    out       = candidates[info_cols + METRIC_COLUMNS + ["fit_score", "risk"] + z_out].copy()
    out       = out.sort_values("fit_score", ascending=False).reset_index(drop=True)
    out.index = out.index + 1                       # 1-based rank
    out.index.name = "Rank"
    return out


# ---------------------------------------------------------------------------
# Figure A — Benchmark comparison (grouped horizontal bars)
# ---------------------------------------------------------------------------

def create_benchmark_comparison_chart(
    target_benchmarks: pd.DataFrame,
    source_benchmarks: dict,
    target_label: str = TARGET_LEAGUE_DISPLAY,
) -> plt.Figure:
    """Grouped horizontal bar chart: target league vs each source league,
    one group per metric, with ±1 std error bars."""

    n_metrics = len(METRIC_COLUMNS)

    # only keep source leagues that have at least one observation
    active_sources = {
        name: bm for name, bm in source_benchmarks.items()
        if bm["count"].sum() > 0
    }
    leagues   = [target_label] + list(active_sources.keys())
    n_leagues = len(leagues)

    # colour palette: target = teal, sources cycle through design system palette
    source_palette = ["#1151ff", "#007d48", "#707072", "#0a7281",
                      "#d30005", "#beaffd", "#cacacb", "#fd79a8", "#6c5ce7", "#fab1a0"]
    colors = ["#0a7281"] + [source_palette[i % len(source_palette)] for i in range(n_leagues - 1)]

    bar_height = 0.7 / n_leagues
    fig, ax    = plt.subplots(figsize=(12, 8))
    apply_nike_style(fig, ax)

    y_positions = np.arange(n_metrics)

    for i, league in enumerate(leagues):
        if league == target_label:
            bm = target_benchmarks
        else:
            bm = active_sources[league]

        means = []
        stds  = []
        for col in METRIC_COLUMNS:
            if col not in bm.index or bm.loc[col, "count"] == 0:
                means.append(0)
                stds.append(0)
            else:
                means.append(bm.loc[col, "mean"] if pd.notna(bm.loc[col, "mean"]) else 0)
                stds.append(bm.loc[col, "std"]   if pd.notna(bm.loc[col, "std"])   else 0)

        offset = (i - n_leagues / 2 + 0.5) * bar_height
        ax.barh(
            y_positions + offset,
            means,
            height=bar_height,
            xerr=stds,
            error_kw={"capsize": 3, "linewidth": 1, "color": "#555"},
            color=colors[i],
            label=league,
            edgecolor="white",
            linewidth=0.6,
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels([METRIC_DISPLAY[col] for col in METRIC_COLUMNS], fontsize=10)
    ax.set_xlabel("Value", fontsize=11)
    ax.set_title(
        f"Physical Proxy Benchmarks — {target_label} vs Source Leagues",
        fontsize=14, fontweight="bold", pad=14,
    )
    ax.legend(loc="best", fontsize=9, framealpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure B — Fit Leaderboard table (mirrors create_outliers_table_figure)
# ---------------------------------------------------------------------------

def create_fit_leaderboard_figure(
    scored_df: pd.DataFrame,
    position_group: str,
    top_n: int = 20,
    target_label: str = TARGET_LEAGUE_DISPLAY,
) -> plt.Figure:
    """Matplotlib table figure: Rank | Player | Team | Age | League |
    Fit Score | Risk.  Cell colours driven by risk category."""

    display_df = scored_df.head(top_n).copy()
    n_rows     = len(display_df)
    fig_height = max(8, n_rows * 0.45 + 3)

    fig, ax = plt.subplots(figsize=(12, fig_height))
    apply_nike_style(fig, ax)

    ax.set_xlim(0, 18)
    ax.set_ylim(-n_rows - 1.5, 1.2)
    ax.axis("off")

    # ── title ───────────────────────────────────────────────────────────────
    ax.text(9, 0.9, f"League Fit Leaderboard — {position_group} → {target_label}",
            fontsize=15, fontweight="bold", ha="center")
    ax.text(9, 0.3, f"Top {n_rows} candidates by physical-proxy fit score",
            fontsize=10, ha="center", style="italic", color="#666")

    # ── column headers ──────────────────────────────────────────────────────
    headers = [
        (0.8,  "Rank"),
        (2.8,  "Player"),
        (6.8,  "Team"),
        (10.0, "Age"),
        (11.8, "League"),
        (14.8, "Fit Score"),
        (17.0, "Risk"),
    ]
    header_y = -0.4
    for x, label in headers:
        ax.text(x, header_y, label, fontsize=11, fontweight="bold", ha="left", va="bottom")
    ax.plot([0.3, 17.7], [header_y - 0.12, header_y - 0.12], "k-", linewidth=1.5)

    # ── data rows ───────────────────────────────────────────────────────────
    row_height = 0.45
    for idx, (rank, row) in enumerate(display_df.iterrows()):
        y = header_y - 0.45 - idx * row_height
        risk = row["risk"]

        # light background stripe for score + risk cells
        bg_color = RISK_BG_COLORS.get(risk, "#fff")
        ax.add_patch(mpatches.FancyBboxPatch(
            (14.3, y - 0.17), 3.6, 0.35,
            boxstyle="round,pad=0.02", facecolor=bg_color, edgecolor="none",
        ))

        # Rank
        ax.text(0.8,  y, str(rank), fontsize=10, ha="left",   va="center")
        # Player
        pname = str(row["Player"])[:28]
        ax.text(2.8,  y, pname,     fontsize=10, ha="left",   va="center")
        # Team
        tname = str(row["Team"])[:16]
        ax.text(6.8,  y, tname,     fontsize=10, ha="left",   va="center")
        # Age
        ax.text(10.0, y, str(int(row["Age"])), fontsize=10, ha="left", va="center")
        # League
        ax.text(11.8, y, str(row["League"])[:14], fontsize=10, ha="left", va="center")
        # Fit Score
        ax.text(14.8, y, f"{row['fit_score']:.1f}", fontsize=11, fontweight="bold",
                ha="left", va="center", color=RISK_COLORS.get(risk, "#333"))
        # Risk
        ax.text(17.0, y, risk, fontsize=10, fontweight="bold",
                ha="left", va="center", color=RISK_COLORS.get(risk, "#333"))

    # ── bottom border ───────────────────────────────────────────────────────
    bottom_y = header_y - 0.45 - n_rows * row_height + 0.22
    ax.plot([0.3, 17.7], [bottom_y, bottom_y], "k-", linewidth=1.5)

    # ── footer ──────────────────────────────────────────────────────────────
    today = datetime.now().strftime("%d/%m/%Y")
    ax.text(0.3, bottom_y - 0.4,
            f"Generated: {today} | Data: Wyscout  |  Position: {position_group}  |  Target: {target_label}",
            fontsize=8, ha="left", va="top", color="#666")

    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure C — Player deep-dive (horizontal bars: target mean vs player value)
# ---------------------------------------------------------------------------

def create_player_deep_dive_figure(
    player_row: pd.Series,
    target_benchmarks: pd.DataFrame,
    df_all: pd.DataFrame,
    position_group: str,
    target_label: str = TARGET_LEAGUE_DISPLAY,
) -> plt.Figure:
    """Horizontal bar chart with two bars per metric (target mean in orange,
    player value in green/red), plus a summary box."""

    n_metrics = len(METRIC_COLUMNS)
    fig, ax   = plt.subplots(figsize=(10, 7))
    apply_nike_style(fig, ax)

    y_pos   = np.arange(n_metrics)
    bar_h   = 0.35
    above   = 0
    below   = 0

    for i, col in enumerate(METRIC_COLUMNS):
        bm        = target_benchmarks.loc[col]
        mean_val  = bm["mean"]
        std_val   = bm["std"]
        missing   = bm["missing"]

        player_val = pd.to_numeric(player_row.get(col, np.nan), errors="coerce")
        if np.isnan(player_val):
            player_val = 0.0

        if missing:
            # grey placeholder
            ax.barh(y_pos[i] - bar_h / 2, 0, height=bar_h, color="#ccc", label="_nolegend_")
            ax.barh(y_pos[i] + bar_h / 2, 0, height=bar_h, color="#ccc", label="_nolegend_")
            continue

        # target bar (teal) with error bar
        ax.barh(y_pos[i] + bar_h / 2, mean_val, height=bar_h,
                color="#0a7281", edgecolor="white", linewidth=0.5,
                xerr=std_val, error_kw={"capsize": 3, "linewidth": 1, "color": "#707072"},
                label="_nolegend_")

        # player bar (green / red)
        normalised_z = ((player_val - mean_val) / std_val) if std_val != 0 else 0
        bar_color = "#007d48" if normalised_z >= 0 else "#d30005"
        ax.barh(y_pos[i] - bar_h / 2, player_val, height=bar_h,
                color=bar_color, edgecolor="white", linewidth=0.5, label="_nolegend_")

        if normalised_z >= 0:
            above += 1
        else:
            below += 1

    # ── labels & legend patches ─────────────────────────────────────────────
    ax.set_yticks(y_pos)
    ax.set_yticklabels([METRIC_DISPLAY[col] for col in METRIC_COLUMNS], fontsize=10)
    ax.set_xlabel("Value", fontsize=11)

    player_name = str(player_row.get("Player", "Unknown"))
    ax.set_title(f"Player Deep Dive — {player_name}", fontsize=14, fontweight="bold", pad=12)

    legend_patches = [
        mpatches.Patch(color="#0a7281", label=f"{target_label} mean (±1 std)"),
        mpatches.Patch(color="#007d48", label="Player (≥ mean)"),
        mpatches.Patch(color="#d30005", label="Player (< mean)"),
    ]
    ax.legend(handles=legend_patches, loc="best", fontsize=9, framealpha=0.9)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    # ── summary box (top-right) ─────────────────────────────────────────────
    fit_score = player_row.get("fit_score", 0)
    risk      = player_row.get("risk", "Risk")
    risk_color = RISK_COLORS.get(risk, "#333")

    summary_text = (
        f"Fit Score: {fit_score:.1f}\n"
        f"Risk: {risk}\n"
        f"Above avg: {above} / Below avg: {below}"
    )
    props = dict(boxstyle="round,pad=0.6", facecolor=RISK_BG_COLORS.get(risk, "#fff"),
                 edgecolor=risk_color, linewidth=2)
    ax.text(0.98, 0.97, summary_text, transform=ax.transAxes,
            fontsize=10, verticalalignment="top", horizontalalignment="right",
            bbox=props, color=risk_color, fontweight="bold")

    plt.tight_layout()
    return fig
