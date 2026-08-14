"""
Statistical categories for player comparison
Maps CSV columns to comprehensive categories for player analysis

Indicator values:
- HIGHER_IS_GOOD (default): Higher values are better (e.g., goals, assists, passes)
- LOWER_IS_GOOD: Lower values are better (e.g., fouls, cards, conceded goals)
"""

STAT_CATEGORIES = {
    "Defensive": {
        "display_name": "Defensive",
        "stats": [
            {"column": "Duels won, %", "display": "Duels Won %", "indicator": "HIGHER_IS_GOOD"},
            {"column": "Duels per 90", "display": "Duels per 90", "indicator": "HIGHER_IS_GOOD"},
            {"column": "Defensive duels per 90", "display": "Defensive Duels per 90", "indicator": "HIGHER_IS_GOOD"},
            {"column": "Defensive duels won, %", "display": "Defensive Duels Won %", "indicator": "HIGHER_IS_GOOD"},
            {"column": "Aerial duels per 90", "display": "Aerial Duels per 90", "indicator": "HIGHER_IS_GOOD"},
            {"column": "Aerial duels won, %", "display": "Aerial Duels Won %", "indicator": "HIGHER_IS_GOOD"},
            {"column": "Sliding tackles per 90", "display": "Sliding Tackles per 90", "indicator": "HIGHER_IS_GOOD"},
            {"column": "PAdj Sliding tackles", "display": "PAdj Sliding Tackles", "indicator": "HIGHER_IS_GOOD"},
            {"column": "Shots blocked per 90", "display": "Shots Blocked per 90", "indicator": "HIGHER_IS_GOOD"},
            {"column": "Interceptions per 90", "display": "Interceptions per 90", "indicator": "HIGHER_IS_GOOD"},
            {"column": "PAdj Interceptions", "display": "PAdj Interceptions", "indicator": "HIGHER_IS_GOOD"},
            {"column": "Successful defensive actions per 90", "display": "Defensive Actions per 90", "indicator": "HIGHER_IS_GOOD"},
            {"column": "Fouls per 90", "display": "Fouls per 90", "indicator": "LOWER_IS_GOOD"},
            {"column": "Yellow cards per 90", "display": "Yellow Cards per 90", "indicator": "LOWER_IS_GOOD"},
            {"column": "Red cards per 90", "display": "Red Cards per 90", "indicator": "LOWER_IS_GOOD"},
            # {"column": "Conceded goals per 90", "display": "Conceded Goals per 90", "indicator": "LOWER_IS_GOOD"},
            # {"column": "Shots against per 90", "display": "Shots Against per 90", "indicator": "LOWER_IS_GOOD"},
            # {"column": "Prevented goals per 90", "display": "Prevented Goals per 90", "indicator": "HIGHER_IS_GOOD"},
        ]
    },
    "Offensive": {
        "display_name": "Offensive",
        "stats": [
            {"column": "Goals per 90", "display": "Goals per 90"},
            {"column": "xG per 90", "display": "xG per 90"},
            {"column": "Non-penalty goals per 90", "display": "Non-Penalty Goals per 90"},
            {"column": "Head goals per 90", "display": "Head Goals per 90"},
            {"column": "Shots per 90", "display": "Shots per 90"},
            {"column": "Shots on target, %", "display": "Shots on Target %"},
            {"column": "Goal conversion, %", "display": "Goal Conversion %"},
            {"column": "Assists per 90", "display": "Assists per 90"},
            {"column": "xA per 90", "display": "xA per 90"},
            {"column": "Successful attacking actions per 90", "display": "Attacking Actions per 90"},
            {"column": "Dribbles per 90", "display": "Dribbles per 90"},
            {"column": "Successful dribbles, %", "display": "Successful Dribbles %"},
            {"column": "Offensive duels per 90", "display": "Offensive Duels per 90"},
            {"column": "Offensive duels won, %", "display": "Offensive Duels Won %"},
            {"column": "Touches in box per 90", "display": "Touches in Box per 90"},
            {"column": "Progressive runs per 90", "display": "Progressive Runs per 90"},
            {"column": "Accelerations per 90", "display": "Accelerations per 90"},
            {"column": "Received passes per 90", "display": "Received Passes per 90"},
            {"column": "Received long passes per 90", "display": "Received Long Passes per 90"},
            {"column": "Fouls suffered per 90", "display": "Fouls Suffered per 90"},
            {"column": "Penalties taken", "display": "Penalties Taken"},
            {"column": "Penalty conversion, %", "display": "Penalty Conversion %"},
            {"column": "Goals", "display": "Total Goals"},
        ]
    },
    "Progressive": {
        "display_name": "Progressive",
        "stats": [
            {"column": "Passes per 90", "display": "Passes per 90"},
            {"column": "Accurate passes, %", "display": "Pass Accuracy %"},
            {"column": "Forward passes per 90", "display": "Forward Passes per 90"},
            {"column": "Accurate forward passes, %", "display": "Forward Pass Accuracy %"},
            {"column": "Back passes per 90", "display": "Back Passes per 90"},
            {"column": "Accurate back passes, %", "display": "Back Pass Accuracy %"},
            {"column": "Short / medium passes per 90", "display": "Short/Medium Passes per 90"},
            {"column": "Accurate short / medium passes, %", "display": "Short/Medium Pass Accuracy %"},
            {"column": "Long passes per 90", "display": "Long Passes per 90"},
            {"column": "Accurate long passes, %", "display": "Long Pass Accuracy %"},
            {"column": "Progressive passes per 90", "display": "Progressive Passes per 90"},
            {"column": "Accurate progressive passes, %", "display": "Progressive Pass Accuracy %"},
            {"column": "Vertical passes per 90", "display": "Vertical Passes per 90"},
            {"column": "Accurate vertical passes, %", "display": "Vertical Pass Accuracy %"},
            {"column": "Average pass length, m", "display": "Avg Pass Length (m)"},
        ]
    },
    "Chance Creation": {
        "display_name": "Chance Creation",
        "stats": [
            {"column": "Shot assists per 90", "display": "Shot Assists per 90"},
            {"column": "Second assists per 90", "display": "Second Assists per 90"},
            {"column": "Third assists per 90", "display": "Third Assists per 90"},
            {"column": "Smart passes per 90", "display": "Smart Passes per 90"},
            {"column": "Accurate smart passes, %", "display": "Smart Pass Accuracy %"},
            {"column": "Key passes per 90", "display": "Key Passes per 90"},
            {"column": "Passes to final third per 90", "display": "Passes to Final Third per 90"},
            {"column": "Accurate passes to final third, %", "display": "Final Third Pass Accuracy %"},
            {"column": "Passes to penalty area per 90", "display": "Passes to Penalty Area per 90"},
            {"column": "Accurate passes to penalty area, %", "display": "Penalty Area Pass Accuracy %"},
            {"column": "Through passes per 90", "display": "Through Passes per 90"},
            {"column": "Accurate through passes, %", "display": "Through Pass Accuracy %"},
            {"column": "Deep completions per 90", "display": "Deep Completions per 90"},
            {"column": "Deep completed crosses per 90", "display": "Deep Completed Crosses per 90"},
            {"column": "Crosses per 90", "display": "Crosses per 90"},
            {"column": "Accurate crosses, %", "display": "Cross Accuracy %"},
            {"column": "Crosses from left flank per 90", "display": "Left Flank Crosses per 90"},
            {"column": "Accurate crosses from left flank, %", "display": "Left Flank Cross Accuracy %"},
            {"column": "Crosses from right flank per 90", "display": "Right Flank Crosses per 90"},
            {"column": "Accurate crosses from right flank, %", "display": "Right Flank Cross Accuracy %"},
            {"column": "Crosses to goalie box per 90", "display": "Crosses to Goalie Box per 90"},
        ]
    },
    "General": {
        "display_name": "General",
        "stats": [
            {"column": "Matches played", "display": "Matches Played"},
            {"column": "Minutes played", "display": "Minutes Played"},
            {"column": "Clean sheets", "display": "Clean Sheets"},
            # {"column": "Save rate, %", "display": "Save Rate %", "indicator": "HIGHER_IS_GOOD"},
            {"column": "xG against per 90", "display": "xG Against per 90", "indicator": "LOWER_IS_GOOD"},
            # {"column": "Prevented goals per 90", "display": "Prevented Goals per 90", "indicator": "HIGHER_IS_GOOD"},
            # {"column": "Back passes received as GK per 90", "display": "Back Passes Received per 90"},
            # {"column": "Exits per 90", "display": "Exits per 90"},
            {"column": "Average long pass length, m", "display": "Avg Long Pass Length (m)"},
            {"column": "Yellow cards", "display": "Yellow Cards", "indicator": "LOWER_IS_GOOD"},
            {"column": "Red cards", "display": "Red Cards", "indicator": "LOWER_IS_GOOD"},
        ]
    },
    "Set Pieces": {
        "display_name": "Set Pieces",
        "stats": [
            {"column": "Free kicks per 90", "display": "Free Kicks per 90"},
            {"column": "Direct free kicks per 90", "display": "Direct Free Kicks per 90"},
            {"column": "Direct free kicks on target, %", "display": "Direct Free Kick Accuracy %"},
            {"column": "Corners per 90", "display": "Corners per 90"},
            # {"column": "Penalty conversion, %", "display": "Penalty Conversion %"},
        ]
    },
    "Goalkeeper": {
        "display_name": "Goalkeeper",
        "stats": [
            {"column": "Save rate, %",                      "display": "Save Rate %",               "indicator": "HIGHER_IS_GOOD"},
            {"column": "Prevented goals per 90",            "display": "Prevented Goals p90",        "indicator": "HIGHER_IS_GOOD"},
            {"column": "Conceded goals per 90",             "display": "Conceded Goals p90",         "indicator": "LOWER_IS_GOOD"},
            {"column": "Shots against per 90",              "display": "Shots Against p90",          "indicator": "LOWER_IS_GOOD"},
            {"column": "xG against per 90",                 "display": "xG Against p90",             "indicator": "LOWER_IS_GOOD"},
            {"column": "Clean sheets",                      "display": "Clean Sheets",               "indicator": "HIGHER_IS_GOOD"},
            {"column": "Exits per 90",                      "display": "Exits p90",                  "indicator": "HIGHER_IS_GOOD"},
            {"column": "Aerial duels per 90",               "display": "Aerial Duels p90",           "indicator": "HIGHER_IS_GOOD"},
            {"column": "Aerial duels won, %",               "display": "Aerial Duels Won %",         "indicator": "HIGHER_IS_GOOD"},
            {"column": "Back passes received as GK per 90", "display": "Back Passes Received p90",   "indicator": "HIGHER_IS_GOOD"},
            {"column": "Accurate passes, %",                "display": "Pass Accuracy %",            "indicator": "HIGHER_IS_GOOD"},
            {"column": "Accurate long passes, %",           "display": "Long Pass Accuracy %",       "indicator": "HIGHER_IS_GOOD"},
            {"column": "Long passes per 90",                "display": "Long Passes p90",            "indicator": "HIGHER_IS_GOOD"},
            {"column": "Progressive passes per 90",         "display": "Progressive Passes p90",     "indicator": "HIGHER_IS_GOOD"},
        ]
    }
}

