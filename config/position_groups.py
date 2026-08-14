"""
Position grouping configuration for simplified filtering
Defines logical position groups for easier player filtering
"""


POSITION_GROUP_ORDER = ["GK", "CB", "Fullback", "DM", "Midfielder", "AM", "Winger", "CF", "Forward", "Defender"]

POSITION_GROUP_ICONS = {
    "GK": "🧤",
    "CB": "🛡️",
    "Fullback": "🛡️",
    "DM": "⚙️",
    "Midfielder": "⚙️",
    "AM": "🎯",
    "Winger": "🎯",
    "CF": "🎯",
    "Forward": "🎯",
    "Defender": "🛡️",
    "All": "🌐"
}


POSITION_GROUPS = {
    "All": None,
    "GK": ["GK"],
    "CB": ["CB", "RCB", "LCB", "RCB3", "LCB3"],
    "Fullback": ["LB", "RB", "LB5", "RB5", "LWB", "RWB"],
    "Defender": ["CB", "RCB", "LCB", "RCB3", "LCB3", "LB", "RB", "LB5", "RB5", "LWB", "RWB"],
    "DM": ["DMF", "LDMF", "RDMF", "LCMF", "RCMF", "LCMF3", "RCMF3"],
    "AM": ["AMF", "LAMF", "RAMF"],
    #"Midfielder": ["DMF", "LDMF", "RDMF", "LCMF", "RCMF", "LCMF3", "RCMF3"],
    "Midfielder_N_AM": ["DMF", "LDMF", "RDMF", "LCMF", "RCMF", "LCMF3", "RCMF3", "AMF", "LAMF", "RAMF"],
    "Winger": ["LW", "RW", "LWF", "RWF","RAMF","LAMF"],
    "Forward": ["CF", "LW", "RW", "LWF", "RWF", "AMF", "LAMF", "RAMF"],
    "CF": ["CF"]
}


def get_position_group_options():
    """
    Returns list of position group names for UI dropdown

    Returns:
        List of position group names
    """
    return list(POSITION_GROUPS.keys())


def filter_by_position_group(df, group_name):
    """
    Filter dataframe by position group

    Args:
        df: Player dataframe
        group_name: Key from POSITION_GROUPS

    Returns:
        Filtered dataframe
    """
    if group_name == "All" or group_name not in POSITION_GROUPS:
        return df.copy()

    positions = POSITION_GROUPS[group_name]
    if positions is None:
        return df.copy()

    # Filter using .isin() for exact matches
    return df[df['Primary position'].isin(positions)].copy()

def get_group_for_position(position):
    # Split the string by commas and clean up any extra whitespace
    positions = [pos.strip() for pos in position.split(',')]
    
    # Iterate through your ordered groups
    for group in POSITION_GROUP_ORDER:
        allowed_positions = POSITION_GROUPS.get(group)
        
        # If the group exists and has assigned positions
        if allowed_positions:
            # Check if any of the split positions (e.g., "RCB3" or "LCB3") are in the group
            if any(pos in allowed_positions for pos in positions):
                return group
                
    return None

def get_group_for_single_position(position: str) -> str:
    """
    Find the most specific position group for a given player position.
    
    Args:
        position: Player's specific position (e.g., 'RCB', 'LB', 'DMF')
        
    Returns:
        The matching group name (e.g., 'CB', 'Fullback', 'DM') or 'All' if no match.
    """
    # Use the standardized order for priority
    for group in POSITION_GROUP_ORDER:
        if group in POSITION_GROUPS and POSITION_GROUPS[group] is not None:
            if position in POSITION_GROUPS[group]:
                return group
                
    return "All"
