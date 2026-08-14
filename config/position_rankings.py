"""
Position-based ranking configuration
Defines which composite attributes are most relevant for each position type
Includes defender, forward, and attacking midfielder positions
"""

POSITION_RANKINGS = {
    # ========== DEFENDER POSITIONS ==========
    
    "CB": {
        "display_name": "Center Backs",
        "key_attributes": [
            "ProgPass",
            "BallCarrying",
            "Security",
            "Duelling",
            "ProactiveDefending",
            "BoxDefending",
            "Sweeping",
        ]
    },

    "Fullback": {
        "display_name": "Full Backs / Wing Backs",
        "key_attributes": [
            "FB_BallCarrying",
            "Overlapping",
            "FinalThird",
            "Playmaking",
            "Security",
            "Pressing",
            "Duelling",
            "BoxDefending"
        ]
    },

   

    "Wide CB": {
        "display_name": "Wide Centre Backs",
        "key_attributes": [
            "BallCarrying",
            "Creativity",
            "ProgPass",
            "Duelling",
            "ProactiveDefending"
        ]
    },

    "Back Three": {
        "display_name": "Back Three Defenders",
        "key_attributes": [
            "Security",
            "Sweeping",
            "BoxDefending",
            "Creativity",
            "BallCarrying"
        ]
    },

    "FB/WB": {
        "display_name": "Full Backs / Wing Backs",
        "key_attributes": [
            "FB_BallCarrying",
            "Overlapping",
            "FinalThird",
            "Playmaking",
            "Security",
            "Pressing",
            "Duelling",
            "BoxDefending"
        ]
    },

    "DM": {
        "display_name": "Central Midfielders",
        "key_attributes": [
            "DM_Destroying",
            "DM_BallWinning",
            "DM_Dictating",
            "DM_ProgPass",
            "DM_BallCarrying",
            "DM_Creativity",
            "DM_Anchor"
        ]
    },

    "Midfielder": {
        "display_name": "Central Midfielders",
        "key_attributes": [
            "DM_Anchor",
            "DM_Destroying",
            "DM_BallWinning",
            "DM_Dictating",
            "DM_ProgPass",
            "BallCarrying",
            "Creativity",
            "BoxPresence",
            "FinalBall",
            "WideCreation",
            "Finishing",
            "Pressing",
        ]
    },
    # ========== FORWARD POSITIONS ==========
    
    "CF": {
        "display_name": "Centre Forwards",
        "key_attributes": [
            "Finishing",
            "BoxPresence",
            "Movement",
            "LinkPlay",
            "FinalBall",
            "BallCarrying",
            "Pressing",
            # "Technical"
        ]
    },
    
    "Winger": {
        "display_name": "Wingers",
        "key_attributes": [
            "OneOnOneAbility",
            "WideCreation",
            "BallCarrying",
            "Finishing",
            "BoxPresence",
            "Pressing"
        ]
    },
    
    "AM": {
        "display_name": "Attacking Midfielders",
        "key_attributes": [
            "FinalBall",
            "BuildUp",
            "WideCreation",
            "Finishing",
            "Creativity",
            "Pressing",
            "BallCarrying",
            "BoxPresence"
        ]
    },
    
    "Complete Forward": {
        "display_name": "Complete Forwards",
        "key_attributes": [
            "CF_Finishing",
            "CF_BoxPresence",
            "CF_Movement",
            "CF_LinkPlay",
            "CF_Creativity",
            "CF_BallCarrying"
        ]
    }
}
