"""
Helper functions for position-based similarity weights
Handles weight generation from composite attributes and preset management
"""

import pandas as pd
from config.position_rankings import POSITION_RANKINGS
from config.position_groups import POSITION_GROUPS
from config.composite_attributes import COMPOSITE_ATTRIBUTES
from config.similarity_presets import (
    POSITION_SIMILARITY_PRESETS,
    ROLE_SIMILARITY_PRESETS,
    get_applicable_presets
)


def map_position_to_group(position: str) -> str:
    """
    Map specific position to broad position group

    Maps specific position codes (e.g., "RCB3", "LWF") to broad position groups
    (e.g., "CB", "Winger") that match keys in POSITION_RANKINGS

    Args:
        position: Specific position code (e.g., "CB", "RCB3", "LW")

    Returns:
        Position group key matching POSITION_RANKINGS (e.g., "CB", "DM/CM", "Winger")
        Defaults to "CB" if position not found

    Examples:
        >>> map_position_to_group("RCB3")
        "CB"
        >>> map_position_to_group("LWF")
        "Winger"
        >>> map_position_to_group("CDM")
        "DM/CM"
    """
    # Direct match in POSITION_RANKINGS
    if position in POSITION_RANKINGS:
        return position

    # Search through POSITION_GROUPS to find containing group
    for group_name, positions in POSITION_GROUPS.items():
        if positions and position in positions:
            # Map POSITION_GROUPS key to POSITION_RANKINGS key
            # CB group → CB ranking
            if "CB" in group_name or group_name == "CB":
                if "CB" in POSITION_RANKINGS:
                    return "CB"

            # Fullback/WB group → Fullback ranking
            elif "Fullback" in group_name or "WB" in group_name:
                if "Fullback" in POSITION_RANKINGS:
                    return "Fullback"

            # DM group → DM/CM ranking
            elif "DM" in group_name:
                if "DM/CM" in POSITION_RANKINGS:
                    return "DM/CM"

            # Winger group → Winger ranking
            elif "Winger" in group_name:
                if "Winger" in POSITION_RANKINGS:
                    return "Winger"

            # AM group → AM ranking
            elif "AM" in group_name:
                if "AM" in POSITION_RANKINGS:
                    return "AM"

            # CF group → CF ranking
            elif "CF" in group_name:
                if "CF" in POSITION_RANKINGS:
                    return "CF"

    # Fallback to CB
    return "CB"


def build_position_weights_from_composites(position_group: str) -> dict:
    """
    Auto-generate position similarity weights from composite attributes

    Aggregates all stats from the position's key composite attributes,
    sums weights for stats appearing in multiple composites, and
    normalizes to sum to 1.0

    Args:
        position_group: Position key from POSITION_RANKINGS (e.g., "CB", "DM/CM")

    Returns:
        Dict of {stat_name: normalized_weight} summing to 1.0

    Raises:
        ValueError: If position_group not in POSITION_SIMILARITY_PRESETS

    Algorithm:
        1. Get composite attribute names for position from POSITION_SIMILARITY_PRESETS
        2. For each composite:
           - Extract component stats and their weights
           - Use absolute value of weights (negative weights become positive)
           - Accumulate: if stat appears in multiple composites, sum the weights
        3. Normalize all weights to sum to 1.0

    Example:
        For CB position with composites ["Security", "Duelling", "BoxDefending"]:

        From Security composite:
          - "Duels won, %": weight 0.12
        From Duelling composite:
          - "Duels won, %": weight 0.30

        Accumulated weight for "Duels won, %": 0.12 + 0.30 = 0.42
        (Higher total indicates higher importance across multiple position aspects)

        Final weights are normalized so all weights sum to 1.0
    """
    # Get preset configuration
    if position_group not in POSITION_SIMILARITY_PRESETS:
        raise ValueError(f"Unknown position: {position_group}")

    preset_config = POSITION_SIMILARITY_PRESETS[position_group]
    composite_names = preset_config["composites"]

    # Aggregate stat weights from all composites
    stat_weights = {}
    for comp_name in composite_names:
        if comp_name not in COMPOSITE_ATTRIBUTES:
            continue  # Skip if composite not found

        components = COMPOSITE_ATTRIBUTES[comp_name]["components"]
        for component in components:
            stat = component["stat"]
            weight = abs(component["weight"])  # CRITICAL: Use absolute value

            # Accumulate weights (stats may appear in multiple composites)
            stat_weights[stat] = stat_weights.get(stat, 0) + weight

    # Normalize weights to sum to 1.0
    total_weight = sum(stat_weights.values())
    if total_weight > 0:
        normalized_weights = {k: v / total_weight for k, v in stat_weights.items()}
    else:
        normalized_weights = {}

    return normalized_weights


