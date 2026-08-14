"""
Team Analysis Configuration

Defines team-level metrics, playing style dimensions, and visualization settings
for the Team Analysis Dashboard.
"""

from typing import Dict, List, Tuple

# Color scheme (Nike design system)
COLORS = {
    "background": "#ffffff",
    "primary":    "#111111",
    "secondary":  "#707072",
    "accent1":    "#d30005",  # ALERT
    "accent2":    "#1151ff",  # INFO
    "accent3":    "#007d48",  # SUCCESS
    "accent4":    "#0a7281",  # ACCENT_TEAL
    "accent5":    "#9b59b6",  # purple (kept for team analysis variety)
    "grid":       "#cacacb",  # HAIRLINE
    "text":       "#111111",
}

# Team-level metrics organized by category
TEAM_METRICS = {
    "Possession & Build-up": {
        "Passes per 90": {"weight": 1.0, "higher_is_better": True},
        "Accurate passes, %": {"weight": 1.0, "higher_is_better": True},
        "Short / medium passes per 90": {"weight": 1.0, "higher_is_better": True},
        "Accurate short / medium passes, %": {"weight": 1.0, "higher_is_better": True},
        "Back passes per 90": {"weight": 0.5, "higher_is_better": True},
        "Average pass length, m": {
            "weight": 0.5,
            "higher_is_better": False,
        },  # Lower = more possession
    },
    "Directness & Verticality": {
        "Long passes per 90": {"weight": 1.0, "higher_is_better": True},
        "Accurate long passes, %": {"weight": 0.5, "higher_is_better": True},
        "Forward passes per 90": {"weight": 1.0, "higher_is_better": True},
        "Progressive passes per 90": {"weight": 1.5, "higher_is_better": True},
        "Accurate progressive passes, %": {"weight": 0.5, "higher_is_better": True},
        "Progressive runs per 90": {"weight": 1.0, "higher_is_better": True},
        "Accelerations per 90": {"weight": 1.0, "higher_is_better": True},
        "Vertical passes per 90": {"weight": 1.0, "higher_is_better": True},
    },
    "Pressing & Defense": {
        "Defensive duels per 90": {"weight": 1.0, "higher_is_better": True},
        "Defensive duels won, %": {"weight": 0.5, "higher_is_better": True},
        "PAdj Interceptions": {"weight": 1.5, "higher_is_better": True},
        "Sliding tackles per 90": {"weight": 0.5, "higher_is_better": True},
        "PAdj Sliding tackles": {"weight": 0.5, "higher_is_better": True},
        "Successful defensive actions per 90": {
            "weight": 1.0,
            "higher_is_better": True,
        },
        "Fouls per 90": {"weight": 0.3, "higher_is_better": False},
    },
    "Width & Crossing": {
        "Crosses per 90": {"weight": 1.0, "higher_is_better": True},
        "Accurate crosses, %": {"weight": 0.5, "higher_is_better": True},
        "Crosses from left flank per 90": {"weight": 0.5, "higher_is_better": True},
        "Crosses from right flank per 90": {"weight": 0.5, "higher_is_better": True},
        "Deep completed crosses per 90": {"weight": 0.8, "higher_is_better": True},
    },
    "Creativity & Chance Creation": {
        "Key passes per 90": {"weight": 1.5, "higher_is_better": True},
        "Shot assists per 90": {"weight": 1.5, "higher_is_better": True},
        "xA per 90": {"weight": 1.5, "higher_is_better": True},
        "Smart passes per 90": {"weight": 1.0, "higher_is_better": True},
        "Accurate smart passes, %": {"weight": 0.5, "higher_is_better": True},
        "Passes to penalty area per 90": {"weight": 1.0, "higher_is_better": True},
        "Accurate passes to penalty area, %": {"weight": 0.5, "higher_is_better": True},
        "Through passes per 90": {"weight": 0.8, "higher_is_better": True},
        "Deep completions per 90": {"weight": 1.0, "higher_is_better": True},
    },
    "Goal Threat": {
        "Shots per 90": {"weight": 1.0, "higher_is_better": True},
        "Shots on target, %": {"weight": 0.5, "higher_is_better": True},
        "Goal conversion, %": {"weight": 0.5, "higher_is_better": True},
        "xG per 90": {"weight": 1.5, "higher_is_better": True},
        "Touches in box per 90": {"weight": 1.0, "higher_is_better": True},
        "Goals per 90": {"weight": 1.0, "higher_is_better": True},
    },
    "Dribbling & Carrying": {
        "Dribbles per 90": {"weight": 1.0, "higher_is_better": True},
        "Successful dribbles, %": {"weight": 0.5, "higher_is_better": True},
        "Offensive duels per 90": {"weight": 0.8, "higher_is_better": True},
        "Offensive duels won, %": {"weight": 0.5, "higher_is_better": True},
    },
    "Aerial Presence": {
        "Aerial duels per 90": {"weight": 1.0, "higher_is_better": True},
        "Aerial duels won, %": {"weight": 0.5, "higher_is_better": True},
        "Head goals per 90": {"weight": 0.3, "higher_is_better": True},
    },
    "Set Pieces": {
        "Corners per 90": {"weight": 0.5, "higher_is_better": True},
        "Free kicks per 90": {"weight": 0.3, "higher_is_better": True},
        "Direct free kicks per 90": {"weight": 0.3, "higher_is_better": True},
    },
}

