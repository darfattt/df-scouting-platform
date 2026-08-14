"""
Central Configuration Registry
Single source of truth for Position Group → Responsibilities → Roles relationships
Maps position groups to their relevant composite attributes and tactical roles
"""

from typing import List, Dict, Optional


# ========== POSITION → RESPONSIBILITIES MAPPING ==========
# Maps position groups to their relevant composite attributes (responsibilities)

POSITION_RESPONSIBILITIES = {
    "GK": [
        "GK_ShotStopping",
        "GK_Distribution",
        "GK_AerialAbility",
        "GK_Sweeping",
        "GK_FootWork",
        "GK_Commanding",
    ],
    "CB": [
        "Security",
        "ProgPass",
        "BallCarrying",
        "ProactiveDefending",
        "Duelling",
        "BoxDefending",
        "Sweeping",
        "Creativity",
    ],
    "Fullback": [
        "FB_BallCarrying",
        "Overlapping",
        "FinalThird",
        "Playmaking",
        "Security",
        "Pressing",
        "Duelling",
        "BoxDefending",
    ],
    "DM": [
        "DM_Destroying",
        "DM_BallWinning",
        "DM_Dictating",
        "DM_ProgPass",
        "DM_BallCarrying",
        "DM_BoxCrashing",
        "DM_Creativity",
        "DM_Anchor",
        "DM_DLP",
        "DM_BoxToBox",
        "DM_Playmaker",
        "DM_AttackingMid",
        "DM_Destroyer",
        "DM_Regista",
        "DM_Carrilero",
    ],
    "CM": [
        "DM_Destroying",
        "DM_BallWinning",
        "DM_Dictating",
        "DM_ProgPass",
        "DM_BallCarrying",
        "DM_BoxCrashing",
        "DM_Creativity",
        "DM_BoxToBox",
        "DM_Playmaker",
        "DM_AttackingMid",
        "BallCarrying",
        "Creativity",
        "BoxPresence",
        "FinalBall",
        "Pressing",
    ],
    "AM": [
        "FinalBall",
        "BuildUp",
        "WideCreation",
        "Finishing",
        "Creativity",
        "Pressing",
        "BallCarrying",
        "BoxPresence",
        "Movement",
        "OneOnOneAbility",
        "AM_Creativity",
        "AM_GoalThreat",
        "AM_BallRetention",
    ],
    "Winger": [
        "OneOnOneAbility",
        "WideCreation",
        "WINGER_BallCarrying",
        "Finishing",
        "BoxPresence",
        "Pressing",
        "Movement",
    ],
    "CF": [
        "Finishing",
        "BoxPresence",
        "Movement",
        "LinkPlay",
        "FinalBall",
        "BallCarrying",
        "Pressing",
    ],
    "Forward": [
        "Finishing",
        "BoxPresence",
        "Movement",
        "LinkPlay",
        "FinalBall",
        "BallCarrying",
        "Pressing",
        "OneOnOneAbility",
        "WideCreation",
    ],
    "Defender": [
        "Security", "ProgPass", "BallCarrying", "ProactiveDefending", "Duelling", "BoxDefending", "Sweeping", "Creativity",
        "FB_BallCarrying", "Overlapping", "FinalThird", "Playmaking", "Pressing"
    ],
    "Midfielder": [
        "DM_Destroying", "DM_BallWinning", "DM_Dictating", "DM_ProgPass", "DM_BallCarrying", "DM_BoxCrashing", "DM_Creativity",
        "DM_BoxToBox", "DM_Playmaker", "DM_AttackingMid", "BallCarrying", "Creativity", "BoxPresence", "FinalBall", "Pressing"
    ],
    "Midfielder_N_AM": [
        "DM_Destroying", "DM_BallWinning", "DM_Dictating", "DM_ProgPass", "DM_BallCarrying", "DM_BoxCrashing", "DM_Creativity",
        "DM_BoxToBox", "DM_Playmaker", "DM_AttackingMid", "BallCarrying", "Creativity", "BoxPresence", "FinalBall", "Pressing",
        "AM_Creativity", "AM_GoalThreat", "AM_BallRetention"
    ],
}