def get_position_similarity_weights(
    df_filtered: pd.DataFrame,
    selected_player: str,
    player_position: str,
    preset_key: str = "auto"
) -> dict:
    """
    Get similarity weights based on position/role preset

    Main function for retrieving stat weights for similarity calculation.
    Replaces the old get_top_stats_with_weights() function.

    Args:
        df_filtered: Filtered player DataFrame with stat columns
        selected_player: Selected player name (kept for API compatibility, not used)
        player_position: Player's specific position (e.g., "CB", "RCB3", "LW")
        preset_key: Preset selection:
            - "auto": Use position-based preset (default)
            - Position key (e.g., "CB", "Winger"): Use position-based preset
            - Role key (e.g., "Ball_Playing_CB"): Use role-based preset

    Returns:
        Dict of {stat_name: normalized_weight} where:
        - Only includes stats present in df_filtered.columns
        - Weights sum to 1.0
        - All weights are positive

    Fallback Behavior:
        - Unknown preset_key → defaults to position preset for player's position
        - Unknown position → defaults to "CB"
        - No valid stats in DataFrame → equal weights across all available stats

    Example:
        >>> weights = get_position_similarity_weights(df, "Player A", "RCB", "auto")
        >>> weights
        {"Duels won, %": 0.15, "Defensive duels won, %": 0.12, ...}
        >>> sum(weights.values())
        1.0
    """
    # Step 1: Map position to group
    position_group = map_position_to_group(player_position)
    print("")

    # Step 2: Determine which preset to use
    if preset_key == "auto":
        # Default to position-based preset
        use_position_preset = True
        target_preset = position_group
    elif preset_key in POSITION_SIMILARITY_PRESETS:
        # Position preset explicitly selected
        use_position_preset = True
        target_preset = preset_key
    elif preset_key in ROLE_SIMILARITY_PRESETS:
        # Role preset selected
        use_position_preset = False
        target_preset = preset_key
    else:
        # Unknown preset, fallback to position
        use_position_preset = True
        target_preset = position_group

    # Step 3: Get weights based on preset type
    if use_position_preset:
        # Auto-generate from composites
        try:
            weights = build_position_weights_from_composites(target_preset)
        except ValueError:
            # Fallback to CB if position preset not found
            weights = build_position_weights_from_composites("CB")
    else:
        # Get from role preset
        preset_config = ROLE_SIMILARITY_PRESETS[target_preset]
        weights = preset_config["weights"].copy()

    # Step 4: Filter to valid columns (only stats present in DataFrame)
    valid_weights = {
        stat: weight
        for stat, weight in weights.items()
        if stat in df_filtered.columns
    }

    # Step 5: Normalize filtered weights to sum to 1.0
    total_weight = sum(abs(w) for w in valid_weights.values())
    if total_weight > 0:
        normalized_weights = {k: v / total_weight for k, v in valid_weights.items()}
    else:
        # Emergency fallback: equal weights on all available stats
        from utils.data_loader import get_all_stat_columns
        from config.stat_categories import STAT_CATEGORIES
        all_stats = get_all_stat_columns(STAT_CATEGORIES)
        valid_stats = [s for s in all_stats if s in df_filtered.columns]

        if len(valid_stats) > 0:
            normalized_weights = {s: 1.0 / len(valid_stats) for s in valid_stats}
        else:
            # Ultimate fallback: empty dict (should never happen)
            normalized_weights = {}

    return normalized_weights


def get_presets_for_position(position: str) -> list:
    """
    Get all applicable presets for a position

    Wrapper around config.similarity_presets.get_applicable_presets()
    for convenience and API consistency

    Args:
        position: Specific position code (e.g., "CB", "LW", "CDM")

    Returns:
        List of preset dicts, each containing:
        - key: Preset identifier
        - type: "position" or "role"
        - display_name: Human-readable name
        - description: What the preset represents
        - applicable_positions: List of positions
        - (other preset-specific fields)

    Example:
        >>> presets = get_presets_for_position("CB")
        >>> [p["display_name"] for p in presets]
        ["Center Back (All-round)", "Ball Playing CB", "Libero", "Aggressor", ...]
    """
    return get_applicable_presets(position)
