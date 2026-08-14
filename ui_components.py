import streamlit as st
from config.stat_categories import STAT_CATEGORIES
from utils.data_loader import get_all_stat_columns
from config.defender_presets import DEFENDER_PRESETS
from config.fullback_presets import FULLBACK_PRESETS
from config.midfielder_presets import MIDFIELDER_PRESETS
from config.forward_presets import FORWARD_PRESETS
from config.attacking_midfielder_presets import ATTACKING_MIDFIELDER_PRESETS
from config.position_groups import POSITION_GROUPS

def sanitize_key(text: str, prefix: str = "") -> str:
    """
    Sanitize text to create a valid Streamlit widget key

    Args:
        text: The text to sanitize
        prefix: Optional prefix to add

    Returns:
        Sanitized string safe for use as Streamlit key
    """
    sanitized = (
        text.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("%", "pct")
        .replace(",", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
        .replace(".", "_")
    )

    sanitized = "".join(c if c.isalnum() or c == "_" else "" for c in sanitized)

    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")

    if prefix:
        sanitized = f"{prefix}_{sanitized}"

    return sanitized


def build_custom_preset_ui():
    """
    Build custom preset configuration in main content area

    Returns:
        Dictionary matching DEFENDER_PRESETS structure or None if no metrics added
    """
    st.markdown("#### 🛠️ Custom Preset Builder")

    # Initialize session state
    if "custom_metrics" not in st.session_state:
        st.session_state.custom_metrics = []

    with st.expander("⚙️ Configure Metrics", expanded=True):
        # Preset name and description
        preset_name = st.text_input(
            "Preset Name:", value="My Custom Preset", key="custom_preset_name"
        )

        preset_description = st.text_area(
            "Description:",
            value="Custom weighted scoring profile",
            height=60,
            key="custom_preset_description",
        )

        st.markdown("---")
        st.markdown("**Add Metrics:**")

        # Get all available stats
        all_stats = get_all_stat_columns(STAT_CATEGORIES)

        # Metric selector
        selected_metric = st.selectbox(
            "Choose a metric:", options=[""] + all_stats, key="metric_selector"
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            metric_weight = st.number_input(
                "Weight:",
                min_value=-1.0,
                max_value=1.0,
                value=0.25,
                step=0.05,
                help="Negative weights invert metric (lower is better)",
                key="metric_weight_input",
            )

        with col2:
            if st.button("➕ Add", key="add_metric_btn"):
                if selected_metric and selected_metric != "":
                    # Check if metric already added
                    existing_metrics = [
                        m["stat"] for m in st.session_state.custom_metrics
                    ]
                    if selected_metric not in existing_metrics:
                        st.session_state.custom_metrics.append(
                            {"stat": selected_metric, "weight": metric_weight}
                        )
                        st.rerun()
                    else:
                        st.warning(f"'{selected_metric}' already added")

        st.markdown("---")
        st.markdown("**Selected Metrics:**")

        # Display current metrics
        if len(st.session_state.custom_metrics) == 0:
            st.info("No metrics added yet. Add at least 1 metric.")
        else:
            for i, metric_config in enumerate(st.session_state.custom_metrics):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.text(metric_config["stat"][:30])  # Truncate long names
                with col2:
                    st.text(f"Weight: {metric_config['weight']:.2f}")
                with col3:
                    if st.button("🗑️", key=f"remove_metric_{i}"):
                        st.session_state.custom_metrics.pop(i)
                        st.rerun()

        st.markdown("---")

        # Summary
        total_weight = sum(abs(m["weight"]) for m in st.session_state.custom_metrics)
        st.metric("Total Metrics", len(st.session_state.custom_metrics))
        st.metric("Total Weight (abs)", f"{total_weight:.2f}")

        # Clear all button
        if st.button("🔄 Clear All Metrics", key="clear_all_metrics"):
            st.session_state.custom_metrics = []
            st.rerun()

    # Return preset configuration
    if len(st.session_state.custom_metrics) == 0:
        return None

    return {
        "display_name": preset_name,
        "description": preset_description,
        "components": st.session_state.custom_metrics,
        "icon": "🎯",  # Default icon for custom presets
    }

def get_relevant_presets(df_filtered):
    """
    Get relevant presets based on position groups present in filtered data

    Args:
        df_filtered: Filtered player dataframe

    Returns:
        Dict of relevant presets
    """
    # Check what positions are in filtered data
    positions_in_data = df_filtered["Position"].unique()

    # Get position groups
    cf_positions = POSITION_GROUPS.get("CF", [])
    winger_positions = POSITION_GROUPS.get("Winger", [])
    am_positions = POSITION_GROUPS.get("AM", [])
    defender_positions = POSITION_GROUPS.get("Defender", [])
    fullback_positions = POSITION_GROUPS.get("Fullback", [])
    dm_positions = POSITION_GROUPS.get("DM", [])
    all_forward_positions = cf_positions + winger_positions + am_positions

    # Determine what positions are present
    has_strikers = any(pos in positions_in_data for pos in cf_positions)
    has_wingers = any(pos in positions_in_data for pos in winger_positions)
    has_am = any(pos in positions_in_data for pos in am_positions)
    has_defenders = any(pos in positions_in_data for pos in defender_positions)
    has_fullbacks = any(pos in positions_in_data for pos in fullback_positions)
    has_dms = any(pos in positions_in_data for pos in dm_positions)
    has_forwards = has_strikers or has_wingers or has_am

    # Build relevant presets dict
    all_presets = {}

    if has_defenders:
        all_presets.update(DEFENDER_PRESETS)

    if has_fullbacks:
        all_presets.update(FULLBACK_PRESETS)

    if has_dms:
        all_presets.update(MIDFIELDER_PRESETS)

    if has_am:
        all_presets.update(MIDFIELDER_PRESETS)
        all_presets.update(ATTACKING_MIDFIELDER_PRESETS)

    if has_forwards:
        # Include all forward and AM presets
        all_presets.update(FORWARD_PRESETS)
        all_presets.update(ATTACKING_MIDFIELDER_PRESETS)

    # If no positions detected, return all presets as fallback
    if not all_presets:
        all_presets.update(DEFENDER_PRESETS)
        all_presets.update(FULLBACK_PRESETS)
        all_presets.update(MIDFIELDER_PRESETS)
        all_presets.update(FORWARD_PRESETS)
        all_presets.update(ATTACKING_MIDFIELDER_PRESETS)

    return all_presets