# ========== POSITION → ROLES MAPPING ==========
# Maps position groups to their available tactical roles/presets

POSITION_ROLES = {
    "GK": [
        "Shot Stopper",
        "Ball-Playing GK",
        "Sweeper Keeper",
        "Modern GK",
    ],
    "CB": [
        "Ball Playing",
        "Libero",
        "Wide Creator",
        "Aggressor",
        "Physical Dominator",
        "Box Defender",
    ],
    "Fullback": [
        "False Winger",
        "Flyer",
        "Playmaker",
        "Safety",
        "Ball Winner",
        "Defensive Fullback",
    ],
    "DM": [
        "Anchor",
        "DLP",
        "Ball Winner",
        "Box-to-Box",
        "Box Crasher",
        "Playmaker",
        "Attacking Mid",
        "Destroyer",
        "Regista",
        "Carrilero",
    ],
    "CM": [
        "Anchor",
        "DLP",
        "Ball Winner",
        "Box-to-Box",
        "Box Crasher",
        "Playmaker",
        "Attacking Mid",
        "Destroyer",
        "Regista",
        "Carrilero",
    ],
    "AM": [
        "Winger",
        "Direct Dribbler",
        "Industrious Winger",
        "Inside Forward",
        "Shadow Striker",
        "Wide Playmaker",
        "Playmaker",
    ],
    "Winger": [
        "Winger",
        "Direct Dribbler",
        "Industrious Winger",
        "Inside Forward",
        "Shadow Striker",
        "Wide Playmaker",
    ],
    "CF": [
        "Poacher",
        "Second Striker",
        "Link Forward",
        "False Nine",
        "Complete Forward",
        "Power Forward",
        "Pressing Forward",
    ],
    "Forward": [
        "Poacher",
        "Second Striker",
        "Link Forward",
        "False Nine",
        "Complete Forward",
        "Power Forward",
        "Pressing Forward",
        "Winger",
        "Direct Dribbler",
        "Industrious Winger",
        "Inside Forward",
        "Shadow Striker",
        "Wide Playmaker",
        "Playmaker",
    ],
    "Defender": [
        "Ball Playing", "Libero", "Wide Creator", "Aggressor", "Physical Dominator", "Box Defender",
        "False Winger", "Flyer", "Playmaker", "Safety", "Ball Winner", "Defensive Fullback"
    ],
    "Midfielder": [
        "Anchor", "DLP", "Ball Winner", "Box-to-Box", "Box Crasher", "Playmaker", "Attacking Mid", "Destroyer", "Regista", "Carrilero"
    ],
    "Midfielder_N_AM": [
        "Anchor", "DLP", "Ball Winner", "Box-to-Box", "Box Crasher", "Playmaker", "Attacking Mid", "Destroyer", "Regista", "Carrilero",
        "Winger", "Direct Dribbler", "Industrious Winger", "Inside Forward", "Shadow Striker", "Wide Playmaker"
    ],
}


# ========== COMBINED POSITION GROUPS ==========
# Groups of positions for broader filtering and analysis

COMBINED_POSITIONS = {
    "Defender": ["CB", "Fullback"],
    "Midfielder": ["DM", "CM", "AM"],
    "Forward": ["AM", "CF", "Winger"],
    "All Defenders": ["CB", "Fullback"],
    "All Midfielders": ["DM", "CM"],
    "All Attackers": ["AM", "Winger", "CF"],
}


# ========== HELPER FUNCTIONS ==========


def get_responsibilities_for_position(position_group: str) -> List[str]:
    """
    Get relevant composite attributes (responsibilities) for a position group

    Args:
        position_group: Position group name (e.g., "CB", "DM", "Winger")

    Returns:
        List of composite attribute names relevant to the position
        Returns empty list if position not found

    Example:
        >>> get_responsibilities_for_position("CB")
        ["Security", "ProgPass", "BallCarrying", "Duelling", ...]
    """
    return POSITION_RESPONSIBILITIES.get(position_group, [])


