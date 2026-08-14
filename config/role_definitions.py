"""
Consolidated Role/Preset Definitions
Single source for all tactical role definitions across all positions
Replaces scattered definitions in defender_presets.py, midfielder_presets.py, etc.
"""

from typing import Dict, List, Optional


# ========== DEFENDER ROLES (CB) ==========

DEFENDER_ROLES = {
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


# ========== FULLBACK ROLES ==========

FULLBACK_ROLES = {
    "False Winger": {
        "display_name": "False Winger",
        "description": "A fullback who plays almost as a winger in possession, dribbling and creating in the final third.",
        "archetypes": ["Dilane Bakwa", "Patrick Dorgu", "Keane Lewis-Potter"],
        "components": [
            {"stat": "Touches in final third per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "Crosses per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Successful dribbles, %", "weight": 0.16, "use_percentile": False},
            {"stat": "Progressive runs per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Key passes per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Shot assists per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Passes to penalty area per 90", "weight": 0.07, "use_percentile": False},
        ],
        "icon": "🏃‍♂️"
    },
    "Flyer": {
        "display_name": "Flyer",
        "description": "High energy, box-to-box style fullbacks that press high, overlap well and cover a lot of ground.",
        "archetypes": ["Jeremie Frimpong", "Diego Moreira", "Alessandro Zanoli"],
        "components": [
            {"stat": "Progressive runs per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Touches in final third per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Successful defensive actions per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "Accelerations per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Crosses per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.07, "use_percentile": False},
        ],
        "icon": "🚀"
    },
    "Playmaker": {
        "display_name": "Playmaker",
        "description": "Creative fullbacks who do their offensive work from deep, often inverting or holding a position in the half space, playing a lot of passes to progress and create.",
        "archetypes": ["Maximilian Mittelstädt", "Nuno Mendes", "Przemysław Frankowski"],
        "components": [
            {"stat": "Progressive passes per 90", "weight": 0.25, "use_percentile": False},
            {"stat": "Smart passes per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Passes to final third per 90", "weight": 0.16, "use_percentile": False},
            {"stat": "xA per 90", "weight": 0.14, "use_percentile": False},
            {"stat": "Key passes per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Passes per 90", "weight": 0.08, "use_percentile": False},
            {"stat": "Passes to penalty area per 90", "weight": 0.07, "use_percentile": False},
        ],
        "icon": "🎨"
    },
    "Safety": {
        "display_name": "Safety",
        "description": "A player used primarily as a secure passing option, who can help defuse danger as it is created. They often tuck into midfield during possession.",
        "archetypes": ["Carlos Augusto", "Myles Lewis-Skelly", "Raphaël Guerreiro"],
        "components": [
            {"stat": "Accurate short / medium passes, %", "weight": 0.28, "use_percentile": False},
            {"stat": "Accurate passes, %", "weight": 0.20, "use_percentile": False},
            {"stat": "Successful dribbles, %", "weight": 0.18, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.15, "use_percentile": False},
            {"stat": "Progressive runs per 90", "weight": 0.12, "use_percentile": False},
            {"stat": "Fouls per 90", "weight": -0.07, "use_percentile": False},
        ],
        "icon": "🛡️"
    },
    "Ball Winner": {
        "display_name": "Ball Winner",
        "description": "Tenacious fullbacks that like to win the ball back with high pressing and duelling.",
        "archetypes": ["Daniel Muñoz", "Ali Abdi", "Nordi Mukiele"],
        "components": [
            {"stat": "Successful defensive actions per 90", "weight": 0.22, "use_percentile": False},
            {"stat": "Defensive duels per 90", "weight": 0.18, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.18, "use_percentile": False},
            {"stat": "Defensive duels won, %", "weight": 0.16, "use_percentile": False},
            {"stat": "PAdj Sliding tackles", "weight": 0.12, "use_percentile": False},
            {"stat": "Interceptions per 90", "weight": 0.10, "use_percentile": False},
            {"stat": "Fouls per 90", "weight": -0.06, "use_percentile": False},
        ],
        "icon": "⚔️"
    },
    "Defensive Fullback": {
        "display_name": "Defensive Fullback",
        "description": "Solid defenders, sometimes tucking into a hybrid centre back and fullback role, who offer most value in defending the box.",
        "archetypes": ["Vladimír Coufal", "Ben White", "Neco Williams"],
        "components": [
            {"stat": "Shots blocked per 90", "weight": 0.25, "use_percentile": False},
            {"stat": "Aerial duels won, %", "weight": 0.22, "use_percentile": False},
            {"stat": "Successful defensive actions per 90", "weight": 0.20, "use_percentile": False},
            {"stat": "Interceptions per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Conceded goals per 90", "weight": -0.12, "use_percentile": False},
            {"stat": "Duels won, %", "weight": 0.06, "use_percentile": False},
        ],
        "icon": "🧱"
    }
}


# ========== MIDFIELDER ROLES (DM/CM) ==========

MIDFIELDER_ROLES = {
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


# ========== ATTACKING MIDFIELDER & WINGER ROLES ==========

ATTACKING_MIDFIELDER_ROLES = {
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


# ========== FORWARD ROLES (CF/Striker) ==========

FORWARD_ROLES = {
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


# ========== GOALKEEPER ROLES ==========

GK_ROLES = {
    "Shot Stopper": {
        "display_name": "Shot Stopper",
        "description": "Traditional shot-stopping focused goalkeeper who prioritises save rate and goal prevention above all else. Dominant inside the box, winning saves through reflexes and positioning.",
        "archetypes": ["Jan Oblak", "Emiliano Martínez", "Mike Maignan"],
        "components": [
            {"stat": "Save rate, %",           "weight": 0.35, "use_percentile": False},
            {"stat": "Prevented goals per 90", "weight": 0.30, "use_percentile": False},
            {"stat": "Conceded goals per 90",  "weight": -0.20, "use_percentile": False},
            {"stat": "Shots against per 90",   "weight": -0.15, "use_percentile": False},
        ],
        "icon": "🥅"
    },
    "Ball-Playing GK": {
        "display_name": "Ball-Playing GK",
        "description": "Distribution-first goalkeeper who acts as an extra outfield player in build-up. Combines excellent long-range passing with short distribution accuracy, receiving back passes under pressure.",
        "archetypes": ["Ederson", "Alisson Becker", "Marc-André ter Stegen"],
        "components": [
            {"stat": "Accurate long passes, %",           "weight": 0.30, "use_percentile": False},
            {"stat": "Progressive passes per 90",         "weight": 0.25, "use_percentile": False},
            {"stat": "Accurate passes, %",                "weight": 0.20, "use_percentile": False},
            {"stat": "Back passes received as GK per 90", "weight": 0.15, "use_percentile": False},
            {"stat": "Save rate, %",                      "weight": 0.10, "use_percentile": False},
        ],
        "icon": "🎯"
    },
    "Sweeper Keeper": {
        "display_name": "Sweeper Keeper",
        "description": "Proactive off-line goalkeeper who aggressively sweeps up through balls and loose passes behind a high defensive line. Combines excellent exits with aerial dominance and solid saves.",
        "archetypes": ["Manuel Neuer", "Ederson", "Yann Sommer"],
        "components": [
            {"stat": "Exits per 90",          "weight": 0.35, "use_percentile": False},
            {"stat": "Aerial duels per 90",   "weight": 0.25, "use_percentile": False},
            {"stat": "Aerial duels won, %",   "weight": 0.25, "use_percentile": False},
            {"stat": "Save rate, %",          "weight": 0.15, "use_percentile": False},
        ],
        "icon": "🧹"
    },
    "Modern GK": {
        "display_name": "Modern GK",
        "description": "Complete modern goalkeeper who excels across all dimensions — shot stopping, sweeping, aerial command, and distribution. The ideal profile for high-pressing possession-based teams.",
        "archetypes": ["Alisson Becker", "Manuel Neuer", "David Raya"],
        "components": [
            {"stat": "Save rate, %",                  "weight": 0.25, "use_percentile": False},
            {"stat": "Prevented goals per 90",        "weight": 0.20, "use_percentile": False},
            {"stat": "Exits per 90",                  "weight": 0.20, "use_percentile": False},
            {"stat": "Aerial duels won, %",           "weight": 0.20, "use_percentile": False},
            {"stat": "Accurate long passes, %",       "weight": 0.15, "use_percentile": False},
        ],
        "icon": "🌟"
    }
}


# ========== HELPER FUNCTIONS ==========

def get_all_roles() -> Dict[str, Dict]:
    """
    Get all role definitions merged into a single dictionary

    Returns:
        Dictionary with all role definitions from all positions

    Example:
        >>> roles = get_all_roles()
        >>> "Ball Playing" in roles
        True
    """
    all_roles = {}
    all_roles.update(GK_ROLES)
    all_roles.update(DEFENDER_ROLES)
    all_roles.update(FULLBACK_ROLES)
    all_roles.update(MIDFIELDER_ROLES)
    all_roles.update(ATTACKING_MIDFIELDER_ROLES)
    all_roles.update(FORWARD_ROLES)
    return all_roles


def get_roles_for_position_type(position_type: str) -> Dict[str, Dict]:
    """
    Get role definitions for a specific position type

    Args:
        position_type: Position type ("CB", "Fullback", "DM", "AM", "CF", etc.)

    Returns:
        Dictionary of role definitions for that position type
        Returns empty dict if position type not found

    Example:
        >>> roles = get_roles_for_position_type("CB")
        >>> "Ball Playing" in roles
        True
    """
    position_role_map = {
        "GK": GK_ROLES,
        "CB": DEFENDER_ROLES,
        "Fullback": FULLBACK_ROLES,
        "DM": MIDFIELDER_ROLES,
        "CM": MIDFIELDER_ROLES,
        "AM": ATTACKING_MIDFIELDER_ROLES,
        "Winger": ATTACKING_MIDFIELDER_ROLES,
        "CF": FORWARD_ROLES,
        "Forward": {**FORWARD_ROLES, **ATTACKING_MIDFIELDER_ROLES}
    }
    return position_role_map.get(position_type, {})


def get_role_definition(role_name: str) -> Optional[Dict]:
    """
    Get the definition for a specific role

    Args:
        role_name: Name of the role (e.g., "Ball Playing", "Anchor")

    Returns:
        Role definition dictionary, or None if not found

    Example:
        >>> role = get_role_definition("Ball Playing")
        >>> role["display_name"]
        "Ball Playing"
    """
    all_roles = get_all_roles()
    return all_roles.get(role_name)


# ========== BACKWARDS COMPATIBILITY EXPORTS ==========
# These allow old imports to still work

GK_PRESETS = GK_ROLES
DEFENDER_PRESETS = DEFENDER_ROLES
FULLBACK_PRESETS = FULLBACK_ROLES
MIDFIELDER_PRESETS = MIDFIELDER_ROLES
ATTACKING_MIDFIELDER_PRESETS = ATTACKING_MIDFIELDER_ROLES
FORWARD_PRESETS = FORWARD_ROLES
