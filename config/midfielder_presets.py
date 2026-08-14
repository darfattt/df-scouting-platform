"""
Midfielder preset definitions for Player Finder
Weighted scoring formulas for different DM, CM, and AM roles
Focused on modern midfielder play styles and responsibilities

DEPRECATED: This file is maintained for backward compatibility only.
All role definitions have been consolidated into config/role_definitions.py
"""

# Import from the centralized role definitions
from config.role_definitions import MIDFIELDER_ROLES as MIDFIELDER_PRESETS

# DEPRECATED: Old definitions below - kept as reference only
"""
MIDFIELDER_PRESETS_OLD = {
    "Anchor": {
        "display_name": "Anchor",
        "description": "Defensive midfielders, perhaps called a number 6, who tend to anchor midfield, protecting backline.",
        "archetypes": ["Casemiro", "Azor Matusiwa", "Moisés Caicedo"],
        "components": [
            {"stat": "Defensive duels per 90", "weight": 0.28, "use_percentile": False},
            {"stat": "Aerial duels won, %", "weight": 0.22, "use_percentile": False},
            {"stat": "Interceptions per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.12, "use_percentile": False},
            {"stat": "PAdj Interceptions", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🔒"
    },

    "DLP": {
        "display_name": "DLP",
        "description": "Deep-Lying Playmakers are ball-dominant players with excellent passing, who tend to sit in a deeper position, dictating play from deep.",
        "archetypes": ["Mattéo Guendouzi", "Granit Xhaka", "Pedri"],
        "components": [
            {"stat": "Smart passes per 90", "weight": 0.25, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Accurate passes, %", "weight": 0.15, "use_percentile": False},
            {"stat": "Progressive passes per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Average pass length, m", "weight": 0.12, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.09, "use_percentile": False},
            {"stat": "Passes to penalty area per 90", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🎭"
    },

    "Ball Winner": {
        "display_name": "Ball Winner",
        "description": "Aggressive, high energy midfielders who are tasked with winning ball across all thirds. They primarily press, duel and intercept, trying to control middle third.",
        "archetypes": ["Nicolás Domínguez", "Eduardo Camavinga", "Manuel Ugarte Ribeiro"],
        "components": [
            {"stat": "Successful defensive actions per 90", "weight": 0.25, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "PAdj Interceptions", "weight": 0.18, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.17, "use_percentile": False},
            {"stat": "Interceptions per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Fouls per 90", "weight": -0.08, "use_percentile": False},
        ],
        "icon": "⚔️"
    },

    "Box-to-Box": {
        "display_name": "Box-to-Box",
        "description": "Dynamic midfielders who can contribute at both ends of pitch, and have high work rate to travel up-and-down effectively.",
        "archetypes": ["Tanguy Ndombele", "Rabby Nzingoula", "Elliot Anderson"],
        "components": [
            {"stat": "Touches in final third per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "Touches in box per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Successful defensive actions per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Progressive runs per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.13, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.06, "use_percentile": False},
            {"stat": "Shots per 90", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🔄"
    },

    "Box Crasher": {
        "display_name": "Box Crasher",
        "description": "Offensively valuable midfielders, not necessarily creative, who can break into box and finish chances for their team.",
        "archetypes": ["Scott McTominay", "Abdoulaye Doucouré", "Giuliano Simeone"],
        "components": [
            {"stat": "Shots per 90", "weight": 0.25, "use_percentile": False},
            {"stat": "xG per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "Goals per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Shot assists per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Touches in box per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Non-penalty goals per 90", "weight": 0.08, "use_percentile": False},
        ],
        "icon": "💥"
    },

    "Playmaker": {
        "display_name": "Playmaker",
        "description": "Ball dominant, creative midfielders, primarily playing in a 8/central midfield role, creating chances and penetrating final third for their team.",
        "archetypes": ["Rodrigo De Paul", "Habib Diarra", "Adam Wharton"],
        "components": [
            {"stat": "Smart passes per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Key passes per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Accurate passes, %", "weight": 0.11, "use_percentile": False},
            {"stat": "Shot assists per 90", "weight": 0.05, "use_percentile": False},
            {"stat": "Passes to penalty area per 90", "weight": 0.06, "use_percentile": False},
        ],
        "icon": "⚡"
    },

    "Attacking Mid": {
        "display_name": "Attacking Mid",
        "description": "Attack minded midfielders who can score and create, but still tend to play in a midfield pair or trio (there is some overlap between this midfield profile and those categorised as Attacking Midfielders).",
        "archetypes": ["Romano Schmid", "Morgan Gibbs-White", "Julian Brandt"],
        "components": [
            {"stat": "Shots per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "xG per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Goals per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Non-penalty goals per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Shot assists per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Key passes per 90", "weight": 0.08, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.04, "use_percentile": False},
        ],
        "icon": "🎯"
    },

    "Destroyer": {
        "display_name": "Destroyer",
        "description": "Aggressive defensive midfielders who protect backline through duels, recoveries and ball winning.",
        "archetypes": ["Bruno Fernandes", "Pierre-Emile Højbjerg", "Marc Casemiro"],
        "components": [
            {"stat": "Successful defensive actions per 90", "weight": 0.30, "use_percentile": False},
            {"stat": "PAdj Interceptions", "weight": 0.20, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Sliding tackles per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.08, "use_percentile": False},
        ],
        "icon": "🗑️"
    },

    "Regista": {
        "display_name": "Regista",
        "description": "Creative deep-lying midfielders who combine ball progression with defensive discipline. They act as deep playmakers while maintaining defensive solidity.",
        "archetypes": ["Toni Kroos", "Dani Ceballos", "Martin Ødegaard"],
        "components": [
            {"stat": "Smart passes per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Accurate progressive passes, %", "weight": 0.14, "use_percentile": False},
            {"stat": "Progressive passes per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.08, "use_percentile": False},
            {"stat": "Accurate passes, %", "weight": 0.06, "use_percentile": False},
            {"stat": "Accurate short / medium passes, %", "weight": 0.06, "use_percentile": False},
            {"stat": "Sliding tackles per 90", "weight": 0.03, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.03, "use_percentile": False},
        ],
        "icon": "🎨"
    },

    "Carrilero": {
        "display_name": "Carrilero",
        "description": "Technical defensive midfielders who progress play with the ball, providing both defensive solidity and ball progression from deep.",
        "archetypes": ["João Palhinha", "Thiago Alcántara", "Isco"],
        "components": [
            {"stat": "Progressive runs per 90", "weight": 0.35, "use_percentile": False},
            {"stat": "Progressive passes per 90", "weight": 0.30, "use_percentile": False},
            {"stat": "Accurate passes, %", "weight": 0.10, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.05, "use_percentile": False},
            {"stat": "Successful dribbles, %", "weight": 0.10, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.05, "use_percentile": False},
            {"stat": "Sliding tackles per 90", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🏃"
    }
}
"""


def get_midfielder_preset_options():
    """
    Returns list of midfielder preset names for UI dropdown

    Returns:
        List of midfielder preset names
    """
    return list(MIDFIELDER_PRESETS.keys())