def get_roles_for_position(position_group: str) -> List[str]:
    """
    Get available tactical roles for a position group

    Args:
        position_group: Position group name (e.g., "CB", "DM", "Winger")

    Returns:
        List of role names available for the position
        Returns empty list if position not found

    Example:
        >>> get_roles_for_position("DM")
        ["Anchor", "DLP", "Ball Winner", "Box-to-Box", ...]
    """
    return POSITION_ROLES.get(position_group, [])


def get_all_position_groups() -> List[str]:
    """
    Get all available position groups

    Returns:
        List of all position group names

    Example:
        >>> get_all_position_groups()
        ["CB", "Fullback", "DM", "CM", "AM", "Winger", "CF", "Forward"]
    """
    return list(POSITION_RESPONSIBILITIES.keys())


def get_combined_positions(group_name: str) -> Optional[List[str]]:
    """
    Get position groups included in a combined position category

    Args:
        group_name: Combined position group name (e.g., "Defender", "Midfielder")

    Returns:
        List of position groups in the combined category
        Returns None if group not found

    Example:
        >>> get_combined_positions("Defender")
        ["CB", "Fullback"]
    """
    return COMBINED_POSITIONS.get(group_name)


def position_supports_role(position_group: str, role_name: str) -> bool:
    """
    Check if a position group supports a specific role

    Args:
        position_group: Position group name (e.g., "CB", "DM")
        role_name: Role name (e.g., "Ball Playing", "Anchor")

    Returns:
        True if position supports the role, False otherwise

    Example:
        >>> position_supports_role("CB", "Ball Playing")
        True
        >>> position_supports_role("CB", "Poacher")
        False
    """
    roles = get_roles_for_position(position_group)
    return role_name in roles


def position_has_responsibility(position_group: str, responsibility: str) -> bool:
    """
    Check if a position group has a specific responsibility (composite attribute)

    Args:
        position_group: Position group name (e.g., "CB", "DM")
        responsibility: Composite attribute name (e.g., "Security", "DM_Destroying")

    Returns:
        True if position has the responsibility, False otherwise

    Example:
        >>> position_has_responsibility("CB", "Security")
        True
        >>> position_has_responsibility("CB", "DM_Destroying")
        False
    """
    responsibilities = get_responsibilities_for_position(position_group)
    return responsibility in responsibilities


def get_positions_for_role(role_name: str) -> List[str]:
    """
    Get all position groups that support a specific role

    Args:
        role_name: Role name (e.g., "Playmaker", "Box-to-Box")

    Returns:
        List of position groups that support the role

    Example:
        >>> get_positions_for_role("Playmaker")
        ["DM", "CM", "AM", "Fullback"]
    """
    positions = []
    for position, roles in POSITION_ROLES.items():
        if role_name in roles:
            positions.append(position)
    return positions


def get_positions_for_responsibility(responsibility: str) -> List[str]:
    """
    Get all position groups that have a specific responsibility

    Args:
        responsibility: Composite attribute name (e.g., "BallCarrying", "Pressing")

    Returns:
        List of position groups that have the responsibility

    Example:
        >>> get_positions_for_responsibility("Pressing")
        ["Fullback", "CM", "AM", "Winger", "CF", "Forward"]
    """
    positions = []
    for position, responsibilities in POSITION_RESPONSIBILITIES.items():
        if responsibility in responsibilities:
            positions.append(position)
    return positions


# ========== POSITION GROUP DISPLAY NAMES ==========
# User-friendly display names for position groups

POSITION_DISPLAY_NAMES = {
    "GK": "Goalkeepers",
    "CB": "Center Backs",
    "Fullback": "Fullbacks / Wing Backs",
    "DM": "Defensive Midfielders",
    "CM": "Central Midfielders",
    "AM": "Attacking Midfielders",
    "Winger": "Wingers",
    "CF": "Center Forwards / Strikers",
    "Forward": "Forwards (All)",
    "Defender": "Defenders (All)",
    "Midfielder": "Midfielders (All)",
}


def get_position_display_name(position_group: str) -> str:
    """
    Get user-friendly display name for a position group

    Args:
        position_group: Position group name (e.g., "CB", "DM")

    Returns:
        Display name for the position, or the position_group itself if not found

    Example:
        >>> get_position_display_name("CB")
        "Center Backs"
    """
    return POSITION_DISPLAY_NAMES.get(position_group, position_group)
