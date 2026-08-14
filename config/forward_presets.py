"""
Striker and Centre Forward preset definitions for Player Finder
Weighted scoring formulas for different striker and CF roles
Focused on modern forward play styles

DEPRECATED: This file is maintained for backward compatibility only.
All role definitions have been consolidated into config/role_definitions.py
"""

# Import from the centralized role definitions
from config.role_definitions import FORWARD_ROLES as FORWARD_PRESETS

# DEPRECATED: Old definitions below - kept as reference only
"""
FORWARD_PRESETS_OLD = {
    "Poacher": {
        "display_name": "Poacher",
        "description": "Box specialists, forwards who don't influence the game outside of the penalty area but instead find space within it to finish.",
        "archetypes": ["Romelu Lukaku", "Ante Budimir", "Erling Haaland"],
        "components": [
            {"stat": "Goal conversion, %", "weight": 0.30, "use_percentile": False},
            {"stat": "Touches in box per 90", "weight": 0.25, "use_percentile": False},
            {"stat": "Non-penalty goals per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Shots per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "xG per 90", "weight": 0.10, "use_percentile": False},
        ],
        "icon": "🎯"
    },
    
    "Second Striker": {
        "display_name": "Second Striker",
        "description": "They tend to work best off of a main striker, as they won't dominate the box, they prefer to make runs and find space before linking play, creating and scoring.",
        "archetypes": ["Hugo Ekitike", "Marcus Thuram", "Deniz Undav"],
        "components": [
            {"stat": "Non-penalty goals per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Shot assists per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Accelerations per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Touches in box per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Progressive runs per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Goal conversion, %", "weight": 0.08, "use_percentile": False},
        ],
        "icon": "2️⃣"
    },
    
    "Link Forward": {
        "display_name": "Link Forward",
        "description": "These forwards offer their teammates a passing option, and are able to hold the ball and link play quickly. They often drop off the centre backs, dragging them in to create space behind for a teammate.",
        "archetypes": ["Eddie Nketiah", "Loïs Openda", "Georges Mikautadze"],
        "components": [
            {"stat": "Accurate passes, %", "weight": 0.20, "use_percentile": False},
            {"stat": "Received passes per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Received long passes per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.12, "use_percentile": False},
            {"stat": "Offensive duels won, %", "weight": 0.10, "use_percentile": False},
            {"stat": "Touches in box per 90", "weight": 0.10, "use_percentile": False},
        ],
        "icon": "🔗"
    },
    
    "False Nine": {
        "display_name": "False Nine",
        "description": "Similar to a link forward, these attackers like to drop off the centre backs. But they tend to have more possession, creating chances for others with their passing.",
        "archetypes": ["Hugo Ekitike", "Alexander Isak", "Kylian Mbappé"],
        "components": [
            {"stat": "Shot assists per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Accurate passes, %", "weight": 0.14, "use_percentile": False},
            {"stat": "Key passes per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Progressive passes per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Smart passes per 90", "weight": 0.08, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.04, "use_percentile": False},
        ],
        "icon": "🎭"
    },
    
    "Complete Forward": {
        "display_name": "Complete Forward",
        "description": "As the name suggests, they are strong in pretty much every area, providing movement, goalscoring, creativity and link play.",
        "archetypes": ["Nick Woltemade", "Jonathan David", "Lautaro Martínez"],
        "components": [
            {"stat": "Non-penalty goals per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Shot assists per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Touches in box per 90", "weight": 0.13, "use_percentile": False},
            {"stat": "Progressive runs per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Goal conversion, %", "weight": 0.12, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.10, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.08, "use_percentile": False},
            {"stat": "Accelerations per 90", "weight": 0.06, "use_percentile": False},
        ],
        "icon": "🌟"
    },
    
    "Power Forward": {
        "display_name": "Power Forward",
        "description": "Dynamic, physically powerful forwards who like to make off ball runs, but also carry the ball themselves. They're often difficult to handle in the box as well.",
        "archetypes": ["Thierno Barry", "Marcus Thuram", "Moise Kean"],
        "components": [
            {"stat": "Progressive runs per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Accelerations per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Touches in box per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.16, "use_percentile": False},
            {"stat": "Aerial duels won, %", "weight": 0.14, "use_percentile": False},
            {"stat": "Successful dribbles, %", "weight": 0.10, "use_percentile": False},
            {"stat": "Non-penalty goals per 90", "weight": 0.06, "use_percentile": False},
        ],
        "icon": "💪"
    },
    
    "Pressing Forward": {
        "display_name": "Pressing Forward",
        "description": "Selfless forwards who expend a lot of their energy defensively, pressing on the opponent to try and win the ball back.",
        "archetypes": ["Maximilian Beier", "Zakaria Aboukhlal", "Darwin Núñez"],
        "components": [
            {"stat": "Successful defensive actions per 90", "weight": 0.25, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Defensive duels won, %", "weight": 0.20, "use_percentile": False},
            {"stat": "Accelerations per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Interceptions per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Fouls per 90", "weight": -0.08, "use_percentile": False},
        ],
        "icon": "🔥"
    }
}
"""


def get_forward_preset_options():
    """
    Returns list of forward preset names for UI dropdown

    Returns:
        List of forward preset names
    """
    return list(FORWARD_PRESETS.keys())


def get_all_preset_options():
    """
    Returns all preset options (defender + fullback + midfielder + forward + attacking midfielder) for UI dropdown

    Returns:
        Dict of all presets merged
    """
    from config.defender_presets import DEFENDER_PRESETS
    from config.fullback_presets import FULLBACK_PRESETS
    from config.midfielder_presets import MIDFIELDER_PRESETS
    from config.attacking_midfielder_presets import ATTACKING_MIDFIELDER_PRESETS

    all_presets = {}
    all_presets.update(DEFENDER_PRESETS)
    all_presets.update(FULLBACK_PRESETS)
    all_presets.update(MIDFIELDER_PRESETS)
    all_presets.update(FORWARD_PRESETS)
    all_presets.update(ATTACKING_MIDFIELDER_PRESETS)

    return all_presets
