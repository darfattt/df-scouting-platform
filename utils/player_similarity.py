"""
Player similarity calculation using multiple similarity methods
Supports: Cosine Similarity, Euclidean Distance, and Pearson Correlation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import requests
from io import BytesIO
from styles.design_system import CANVAS, SOFT_CLOUD, INK, MUTE, SUCCESS, apply_nike_style
from datetime import datetime


class SimilarityScorer:
    """
    Calculate player-to-player similarity using weighted metrics
    """

    def __init__(
        self,
        df: pd.DataFrame,
        stat_columns: List[str],
        composite_columns: List[str] = None,
    ):
        """
        Initialize scorer with dataset

        Args:
            df: Player dataframe with all statistics
            stat_columns: List of metric columns to use for similarity
            composite_columns: List of composite attribute columns (e.g., COMP_Security)
        """
        self.df = df.copy()
        # Deduplicate by Wyscout id to prevent the same player appearing multiple times
        # when data is loaded from multiple league CSV files. Keep row with most minutes.
        if "Wyscout id" in self.df.columns:
            if "Minutes" in self.df.columns:
                self.df = (
                    self.df.sort_values("Minutes", ascending=False)
                    .drop_duplicates(subset=["Wyscout id"], keep="first")
                )
            else:
                self.df = self.df.drop_duplicates(subset=["Wyscout id"], keep="first")
        self.stat_columns = stat_columns
        self.composite_columns = composite_columns if composite_columns else []
        self.all_selectable_columns = stat_columns + self.composite_columns
        self.negative_metrics = [
            "Fouls per 90",
            "Cards per 90",
            "Conceded goals per 90",
        ]  # Metrics where lower is better

    def calculate_similarity(
        self,
        reference_player_name: str,
        weights: Dict[str, float],
        method: str = "cosine",
        min_minutes: int = 0,
        age_range: Tuple[int, int] = (15, 40),
        league_weights: Dict[str, float] = None,
        same_position_only: bool = True,
    ) -> pd.DataFrame:
        """
        Find most similar players to reference player using specified method

        Args:
            reference_player_name: Name of reference player
            method: Similarity method - 'cosine', 'euclidean', or 'pearson' (default: 'cosine')
            weights: Dictionary of {metric: weight} for similarity calculation
            min_minutes: Minimum minutes played filter
            age_range: (min_age, max_age) tuple
            league_weights: Dictionary of {league: multiplier} for weighting leagues
            same_position_only: If True, only compare to players in same position

        Returns:
            DataFrame with all similar players sorted by score (top N applied at display layer)
        """
        # STEP 0: Validate method
        if method not in ["cosine", "euclidean", "pearson"]:
            raise ValueError(
                f"Unknown method: '{method}'. Use 'cosine', 'euclidean', or 'pearson'"
            )

        # STEP 1: Get reference player
        ref_player = self.df[self.df["Player"] == reference_player_name]
        if len(ref_player) == 0:
            raise ValueError(f"Player '{reference_player_name}' not found")
        ref_player = ref_player.iloc[0]

        # STEP 2: Apply filters to candidate pool
        candidates = self.df.copy()

        # Exclude reference player from candidates
        candidates = candidates[candidates["Player"] != reference_player_name]

        # Minutes filter (if Minutes column exists)
        if "Minutes" in candidates.columns:
            candidates = candidates[candidates["Minutes"] >= min_minutes]

        # Age filter
        if "Age" in candidates.columns:
            min_age, max_age = age_range
            candidates = candidates[
                (candidates["Age"] >= min_age) & (candidates["Age"] <= max_age)
            ]

        # Same position filter
        if same_position_only and "Position" in candidates.columns:
            ref_position = ref_player["Position"]
            candidates = candidates[candidates["Position"] == ref_position]

        # Deduplicate by Wyscout id (keep highest minutes among duplicates)
        if "Wyscout id" in candidates.columns:
            if "Minutes" in candidates.columns:
                candidates = (
                    candidates.sort_values("Minutes", ascending=False)
                    .drop_duplicates(subset=["Wyscout id"], keep="first")
                )
            else:
                candidates = candidates.drop_duplicates(subset=["Wyscout id"], keep="first")

        if len(candidates) == 0:
            # Return empty dataframe with expected columns
            return pd.DataFrame(
                columns=[
                    "Rank",
                    "Player",
                    "Team",
                    "Position",
                    "Age",
                    "Similarity_Score",
                    "Similarity_Percentile",
                ]
            )

        # STEP 3: Filter weights to only valid metrics
        valid_weights = {
            k: v
            for k, v in weights.items()
            if k in self.all_selectable_columns and k in candidates.columns
        }

        if not valid_weights:
            raise ValueError("No valid metrics found for similarity calculation")

        # Normalize weights to sum to 1.0
        total_weight = sum(abs(w) for w in valid_weights.values())
        normalized_weights = {k: v / total_weight for k, v in valid_weights.items()}

        # STEP 4: Calculate weighted similarity
        metric_names = list(normalized_weights.keys())

        # Extract and normalize metric values
        ref_vector = []
        candidate_vectors = []

        for metric in metric_names:
            # Get values
            ref_val = ref_player[metric]
            cand_vals = candidates[metric].values

            # Handle NaN
            if pd.isna(ref_val):
                ref_val = 0
            cand_vals = np.nan_to_num(cand_vals, 0)

            # Normalize to 0-100 scale for consistency
            all_vals = np.append(cand_vals, ref_val)
            val_min = all_vals.min()
            val_max = all_vals.max()

            if val_max == val_min:
                ref_normalized = 50.0
                cand_normalized = np.full(len(cand_vals), 50.0)
            else:
                # Invert for negative metrics
                if metric in self.negative_metrics:
                    ref_normalized = 100 - (
                        (ref_val - val_min) / (val_max - val_min) * 100
                    )
                    cand_normalized = 100 - (
                        (cand_vals - val_min) / (val_max - val_min) * 100
                    )
                else:
                    ref_normalized = (ref_val - val_min) / (val_max - val_min) * 100
                    cand_normalized = (cand_vals - val_min) / (val_max - val_min) * 100

            # Apply weight
            weight = normalized_weights[metric]
            ref_vector.append(ref_normalized * weight)
            candidate_vectors.append(cand_normalized * weight)

        # Convert to numpy arrays
        ref_vector = np.array(ref_vector).reshape(1, -1)
        candidate_matrix = np.array(candidate_vectors).T

        # Calculate similarity using selected method
        if method == "cosine":
            similarities = self._cosine_similarity(ref_vector, candidate_matrix)
        elif method == "euclidean":
            similarities = self._euclidean_similarity(ref_vector, candidate_matrix)
        elif method == "pearson":
            similarities = self._pearson_similarity(ref_vector, candidate_matrix)

        # STEP 5: Apply league weights if provided
        if league_weights and "League" in candidates.columns:
            league_multipliers = (
                candidates["League"].map(league_weights).fillna(1.0).values
            )
            similarities = similarities * league_multipliers

        # STEP 6: Add similarity scores to candidates
        candidates = candidates.copy()
        candidates["Similarity_Score"] = similarities

        # Calculate percentile (avoid division by zero)
        max_sim = similarities.max()
        if max_sim > 0:
            candidates["Similarity_Percentile"] = similarities / max_sim * 100
        else:
            candidates["Similarity_Percentile"] = 50.0

        # STEP 7: Sort by similarity score (top N applied at display layer)
        result = candidates.sort_values("Similarity_Score", ascending=False)
        result["Rank"] = range(1, len(result) + 1)

        # Select relevant columns
        display_cols = [
            "Rank",
            "Player",
            "Full name",
            "Team",
            "Position",
            "Age",
            "Passport country",
            "Foot",
            "Height",
            "Weight",
            "Contract expires",
            "Market value",
            "Matches played",
            "Similarity_Score",
            "Similarity_Percentile",
        ] + metric_names

        # Remove duplicates while preserving order
        display_cols = list(dict.fromkeys(display_cols))

        # Filter to only existing columns
        display_cols = [col for col in display_cols if col in result.columns]

        return result[display_cols].reset_index(drop=True)

    def _cosine_similarity(self, reference_vector, comparison_matrix):
        """
        Calculate cosine similarity between reference player and comparison players

        Args:
            reference_vector: 2D array (1, n_features) - weighted reference player stats
            comparison_matrix: 2D array (n_players, n_features) - weighted comparison players stats

        Returns:
            1D array of similarity scores (0-1 range, 1=most similar)
        """
        similarities = cosine_similarity(reference_vector, comparison_matrix)[0]
        return similarities

    def _euclidean_similarity(self, reference_vector, comparison_matrix):
        """
        Calculate Euclidean distance and convert to similarity score

        Distance is inverse of similarity:
        - distance=0 → similarity=1.0 (identical players)
        - distance=∞ → similarity≈0 (completely different)

        Conversion formula: similarity = 1 / (1 + distance)

        Args:
            reference_vector: 2D array (1, n_features) - weighted reference player stats
            comparison_matrix: 2D array (n_players, n_features) - weighted comparison players stats

        Returns:
            1D array of similarity scores (0-1 range, 1=most similar)
        """
        distances = euclidean_distances(reference_vector, comparison_matrix)[0]
        # Convert distance to similarity (0-1 range)
        # The +1 prevents division by zero for identical players
        similarities = 1 / (1 + distances)
        return similarities

    def _pearson_similarity(self, reference_vector, comparison_matrix):
        """
        Calculate Pearson correlation and rescale to 0-1 range

        Correlation range is [-1, 1], rescaled to [0, 1]:
        - correlation=1 → similarity=1.0 (perfect positive correlation)
        - correlation=0 → similarity=0.5 (no correlation)
        - correlation=-1 → similarity=0.0 (perfect negative correlation)

        Rescale formula: similarity = (correlation + 1) / 2

        Args:
            reference_vector: 2D array (1, n_features) - weighted reference player stats
            comparison_matrix: 2D array (n_players, n_features) - weighted comparison players stats

        Returns:
            1D array of similarity scores (0-1 range, 1=most similar)
        """
        reference_1d = reference_vector.flatten()
        correlations = []

        for comparison in comparison_matrix:
            # Handle edge case: constant values (std=0)
            if np.std(reference_1d) == 0 or np.std(comparison) == 0:
                # No variation = cannot compute correlation
                # Assign neutral similarity (0.5)
                correlations.append(0.5)
                continue

            try:
                corr, _ = pearsonr(reference_1d, comparison)

                # Handle NaN (shouldn't happen with std check, but defensive)
                if np.isnan(corr):
                    correlations.append(0.5)
                else:
                    # Rescale from [-1, 1] to [0, 1]
                    similarity = (corr + 1) / 2
                    correlations.append(similarity)
            except Exception:
                # Fallback for any unexpected errors
                correlations.append(0.5)

        return np.array(correlations)

    def get_metric_contributions(
        self,
        reference_player_name: str,
        similar_player_name: str,
        weights: Dict[str, float],
    ) -> Dict[str, Dict]:
        """
        Get detailed metric breakdown for why two players are similar

        Args:
            reference_player_name: Reference player
            similar_player_name: Player to compare to
            weights: Metric weights used

        Returns:
            Dictionary with metric-by-metric comparison
        """
        ref_player = self.df[self.df["Player"] == reference_player_name].iloc[0]
        sim_player = self.df[self.df["Player"] == similar_player_name].iloc[0]

        contributions = {}

        for metric, weight in weights.items():
            if metric not in self.stat_columns or metric not in self.df.columns:
                continue

            ref_val = ref_player[metric]
            sim_val = sim_player[metric]

            # Handle NaN values
            if pd.isna(ref_val):
                ref_val = 0
            if pd.isna(sim_val):
                sim_val = 0

            # Calculate difference
            diff = abs(ref_val - sim_val)

            # Calculate similarity for this metric (1 - normalized difference)
            max_diff = self.df[metric].max() - self.df[metric].min()
            if max_diff > 0:
                metric_similarity = 1 - (diff / max_diff)
            else:
                metric_similarity = 1.0

            # Ensure similarity is in valid range
            metric_similarity = max(0, min(1, metric_similarity))

            contributions[metric] = {
                "reference_value": ref_val,
                "similar_value": sim_val,
                "difference": diff,
                "metric_similarity": metric_similarity * 100,  # 0-100 scale
                "weight": weight,
                "weighted_contribution": metric_similarity * abs(weight) * 100,
            }

        return contributions

    def get_composite_contributions(
        self,
        reference_player_name: str,
        similar_player_name: str,
        weights: Dict[str, float],
        composite_attributes: Dict,
    ) -> Dict[str, Dict]:
        """
        Get detailed composite attribute breakdown for similarity comparison

        Similar to get_metric_contributions() but for composite attributes (COMP_* columns)

        Args:
            reference_player_name: Reference player name
            similar_player_name: Player to compare against
            weights: Metric weights dict (should include COMP_* keys)
            composite_attributes: COMPOSITE_ATTRIBUTES config from config/composite_attributes.py

        Returns:
            Dictionary with composite-by-composite comparison:
            {
                'COMP_Tackling': {
                    'display_name': '🛡️ Tackling',
                    'reference_value': 85.2,
                    'similar_value': 82.7,
                    'difference': 2.5,
                    'metric_similarity': 92.3,  # 0-100 scale
                    'weight': 0.25,
                    'weighted_contribution': 23.075
                },
                ...
            }
        """
        # STEP 1: Get both players from DataFrame
        ref_player = self.df[self.df["Player"] == reference_player_name]
        sim_player = self.df[self.df["Player"] == similar_player_name]

        if len(ref_player) == 0:
            raise ValueError(f"Reference player '{reference_player_name}' not found")
        if len(sim_player) == 0:
            raise ValueError(f"Similar player '{similar_player_name}' not found")

        ref_player = ref_player.iloc[0]
        sim_player = sim_player.iloc[0]

        contributions = {}

        # STEP 2: Filter weights to only composite attributes
        composite_weights = {k: v for k, v in weights.items() if k.startswith("COMP_")}

        if not composite_weights:
            return {}  # No composite attributes selected

        # STEP 3: Calculate contribution for each composite attribute
        for comp_col, weight in composite_weights.items():
            # Extract attribute key: COMP_Tackling → Tackling
            attr_key = comp_col.replace("COMP_", "")

            # Verify column exists in DataFrame
            if comp_col not in self.df.columns:
                continue

            # Get values for both players
            ref_val = ref_player[comp_col]
            sim_val = sim_player[comp_col]

            # Handle NaN (use percentile=50 as default)
            if pd.isna(ref_val):
                ref_val = 50.0
            if pd.isna(sim_val):
                sim_val = 50.0

            # Calculate absolute difference
            diff = abs(ref_val - sim_val)

            # Calculate metric similarity (1 - normalized difference)
            # PATTERN: Same as get_metric_contributions() lines 218-222
            max_diff = self.df[comp_col].max() - self.df[comp_col].min()
            if max_diff > 0:
                metric_similarity = 1 - (diff / max_diff)
            else:
                metric_similarity = 1.0  # No variance in dataset

            # Clamp to [0, 1] range
            metric_similarity = max(0, min(1, metric_similarity))

            # Get display metadata from composite_attributes config
            attr_config = composite_attributes.get(attr_key, {})
            display_name = attr_config.get("display_name", attr_key)
            icon = attr_config.get("icon", "")

            # Store contribution data
            contributions[comp_col] = {
                "display_name": f"{icon} {display_name}".strip(),
                "reference_value": float(ref_val),
                "similar_value": float(sim_val),
                "difference": float(diff),
                "metric_similarity": float(
                    metric_similarity * 100
                ),  # Convert to percentage
                "weight": float(weight),
                "weighted_contribution": float(metric_similarity * abs(weight) * 100),
            }

        return contributions

    def get_all_composite_contributions(
        self,
        reference_player_name: str,
        similar_player_name: str,
        composite_attributes: Dict,
    ) -> Dict[str, Dict]:
        """
        Get ALL composite attribute contributions (not filtered by weights)

        Args:
            reference_player_name: Reference player name
            similar_player_name: Player to compare against
            composite_attributes: COMPOSITE_ATTRIBUTES config from config/composite_attributes.py

        Returns:
            Dictionary with ALL composite-by-composite comparison
        """
        ref_player = self.df[self.df["Player"] == reference_player_name]
        sim_player = self.df[self.df["Player"] == similar_player_name]

        if len(ref_player) == 0:
            raise ValueError(f"Reference player '{reference_player_name}' not found")
        if len(sim_player) == 0:
            raise ValueError(f"Similar player '{similar_player_name}' not found")

        ref_player = ref_player.iloc[0]
        sim_player = sim_player.iloc[0]

        contributions = {}

        for attr_key, attr_config in composite_attributes.items():
            comp_col = f"COMP_{attr_key}"

            if comp_col not in self.df.columns:
                continue

            ref_val = ref_player[comp_col]
            sim_val = sim_player[comp_col]

            ref_val = 50.0 if pd.isna(ref_val) else float(ref_val)
            sim_val = 50.0 if pd.isna(sim_val) else float(sim_val)

            diff = abs(ref_val - sim_val)
            max_diff = self.df[comp_col].max() - self.df[comp_col].min()

            if max_diff > 0:
                metric_similarity = 1 - (diff / max_diff)
            else:
                metric_similarity = 1.0

            metric_similarity = max(0, min(1, metric_similarity))

            display_name = attr_config.get("display_name", attr_key)
            icon = attr_config.get("icon", "")

            contributions[comp_col] = {
                "display_name": f"{icon} {display_name}".strip(),
                "reference_value": ref_val,
                "similar_value": sim_val,
                "difference": diff,
                "metric_similarity": float(metric_similarity * 100),
            }

        return contributions

    def compare_methods(
        self,
        reference_player_name: str,
        weights: Dict[str, float] = None,
        top_n: int = 10,
        min_minutes: int = 0,
        age_range: Tuple[int, int] = (15, 40),
        same_position_only: bool = True,
    ) -> pd.DataFrame:
        """
        Compare all three similarity methods side-by-side

        Runs cosine, euclidean, and pearson similarity calculations with identical parameters
        and returns a merged DataFrame showing how each method ranks players.

        Args:
            reference_player_name: Name of reference player
            weights: Dictionary of {metric: weight} for similarity calculation
            top_n: Number of top similar players to return per method
            min_minutes: Minimum minutes played filter
            age_range: (min_age, max_age) tuple
            same_position_only: If True, only compare to players in same position

        Returns:
            DataFrame with columns:
            - Player: Player name
            - cosine_score: Cosine similarity (0-1)
            - euclidean_score: Euclidean similarity (0-1)
            - pearson_score: Pearson similarity (0-1)
            - average_score: Mean of three scores (0-1)

            Sorted by average_score descending
        """
        results = {}

        # Run all three methods with same parameters
        for method in ["cosine", "euclidean", "pearson"]:
            result_df = self.calculate_similarity(
                reference_player_name=reference_player_name,
                weights=weights,
                method=method,
                min_minutes=min_minutes,
                age_range=age_range,
                same_position_only=same_position_only,
                top_n=top_n,
            )

            # Extract player + score columns only
            if len(result_df) > 0:
                method_results = result_df[["Player", "Similarity_Score"]].copy()
                method_results = method_results.rename(
                    columns={"Similarity_Score": f"{method}_score"}
                )
                results[method] = method_results

        # Handle case where no results for any method
        if not results:
            return pd.DataFrame(
                columns=[
                    "Player",
                    "cosine_score",
                    "euclidean_score",
                    "pearson_score",
                    "average_score",
                ]
            )

        # Merge results (outer join to capture all players across methods)
        comparison_df = results.get(
            "cosine", pd.DataFrame(columns=["Player", "cosine_score"])
        )

        if "euclidean" in results:
            comparison_df = comparison_df.merge(
                results["euclidean"], on="Player", how="outer"
            )
        else:
            comparison_df["euclidean_score"] = 0.0

        if "pearson" in results:
            comparison_df = comparison_df.merge(
                results["pearson"], on="Player", how="outer"
            )
        else:
            comparison_df["pearson_score"] = 0.0

        # Fill missing values (player not in top N for that method)
        comparison_df = comparison_df.fillna(0.0)

        # Calculate average similarity
        comparison_df["average_score"] = comparison_df[
            ["cosine_score", "euclidean_score", "pearson_score"]
        ].mean(axis=1)

        # Sort by average (most similar first)
        comparison_df = comparison_df.sort_values("average_score", ascending=False)

        return comparison_df.reset_index(drop=True)


def create_similarity_table_figure(
    comparison_df: pd.DataFrame,
    reference_player: str,
    df_filtered: pd.DataFrame,
    top_n: int = 20,
) -> plt.Figure:
    """
    Create a matplotlib figure displaying similar players in a table format with team logos

    Displays: Player | Club | Age | Cosine | Euclidean | Pearson | Average

    Args:
        comparison_df: DataFrame with similarity scores (Player, cosine_score, euclidean_score, pearson_score, average_score)
        reference_player: Name of the reference player
        df_filtered: Full DataFrame with player details (Team, Team logo, Age)
        top_n: Number of players to display

    Returns:
        matplotlib Figure object
    """
    # Merge comparison_df with full player data
    merged_df = comparison_df.head(top_n).merge(
        df_filtered[["Player", "Team", "Team logo", "Age"]], on="Player", how="left"
    )

    # Remove duplicates - keep only unique Player + Team combinations
    # This ensures each player-team pair appears only once
    merged_df = merged_df.drop_duplicates(subset=["Player", "Team"], keep="first")

    # Re-limit to top_n after deduplication
    merged_df = merged_df.head(top_n)

    # Calculate figure dimensions
    n_rows = len(merged_df)
    row_height = 0.5
    fig_height = max(8, n_rows * row_height + 2)

    # Create figure with wider width to accommodate all columns
    fig, ax = plt.subplots(figsize=(10, fig_height))
    apply_nike_style(fig, ax)

    # Remove axes
    ax.set_xlim(0, 14)
    ax.set_ylim(-n_rows - 1, 1)
    ax.axis("off")

    # Title
    title_text = f"Similar players to {reference_player}"
    ref_team = df_filtered[df_filtered["Player"] == reference_player]["Team"].values
    if len(ref_team) > 0:
        title_text += f" - {ref_team[0]}"

    ax.text(7, 0.5, title_text, fontsize=16, fontweight="bold", ha="center", va="top")
    ax.text(
        7,
        0,
        "Finding similar players: Cosine similarity, Euclidean Distance & Pearson Correlation. ",
        fontsize=10,
        ha="center",
        va="top",
        style="italic",
        color="#666",
    )

    # Column headers - Player | Club | Age | Cosine | Euclidean | Pearson | Average
    header_y = -0.8
    ax.text(
        0.5, header_y, "Player", fontsize=11, fontweight="bold", ha="left", va="bottom"
    )
    ax.text(
        4.3, header_y, "Club", fontsize=11, fontweight="bold", ha="center", va="bottom"
    )
    ax.text(
        7.5, header_y, "Age", fontsize=11, fontweight="bold", ha="center", va="bottom"
    )
    ax.text(
        9.0,
        header_y,
        "Cosine",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="bottom",
    )
    ax.text(
        10.5,
        header_y,
        "Euclidean",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="bottom",
    )
    ax.text(
        12.0,
        header_y,
        "Pearson",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="bottom",
    )
    ax.text(
        13.5,
        header_y,
        "Average",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="bottom",
    )

    # Header line
    ax.plot([0.3, 13.7], [header_y - 0.1, header_y - 0.1], "k-", linewidth=1.5)

    # Data rows
    for idx, (_, row) in enumerate(merged_df.iterrows()):
        y_pos = header_y - 0.5 - (idx * row_height)

        # Player name
        player_name = row["Player"]
        ax.text(0.5, y_pos, player_name, fontsize=10, ha="left", va="center")

        # Team name
        team_name = row["Team"] if pd.notna(row["Team"]) else "Unknown"
        ax.text(4.0, y_pos, team_name, fontsize=10, ha="left", va="center")

        # Team logo
        if pd.notna(row["Team logo"]):
            try:
                # Download and display team logo
                response = requests.get(row["Team logo"], timeout=3)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    imagebox = OffsetImage(img, zoom=0.15)
                    ab = AnnotationBbox(
                        imagebox, (3.6, y_pos), frameon=False, box_alignment=(0.5, 0.5)
                    )
                    ax.add_artist(ab)
            except:
                # If logo fails to load, skip it
                pass

        # Age
        age = int(row["Age"]) if pd.notna(row["Age"]) else "-"
        ax.text(7.5, y_pos, str(age), fontsize=10, ha="center", va="center")

        # Cosine score
        cosine_score = row["cosine_score"]
        ax.text(
            9.0, y_pos, f"{cosine_score:.2f}", fontsize=10, ha="center", va="center"
        )

        # Euclidean score
        euclidean_score = row["euclidean_score"]
        ax.text(
            10.5, y_pos, f"{euclidean_score:.2f}", fontsize=10, ha="center", va="center"
        )

        # Pearson score
        pearson_score = row["pearson_score"]
        ax.text(
            12.0, y_pos, f"{pearson_score:.2f}", fontsize=10, ha="center", va="center"
        )

        # Average score
        average_score = row["average_score"]
        ax.text(
            13.5,
            y_pos,
            f"{average_score:.2f}",
            fontsize=10,
            ha="center",
            va="center",
            fontweight="bold",
        )

    # Bottom border line
    bottom_y = header_y - 0.5 - (n_rows * row_height) + 0.25
    ax.plot([0.3, 13.7], [bottom_y, bottom_y], "k-", linewidth=1.5)

    # Footer note
    footer_y = bottom_y - 0.5
    today_date = datetime.now().strftime("%d/%m/%Y")
    # ax.text(0.5, footer_y, f"Data as of {today_date} | Data: Wyscout",
    #         fontsize=8, ha='left', va='top', color='#666')
    footer_text = (
        f"Generated at {today_date}\n"
        "Data : Wyscout via Best11Scouting\n\n"
        "Filters:\n"
        "• 1st Tier Liga Musim 25/26:\n"
        "  Inggris, Jerman, Italia, Belanda, Spanyol, Prancis,\n"
        "  Brazil, Uruguay, Argentina, Swedia, Norway, Finland, Denmark\n"
        "• Range Umur : 22 – 28\n"
        "• Posisi : Winger\n"
        "• Min Played : ≥ 500 Menit"
    )

    ax.text(
        0.01,
        footer_y,
        footer_text,
        fontsize=8,
        ha="left",
        va="top",
        color="#666",
    )
    plt.tight_layout()
    return fig
