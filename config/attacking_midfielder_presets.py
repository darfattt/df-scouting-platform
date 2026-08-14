"""
Attacking Midfielder and Winger preset definitions for Player Finder
Weighted scoring formulas for different AM and Winger roles
Focused on modern attacking midfield and wing play styles

DEPRECATED: This file is maintained for backward compatibility only.
All role definitions have been consolidated into config/role_definitions.py
"""

# Import from the centralized role definitions
from config.role_definitions import ATTACKING_MIDFIELDER_ROLES as ATTACKING_MIDFIELDER_PRESETS

# DEPRECATED: Old definitions below - kept as reference only
"""
ATTACKING_MIDFIELDER_PRESETS_OLD = {
    "Winger": {
        "display_name": "Winger",
        "description": "Classic wingers, those who can create chances from wide positions using their dribbling and passing abilities.",
        "archetypes": ["Moses Simon", "Yankuba Minteh", "David Neres"],
        "components": [
            {"stat": "Shot assists per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Crosses per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Accurate crosses, %", "weight": 0.16, "use_percentile": False},
            {"stat": "Successful dribbles, %", "weight": 0.15, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Key passes per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Dribbles per 90", "weight": 0.08, "use_percentile": False},
            {"stat": "Passes to penalty area per 90", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🎯"
    },
    
    "Direct Dribbler": {
        "display_name": "Direct Dribbler",
        "description": "Tricky wingers who are relentless in 1v1 situations, able to get past their opponent continuously.",
        "archetypes": ["Chidera Ejuke", "Jamie Gittens", "Jeremy Doku"],
        "components": [
            {"stat": "Successful dribbles, %", "weight": 0.28, "use_percentile": False},
            {"stat": "Dribbles per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "Offensive duels won, %", "weight": 0.20, "use_percentile": False},
            {"stat": "Offensive duels per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Fouls suffered per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Progressive runs per 90", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🥋"
    },
    
    "Industrious Winger": {
        "display_name": "Industrious Winger",
        "description": "Hard working wingers who cover a lot of ground, both defensively when pressing but also offensively, carrying the ball or making runs off the ball.",
        "archetypes": ["Kaoru Mitoma", "Amad Diallo", "Dango Ouattara"],
        "components": [
            {"stat": "Progressive runs per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Successful defensive actions per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Accelerations per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Dribbles per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Successful dribbles, %", "weight": 0.10, "use_percentile": False},
            {"stat": "Shots per 90", "weight": 0.08, "use_percentile": False},
            {"stat": "Fouls per 90", "weight": -0.08, "use_percentile": False},
        ],
        "icon": "🏃"
    },
    
    "Inside Forward": {
        "display_name": "Inside Forward",
        "description": "Goal-focused attacking midfielders, primarily playing off of the flank, occupying the half space channel. They are equally focused on scoring as creating.",
        "archetypes": ["Omar Marmoush", "Vinicius Júnior", "Luis Díaz"],
        "components": [
            {"stat": "Non-penalty goals per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Shot assists per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Touches in box per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Goal conversion, %", "weight": 0.12, "use_percentile": False},
            {"stat": "Successful dribbles, %", "weight": 0.12, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Shots per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Progressive runs per 90", "weight": 0.08, "use_percentile": False},
        ],
        "icon": "⚽"
    },
    
    "Shadow Striker": {
        "display_name": "Shadow Striker",
        "description": "Not ball-dominant attackers, they prefer to move off the ball, making runs in behind or into the box before scoring or assisting a teammate.",
        "archetypes": ["Ademola Lookman", "Noni Madueke", "Alejandro Garnacho"],
        "components": [
            {"stat": "Non-penalty goals per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "Touches in box per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Accelerations per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Shots per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Goal conversion, %", "weight": 0.12, "use_percentile": False},
            {"stat": "Shot assists per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Received passes per 90", "weight": 0.08, "use_percentile": False},
        ],
        "icon": "👻"
    },
    
    "Wide Playmaker": {
        "display_name": "Wide Playmaker",
        "description": "Creative wide men, often more focused on passing or crossing the ball, but also able to beat a man in isolated areas.",
        "archetypes": ["Rayan Cherki", "Michael Olise", "Junya Ito"],
        "components": [
            {"stat": "Shot assists per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "Key passes per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Smart passes per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Accurate passes, %", "weight": 0.10, "use_percentile": False},
            {"stat": "Crosses per 90", "weight": 0.08, "use_percentile": False},
        ],
        "icon": "🎨"
    },
    
    "Playmaker": {
        "display_name": "Playmaker",
        "description": "Creative attacking midfielders, those who can execute passes into the box, creating chances for others, but also contribute to build up and final third penetration. They tend to be ball-dominant and play centrally.",
        "archetypes": ["Martin Ødegaard", "Kevin De Bruyne", "Isco"],
        "components": [
            {"stat": "Shot assists per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Smart passes per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Key passes per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Progressive passes per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Passes to penalty area per 90", "weight": 0.06, "use_percentile": False},
            {"stat": "Accurate passes, %", "weight": 0.04, "use_percentile": False},
        ],
        "icon": "⚡"
    }
}
"""


def get_attacking_midfielder_preset_options():
    """
    Returns list of attacking midfielder preset names for UI dropdown

    Returns:
        List of attacking midfielder preset names
    """
    return list(ATTACKING_MIDFIELDER_PRESETS.keys())
