"""
Position and role-based presets for player similarity search
Defines which stats matter most for finding similar players by position/role
"""

from config.defender_presets import DEFENDER_PRESETS
from config.fullback_presets import FULLBACK_PRESETS
from config.midfielder_presets import MIDFIELDER_PRESETS
from config.forward_presets import FORWARD_PRESETS
from config.attacking_midfielder_presets import ATTACKING_MIDFIELDER_PRESETS

# ==================== POSITION-BASED PRESETS ====================
# These presets use composite attributes to auto-generate weights
# covering all relevant stats for each position type

POSITION_SIMILARITY_PRESETS = {
    "CB": {
        "display_name": "Center Back (All-round)",
        "description": "Comprehensive stats for center backs focusing on defending, duelling, and progression",
        "applicable_positions": [
            "CB",
            "RCB",
            "LCB",
            "RCB3",
            "LCB3",
            "CB3",
            "RCB5",
            "LCB5",
        ],
        "weights": None,
        "composites": ["Security", "Duelling", "BoxDefending", "Sweeping", "ProgPass"],
    },
    "DM/CM": {
        "display_name": "Defensive / Central Midfielder",
        "description": "Comprehensive stats for defensive and central midfielders focusing on defending, ball winning, progression, and creativity",
        "applicable_positions": [
            "DMF",
            "LDMF",
            "RDMF",
            "CDM",
            "DMF",
            "LCMF",
            "RCMF3",
            "LCMF3",
            "RCMF3",
        ],
        "weights": None,
        "composites": [
            "DM_Destroying",
            "DM_BallWinning",
            "DM_Dictating",
            "DM_ProgPass",
            "DM_BallCarrying",
            "DM_Creativity",
            "DM_Anchor",
            "DM_DLP",
            "DM_BallWinner",
            "DM_BoxToBox",
            "DM_BoxCrashing",
            "DM_Playmaker",
            "DM_AttackingMid",
            "DM_Destroyer",
            "DM_Regista",
            "DM_Carrilero",
        ],
    },
    "Fullback": {
        "display_name": "Fullback/Wingback",
        "description": "Comprehensive stats for fullbacks and wingbacks focusing on duelling, ball carrying, overlapping, and progression",
        "applicable_positions": [
            "LB",
            "RB",
            "WB",
            "RWB",
            "LWB",
            "LB5",
            "RB5",
            "LWB5",
            "RWB5",
        ],
        "weights": None,
        "composites": [
            "FB_BallCarrying",
            "Overlapping",
            "FinalThird",
            "Playmaking",
            "Security",
            "Pressing",
            "Duelling",
            "BoxDefending",
        ],
    },
    "Winger": {
        "display_name": "Winger",
        "description": "Comprehensive stats for wingers focusing on dribbling, creation, and goal threat",
        "applicable_positions": ["LW", "RW", "LWF", "RWF", "RM", "LM"],
        "weights": None,
        "composites": [
            "OneOnOneAbility",
            "WideCreation",
            "WINGER_BallCarrying",
            "Finishing",
            "BoxPresence",
            "Pressing",
        ],
    },
    "AM": {
        "display_name": "Attacking Midfielder",
        "description": "Comprehensive stats for attacking midfielders focusing on creativity, finishing, and build-up play",
        "applicable_positions": ["AMF", "LCMF", "LAMF", "RAMF", "LCMF3", "RCMF3"],
        "weights": None,
        "composites": [
            "FinalBall",
            "BuildUp",
            "WideCreation",
            "Finishing",
            "Creativity",
            "Pressing",
            "WINGER_BallCarrying",
            "AM_Creativity",
            "AM_GoalThreat",
            "AM_BallRetention",
        ],
    },
    "CF": {
        "display_name": "Centre Forward",
        "description": "Comprehensive stats for centre forwards focusing on finishing, box presence, and link play",
        "applicable_positions": ["CF"],
        "weights": None,
        "composites": [
            "CF_Finishing",
            "CF_BoxPresence",
            "CF_Movement",
            "CF_LinkPlay",
            "CF_Creativity",
            "CF_BallCarrying",
            "CF_Pressing",
        ],
    },
}


# ==================== ROLE-BASED PRESETS ====================
# These presets use weights from existing role definitions
# for specialized player similarity searches


def _extract_weights_from_preset(preset_dict):
    """
    Extract stat weights from preset components

    Args:
        preset_dict: Preset dictionary with 'components' list

    Returns:
        Dict of {stat_name: weight}
    """
    weights = {}
    for component in preset_dict.get("components", []):
        stat = component["stat"]
        weight = component["weight"]
        weights[stat] = weight
    return weights


