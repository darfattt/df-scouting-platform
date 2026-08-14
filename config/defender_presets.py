"""
Defender preset definitions for Player Finder
Weighted scoring formulas for different defender profiles
Focused on modern defender roles and responsibilities

DEPRECATED: This file is maintained for backward compatibility only.
All role definitions have been consolidated into config/role_definitions.py
"""

# Import from the centralized role definitions
from config.role_definitions import DEFENDER_ROLES as DEFENDER_PRESETS

# DEPRECATED: Old definitions below - kept as reference only
"""
DEFENDER_PRESETS_OLD = {
    "Ball Playing": {
        "display_name": "Ball Playing",
        "description": "Excellent passers, able to progress play through thirds and pass over distance.",
        "archetypes": ["Marquinhos", "Dayot Upamecano", "Nico Schlotterbeck"],
        "components": [
            {"stat": "Progressive passes per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Accurate long passes, %", "weight": 0.18, "use_percentile": False},
            {"stat": "Accurate short / medium passes, %", "weight": 0.15, "use_percentile": False},
            {"stat": "Accurate forward passes, %", "weight": 0.13, "use_percentile": False},
            {"stat": "Smart passes per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Average pass length, m", "weight": 0.07, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "⚡"
    },
    "Libero": {
        "display_name": "Libero",
        "description": "Sweeper style defenders, secure and safe both in and out of possession, primarily cleaning up behind the defensive line.",
        "archetypes": ["Willian Pacho", "Niklas Süle", "Stefan de Vrij"],
        "components": [
            {"stat": "PAdj Interceptions", "weight": 0.22, "use_percentile": False},
            {"stat": "Accurate short / medium passes, %", "weight": 0.18, "use_percentile": False},
            {"stat": "Successful defensive actions per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Progressive runs per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "PAdj Sliding tackles", "weight": 0.14, "use_percentile": False},
            {"stat": "Accurate passes, %", "weight": 0.10, "use_percentile": False},
            {"stat": "Fouls per 90", "weight": -0.05, "use_percentile": False},
        ],
        "icon": "🧹"
    },
    "Wide Creator": {
        "display_name": "Wide Creator",
        "description": "Creative centre backs, often in a back three, who play an advanced role with a lot of creative responsibility.",
        "archetypes": ["Alessandro Bastoni", "Eric García", "Daley Blind"],
        "components": [
            {"stat": "Shot assists per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Progressive passes per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Smart passes per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Passes to penalty area per 90", "weight": 0.13, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Crosses per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Deep completions per 90", "weight": 0.09, "use_percentile": False},
            {"stat": "Accurate passes to penalty area, %", "weight": 0.07, "use_percentile": False},
        ],
        "icon": "🎨"
    },
    "Aggressor": {
        "display_name": "Aggressor",
        "description": "Physical aggressive, proactive defenders who like to defend in a high line, winning ball in middle third.",
        "archetypes": ["Marcos Senesi", "Dayot Upamecano", "Sead Kolašinac"],
        "components": [
            {"stat": "Duels won, %", "weight": 0.25, "use_percentile": False},
            {"stat": "Successful defensive actions per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Defensive duels won, %", "weight": 0.15, "use_percentile": False},
            {"stat": "PAdj Sliding tackles", "weight": 0.13, "use_percentile": False},
            {"stat": "Sliding tackles per 90", "weight": 0.09, "use_percentile": False},
        ],
        "icon": "⚔️"
    },
    "Physical Dominator": {
        "display_name": "Physical Dominator",
        "description": "Excellent duelling defenders, those who use their size to control isolated situations against a forward.",
        "archetypes": ["Nikola Milenković", "Moritz Jenz", "Berat Djimsiti"],
        "components": [
            {"stat": "Duels won, %", "weight": 0.30, "use_percentile": False},
            {"stat": "Aerial duels won, %", "weight": 0.28, "use_percentile": False},
            {"stat": "Aerial duels per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Defensive duels won, %", "weight": 0.12, "use_percentile": False},
            {"stat": "Duels per 90", "weight": 0.10, "use_percentile": False},
        ],
        "icon": "💪"
    },
    "Box Defender": {
        "display_name": "Box Defender",
        "description": "A centre back style based on defending deep, protecting goal and box. These defenders love to block, clear and head away danger.",
        "archetypes": ["Marvin Friedrich", "Robin Koch", "Jan Bednarek"],
        "components": [
            {"stat": "Shots blocked per 90", "weight": 0.25, "use_percentile": False},
            {"stat": "Aerial duels won, %", "weight": 0.25, "use_percentile": False},
            {"stat": "Successful defensive actions per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Interceptions per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Conceded goals per 90", "weight": -0.15, "use_percentile": False},
        ],
        "icon": "🧱"
    }
}
"""


def get_defender_preset_options():
    """
    Returns list of defender preset names for UI dropdown

    Returns:
        List of defender preset names
    """
    return list(DEFENDER_PRESETS.keys())
