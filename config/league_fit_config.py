"""
League Fit Analysis configuration.

Defines the target league, 11 event-based physical proxy metrics,
position-specific weight tables, and risk-classification thresholds.
"""

# ---------------------------------------------------------------------------
# Target league
# ---------------------------------------------------------------------------
TARGET_LEAGUE = "Liga 1"              # exact value in Competition / League column
TARGET_LEAGUE_DISPLAY = "BRI Liga 1"  # human-readable label

# ---------------------------------------------------------------------------
# Physical proxy metrics  (all confirmed present in every Wyscout CSV)
# ---------------------------------------------------------------------------
PHYSICAL_PROXY_METRICS = [
    {"column": "Accelerations per 90",                  "display": "Accelerations",           "proxy_for": "Explosive movement"},
    {"column": "Duels per 90",                          "display": "Duels volume",            "proxy_for": "Physical contest volume"},
    {"column": "Duels won, %",                          "display": "Duels won %",             "proxy_for": "Physical dominance"},
    {"column": "Aerial duels per 90",                   "display": "Aerial duels",            "proxy_for": "Aerial engagement"},
    {"column": "Aerial duels won, %",                   "display": "Aerial won %",            "proxy_for": "Aerial effectiveness"},
    {"column": "Progressive runs per 90",               "display": "Prog. runs",              "proxy_for": "Forward drive / stamina"},
    {"column": "Successful defensive actions per 90",   "display": "Def. actions",            "proxy_for": "Pressing intensity"},
    {"column": "Offensive duels per 90",                "display": "Off. duels",              "proxy_for": "Attacking engagement"},
    {"column": "Offensive duels won, %",                "display": "Off. duels won %",        "proxy_for": "Attacking effectiveness"},
    {"column": "Dribbles per 90",                       "display": "Dribbles",                "proxy_for": "1v1 engagement"},
    {"column": "Successful dribbles, %",                "display": "Dribbles won %",          "proxy_for": "1v1 effectiveness"},
]

METRIC_COLUMNS = [m["column"] for m in PHYSICAL_PROXY_METRICS]
METRIC_DISPLAY  = {m["column"]: m["display"] for m in PHYSICAL_PROXY_METRICS}