# Player info columns
PLAYER_INFO_COLUMNS = {
    "name": "Player",
    "age": "Age",
    "team": "Team",
    "minutes": "Minutes played",
    "country": "Birth country",
    "position": "Position",
    "league": "Competition"
}

# Colors for up to 3 players — Nike design system
from styles.design_system import PLAYER_COLORS  # noqa: F401


# ========== HELPER FUNCTIONS ==========

def get_stat_indicator(stat_column: str) -> str:
    """
    Returns the indicator for a stat: 'HIGHER_IS_GOOD' or 'LOWER_IS_GOOD'

    Args:
        stat_column: The column name of the stat (e.g., "Goals per 90", "Fouls per 90")

    Returns:
        'HIGHER_IS_GOOD' (default) or 'LOWER_IS_GOOD' for the stat
        Defaults to 'HIGHER_IS_GOOD' if not explicitly specified

    Example:
        >>> get_stat_indicator("Goals per 90")
        "HIGHER_IS_GOOD"
        >>> get_stat_indicator("Fouls per 90")
        "LOWER_IS_GOOD"
    """
    # Search through all categories and stats
    for category_name, category_data in STAT_CATEGORIES.items():
        for stat in category_data["stats"]:
            if stat["column"] == stat_column:
                # Return indicator if specified, default to HIGHER_IS_GOOD
                return stat.get("indicator", "HIGHER_IS_GOOD")

    # If stat not found, default to HIGHER_IS_GOOD
    return "HIGHER_IS_GOOD"


def get_all_stat_columns() -> list:
    """
    Get all stat column names across all categories

    Returns:
        List of all stat column names

    Example:
        >>> columns = get_all_stat_columns()
        >>> "Goals per 90" in columns
        True
    """
    columns = []
    for category_name, category_data in STAT_CATEGORIES.items():
        for stat in category_data["stats"]:
            columns.append(stat["column"])
    return columns


def is_lower_better(stat_column: str) -> bool:
    """
    Check if lower values are better for a stat

    Args:
        stat_column: The column name of the stat

    Returns:
        True if lower is better, False otherwise

    Example:
        >>> is_lower_better("Fouls per 90")
        True
        >>> is_lower_better("Goals per 90")
        False
    """
    return get_stat_indicator(stat_column) == "LOWER_IS_GOOD"
