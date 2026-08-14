"""
Nike-inspired Design System — Single Source of Truth
All color tokens, semantic colors, and chart helpers live here.
"""
# ── Canvas & Surface ──────────────────────────────────────────────────────────
CANVAS     = "#ffffff"   # main bg (was #f5f3e8)
SOFT_CLOUD = "#f5f5f5"   # card/chart surface
INK        = "#111111"   # primary text (was #2c3e50)
MUTE       = "#707072"   # secondary text (was #95a5a6)
HAIRLINE   = "#cacacb"   # dividers/borders (was #e0e0e0)

# ── Semantic Colors ───────────────────────────────────────────────────────────
SUCCESS     = "#007d48"  # Elite / Ready / high percentile (was #2ecc71)
ALERT       = "#d30005"  # Risk / Below Avg / low percentile (was #e74c3c)
INFO        = "#1151ff"  # Good / informational (was #3498db)
ACCENT_TEAL = "#0a7281"  # Average / neutral accent (replaces #f39c12)

# ── Performance Tier Colors ───────────────────────────────────────────────────
TIER_COLORS = {
    "Elite":         SUCCESS,
    "Good":          INFO,
    "Average":       ACCENT_TEAL,
    "Below Average": ALERT,
}

# ── Risk Classification Colors ────────────────────────────────────────────────
RISK_COLORS = {
    "Ready":   SUCCESS,
    "Monitor": ACCENT_TEAL,
    "Risk":    ALERT,
}
RISK_BG_COLORS = {
    "Ready":   "#e6f4ed",
    "Monitor": "#e6f1f2",
    "Risk":    "#fce6e6",
}

# ── Player Comparison Colors (3-player) ───────────────────────────────────────
# INK (black) / ALERT (red) / INFO (blue) — replaces #f01616, #3498db, #e67e22
PLAYER_COLORS = [INK, ALERT, INFO]


# ── Percentile → Color Mapping ────────────────────────────────────────────────
def get_percentile_color(pct: float) -> str:
    """3-band semantic color for a 0–100 percentile value."""
    if pct >= 67:
        return SUCCESS
    if pct >= 34:
        return ACCENT_TEAL
    return ALERT


def get_percentile_color_10(pct: float) -> str:
    """10-bucket version for player_finder gradient bars."""
    bucket = min(int(pct // 10), 9)
    if bucket >= 6:
        return SUCCESS
    if bucket >= 3:
        return ACCENT_TEAL
    return ALERT


# ── Matplotlib Chart Helper ───────────────────────────────────────────────────
def apply_nike_style(fig, ax=None, axes=None):
    """Apply Nike canvas styling to a matplotlib figure."""
    fig.patch.set_facecolor(CANVAS)
    targets = ([ax] if ax else []) + (axes or [])
    if not targets:
        targets = list(fig.axes)
    for a in targets:
        a.set_facecolor(SOFT_CLOUD)
        a.tick_params(colors=INK, labelsize=9)
        a.xaxis.label.set_color(INK)
        a.yaxis.label.set_color(INK)
        a.title.set_color(INK)
        a.grid(True, color=HAIRLINE, linewidth=0.5, linestyle="-", alpha=0.7)
        a.set_axisbelow(True)
        for s in ["top", "right"]:
            a.spines[s].set_visible(False)
        for s in ["left", "bottom"]:
            a.spines[s].set_color(HAIRLINE)


def apply_nike_style_plotly(fig):
    """Apply Nike canvas to a Plotly figure."""
    fig.update_layout(
        plot_bgcolor=SOFT_CLOUD,
        paper_bgcolor=CANVAS,
        font=dict(family="Inter, sans-serif", color=INK),
    )
    return fig