# Defender role presets
ROLE_SIMILARITY_PRESETS = {
    "Ball_Playing_CB": {
        "display_name": "Ball Playing CB",
        "description": "Excellent passers, able to progress play through thirds and pass over distance",
        "applicable_positions": [
            "CB",
            "RCB",
            "LCB",
            "RCB3",
            "LCB3",
            "CB3",
            "RCB5",
            "LCB5",
        ],
        "source_preset": "DEFENDER_PRESETS.Ball Playing",
        "weights": _extract_weights_from_preset(DEFENDER_PRESETS["Ball Playing"]),
        "icon": "⚡",
    },
    "Libero_CB": {
        "display_name": "Libero",
        "description": "Sweeper style defenders, secure both in and out of possession, cleaning up behind defensive line",
        "applicable_positions": [
            "CB",
            "RCB",
            "LCB",
            "RCB3",
            "LCB3",
            "CB3",
            "RCB5",
            "LCB5",
        ],
        "source_preset": "DEFENDER_PRESETS.Libero",
        "weights": _extract_weights_from_preset(DEFENDER_PRESETS["Libero"]),
        "icon": "🧹",
    },
    "Wide_Creator_CB": {
        "display_name": "Wide Creator",
        "description": "Creative centre backs in back three, with advanced role and creative responsibility",
        "applicable_positions": [
            "CB",
            "RCB",
            "LCB",
            "RCB3",
            "LCB3",
            "CB3",
            "RCB5",
            "LCB5",
        ],
        "source_preset": "DEFENDER_PRESETS.Wide Creator",
        "weights": _extract_weights_from_preset(DEFENDER_PRESETS["Wide Creator"]),
        "icon": "🎨",
    },
    "Aggressor_CB": {
        "display_name": "Aggressor",
        "description": "Physical aggressive defenders in high line, winning ball in middle third",
        "applicable_positions": [
            "CB",
            "RCB",
            "LCB",
            "RCB3",
            "LCB3",
            "CB3",
            "RCB5",
            "LCB5",
        ],
        "source_preset": "DEFENDER_PRESETS.Aggressor",
        "weights": _extract_weights_from_preset(DEFENDER_PRESETS["Aggressor"]),
        "icon": "⚔️",
    },
    "Physical_Dominator_CB": {
        "display_name": "Physical Dominator",
        "description": "Excellent duelling defenders, using size to control isolated situations",
        "applicable_positions": [
            "CB",
            "RCB",
            "LCB",
            "RCB3",
            "LCB3",
            "CB3",
            "RCB5",
            "LCB5",
        ],
        "source_preset": "DEFENDER_PRESETS.Physical Dominator",
        "weights": _extract_weights_from_preset(DEFENDER_PRESETS["Physical Dominator"]),
        "icon": "💪",
    },
    "Box_Defender_CB": {
        "display_name": "Box Defender",
        "description": "Deep defending centre backs protecting goal and box, blocking and clearing danger",
        "applicable_positions": [
            "CB",
            "RCB",
            "LCB",
            "RCB3",
            "LCB3",
            "CB3",
            "RCB5",
            "LCB5",
        ],
        "source_preset": "DEFENDER_PRESETS.Box Defender",
        "weights": _extract_weights_from_preset(DEFENDER_PRESETS["Box Defender"]),
        "icon": "🧱",
    },
    # Forward role presets
    "Poacher_CF": {
        "display_name": "Poacher",
        "description": "Box specialists, finding space in penalty area to finish",
        "applicable_positions": ["CF"],
        "source_preset": "FORWARD_PRESETS.Poacher",
        "weights": _extract_weights_from_preset(FORWARD_PRESETS["Poacher"]),
        "icon": "🎯",
    },
    "Second_Striker_CF": {
        "display_name": "Second Striker",
        "description": "Work best off main striker, making runs and linking play",
        "applicable_positions": ["CF"],
        "source_preset": "FORWARD_PRESETS.Second Striker",
        "weights": _extract_weights_from_preset(FORWARD_PRESETS["Second Striker"]),
        "icon": "2️⃣",
    },
    "Link_Forward_CF": {
        "display_name": "Link Forward",
        "description": "Offer teammates passing option, hold ball and link play quickly",
        "applicable_positions": ["CF"],
        "source_preset": "FORWARD_PRESETS.Link Forward",
        "weights": _extract_weights_from_preset(FORWARD_PRESETS["Link Forward"]),
        "icon": "🔗",
    },
    "False_Nine_CF": {
        "display_name": "False Nine",
        "description": "Drop off centre backs, creating chances for others with passing",
        "applicable_positions": ["CF"],
        "source_preset": "FORWARD_PRESETS.False Nine",
        "weights": _extract_weights_from_preset(FORWARD_PRESETS["False Nine"]),
        "icon": "🎭",
    },
    "Complete_Forward_CF": {
        "display_name": "Complete Forward",
        "description": "Strong in all areas: movement, goalscoring, creativity, and link play",
        "applicable_positions": ["CF"],
        "source_preset": "FORWARD_PRESETS.Complete Forward",
        "weights": _extract_weights_from_preset(FORWARD_PRESETS["Complete Forward"]),
        "icon": "🌟",
    },
    "Power_Forward_CF": {
        "display_name": "Power Forward",
        "description": "Dynamic, physically powerful, making runs and carrying ball",
        "applicable_positions": ["CF"],
        "source_preset": "FORWARD_PRESETS.Power Forward",
        "weights": _extract_weights_from_preset(FORWARD_PRESETS["Power Forward"]),
        "icon": "💪",
    },
    "Pressing_Forward_CF": {
        "display_name": "Pressing Forward",
        "description": "Selfless forwards expending energy defensively, pressing opponent",
        "applicable_positions": ["CF"],
        "source_preset": "FORWARD_PRESETS.Pressing Forward",
        "weights": _extract_weights_from_preset(FORWARD_PRESETS["Pressing Forward"]),
        "icon": "🔥",
    },
    # Attacking midfielder/winger role presets
    "Winger_AM": {
        "display_name": "Winger",
        "description": "Classic wingers creating chances from wide using dribbling and passing",
        "applicable_positions": ["LW", "RW", "LWF", "RWF", "RM", "LM"],
        "source_preset": "ATTACKING_MIDFIELDER_PRESETS.Winger",
        "weights": _extract_weights_from_preset(ATTACKING_MIDFIELDER_PRESETS["Winger"]),
        "icon": "🎯",
    },
    "Direct_Dribbler_AM": {
        "display_name": "Direct Dribbler",
        "description": "Tricky wingers relentless in 1v1 situations",
        "applicable_positions": ["LW", "RW", "LWF", "RWF", "RM", "LM"],
        "source_preset": "ATTACKING_MIDFIELDER_PRESETS.Direct Dribbler",
        "weights": _extract_weights_from_preset(
            ATTACKING_MIDFIELDER_PRESETS["Direct Dribbler"]
        ),
        "icon": "🥋",
    },
    "Industrious_Winger_AM": {
        "display_name": "Industrious Winger",
        "description": "Hard working wingers covering ground defensively and offensively",
        "applicable_positions": ["LW", "RW", "LWF", "RWF", "RM", "LM"],
        "source_preset": "ATTACKING_MIDFIELDER_PRESETS.Industrious Winger",
        "weights": _extract_weights_from_preset(
            ATTACKING_MIDFIELDER_PRESETS["Industrious Winger"]
        ),
        "icon": "🏃",
    },
    "Inside_Forward_AM": {
        "display_name": "Inside Forward",
        "description": "Goal-focused attackers from flank, occupying half space channel",
        "applicable_positions": ["LW", "RW", "LWF", "RWF", "RM", "LM"],
        "source_preset": "ATTACKING_MIDFIELDER_PRESETS.Inside Forward",
        "weights": _extract_weights_from_preset(
            ATTACKING_MIDFIELDER_PRESETS["Inside Forward"]
        ),
        "icon": "⚽",
    },
    "Shadow_Striker_AM": {
        "display_name": "Shadow Striker",
        "description": "Not ball-dominant, making runs in behind or into box",
        "applicable_positions": [
            "LW",
            "RW",
            "LWF",
            "RWF",
            "RM",
            "LM",
            "AMF",
            "LCMF",
            "LAMF",
            "RAMF",
            "LCMF3",
            "RCMF3",
        ],
        "source_preset": "ATTACKING_MIDFIELDER_PRESETS.Shadow Striker",
        "weights": _extract_weights_from_preset(
            ATTACKING_MIDFIELDER_PRESETS["Shadow Striker"]
        ),
        "icon": "👻",
    },
    "Wide_Playmaker_AM": {
        "display_name": "Wide Playmaker",
        "description": "Creative wide men focused on passing and crossing",
        "applicable_positions": ["LW", "RW", "LWF", "RWF", "RM", "LM"],
        "source_preset": "ATTACKING_MIDFIELDER_PRESETS.Wide Playmaker",
        "weights": _extract_weights_from_preset(
            ATTACKING_MIDFIELDER_PRESETS["Wide Playmaker"]
        ),
        "icon": "🎨",
    },
    "Playmaker_AM": {
        "display_name": "Playmaker",
        "description": "Creative central attacking midfielders, ball-dominant chance creators",
        "applicable_positions": ["AMF", "LCMF", "LAMF", "RAMF", "LCMF3", "RCMF3"],
        "source_preset": "ATTACKING_MIDFIELDER_PRESETS.Playmaker",
        "weights": _extract_weights_from_preset(
            ATTACKING_MIDFIELDER_PRESETS["Playmaker"]
        ),
        "icon": "⚡",
    },
    # Fullback role presets
    "False_Winger_FB": {
        "display_name": "False Winger",
        "description": "Fullback who plays almost as a winger, dribbling and creating in final third",
        "applicable_positions": [
            "LB",
            "RB",
            "WB",
            "RWB",
            "LWB",
            "LB5",
            "RB5",
            "LWB5",
            "RWB5",
        ],
        "source_preset": "FULLBACK_PRESETS.False Winger",
        "weights": _extract_weights_from_preset(FULLBACK_PRESETS["False Winger"]),
        "icon": "🏃‍♂️",
    },
    "Flyer_FB": {
        "display_name": "Flyer",
        "description": "High energy, box-to-box fullbacks that press high, overlap well and cover ground",
        "applicable_positions": [
            "LB",
            "RB",
            "WB",
            "RWB",
            "LWB",
            "LB5",
            "RB5",
            "LWB5",
            "RWB5",
        ],
        "source_preset": "FULLBACK_PRESETS.Flyer",
        "weights": _extract_weights_from_preset(FULLBACK_PRESETS["Flyer"]),
        "icon": "🚀",
    },
    "Playmaker_FB": {
        "display_name": "Playmaker",
        "description": "Creative fullbacks who do offensive work from deep, inverting or holding half space position",
        "applicable_positions": [
            "LB",
            "RB",
            "WB",
            "RWB",
            "LWB",
            "LB5",
            "RB5",
            "LWB5",
            "RWB5",
        ],
        "source_preset": "FULLBACK_PRESETS.Playmaker",
        "weights": _extract_weights_from_preset(FULLBACK_PRESETS["Playmaker"]),
        "icon": "🎨",
    },
    "Safety_FB": {
        "display_name": "Safety",
        "description": "Secure passing option who can help defuse danger, often tucking into midfield during possession",
        "applicable_positions": [
            "LB",
            "RB",
            "WB",
            "RWB",
            "LWB",
            "LB5",
            "RB5",
            "LWB5",
            "RWB5",
        ],
        "source_preset": "FULLBACK_PRESETS.Safety",
        "weights": _extract_weights_from_preset(FULLBACK_PRESETS["Safety"]),
        "icon": "🛡️",
    },
    "Ball_Winner_FB": {
        "display_name": "Ball Winner",
        "description": "Tenacious fullbacks that win ball back with high pressing and duelling",
        "applicable_positions": [
            "LB",
            "RB",
            "WB",
            "RWB",
            "LWB",
            "LB5",
            "RB5",
            "LWB5",
            "RWB5",
        ],
        "source_preset": "FULLBACK_PRESETS.Ball Winner",
        "weights": _extract_weights_from_preset(FULLBACK_PRESETS["Ball Winner"]),
        "icon": "⚔️",
    },
    "Defensive_Fullback_FB": {
        "display_name": "Defensive Fullback",
        "description": "Solid defenders who tuck into hybrid CB/FB role, offering value in defending box",
        "applicable_positions": [
            "LB",
            "RB",
            "WB",
            "RWB",
            "LWB",
            "LB5",
            "RB5",
            "LWB5",
            "RWB5",
        ],
        "source_preset": "FULLBACK_PRESETS.Defensive Fullback",
        "weights": _extract_weights_from_preset(FULLBACK_PRESETS["Defensive Fullback"]),
        "icon": "🧱",
    },
    # Midfielder role presets
    "Anchor_CM": {
        "display_name": "Anchor",
        "description": "Defensive midfielders, perhaps called a number 6, who tend to anchor midfield, protecting backline.",
        "applicable_positions": [],
        "archetypes": ["Casemiro", "Azor Matusiwa", "Moisés Caicedo"],
        "components": [
            {"stat": "Defensive duels per 90", "weight": 0.28, "use_percentile": False},
            {"stat": "Aerial duels won, %", "weight": 0.22, "use_percentile": False},
            {"stat": "Interceptions per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.12, "use_percentile": False},
            {"stat": "PAdj Interceptions", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🔒",
    },
    "DLP_CM": {
        "display_name": "DLP",
        "description": "Deep-Lying Playmakers are ball-dominant players with excellent passing, who tend to sit in a deeper position, dictating play from deep.",
        "applicable_positions": [],
        "archetypes": ["Mattéo Guendouzi", "Granit Xhaka", "Pedri"],
        "components": [
            {"stat": "Smart passes per 90", "weight": 0.25, "use_percentile": False},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.20,
                "use_percentile": False,
            },
            {"stat": "Accurate passes, %", "weight": 0.15, "use_percentile": False},
            {
                "stat": "Progressive passes per 90",
                "weight": 0.14,
                "use_percentile": False,
            },
            {"stat": "Average pass length, m", "weight": 0.12, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.09, "use_percentile": False},
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.05,
                "use_percentile": False,
            },
        ],
        "icon": "🎭",
    },
    "Ball Winner_CM": {
        "display_name": "Ball Winner",
        "description": "Aggressive, high energy midfielders who are tasked with winning ball across all thirds. They primarily press, duel and intercept, trying to control middle third.",
        "applicable_positions": [],
        "archetypes": [
            "Nicolás Domínguez",
            "Eduardo Camavinga",
            "Manuel Ugarte Ribeiro",
        ],
        "components": [
            {
                "stat": "Successful defensive actions per 90",
                "weight": 0.25,
                "use_percentile": False,
            },
            {"stat": "Defensive duels per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "PAdj Interceptions", "weight": 0.18, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.17, "use_percentile": False},
            {"stat": "Interceptions per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Fouls per 90", "weight": -0.08, "use_percentile": False},
        ],
        "icon": "⚔️",
    },
    "Box-to-Box_CM": {
        "display_name": "Box-to-Box",
        "description": "Dynamic midfielders who can contribute at both ends of pitch, and have high work rate to travel up-and-down effectively.",
        "applicable_positions": [],
        "archetypes": ["Tanguy Ndombele", "Rabby Nzingoula", "Elliot Anderson"],
        "components": [
            {
                "stat": "Touches in final third per 90",
                "weight": 0.22,
                "use_percentile": False,
            },
            {"stat": "Touches in box per 90", "weight": 0.20, "use_percentile": False},
            {
                "stat": "Successful defensive actions per 90",
                "weight": 0.18,
                "use_percentile": False,
            },
            {
                "stat": "Progressive runs per 90",
                "weight": 0.16,
                "use_percentile": False,
            },
            {"stat": "Defensive duels per 90", "weight": 0.13, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.06, "use_percentile": False},
            {"stat": "Shots per 90", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🔄",
    },
    "Box Crasher_CM": {
        "display_name": "Box Crasher",
        "description": "Offensively valuable midfielders, not necessarily creative, who can break into box and finish chances for their team.",
        "applicable_positions": [],
        "archetypes": ["Scott McTominay", "Abdoulaye Doucouré", "Giuliano Simeone"],
        "components": [
            {"stat": "Shots per 90", "weight": 0.25, "use_percentile": False},
            {"stat": "xG per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "Goals per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Shot assists per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Touches in box per 90", "weight": 0.12, "use_percentile": False},
            {
                "stat": "Non-penalty goals per 90",
                "weight": 0.08,
                "use_percentile": False,
            },
        ],
        "icon": "💥",
    },
    "Playmaker_CM": {
        "display_name": "Playmaker",
        "description": "Ball dominant, creative midfielders, primarily playing in a 8/central midfield role, creating chances and penetrating final third for their team.",
        "applicable_positions": [],
        "archetypes": ["Rodrigo De Paul", "Habib Diarra", "Adam Wharton"],
        "components": [
            {"stat": "Smart passes per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Key passes per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.14, "use_percentile": False},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.12,
                "use_percentile": False,
            },
            {"stat": "Accurate passes, %", "weight": 0.11, "use_percentile": False},
            {"stat": "Shot assists per 90", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "⚡",
    },
    "Attacking Mid_CM": {
        "display_name": "Attacking Mid",
        "description": "Attack minded midfielders who can score and create, but still tend to play in a midfield pair or trio (there is some overlap between this midfield profile and those categorised as Attacking Midfielders).",
        "applicable_positions": [],
        "archetypes": ["Romano Schmid", "Morgan Gibbs-White", "Julian Brandt"],
        "components": [
            {"stat": "Shots per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "xG per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Goals per 90", "weight": 0.18, "use_percentile": False},
            {
                "stat": "Non-penalty goals per 90",
                "weight": 0.16,
                "use_percentile": False,
            },
            {"stat": "Shot assists per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Key passes per 90", "weight": 0.08, "use_percentile": False},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.04,
                "use_percentile": False,
            },
        ],
        "icon": "🎯",
    },
    "Destroyer_CM": {
        "display_name": "Destroyer",
        "description": "Aggressive defensive midfielders who protect backline through duels, recoveries and ball winning.",
        "applicable_positions": [],
        "archetypes": ["Bruno Fernandes", "Pierre-Emile Højbjerg", "Marc Casemiro"],
        "components": [
            {
                "stat": "Successful defensive actions per 90",
                "weight": 0.30,
                "use_percentile": False,
            },
            {"stat": "PAdj Interceptions", "weight": 0.20, "use_percentile": False},
            {"stat": "DM_Destroying", "weight": 0.18, "use_percentile": False},
            {"stat": "DM_BallWinning", "weight": 0.15, "use_percentile": False},
            {"stat": "DM_Anchor", "weight": 0.12, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🗑️",
    },
    "Regista_CM": {
        "display_name": "Regista",
        "description": "Creative deep-lying midfielders who combine ball progression with defensive discipline. They act as deep playmakers while maintaining defensive solidity.",
        "applicable_positions": [],
        "archetypes": ["Toni Kroos", "Dani Ceballos", "Martin Ødegaard"],
        "components": [
            {"stat": "Smart passes per 90", "weight": 0.20, "use_percentile": False},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.18,
                "use_percentile": False,
            },
            {
                "stat": "Accurate progressive passes, %",
                "weight": 0.14,
                "use_percentile": False,
            },
            {
                "stat": "Progressive passes per 90",
                "weight": 0.12,
                "use_percentile": False,
            },
            {"stat": "Average pass length, m", "weight": 0.12, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.10, "use_percentile": False},
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.05,
                "use_percentile": False,
            },
            {
                "stat": "Accurate short / medium passes, %",
                "weight": 0.06,
                "use_percentile": False,
            },
            {"stat": "Sliding tackles per 90", "weight": 0.03, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.03, "use_percentile": False},
            {"stat": "DM_Destroying", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🎨",
    },
    "Carrilero_CM": {
        "display_name": "Carrilero",
        "description": "Technical defensive midfielders who progress play with ball, providing both defensive solidity and ball progression from deep.",
        "applicable_positions": [],
        "archetypes": ["João Palhinha", "Thiago Alcántara", "Isco"],
        "components": [
            {
                "stat": "Progressive runs per 90",
                "weight": 0.35,
                "use_percentile": False,
            },
            {
                "stat": "Progressive passes per 90",
                "weight": 0.30,
                "use_percentile": False,
            },
            {"stat": "Accurate passes, %", "weight": 0.10, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.05, "use_percentile": False},
            {"stat": "Successful dribbles, %", "weight": 0.10, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.05, "use_percentile": False},
        ],
        "icon": "🏃",
    },
}


# ==================== HELPER FUNCTIONS ====================


def get_applicable_presets(position: str) -> list:
    """
    Get all applicable presets for a position

    Args:
        position: Specific position (e.g., "CB", "RCB3", "LW", "CDM")

    Returns:
        List of preset dicts with keys: key, type, display_name, description, applicable_positions
    """
    applicable = []

    # Add position preset
    for preset_key, preset_config in POSITION_SIMILARITY_PRESETS.items():
        if position in preset_config["applicable_positions"]:
            applicable.append({"key": preset_key, "type": "position", **preset_config})

    # Add role presets
    for preset_key, preset_config in ROLE_SIMILARITY_PRESETS.items():
        if position in preset_config["applicable_positions"]:
            applicable.append({"key": preset_key, "type": "role", **preset_config})

    return applicable


def get_position_preset_keys():
    """
    Get list of all position preset keys

    Returns:
        List of position preset keys
    """
    return list(POSITION_SIMILARITY_PRESETS.keys())


def get_role_preset_keys():
    """
    Get list of all role preset keys

    Returns:
        List of role preset keys
    """
    return list(ROLE_SIMILARITY_PRESETS.keys())
