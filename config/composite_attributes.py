"""
Composite attribute definitions for forward and attacking midfielder analysis
Each attribute is calculated from weighted combinations of statistical metrics
Focused exclusively on forward and attacking midfielder scouting and evaluation
"""

COMPOSITE_ATTRIBUTES = {
    # DF & DM
    "Security": {
        "display_name": "Security",
        "description": "Retain possession under pressure through passing and ball carrying. Focus on quality and safety of passing, with evasiveness and retention when dribbling. Key for a sweeper defender who acts as a safe passing option.",
        "archetypes": ["William Saliba", "Manuel Akanji", "Lucas Beraldo"],
        "components": [
            {
                "stat": "Accurate short / medium passes, %",
                "weight": 0.28,
                "use_percentile": True,
            },
            {"stat": "Accurate passes, %", "weight": 0.20, "use_percentile": True},
            {"stat": "Successful dribbles, %", "weight": 0.18, "use_percentile": True},
            {"stat": "Progressive runs per 90", "weight": 0.15, "use_percentile": True},
            {"stat": "Duels won, %", "weight": 0.12, "use_percentile": True},
            {"stat": "Fouls per 90", "weight": -0.07, "use_percentile": True},
        ],
        "icon": "🛡️",
    },
    "ProgPass": {
        "display_name": "Prog. Pass",
        "description": "Progress possession through expansive and forward passing. Emphasis on tendency to pass forward, ability to pass through defensive lines or over long distances. Key for a ball playing centre back, tasked with finding midfield and attack during build up play.",
        "archetypes": ["Nico Schlotterbeck", "Dayot Upamecano", "Jan Paul Van Hecke"],
        "components": [
            {
                "stat": "Progressive passes per 90",
                "weight": 0.28,
                "use_percentile": True,
            },
            {
                "stat": "Accurate forward passes, %",
                "weight": 0.18,
                "use_percentile": True,
            },
            {"stat": "Accurate long passes, %", "weight": 0.18, "use_percentile": True},
            {"stat": "Smart passes per 90", "weight": 0.15, "use_percentile": True},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.12,
                "use_percentile": True,
            },
            {"stat": "Average pass length, m", "weight": 0.09, "use_percentile": True},
        ],
        "icon": "⚡",
    },
    "BallCarrying": {
        "display_name": "Ball Carrying",
        "description": "Dribble and carry ball up pitch, exploiting space presented and bypassing opposing defenders. Take on ability is part of responsibility but not focus, focus is more on driving into space ahead of player. Key for a wide centre back who is afforded space in inside channels.",
        "archetypes": ["Arthur Theate", "Oumar Solet", "Noussair Mazraoui"],
        "components": [
            {"stat": "Progressive runs per 90", "weight": 0.30, "use_percentile": True},
            {"stat": "Accelerations per 90", "weight": 0.25, "use_percentile": True},
            {"stat": "Successful dribbles, %", "weight": 0.22, "use_percentile": True},
            {"stat": "Duels won, %", "weight": 0.15, "use_percentile": True},
            {"stat": "Offensive duels won, %", "weight": 0.08, "use_percentile": True},
        ],
        "icon": "🏃",
    },
    "Creativity": {
        "display_name": "Creativity",
        "description": "Create chances for their team, primarily through passing. Vital that player can penetrate box with passes and crosses, execute final ball well, and receive ball in final third. Key for a wide centre back who takes up advanced positions in possession.",
        "archetypes": ["Alessandro Bastoni", "Facundo Medina", "Lisandro Martinez"],
        "components": [
            {"stat": "Shot assists per 90", "weight": 0.22, "use_percentile": True},
            {"stat": "Smart passes per 90", "weight": 0.18, "use_percentile": True},
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.15,
                "use_percentile": True,
            },
            {
                "stat": "Passes to final third per 90",
                "weight": 0.13,
                "use_percentile": True,
            },
            {"stat": "Deep completions per 90", "weight": 0.12, "use_percentile": True},
            {
                "stat": "Accurate passes to penalty area, %",
                "weight": 0.10,
                "use_percentile": True,
            },
            {"stat": "xA per 90", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "🎨",
    },
    "ProactiveDefending": {
        "display_name": "Proactive Defending",
        "description": "Aggressively win ball back from opponent, stepping onto forward and proactively regaining possession. Tackling high up pitch, duelling well and attacking space is key. Key for a centre back holding a high defensive line, allowing their team to press.",
        "archetypes": ["Marcos Senesi", "Sead Kolašinac", "Isak Hien"],
        "components": [
            {"stat": "Duels won, %", "weight": 0.28, "use_percentile": True},
            {
                "stat": "Successful defensive actions per 90",
                "weight": 0.22,
                "use_percentile": True,
            },
            {"stat": "Defensive duels per 90", "weight": 0.18, "use_percentile": True},
            {"stat": "Defensive duels won, %", "weight": 0.15, "use_percentile": True},
            {"stat": "PAdj Sliding tackles", "weight": 0.12, "use_percentile": True},
            {"stat": "Fouls per 90", "weight": -0.05, "use_percentile": True},
        ],
        "icon": "⚔️",
    },
    "Duelling": {
        "display_name": "Duelling",
        "description": "Duel effectively with opposing forward, both on ground and in air. A simple focus on duel volume and success, using physical strength and technique to dominate 50/50 situations. Key for many roles, such as wide defenders, sweepers or aggressors.",
        "archetypes": ["Yerry Mina", "Willi Orban", "Harry Maguire"],
        "components": [
            {"stat": "Duels won, %", "weight": 0.30, "use_percentile": True},
            {"stat": "Defensive duels won, %", "weight": 0.25, "use_percentile": True},
            {"stat": "Aerial duels won, %", "weight": 0.25, "use_percentile": True},
            {"stat": "Aerial duels per 90", "weight": 0.12, "use_percentile": True},
            {"stat": "Duels per 90", "weight": 0.08, "use_percentile": True},
        ],
        "icon": "💪",
    },
    "BoxDefending": {
        "display_name": "Box Defending",
        "description": "Defend deep primarily within penalty area, protecting box as opponent attempts to create chances. This involves clearing danger, blocking shot attempts and defending aerially in box. Key for a centre back playing in a deep block style defence.",
        "archetypes": ["James Tarkowski", "Joachim Andersen", "Willi Orban"],
        "components": [
            {"stat": "Shots blocked per 90", "weight": 0.28, "use_percentile": True},
            {"stat": "Aerial duels won, %", "weight": 0.25, "use_percentile": True},
            {
                "stat": "Successful defensive actions per 90",
                "weight": 0.22,
                "use_percentile": True,
            },
            {"stat": "Interceptions per 90", "weight": 0.12, "use_percentile": True},
            {"stat": "Conceded goals per 90", "weight": -0.13, "use_percentile": True},
        ],
        "icon": "🧱",
    },
    "Sweeping": {
        "display_name": "Sweeping",
        "description": "Sweep behind your defensive line, cleaning up any danger that gets past. Emphasis on high quality tackling behind the defensive line and ability to recover ball by protecting space. Often key for a central centre back in a back three, tasked with covering more advanced wide centre backs.",
        "archetypes": ["Stefan de Vrij", "Loïc Bade", "Maxence Lacroix"],
        "components": [
            {"stat": "PAdj Interceptions", "weight": 0.30, "use_percentile": True},
            {
                "stat": "Successful defensive actions per 90",
                "weight": 0.22,
                "use_percentile": True,
            },
            {"stat": "Sliding tackles per 90", "weight": 0.18, "use_percentile": True},
            {"stat": "PAdj Sliding tackles", "weight": 0.15, "use_percentile": True},
            {"stat": "Conceded goals per 90", "weight": -0.15, "use_percentile": True},
        ],
        "icon": "🧹",
    },
    # ========== DM RESPONSIBILITIES ==========
    "DM_Destroying": {
        "display_name": "Destroying",
        "description": "Ability to protect backline, breaking up opponents transitions and duelling during defensive phase. Emphasis on duels, recoveries and aerials. Key for defensive midfielders.",
        "archetypes": ["Martín Zubimendi", "Anton Stach", "Christian Nørgaard"],
        "components": [
            {"stat": "Duels won, %", "weight": 0.35, "use_percentile": True},
            {"stat": "Defensive duels per 90", "weight": 0.22, "use_percentile": True},
            {"stat": "Aerial duels won, %", "weight": 0.22, "use_percentile": True},
            {"stat": "Aerial duels per 90", "weight": 0.14, "use_percentile": True},
            {"stat": "Interceptions per 90", "weight": 0.07, "use_percentile": True},
        ],
        "icon": "🗑️",
    },
    "DM_BallWinning": {
        "display_name": "Ball Winning",
        "description": "Ability to win possession back from opponent through pressures, interceptions and tackles. Emphasis on defensive volume and height, winning ball in middle and upper thirds of pitch. Key for high-energy midfielders in a pressing system.",
        "archetypes": ["Manuel Ugarte", "Alexis Mac Allister", "Elliot Anderson"],
        "components": [
            {"stat": "PAdj Interceptions", "weight": 0.28, "use_percentile": True},
            {
                "stat": "Successful defensive actions per 90",
                "weight": 0.22,
                "use_percentile": True,
            },
            {"stat": "Interceptions per 90", "weight": 0.15, "use_percentile": True},
            {"stat": "Sliding tackles per 90", "weight": 0.12, "use_percentile": True},
            {"stat": "PAdj Sliding tackles", "weight": 0.09, "use_percentile": True},
            {"stat": "Defensive duels per 90", "weight": 0.08, "use_percentile": True},
            {"stat": "Duels won, %", "weight": 0.05, "use_percentile": True},
        ],
        "icon": "⚔️",
    },
    "DM_Dictating": {
        "display_name": "Dictating",
        "description": "Ability to control possession for your team, receiving ball frequently, moving it quickly and keeping possession secure. Progression or creation is not the aim, more so providing a passing options and controlling tempo of play. Key for a midfielder in a team that holds a lot of ball.",
        "archetypes": ["João Neves", "Aleksandar Pavlovic", "Nicolás González"],
        "components": [
            {"stat": "Passes per 90", "weight": 0.30, "use_percentile": True},
            {"stat": "Accurate passes, %", "weight": 0.22, "use_percentile": True},
            {"stat": "Received passes per 90", "weight": 0.18, "use_percentile": True},
            {
                "stat": "Accurate short / medium passes, %",
                "weight": 0.15,
                "use_percentile": True,
            },
            {"stat": "Average pass length, m", "weight": 0.10, "use_percentile": True},
            {"stat": "Forward passes per 90", "weight": 0.05, "use_percentile": True},
        ],
        "icon": "🎭",
    },
    "DM_ProgPass": {
        "display_name": "Prog. Pass",
        "description": "Ability to progress possession and territory for your team using forward passing. Emphasis on passing through thirds and through defensive lines. Key for a midfielder who drops deeper, trying to pass to forwards in advanced positions.",
        "archetypes": ["Joshua Kimmich", "Daniel Parejo", "Granit Xhaka"],
        "components": [
            {
                "stat": "Progressive passes per 90",
                "weight": 0.30,
                "use_percentile": True,
            },
            {
                "stat": "Passes to final third per 90",
                "weight": 0.20,
                "use_percentile": True,
            },
            {
                "stat": "Accurate forward passes, %",
                "weight": 0.18,
                "use_percentile": True,
            },
            {
                "stat": "Accurate progressive passes, %",
                "weight": 0.15,
                "use_percentile": True,
            },
            {"stat": "Forward passes per 90", "weight": 0.10, "use_percentile": True},
            {"stat": "Average pass length, m", "weight": 0.07, "use_percentile": True},
        ],
        "icon": "⚡",
    },
    "DM_BallCarrying": {
        "display_name": "Ball Carrying",
        "description": "Ability to dribble and carry ball up pitch, progressing play or catalysing a transition for your team. Take on ability is part of responsibility but not the focus, the focus is more on driving into space ahead of player. Key for a box-to-box midfielder playing in a transition heavy side, or one who frequently receives ball in space.",
        "archetypes": ["Elliot Anderson", "Mahdi Camara", "Scott McTominay"],
        "components": [
            {"stat": "Progressive runs per 90", "weight": 0.30, "use_percentile": True},
            {"stat": "Successful dribbles, %", "weight": 0.22, "use_percentile": True},
            {"stat": "Accelerations per 90", "weight": 0.22, "use_percentile": True},
            {"stat": "Offensive duels won, %", "weight": 0.15, "use_percentile": True},
            {"stat": "Dribbles per 90", "weight": 0.08, "use_percentile": True},
            {"stat": "Offensive duels per 90", "weight": 0.03, "use_percentile": True},
        ],
        "icon": "🏃",
    },
    "DM_BoxCrashing": {
        "display_name": "Box Crashing",
        "description": "Ability to move into advanced positions in and around box, receive ball under pressure, and create shooting opportunities for themselves or their teammates. Emphasis on getting into box or on end of crosses and cutbacks. Key for goalscoring midfielder who often joins attacking line.",
        "archetypes": ["Scott McTominay", "Xavi Simons", "Abdoulaye Doucoure"],
        "components": [
            {"stat": "Touches in box per 90", "weight": 0.30, "use_percentile": True},
            {"stat": "Shots per 90", "weight": 0.22, "use_percentile": True},
            {"stat": "xG per 90", "weight": 0.18, "use_percentile": True},
            {"stat": "Shot assists per 90", "weight": 0.16, "use_percentile": True},
            {"stat": "Progressive runs per 90", "weight": 0.10, "use_percentile": True},
            {"stat": "Dribbles per 90", "weight": 0.04, "use_percentile": True},
        ],
        "icon": "💥",
    },
    "DM_Creativity": {
        "display_name": "Creativity",
        "description": "Ability to create chances for their team, primarily through passing. Vital that player can penetrate box with passes and crosses, execute final ball well, and receive ball in final third. Key for an attacking midfielder, 8/10 hybrid player.",
        "archetypes": ["Bruno Fernandes", "Nadiem Amiri", "Kevin Stöger"],
        "components": [
            {"stat": "Smart passes per 90", "weight": 0.22, "use_percentile": True},
            {"stat": "Key passes per 90", "weight": 0.18, "use_percentile": True},
            {"stat": "xA per 90", "weight": 0.18, "use_percentile": True},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.14,
                "use_percentile": True,
            },
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.12,
                "use_percentile": True,
            },
            {"stat": "Shot assists per 90", "weight": 0.10, "use_percentile": True},
            {
                "stat": "Accurate short / medium passes, %",
                "weight": 0.06,
                "use_percentile": True,
            },
        ],
        "icon": "🎨",
    },
    "DM_Anchor": {
        "display_name": "Anchor",
        "description": "Defensive midfielders, perhaps called a number 6, who tend to anchor midfield, protecting backline.",
        "archetypes": ["Casemiro", "Azor Matusiwa", "Moisés Caicedo"],
        "components": [
            {"stat": "Defensive duels per 90", "weight": 0.28, "use_percentile": True},
            {"stat": "Aerial duels won, %", "weight": 0.22, "use_percentile": True},
            {"stat": "Interceptions per 90", "weight": 0.18, "use_percentile": True},
            {"stat": "Passes per 90", "weight": 0.15, "use_percentile": True},
            {"stat": "PAdj Interceptions", "weight": 0.12, "use_percentile": True},
            {"stat": "Duels won, %", "weight": 0.05, "use_percentile": True},
        ],
        "icon": "🔒",
    },
    "DM_DLP": {
        "display_name": "DLP",
        "description": "Deep-Lying Playmakers are ball-dominant players with excellent passing, who tend to sit in a deeper position, dictating play from deep.",
        "archetypes": ["Mattéo Guendouzi", "Granit Xhaka", "Pedri"],
        "components": [
            {"stat": "Smart passes per 90", "weight": 0.25, "use_percentile": True},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.20,
                "use_percentile": True,
            },
            {"stat": "Accurate passes, %", "weight": 0.15, "use_percentile": True},
            {
                "stat": "Progressive passes per 90",
                "weight": 0.14,
                "use_percentile": True,
            },
            {"stat": "Average pass length, m", "weight": 0.12, "use_percentile": True},
            {"stat": "xA per 90", "weight": 0.09, "use_percentile": True},
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.05,
                "use_percentile": True,
            },
        ],
        "icon": "🎭",
    },
    # NOTE: DM_BallWinner was removed as duplicate of DM_BallWinning (line 134)
    "DM_BoxToBox": {
        "display_name": "Box-to-Box",
        "description": "Dynamic midfielders who can contribute at both ends of pitch, and have high work rate to travel up-and-down effectively.",
        "archetypes": ["Tanguy Ndombele", "Rabby Nzingoula", "Elliot Anderson"],
        "components": [
            {
                "stat": "Touches in final third per 90",
                "weight": 0.22,
                "use_percentile": True,
            },
            {"stat": "Touches in box per 90", "weight": 0.20, "use_percentile": True},
            {
                "stat": "Successful defensive actions per 90",
                "weight": 0.18,
                "use_percentile": True,
            },
            {"stat": "Progressive runs per 90", "weight": 0.16, "use_percentile": True},
            {"stat": "Defensive duels per 90", "weight": 0.13, "use_percentile": True},
            {"stat": "Passes per 90", "weight": 0.06, "use_percentile": True},
            {"stat": "Shots per 90", "weight": 0.05, "use_percentile": True},
        ],
        "icon": "🔄",
    },
    # NOTE: DM_BoxCrasher was removed as duplicate of DM_BoxCrashing (line 195)
    "DM_Playmaker": {
        "display_name": "Playmaker",
        "description": "Ball dominant, creative midfielders, primarily playing in a 8/central midfield role, creating chances and penetrating final third for their team.",
        "archetypes": ["Rodrigo De Paul", "Habib Diarra", "Adam Wharton"],
        "components": [
            {"stat": "Smart passes per 90", "weight": 0.20, "use_percentile": True},
            {"stat": "xA per 90", "weight": 0.16, "use_percentile": True},
            {"stat": "Key passes per 90", "weight": 0.16, "use_percentile": True},
            {"stat": "Passes per 90", "weight": 0.14, "use_percentile": True},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.12,
                "use_percentile": True,
            },
            {"stat": "Accurate passes, %", "weight": 0.11, "use_percentile": True},
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.06,
                "use_percentile": True,
            },
            {"stat": "Shot assists per 90", "weight": 0.05, "use_percentile": True},
        ],
        "icon": "⚡",
    },
    "DM_AttackingMid": {
        "display_name": "Attacking Mid",
        "description": "Attack minded midfielders who can score and create, but still tend to play in a midfield pair or trio (there is some overlap between this midfield profile and those categorised as Attacking Midfielders).",
        "archetypes": ["Romano Schmid", "Morgan Gibbs-White", "Julian Brandt"],
        "components": [
            {"stat": "Shots per 90", "weight": 0.22, "use_percentile": True},
            {"stat": "xG per 90", "weight": 0.20, "use_percentile": True},
            {"stat": "Goals per 90", "weight": 0.18, "use_percentile": True},
            {
                "stat": "Non-penalty goals per 90",
                "weight": 0.16,
                "use_percentile": True,
            },
            {"stat": "Shot assists per 90", "weight": 0.12, "use_percentile": True},
            {"stat": "Key passes per 90", "weight": 0.08, "use_percentile": True},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.04,
                "use_percentile": True,
            },
        ],
        "icon": "🎯",
    },
    "DM_Destroyer": {
        "display_name": "Destroyer",
        "description": "Aggressive defensive midfielders who protect backline through duels, recoveries and ball winning.",
        "archetypes": ["Bruno Fernandes", "Pierre-Emile Højbjerg", "Marc Casemiro"],
        "components": [
            {
                "stat": "Successful defensive actions per 90",
                "weight": 0.30,
                "use_percentile": True,
            },
            {"stat": "PAdj Interceptions", "weight": 0.20, "use_percentile": True},
            {"stat": "DM_Destroying", "weight": 0.18, "use_percentile": True},
            {"stat": "DM_BallWinning", "weight": 0.15, "use_percentile": True},
            {"stat": "DM_Anchor", "weight": 0.12, "use_percentile": True},
            {"stat": "Duels won, %", "weight": 0.05, "use_percentile": True},
        ],
        "icon": "🗑️",
    },
    "DM_Regista": {
        "display_name": "Regista",
        "description": "Creative deep-lying midfielders who combine ball progression with defensive discipline. They act as deep playmakers while maintaining defensive solidity.",
        "archetypes": ["Toni Kroos", "Dani Ceballos", "Martin Ødegaard"],
        "components": [
            {"stat": "DM_DLP", "weight": 0.35, "use_percentile": True},
            {"stat": "DM_ProgPass", "weight": 0.25, "use_percentile": True},
            {"stat": "DM_BallCarrying", "weight": 0.20, "use_percentile": True},
            {"stat": "Passes per 90", "weight": 0.15, "use_percentile": True},
            {"stat": "DM_Destroying", "weight": 0.05, "use_percentile": True},
        ],
        "icon": "🎨",
    },
    "DM_Carrilero": {
        "display_name": "Carrilero",
        "description": "Technical defensive midfielders who progress play with the ball, providing both defensive solidity and ball progression from deep.",
        "archetypes": ["João Palhinha", "Thiago Alcántara", "Isco"],
        "components": [
            {"stat": "DM_BallCarrying", "weight": 0.35, "use_percentile": True},
            {"stat": "DM_ProgPass", "weight": 0.30, "use_percentile": True},
            {"stat": "DM_Destroying", "weight": 0.20, "use_percentile": True},
            {"stat": "Accurate passes, %", "weight": 0.10, "use_percentile": True},
            {"stat": "Passes per 90", "weight": 0.05, "use_percentile": True},
        ],
        "icon": "🏃",
    },
    # ========== AM AND WINGER RESPONSIBILITIES ==========
    "Finishing": {
        "display_name": "Finishing",
        "description": "Ability to take chances efficiently. Focus on shooting efficiency when close to goal and shot selection, with a little bit of shot volume. Key for inside forwards who play quite narrow, inside the box.",
        "archetypes": ["Jamal Musiala", "Ousmane Dembélé", "Kevin Schade"],
        "components": [
            {"stat": "Goal conversion, %", "weight": 0.30, "use_percentile": True},
            {"stat": "Shots on target, %", "weight": 0.25, "use_percentile": True},
            {
                "stat": "Non-penalty goals per 90",
                "weight": 0.20,
                "use_percentile": True,
            },
            {"stat": "xG per 90", "weight": 0.15, "use_percentile": True},
            {"stat": "Shots per 90", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "⚽",
    },
    "BoxPresence": {
        "display_name": "Box Presence",
        "description": "Ability to occupy the box, receiving the ball close to goal and converting this into good quality chances. Heavily influenced by a players preferred zones to play in. Key for players who are effective goalscorers, or play a shadow striker style role.",
        "archetypes": ["Ademola Lookman", "Zakaria Aboukhlal", "Ismaila Sarr"],
        "components": [
            {"stat": "Touches in box per 90", "weight": 0.35, "use_percentile": True},
            {"stat": "xG per 90", "weight": 0.25, "use_percentile": True},
            {
                "stat": "Non-penalty goals per 90",
                "weight": 0.20,
                "use_percentile": True,
            },
            {"stat": "Goals per 90", "weight": 0.20, "use_percentile": True},
        ],
        "icon": "📦",
    },
    "OneOnOneAbility": {
        "display_name": "1v1 Ability",
        "description": "Ability to dribble past opponents in an isolated 1v1 situation. Efficacy in take ons, ability to convert this into chances for either the player or their teammate. Also attitude towards take ons, how happy are they to carry towards defenders. Key for wingers who often find themselves in 1v1 situations.",
        "archetypes": ["Jeremy Doku", "Jamie Gittens", "Vinicius Júnior"],
        "components": [
            {"stat": "Successful dribbles, %", "weight": 0.30, "use_percentile": True},
            {"stat": "Offensive duels won, %", "weight": 0.25, "use_percentile": True},
            {"stat": "Dribbles per 90", "weight": 0.25, "use_percentile": True},
            {"stat": "Offensive duels per 90", "weight": 0.10, "use_percentile": True},
            {"stat": "Fouls suffered per 90", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "🥋",
    },
    "WINGER_BallCarrying": {
        "display_name": "Ball Carrying (Winger)",
        "description": "Ability to dribble and carry the ball up the pitch, progressing play or catalysing a transition for your team. Take on ability is part of the responsibility but not the focus, the focus is more on driving into space and retaining the ball. Key for industrious wingers who play in transition sides.",
        "archetypes": ["Bukayo Saka", "Francisco Conceição", "Anthony Gordon"],
        "components": [
            {"stat": "Progressive runs per 90", "weight": 0.30, "use_percentile": True},
            {"stat": "Accelerations per 90", "weight": 0.25, "use_percentile": True},
            {"stat": "Successful dribbles, %", "weight": 0.20, "use_percentile": True},
            {"stat": "Duels won, %", "weight": 0.15, "use_percentile": True},
            {"stat": "Offensive duels won, %", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "🏃",
    },
    "Movement": {
        "display_name": "Movement",
        "description": "Ability to move well both with and without the ball, to progress play into advanced areas. Off-ball movement is key here, making runs and sprints to find dangerous space and then receiving the ball. Key for players playing alongside a ball-dominant playmaker.",
        "archetypes": ["Alejandro Garnacho", "Yankuba Minteh", "Karim Adeyemi"],
        "components": [
            {"stat": "Accelerations per 90", "weight": 0.30, "use_percentile": True},
            {"stat": "Progressive runs per 90", "weight": 0.25, "use_percentile": True},
            {"stat": "Touches in box per 90", "weight": 0.20, "use_percentile": True},
            {"stat": "Received passes per 90", "weight": 0.15, "use_percentile": True},
            {"stat": "Shots per 90", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "🔄",
    },
    "WideCreation": {
        "display_name": "Wide Creation",
        "description": "Ability to turn possession into chances for your team from wide areas. Primarily focused on take ons and crossing, key elements to a traditional wingers game. Key for wingers who are told to stay wide, rather than moving into narrow areas.",
        "archetypes": ["Michael Olise", "Junya Ito", "Dwight McNeil"],
        "components": [
            {"stat": "Shot assists per 90", "weight": 0.22, "use_percentile": True},
            {"stat": "Crosses per 90", "weight": 0.18, "use_percentile": True},
            {"stat": "Accurate crosses, %", "weight": 0.18, "use_percentile": True},
            {"stat": "Successful dribbles, %", "weight": 0.15, "use_percentile": True},
            {"stat": "xA per 90", "weight": 0.12, "use_percentile": True},
            {"stat": "Key passes per 90", "weight": 0.10, "use_percentile": True},
            {
                "stat": "Deep completed crosses per 90",
                "weight": 0.05,
                "use_percentile": True,
            },
        ],
        "icon": "✨",
    },
    "FinalBall": {
        "display_name": "Final Ball",
        "description": "Ability to convert final third possession into chances through passing. Focus on shot-creating actions, box penetration and tendencies around creation. Key for most attacking midfielders, but especially playmakers types.",
        "archetypes": ["Rayan Cherki", "Thomas Müller", "Alex Baena"],
        "components": [
            {"stat": "Shot assists per 90", "weight": 0.25, "use_percentile": True},
            {"stat": "Smart passes per 90", "weight": 0.20, "use_percentile": True},
            {"stat": "Key passes per 90", "weight": 0.18, "use_percentile": True},
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.15,
                "use_percentile": True,
            },
            {"stat": "xA per 90", "weight": 0.12, "use_percentile": True},
            {"stat": "Second assists per 90", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "🎯",
    },
    "BuildUp": {
        "display_name": "Build Up",
        "description": "Ability to contribute to build up and early possession phases. Primarily passing based, focused on ball progression, final third penetration and expansive passing ability. Key for playmakers who tend to drop deeper at times, contributing in early build up.",
        "archetypes": ["Cole Palmer", "Alexsandr Golovin", "Isco"],
        "components": [
            {
                "stat": "Progressive passes per 90",
                "weight": 0.22,
                "use_percentile": True,
            },
            {
                "stat": "Passes to final third per 90",
                "weight": 0.20,
                "use_percentile": True,
            },
            {
                "stat": "Accurate progressive passes, %",
                "weight": 0.15,
                "use_percentile": True,
            },
            {"stat": "Smart passes per 90", "weight": 0.15, "use_percentile": True},
            {"stat": "Accurate passes, %", "weight": 0.12, "use_percentile": True},
            {"stat": "Passes per 90", "weight": 0.10, "use_percentile": True},
            {"stat": "Average pass length, m", "weight": 0.06, "use_percentile": True},
        ],
        "icon": "🏗️",
    },
    "AM_Creativity": {
        "display_name": "AM Creativity",
        "description": "Ability to create high-quality chances through visionary passing. Focuses on xA, key passes, smart passes, and passes into dangerous areas. Key for attacking midfielders who act as primary creative outlets.",
        "archetypes": ["Martin Ødegaard", "Kevin De Bruyne", "Bruno Fernandes"],
        "components": [
            {"stat": "xA per 90", "weight": 0.25, "use_percentile": True},
            {"stat": "Key passes per 90", "weight": 0.20, "use_percentile": True},
            {"stat": "Smart passes per 90", "weight": 0.18, "use_percentile": True},
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.15,
                "use_percentile": True,
            },
            {"stat": "Shot assists per 90", "weight": 0.12, "use_percentile": True},
            {"stat": "Second assists per 90", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "🎨",
    },
    "AM_GoalThreat": {
        "display_name": "AM Goal Threat",
        "description": "Ability to score goals from midfield positions. Emphasis on shot volume, xG, and finishing quality. Key for attacking midfielders who arrive late in the box or shoot from distance.",
        "archetypes": ["Dele Alli", "Kai Havertz", "Mason Mount"],
        "components": [
            {"stat": "xG per 90", "weight": 0.25, "use_percentile": True},
            {"stat": "Shots per 90", "weight": 0.22, "use_percentile": True},
            {
                "stat": "Non-penalty goals per 90",
                "weight": 0.20,
                "use_percentile": True,
            },
            {"stat": "Touches in box per 90", "weight": 0.18, "use_percentile": True},
            {"stat": "Goal conversion, %", "weight": 0.15, "use_percentile": True},
        ],
        "icon": "⚽",
    },
    "AM_BallRetention": {
        "display_name": "AM Ball Retention",
        "description": "Ability to maintain possession under pressure and make safe passing decisions. Focus on pass accuracy and low turnover risk. Key for attacking midfielders who operate as pivot points in possession.",
        "archetypes": ["Marco Verratti", "Thiago Alcântara", "Frenkie de Jong"],
        "components": [
            {"stat": "Accurate passes, %", "weight": 0.28, "use_percentile": True},
            {
                "stat": "Accurate short / medium passes, %",
                "weight": 0.25,
                "use_percentile": True,
            },
            {"stat": "Passes per 90", "weight": 0.20, "use_percentile": True},
            {"stat": "Received passes per 90", "weight": 0.15, "use_percentile": True},
            {"stat": "Duels won, %", "weight": 0.12, "use_percentile": True},
        ],
        "icon": "🔄",
    },
    "Pressing": {
        "display_name": "Pressing",
        "description": "Ability to contribute defensively, applying pressure to the opponent in order to win possession back. Emphasis on defensive volume and height, winning the ball in the final third of the pitch. Key for any attacking midfielders in a pressing system, or those who play for teams often on the back foot.",
        "archetypes": ["Facundo Buonanotte", "Mikkel Damsgaard", "Antoine Semenyo"],
        "components": [
            {
                "stat": "Successful defensive actions per 90",
                "weight": 0.25,
                "use_percentile": True,
            },
            {"stat": "Defensive duels per 90", "weight": 0.20, "use_percentile": True},
            {"stat": "Defensive duels won, %", "weight": 0.20, "use_percentile": True},
            {"stat": "Interceptions per 90", "weight": 0.15, "use_percentile": True},
            {"stat": "Fouls per 90", "weight": -0.10, "use_percentile": True},
            {"stat": "PAdj Interceptions", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "🔥",
    },
    # ========== FULLBACK RESPONSIBILITIES ==========
    "FB_BallCarrying": {
        "display_name": "Ball Carrying",
        "description": "Ability to dribble and carry ball up pitch, progressing play by eating up ground, but also taking on opponents in 1v1 situations. It's important that fullbacks and wingbacks can beat a man 1v1, as wide players are more commonly presented with this opportunity. Key for an energetic, box-to-box style wingback.",
        "archetypes": ["Theo Hernández", "Alphonso Davies", "Achraf Hakimi"],
        "components": [
            {"stat": "Progressive runs per 90", "weight": 0.28, "use_percentile": True},
            {"stat": "Successful dribbles, %", "weight": 0.25, "use_percentile": True},
            {"stat": "Dribbles per 90", "weight": 0.18, "use_percentile": True},
            {"stat": "Offensive duels won, %", "weight": 0.15, "use_percentile": True},
            {"stat": "Accelerations per 90", "weight": 0.10, "use_percentile": True},
            {"stat": "Offensive duels per 90", "weight": 0.04, "use_percentile": True},
        ],
        "icon": "🏃",
    },
    "Overlapping": {
        "display_name": "Overlapping",
        "description": "Ability to get high up the pitch and provide winger-like output. Focus on receiving the ball in advanced areas, or carrying the ball into them. Key for a flying fullback or wingback who overlaps an inverting winger.",
        "archetypes": ["Jeremie Frimpong", "Diego Moreira", "Antonee Robinson"],
        "components": [
            {
                "stat": "Touches in final third per 90",
                "weight": 0.30,
                "use_percentile": True,
            },
            {"stat": "Progressive runs per 90", "weight": 0.25, "use_percentile": True},
            {"stat": "Crosses per 90", "weight": 0.15, "use_percentile": True},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.12,
                "use_percentile": True,
            },
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.10,
                "use_percentile": True,
            },
            {"stat": "Accelerations per 90", "weight": 0.08, "use_percentile": True},
        ],
        "icon": "🚀",
    },
    "FinalThird": {
        "display_name": "Final Third",
        "description": "Ability to execute effectively with the ball inside the final third. Those players that can take on opponents to create chances, or pass and cross into the box. Focus on take ons in advanced areas. Key for fullbacks playing in an advanced role during the possession phase.",
        "archetypes": ["Dilane Bakwa", "Keane Lewis-Potter", "Diego Moreira"],
        "components": [
            {
                "stat": "Touches in final third per 90",
                "weight": 0.28,
                "use_percentile": True,
            },
            {"stat": "Shot assists per 90", "weight": 0.20, "use_percentile": True},
            {"stat": "Successful dribbles, %", "weight": 0.15, "use_percentile": True},
            {"stat": "Crosses per 90", "weight": 0.14, "use_percentile": True},
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.12,
                "use_percentile": True,
            },
            {"stat": "Key passes per 90", "weight": 0.11, "use_percentile": True},
        ],
        "icon": "🎯",
    },
    "Playmaking": {
        "display_name": "Playmaking",
        "description": "Ability to progress and create from deeper areas, sometimes centrally, during the build up and possession phases. Found in fullbacks who are strong passers but not such effective dribblers. Key for fullbacks maintaining deeper positions during the possession phase.",
        "archetypes": [
            "Trent Alexander-Arnold",
            "Maximilian Mittelstädt",
            "Nuno Mendes",
        ],
        "components": [
            {
                "stat": "Progressive passes per 90",
                "weight": 0.28,
                "use_percentile": True,
            },
            {"stat": "Smart passes per 90", "weight": 0.20, "use_percentile": True},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.15,
                "use_percentile": True,
            },
            {"stat": "xA per 90", "weight": 0.14, "use_percentile": True},
            {
                "stat": "Passes to penalty area per 90",
                "weight": 0.12,
                "use_percentile": True,
            },
            {"stat": "Key passes per 90", "weight": 0.11, "use_percentile": True},
        ],
        "icon": "🎨",
    },
    # ========== STRIKER / CF RESPONSIBILITIES ==========
    "CompleteForward": {
        "display_name": "Complete Forward",
        "description": "Ability to take chances efficiently. Focus on shooting efficiency when close to goal and shot selection, with a little bit of shot volume. Key for any goalscoring forward, but especially poachers.",
        "archetypes": ["Kylian Mbappé", "Mika Biereth", "Nick Woltemade"],
        "components": [
            {"stat": "xG per 90", "weight": 0.50, "use_percentile": True},
            {"stat": "Goal conversion, %", "weight": 0.50, "use_percentile": True},
            {"stat": "Received passes per 90", "weight": 0.30, "use_percentile": True},
            {"stat": "Key passes per 90", "weight": 0.10, "use_percentile": True},
            {"stat": "xA per 90", "weight": 0.10, "use_percentile": True},
            {"stat": "Head goals per 90", "weight": 0.05, "use_percentile": True},
            {"stat": "Aerial duels won, %", "weight": 0.05, "use_percentile": True},
            {"stat": "Touches in box per 90", "weight": 0.30, "use_percentile": True},
            {"stat": "Non-penalty goals per 90", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "⚽"
    },
    # "CF_BoxPresence": {
    #     "display_name": "Box Presence",
    #     "description": "Ability to occupy the box, receiving the ball close to goal and converting this into good quality chances. Heavily influenced by a players preferred zones to play in. Key for poachers primarily, though it's a beneficial trait for most.",
    #     "archetypes": ["Alexandre Lacazette", "Erling Haaland", "Artem Dovbyk"],
    #     "components": [
    #         {"stat": "Touches in box per 90", "weight": 0.35, "use_percentile": True},
    #         {"stat": "xG per 90", "weight": 0.25, "use_percentile": True},
    #         {"stat": "Non-penalty goals per 90", "weight": 0.20, "use_percentile": True},
    #         {"stat": "Goals per 90", "weight": 0.20, "use_percentile": True},
    #     ],
    #     "icon": "📦"
    # },
    # "CF_Movement": {
    #     "display_name": "Movement",
    #     "description": "Ability to move well both with and without the ball, to progress play into advanced areas. Off-ball movement is key here, making runs and sprints to find dangerous space and then receiving the ball. Key for forwards who run in behind or into channels, and those who play in counter attacking sides.",
    #     "archetypes": ["Ollie Watkins", "Hugo Ekitike", "Loïs Openda"],
    #     "components": [
    #         {"stat": "Accelerations per 90", "weight": 0.30, "use_percentile": True},
    #         {"stat": "Progressive runs per 90", "weight": 0.25, "use_percentile": True},
    #         {"stat": "Touches in box per 90", "weight": 0.20, "use_percentile": True},
    #         {"stat": "Received passes per 90", "weight": 0.15, "use_percentile": True},
    #         {"stat": "Shots per 90", "weight": 0.10, "use_percentile": True},
    #     ],
    #     "icon": "🔄"
    # },
    "LinkPlay": {
        "display_name": "Link Play",
        "description": "Ability to receive the ball in advanced areas or under pressure, before connecting with teammates around them. Focus on quick passing and receiving the ball in the final third. Key for forwards used as an escape route from pressure, often in counter attacking or defensive sides.",
        "archetypes": ["Romelu Lukaku", "Artem Dovbyk", "Randal Kolo Muani"],
        "components": [
            {"stat": "Accurate passes, %", "weight": 0.25, "use_percentile": True},
            {
                "stat": "Passes to final third per 90",
                "weight": 0.20,
                "use_percentile": True,
            },
            {"stat": "Received passes per 90", "weight": 0.18, "use_percentile": True},
            {
                "stat": "Received long passes per 90",
                "weight": 0.15,
                "use_percentile": True,
            },
            {"stat": "Duels won, %", "weight": 0.12, "use_percentile": True},
            {"stat": "Offensive duels won, %", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "🔗",
    },
    # "CF_Creativity": {
    #     "display_name": "Creativity",
    #     "description": "Ability to create chances for others using their final pass. Primarily focused on passes and crosses into the box, to create shooting chances. Key for false nine style forwards who tend to create space for others before exploiting it with a pass.",
    #     "archetypes": ["Harry Kane", "Jonathan Burkardt", "Matthis Abline"],
    #     "components": [
    #         {"stat": "Shot assists per 90", "weight": 0.25, "use_percentile": True},
    #         {"stat": "Passes to penalty area per 90", "weight": 0.22, "use_percentile": True},
    #         {"stat": "xA per 90", "weight": 0.18, "use_percentile": True},
    #         {"stat": "Key passes per 90", "weight": 0.15, "use_percentile": True},
    #         {"stat": "Crosses per 90", "weight": 0.12, "use_percentile": True},
    #         {"stat": "Second assists per 90", "weight": 0.08, "use_percentile": True},
    #     ],
    #     "icon": "🎨"
    # },
    # "CF_BallCarrying": {
    #     "display_name": "Ball Carrying",
    #     "description": "Ability to dribble and carry the ball up the pitch, progressing play or catalysing a transition for your team. Take on ability is part of the responsibility but not the focus, the focus is more on driving into space and retaining the ball. Key for mobile, powerful forwards, who drive forward with the ball, perhaps in a transition side.",
    #     "archetypes": ["Alexander Isak", "Liam Delap", "Marcus Thuram"],
    #     "components": [
    #         {"stat": "Progressive runs per 90", "weight": 0.30, "use_percentile": True},
    #         {"stat": "Accelerations per 90", "weight": 0.25, "use_percentile": True},
    #         {"stat": "Successful dribbles, %", "weight": 0.20, "use_percentile": True},
    #         {"stat": "Duels won, %", "weight": 0.15, "use_percentile": True},
    #         {"stat": "Offensive duels won, %", "weight": 0.10, "use_percentile": True},
    #     ],
    #     "icon": "🏃"
    # },
    # "CF_Pressing": {
    #     "display_name": "Pressing",
    #     "description": "Ability to contribute defensively, applying pressure to the opponent in order to win possession back. Emphasis on defensive volume and height, winning the ball in the final third of the pitch. Key for any forwards playing in a pressing system, especially one with a high defensive line.",
    #     "archetypes": ["Tim Kleindienst", "Raúl Jiménez", "Beto"],
    #     "components": [
    #         {"stat": "Successful defensive actions per 90", "weight": 0.25, "use_percentile": True},
    #         {"stat": "Defensive duels per 90", "weight": 0.20, "use_percentile": True},
    #         {"stat": "Defensive duels won, %", "weight": 0.20, "use_percentile": True},
    #         {"stat": "Interceptions per 90", "weight": 0.15, "use_percentile": True},
    #         {"stat": "Fouls per 90", "weight": -0.10, "use_percentile": True},
    #         {"stat": "PAdj Interceptions", "weight": 0.10, "use_percentile": True},
    #     ],
    #     "icon": "🔥"
    # }
    # ========== GOALKEEPER RESPONSIBILITIES ==========
    "GK_ShotStopping": {
        "display_name": "Shot Stopping",
        "description": "Core shot-stopping ability — saves relative to chances faced and prevention of goals. Emphasis on save rate and goals prevented vs expected. Key for any goalkeeper, especially in high-volume shot-facing teams.",
        "archetypes": ["Alisson Becker", "Gianluigi Donnarumma", "David Raya"],
        "components": [
            {"stat": "Save rate, %",           "weight": 0.40, "use_percentile": True},
            {"stat": "Prevented goals per 90", "weight": 0.35, "use_percentile": True},
            {"stat": "Conceded goals per 90",  "weight": -0.25, "use_percentile": True},
        ],
        "icon": "🧤",
    },
    "GK_Distribution": {
        "display_name": "Distribution",
        "description": "Passing quality and range from the back — ability to launch accurate long balls and progress possession cleanly through short distribution. Key for goalkeepers in possession-based systems.",
        "archetypes": ["Alisson Becker", "Manuel Neuer", "Ederson"],
        "components": [
            {"stat": "Accurate long passes, %",           "weight": 0.30, "use_percentile": True},
            {"stat": "Accurate passes, %",                "weight": 0.25, "use_percentile": True},
            {"stat": "Long passes per 90",                "weight": 0.20, "use_percentile": True},
            {"stat": "Progressive passes per 90",         "weight": 0.15, "use_percentile": True},
            {"stat": "Back passes received as GK per 90", "weight": 0.10, "use_percentile": True},
        ],
        "icon": "🎯",
    },
    "GK_AerialAbility": {
        "display_name": "Aerial Command",
        "description": "Dominance in aerial situations — claiming crosses, winning aerial duels, and commanding the penalty area. Key for goalkeepers facing teams that deliver frequent crosses or set pieces.",
        "archetypes": ["Jordan Pickford", "Kepa Arrizabalaga", "Lukáš Hrádecký"],
        "components": [
            {"stat": "Aerial duels won, %",  "weight": 0.40, "use_percentile": True},
            {"stat": "Aerial duels per 90",  "weight": 0.35, "use_percentile": True},
            {"stat": "Exits per 90",         "weight": 0.25, "use_percentile": True},
        ],
        "icon": "✊",
    },
    "GK_Sweeping": {
        "display_name": "Sweeping",
        "description": "Off-line sweeper-keeper ability — proactively coming off the line to deal with through balls, high lines and loose balls behind the defence. Key for goalkeepers playing behind a high defensive line.",
        "archetypes": ["Manuel Neuer", "Ederson", "Alisson Becker"],
        "components": [
            {"stat": "Exits per 90",                  "weight": 0.40, "use_percentile": True},
            {"stat": "Progressive passes per 90",     "weight": 0.25, "use_percentile": True},
            {"stat": "Aerial duels per 90",           "weight": 0.20, "use_percentile": True},
            {"stat": "Save rate, %",                  "weight": 0.15, "use_percentile": True},
        ],
        "icon": "🧹",
    },
    "GK_FootWork": {
        "display_name": "Footwork",
        "description": "Ability to play out from the back with the feet — contributing to build-up as an additional outfield player. Emphasis on short and long pass accuracy and volume. Key for goalkeepers in possession-heavy systems requiring a 11th outfield player.",
        "archetypes": ["Ederson", "Marc-André ter Stegen", "Yann Sommer"],
        "components": [
            {"stat": "Accurate passes, %",                "weight": 0.30, "use_percentile": True},
            {"stat": "Accurate long passes, %",           "weight": 0.25, "use_percentile": True},
            {"stat": "Progressive passes per 90",         "weight": 0.25, "use_percentile": True},
            {"stat": "Back passes received as GK per 90", "weight": 0.20, "use_percentile": True},
        ],
        "icon": "🦶",
    },
    "GK_Commanding": {
        "display_name": "Commanding",
        "description": "Overall authority over the penalty area — combining aerial dominance, proactive exits and shot prevention into a composite measure of GK command. Key for leaders who organise and control the defensive line.",
        "archetypes": ["Jan Oblak", "Thibaut Courtois", "Gianluigi Donnarumma"],
        "components": [
            {"stat": "Aerial duels won, %",    "weight": 0.35, "use_percentile": True},
            {"stat": "Exits per 90",           "weight": 0.25, "use_percentile": True},
            {"stat": "Aerial duels per 90",    "weight": 0.25, "use_percentile": True},
            {"stat": "Prevented goals per 90", "weight": 0.15, "use_percentile": True},
        ],
        "icon": "👑",
    },
}


def get_display_name(key: str) -> str:
    """
    Return the human-readable display_name for a composite attribute key.

    Args:
        key: The raw COMPOSITE_ATTRIBUTES key (e.g. "DM_BallWinning", "BoxPresence")

    Returns:
        The display_name string (e.g. "Ball Winning", "Box Presence"),
        or the original key if not found.
    """
    entry = COMPOSITE_ATTRIBUTES.get(key)
    if entry:
        return entry.get("display_name", key)
    return key