# Playing Style Dimensions (composite indices)
PLAYING_STYLE_DIMENSIONS = {
    "Possession": {
        "metrics": [
            "Passes per 90",
            "Accurate passes, %",
            "Short / medium passes per 90",
        ],
        "weights": [0.4, 0.3, 0.3],
        "description": "Ball control and retention tendency",
    },
    "Build-up Quality": {
        "metrics": [
            "Accurate short / medium passes, %",
            "Progressive passes per 90",
            "Back passes per 90",
        ],
        "weights": [0.3, 0.4, 0.3],
        "description": "Patient progression from defense",
    },
    "Directness": {
        "metrics": [
            "Long passes per 90",
            "Forward passes per 90",
            "Average pass length, m",
        ],
        "weights": [0.3, 0.4, 0.3],
        "description": "Verticality and long ball preference",
    },
    "Pressing Intensity": {
        "metrics": [
            "Defensive duels per 90",
            "PAdj Interceptions",
            "Successful defensive actions per 90",
        ],
        "weights": [0.4, 0.4, 0.2],
        "description": "Defensive aggression and work rate",
    },
    "Verticality": {
        "metrics": [
            "Progressive passes per 90",
            "Progressive runs per 90",
            "Accelerations per 90",
            "Vertical passes per 90",
        ],
        "weights": [0.3, 0.3, 0.2, 0.2],
        "description": "Speed of ball and player progression",
    },
    "Width Usage": {
        "metrics": [
            "Crosses per 90",
            "Crosses from left flank per 90",
            "Crosses from right flank per 90",
        ],
        "weights": [0.5, 0.25, 0.25],
        "description": "Utilization of wide areas",
    },
    "Creativity": {
        "metrics": [
            "Key passes per 90",
            "Shot assists per 90",
            "xA per 90",
            "Smart passes per 90",
        ],
        "weights": [0.3, 0.3, 0.3, 0.1],
        "description": "Chance creation and playmaking",
    },
    "Goal Threat": {
        "metrics": [
            "Shots per 90",
            "xG per 90",
            "Touches in box per 90",
            "Goals per 90",
        ],
        "weights": [0.3, 0.3, 0.2, 0.2],
        "description": "Attacking potency and danger",
    },
    "Defensive Solidity": {
        "metrics": [
            "Successful defensive actions per 90",
            "Defensive duels per 90",
            "Aerial duels per 90",
        ],
        "weights": [0.4, 0.3, 0.3],
        "description": "Defensive strength and duels",
    },
    "Dribbling": {
        "metrics": [
            "Dribbles per 90",
            "Successful dribbles, %",
            "Offensive duels per 90",
        ],
        "weights": [0.4, 0.3, 0.3],
        "description": "Individual carrying and beating opponents",
    },
}

# Playing Style Classification Thresholds
STYLE_THRESHOLDS = {
    "Possession-based": {
        "conditions": {
            "Possession": (70, 100),
            "Build-up Quality": (60, 100),
            "Directness": (0, 40),
        },
        "description": "High ball retention, patient build-up, short passing",
        "icon": "🔄",
    },
    "Direct/Counter": {
        "conditions": {
            "Possession": (0, 45),
            "Directness": (60, 100),
            "Build-up Quality": (0, 50),
        },
        "description": "Low possession, quick transitions, long balls",
        "icon": "🚀",
    },
    "High-Press": {
        "conditions": {
            "Pressing Intensity": (70, 100),
            "Defensive Solidity": (60, 100),
        },
        "description": "Aggressive pressing, winning ball high up the pitch",
        "icon": "⚡",
    },
    "Low-Block": {
        "conditions": {
            "Pressing Intensity": (0, 40),
            "Defensive Solidity": (50, 100),
            "Possession": (0, 50),
        },
        "description": "Compact defense, counter-attacking approach",
        "icon": "🛡️",
    },
    "Wide/Crossing": {
        "conditions": {
            "Width Usage": (70, 100),
            "Crosses per 90": (60, 100),
        },
        "description": "Heavy emphasis on flanks and crossing",
        "icon": "↔️",
    },
    "Central/Narrow": {
        "conditions": {
            "Width Usage": (0, 40),
            "Creativity": (60, 100),
            "Build-up Quality": (60, 100),
        },
        "description": "Playing through the middle, intricate passing",
        "icon": "⬆️",
    },
    "Balanced": {
        "conditions": {},  # Default if no specific style matches
        "description": "No dominant style, adaptable approach",
        "icon": "⚖️",
    },
}

# Visualization settings
RADAR_CHART_SETTINGS = {
    "figsize": (10, 10),
    "num_vars": 10,  # Number of playing style dimensions
    "line_width": 2.5,
    "marker_size": 8,
    "alpha": 0.25,
    "grid_color": "#d5d3cc",
    "label_size": 10,
}

# Export settings
EXPORT_SETTINGS = {
    "dpi": 150,
    "format": "png",
    "facecolor": "#ffffff",
    "bbox_inches": "tight",
}

# League files available for analysis
AVAILABLE_LEAGUES = {
    "BRI Liga 1 25-26": "data/2025/BRI Liga 1 25-26.csv",
}

# Minimum minutes threshold for player inclusion
MIN_MINUTES_DEFAULT = 500

# Maximum number of teams to compare
MAX_TEAMS_COMPARE = 3