# ---------------------------------------------------------------------------
# Position-specific weight tables
# Weights do NOT need to sum to 1 — the algorithm normalises by their sum.
# ---------------------------------------------------------------------------
POSITION_WEIGHTS = {
    "CB": {
        "Accelerations per 90":                  0.6,
        "Duels per 90":                          1.2,
        "Duels won, %":                          1.4,
        "Aerial duels per 90":                   1.3,
        "Aerial duels won, %":                   1.4,
        "Progressive runs per 90":               0.4,
        "Successful defensive actions per 90":   1.0,
        "Offensive duels per 90":                0.5,
        "Offensive duels won, %":                0.5,
        "Dribbles per 90":                       0.3,
        "Successful dribbles, %":                0.3,
    },
    "Fullback": {
        "Accelerations per 90":                  1.0,
        "Duels per 90":                          0.9,
        "Duels won, %":                          1.0,
        "Aerial duels per 90":                   0.5,
        "Aerial duels won, %":                   0.5,
        "Progressive runs per 90":               1.2,
        "Successful defensive actions per 90":   1.0,
        "Offensive duels per 90":                0.7,
        "Offensive duels won, %":                0.7,
        "Dribbles per 90":                       0.6,
        "Successful dribbles, %":                0.6,
    },
    "DM": {
        "Accelerations per 90":                  0.7,
        "Duels per 90":                          1.3,
        "Duels won, %":                          1.3,
        "Aerial duels per 90":                   0.5,
        "Aerial duels won, %":                   0.5,
        "Progressive runs per 90":               0.6,
        "Successful defensive actions per 90":   1.4,
        "Offensive duels per 90":                0.6,
        "Offensive duels won, %":                0.6,
        "Dribbles per 90":                       0.4,
        "Successful dribbles, %":                0.4,
    },
    "Midfielder": {
        "Accelerations per 90":                  1.0,
        "Duels per 90":                          1.0,
        "Duels won, %":                          1.0,
        "Aerial duels per 90":                   0.5,
        "Aerial duels won, %":                   0.5,
        "Progressive runs per 90":               1.1,
        "Successful defensive actions per 90":   0.9,
        "Offensive duels per 90":                0.8,
        "Offensive duels won, %":                0.8,
        "Dribbles per 90":                       0.6,
        "Successful dribbles, %":                0.6,
    },
    "AM": {
        "Accelerations per 90":                  1.3,
        "Duels per 90":                          0.6,
        "Duels won, %":                          0.6,
        "Aerial duels per 90":                   0.3,
        "Aerial duels won, %":                   0.3,
        "Progressive runs per 90":               0.9,
        "Successful defensive actions per 90":   0.4,
        "Offensive duels per 90":                1.2,
        "Offensive duels won, %":                1.2,
        "Dribbles per 90":                       1.2,
        "Successful dribbles, %":                1.2,
    },
    "Winger": {
        "Accelerations per 90":                  1.4,
        "Duels per 90":                          0.5,
        "Duels won, %":                          0.5,
        "Aerial duels per 90":                   0.3,
        "Aerial duels won, %":                   0.3,
        "Progressive runs per 90":               1.3,
        "Successful defensive actions per 90":   0.3,
        "Offensive duels per 90":                1.0,
        "Offensive duels won, %":                1.0,
        "Dribbles per 90":                       1.4,
        "Successful dribbles, %":                1.4,
    },
    "Forward": {
        "Accelerations per 90":                  1.1,
        "Duels per 90":                          0.7,
        "Duels won, %":                          0.7,
        "Aerial duels per 90":                   1.0,
        "Aerial duels won, %":                   1.0,
        "Progressive runs per 90":               0.8,
        "Successful defensive actions per 90":   0.4,
        "Offensive duels per 90":                1.1,
        "Offensive duels won, %":                1.1,
        "Dribbles per 90":                       0.7,
        "Successful dribbles, %":                0.7,
    },
    "CF": {
        "Accelerations per 90":                  1.1,
        "Duels per 90":                          0.7,
        "Duels won, %":                          0.7,
        "Aerial duels per 90":                   1.0,
        "Aerial duels won, %":                   1.0,
        "Progressive runs per 90":               0.8,
        "Successful defensive actions per 90":   0.4,
        "Offensive duels per 90":                1.1,
        "Offensive duels won, %":                1.1,
        "Dribbles per 90":                       0.7,
        "Successful dribbles, %":                0.7,
    },
}

# Uniform weights (used when position group is "All" or has no specific table)
POSITION_WEIGHTS_UNIFORM = {col: 1.0 for col in METRIC_COLUMNS}

# ---------------------------------------------------------------------------
# Map every POSITION_GROUPS key → a weight-table key (or None = uniform)
# ---------------------------------------------------------------------------
POSITION_GROUP_TO_WEIGHT_KEY = {
    "All":              None,
    "CB":               "CB",
    "Fullback":         "Fullback",
    "Defender":         "CB",           # Defender = CB + FB; default to CB weights
    "DM":               "DM",
    "Midfielder":       "Midfielder",
    "Midfielder_N_AM":  "Midfielder",
    "AM":               "AM",
    "Winger":           "Winger",
    "Forward":          "Forward",
    "CF":               "CF",
}

# ---------------------------------------------------------------------------
# Risk thresholds  (fit_score boundaries)
# ---------------------------------------------------------------------------
RISK_READY_MIN   = 60   # >= 60  →  "Ready"   (green)
RISK_MONITOR_MIN = 45   # 45-59  →  "Monitor" (yellow)
                        # < 45   →  "Risk"    (red)

from styles.design_system import RISK_COLORS, RISK_BG_COLORS  # noqa: F401
