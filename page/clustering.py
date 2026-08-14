import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from config.stat_categories import STAT_CATEGORIES

def render_clustering_analysis_page(df_filtered, selected_position_group):
    """
    K-Means clustering analysis to identify player archetypes within position groups.
    Uses PCA for 2D visualization and elbow method for optimal cluster determination.
    """
    st.header("K-Means Clustering Analysis")

    if len(df_filtered) == 0:
        st.warning("⚠️ No players match the selected filters. Adjust global filters in sidebar.")
        return

    st.markdown("Identify player archetypes using unsupervised machine learning. Group similar players based on statistical profiles.")
    
    # Configuration
    st.markdown("---")
    st.markdown("### ⚙️ Clustering Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        if "Age" in df_filtered.columns:
            min_age_df = int(df_filtered["Age"].min())
            max_age_df = int(df_filtered["Age"].max())
            age_range = st.slider("Age Range:", min_value=min_age_df, max_value=max_age_df, value=(22, 35), key="clustering_age_range")
        else:
            age_range = (18, 40)
    with col2:
        if "Minutes played" in df_filtered.columns:
            min_minutes = st.number_input("Minimum Minutes Played:", min_value=0, max_value=int(df_filtered["Minutes played"].max()), value=900, step=100, key="clustering_min_minutes")
        else:
            min_minutes = 0

    df_analysis = df_filtered[(df_filtered["Age"] >= age_range[0]) & (df_filtered["Age"] <= age_range[1]) & (df_filtered["Minutes played"] >= min_minutes)].copy()

    if len(df_analysis) == 0:
        st.warning("⚠️ No players match the filters. Try adjusting values.")
        return

    st.info(f"📊 {len(df_analysis)} players available for clustering")

    # Features
    available_features = []
    for cat, stats in STAT_CATEGORIES.items():
        available_features.extend([s["column"] for s in stats["stats"] if s["column"] in df_analysis.columns and "per 90" in s["column"]])
    available_features.extend([c for c in df_analysis.columns if c.startswith("COMP_")])
    available_features = sorted(list(set(available_features)))

    # --- Feature Presets ---
    FEATURE_PRESETS = {
        "Custom (manual)": [],
        "CB / Centre-Back": [
            "Defensive duels per 90", "Defensive duels won, %",
            "Aerial duels per 90", "Aerial duels won, %",
            "Interceptions per 90", "Sliding tackles per 90",
            "Shots blocked per 90", "Successful defensive actions per 90",
            "Passes per 90", "Accurate passes, %",
            "Forward passes per 90", "Long passes per 90",
            "Progressive passes per 90",
        ],
        "FB / Wing-Back": [
            "Defensive duels per 90", "Defensive duels won, %",
            "Interceptions per 90", "Successful defensive actions per 90",
            "Crosses per 90", "Accurate crosses, %",
            "Dribbles per 90", "Successful dribbles, %",
            "Progressive runs per 90", "Accelerations per 90",
            "Passes to final third per 90", "Key passes per 90",
            "Shot assists per 90",
        ],
        "CM / DM (Midfielder)": [
            "Passes per 90", "Accurate passes, %",
            "Forward passes per 90", "Progressive passes per 90",
            "Key passes per 90", "Shot assists per 90",
            "Defensive duels per 90", "Interceptions per 90",
            "Duels per 90", "Duels won, %",
            "Dribbles per 90", "Successful dribbles, %",
            "Long passes per 90", "Accurate long passes, %",
        ],
        "AM / Winger": [
            "Goals per 90", "xG per 90", "Assists per 90", "xA per 90",
            "Shots per 90", "Dribbles per 90", "Successful dribbles, %",
            "Key passes per 90", "Shot assists per 90",
            "Crosses per 90", "Accurate crosses, %",
            "Progressive runs per 90", "Accelerations per 90",
            "Touches in box per 90", "Offensive duels per 90",
        ],
        "ST / CF (Striker)": [
            "Goals per 90", "Non-penalty goals per 90", "xG per 90",
            "Shots per 90", "Shots on target, %", "Head goals per 90",
            "Assists per 90", "xA per 90",
            "Dribbles per 90", "Offensive duels per 90", "Offensive duels won, %",
            "Aerial duels per 90", "Aerial duels won, %",
            "Touches in box per 90", "Received passes per 90",
        ],
        "Forward" : ['xG per 90', 'Assists per 90', 'xA per 90', 'Shots per 90', 'Dribbles per 90', 'Key passes per 90', 'Shot assists per 90', 'Crosses per 90', 'Progressive runs per 90', 'Accelerations per 90', 'Touches in box per 90', 'Offensive duels per 90', 'Smart passes per 90', 'Deep completions per 90', 'Aerial duels per 90', 'Passes to penalty area per 90'],
        "GK / Goalkeeper": [
            "Save rate, %",
            "Prevented goals per 90",
            "Conceded goals per 90",
            "xG against per 90",
            "Exits per 90",
            "Aerial duels per 90",
            "Aerial duels won, %",
            "Back passes received as GK per 90",
            "Accurate passes, %",
            "Accurate long passes, %",
            "Long passes per 90",
            "Progressive passes per 90",
        ],
    }

    def _on_preset_change():
        """Write preset features into multiselect session state."""
        print(f"preset changes...")
        chosen = st.session_state.get("clustering_preset", "Custom (manual)")
        filtered = [f for f in FEATURE_PRESETS.get(chosen, []) if f in available_features]
        st.session_state["clustering_features"] = filtered

    print(f"available_features : {available_features}")
    preset_choice = st.selectbox(
        "📋 Feature Preset:",
        list(FEATURE_PRESETS.keys()),
        index=0,
        key="clustering_preset",
        help="Pick a preset to auto-fill features for a position archetype, then adjust as needed.",
        on_change=_on_preset_change,
    )
    print(f"preset_choice : {preset_choice}")

    # Filter preset features to only those available in current data
    preset_defaults = [f for f in FEATURE_PRESETS[preset_choice] if f in available_features]
    print(f"preset_defaults : {preset_defaults}")
    feature_cols = st.multiselect(
        "Select Features for Clustering:",
        available_features,
        default=preset_defaults,
        key="clustering_features",
    )

    if len(feature_cols) < 5:
        st.warning("⚠️ Please select at least 5 features.")
        return

    scaling_method = st.radio("Normalization Method:", options=["StandardScaler", "MinMaxScaler"], index=0, key="clustering_scaling", horizontal=True)

    print(f"feature_cols : {feature_cols}")
    if st.button("▶️ Run Clustering Analysis", type="primary"):
        with st.spinner("Calculating..."):
            # Include League and player info in the data pipeline
            meta_cols = ["Player", "Team", "Age", "Position", "Minutes played"]
            extra_info_cols = ["League", "Contract expires", "Passport country", "Foot", "Height", "Weight", "Market value"]
            for col in extra_info_cols:
                if col in df_analysis.columns:
                    meta_cols.append(col)
            
            df_clean = df_analysis[meta_cols + feature_cols].dropna()
            if len(df_clean) < 10:
                st.error("❌ Not enough data after removing NaNs.")
                return
            X = df_clean[feature_cols].values
            scaler = StandardScaler() if scaling_method == "StandardScaler" else MinMaxScaler()
            X_scaled = scaler.fit_transform(X)
            
            wcss = []
            k_range = range(2, 11)
            for k in k_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(X_scaled)
                wcss.append(kmeans.inertia_)
            
            pca = PCA(n_components=2, random_state=42)
            X_pca = pca.fit_transform(X_scaled)
            
            st.session_state["clustering_results"] = {
                "df_clean": df_clean, "X_scaled": X_scaled, "X_pca": X_pca,
                "pca": pca, "feature_cols": feature_cols, "wcss": wcss,
                "k_range": list(k_range), "scaling_method": scaling_method
            }

    if "clustering_results" in st.session_state:
        results = st.session_state["clustering_results"]
        
        # Elbow plot
        fig_elbow, ax_elbow = plt.subplots(figsize=(10, 4))
        ax_elbow.plot(results["k_range"], results["wcss"], marker="o")
        ax_elbow.set_title("Elbow Method")
        st.pyplot(fig_elbow)
        plt.close(fig_elbow)

        n_clusters = st.slider("Select Number of Clusters (k):", 2, 10, 5, key="clustering_n_clusters")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(results["X_scaled"])
        
        df_res = results["df_clean"].copy()
        df_res["Cluster"] = cluster_labels.astype(str)
        df_res["PC1"] = results["X_pca"][:, 0]
        df_res["PC2"] = results["X_pca"][:, 1]

        # Visualization
        tab1, tab2, tab3, tab4 = st.tabs(["2D Projection", "Cluster Stats", "Player Table", "How to Interpret"])
        
        with tab1:
            # Optional opacity highlight by Club or League
            hl_col1, hl_col2 = st.columns(2)
            with hl_col1:
                if "Team" in df_res.columns:
                    all_clubs = sorted(df_res["Team"].dropna().unique().tolist())
                    highlight_clubs = st.multiselect("🏟️ Highlight Clubs (opacity):", all_clubs, default=[], key="clustering_hl_clubs")
                else:
                    highlight_clubs = []
            with hl_col2:
                if "League" in df_res.columns:
                    all_leagues = sorted(df_res["League"].dropna().unique().tolist())
                    highlight_leagues = st.multiselect("🏆 Highlight Leagues (opacity):", all_leagues, default=[], key="clustering_hl_leagues")
                else:
                    highlight_leagues = []
            
            # Calculate opacity per player
            if highlight_clubs or highlight_leagues:
                mask = pd.Series(False, index=df_res.index)
                if highlight_clubs:
                    mask = mask | df_res["Team"].isin(highlight_clubs)
                if highlight_leagues and "League" in df_res.columns:
                    mask = mask | df_res["League"].isin(highlight_leagues)
                df_res["_opacity"] = mask.map({True: 1.0, False: 0.15})
            else:
                df_res["_opacity"] = 1.0
            
            # Toggle to show only expiring contract labels
            hide_non_expiring = st.toggle("🔴 Show only expiring contract names (before 31/08/2026)", value=False, key="clustering_hide_non_expiring")
            
            # Determine text color per player (dark red if contract expires before 31/08/2026)
            contract_cutoff = datetime(2026, 8, 31)
            def _is_expiring(row):
                if "Contract expires" not in row.index or pd.isna(row.get("Contract expires")):
                    return False
                try:
                    contract_str = str(row["Contract expires"]).strip()
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%b %d, %Y", "%d %b %Y", "%d.%m.%Y"):
                        try:
                            dt = datetime.strptime(contract_str, fmt)
                            return dt < contract_cutoff
                        except ValueError:
                            continue
                    return False
                except Exception:
                    return False
            
            df_res["_expiring"] = df_res.apply(_is_expiring, axis=1)
            df_res["_text_color"] = df_res["_expiring"].map({True: "#633333", False: "#CCCCCC"})
            # If toggle is on, blank out non-expiring player labels
            df_res["_label"] = df_res.apply(
                lambda r: r["Player"] if (r["_expiring"] or not hide_non_expiring) else "",
                axis=1
            )
            
            # Plotly scatter — always colored by Cluster, opacity by highlight
            hover_cols = ["Player", "Team", "Age", "Cluster"]
            if "League" in df_res.columns:
                hover_cols.append("League")
            if "Contract expires" in df_res.columns:
                hover_cols.append("Contract expires")
            
            fig = px.scatter(
                df_res,
                x="PC1",
                y="PC2",
                color="Cluster",
                text="_label",
                hover_data=hover_cols,
                title="2D PCA Projection — Colored by Cluster",
                labels={"PC1": f"PC1 ({results['pca'].explained_variance_ratio_[0]:.1%} var.)",
                        "PC2": f"PC2 ({results['pca'].explained_variance_ratio_[1]:.1%} var.)"},
            )
            fig.update_traces(
                textposition="top center",
                textfont_size=9,
                marker=dict(size=10, line=dict(width=0.5, color="DarkSlateGrey")),
            )
            # Apply per-point opacity and text color
            for trace in fig.data:
                trace_players = trace.customdata if trace.customdata is not None else []
                trace_labels = trace.text if trace.text is not None else []
                opacities = []
                text_colors = []
                for i, label in enumerate(trace_labels):
                    # Get player name from customdata (first column = Player)
                    player_name = trace_players[i][0] if i < len(trace_players) else label
                    row = df_res[df_res["Player"] == player_name]
                    if not row.empty:
                        opacities.append(row["_opacity"].iloc[0])
                        text_colors.append(row["_text_color"].iloc[0])
                    else:
                        opacities.append(1.0)
                        text_colors.append("#CCCCCC")
                if opacities:
                    trace.marker.opacity = opacities
                if text_colors:
                    trace.textfont = dict(color=text_colors, size=9)
            
            fig.update_layout(
                plot_bgcolor="#f5f5f5",
                paper_bgcolor="#ffffff",
                height=650,
                legend_title_text="Cluster",
                font=dict(family="Inter, sans-serif", color="#111111"),
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.dataframe(df_res.groupby("Cluster")[results["feature_cols"]].mean().round(2))
        
        with tab3:
            st.markdown("### 📋 Players per Cluster")
            # Build display table with player info + cluster + feature values
            info_cols = ["Player", "Team", "Position", "Age", "Passport country", "Foot", "Height", "Weight", "Contract expires", "Market value"]
            display_info = [c for c in info_cols if c in df_res.columns]
            display_cols = display_info + ["Cluster"] + results["feature_cols"]
            df_table = df_res[display_cols].sort_values(["Cluster", "Player"]).reset_index(drop=True)
            
            # Cluster filter
            all_clusters = sorted(df_table["Cluster"].unique(), key=lambda x: int(x))
            selected_clusters = st.multiselect(
                "Filter by Cluster:", all_clusters, default=all_clusters, key="clustering_table_filter"
            )
            df_table_filtered = df_table[df_table["Cluster"].isin(selected_clusters)]
            st.markdown(f"**{len(df_table_filtered)}** players across **{len(selected_clusters)}** cluster(s)")
            st.dataframe(df_table_filtered, use_container_width=True, height=600)
        
        with tab4:
            st.markdown("### 📖 Cluster Interpretation")
            st.markdown("Dynamic analysis of each cluster based on the selected features.")
            
            # Calculate overall means for comparison
            feature_cols = results["feature_cols"]
            overall_mean = df_res[feature_cols].mean()
            cluster_means = df_res.groupby("Cluster")[feature_cols].mean()
            
            # Generate per-cluster interpretation
            for cluster_id in sorted(df_res["Cluster"].unique(), key=lambda x: int(x)):
                cluster_data = df_res[df_res["Cluster"] == cluster_id]
                cluster_avg = cluster_means.loc[cluster_id]
                
                # Calculate deviation from overall mean (z-score-like)
                diff_from_mean = cluster_avg - overall_mean
                top_strengths = diff_from_mean.nlargest(5)
                top_weaknesses = diff_from_mean.nsmallest(5)
                
                # Player list
                players_in_cluster = cluster_data[["Player", "Team"]].values.tolist()
                
                with st.expander(f"🔹 Cluster {cluster_id}  — {len(cluster_data)} players", expanded=True):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**💪 Top Strengths** _(above average)_")
                        for feat, val in top_strengths.items():
                            if val > 0:
                                clean_name = feat.replace(" per 90", "/90").replace("COMP_", "⭐ ")
                                st.markdown(f"- **{clean_name}**: +{val:.2f}")
                            else:
                                st.markdown(f"_No features significantly above average_")
                                break
                    
                    with col_b:
                        st.markdown("**📉 Top Weaknesses** _(below average)_")
                        for feat, val in top_weaknesses.items():
                            if val < 0:
                                clean_name = feat.replace(" per 90", "/90").replace("COMP_", "⭐ ")
                                st.markdown(f"- **{clean_name}**: {val:.2f}")
                            else:
                                st.markdown(f"_No features significantly below average_")
                                break
                    
                    # League/Club composition
                    comp_cols = st.columns(2)
                    with comp_cols[0]:
                        if "League" in cluster_data.columns:
                            league_counts = cluster_data["League"].value_counts()
                            st.markdown("**🏆 League Composition**")
                            for league, count in league_counts.items():
                                st.markdown(f"- {league}: {count} players")
                    with comp_cols[1]:
                        club_counts = cluster_data["Team"].value_counts().head(5)
                        st.markdown("**🏟️ Top Clubs**")
                        for club, count in club_counts.items():
                            st.markdown(f"- {club}: {count}")
                    
                    # Player list
                    st.markdown("**👥 Players**")
                    player_str = ", ".join([f"{p[0]} ({p[1]})" for p in players_in_cluster])
                    st.caption(player_str)
            
            # General reading guide
            with st.expander("ℹ️ How to read the 2D Projection", expanded=False):
                st.markdown("""
- **PCA** compresses all features into 2 axes. PC1 = greatest variance, PC2 = second greatest.
- **Players close together** share similar statistical profiles.
- **Tight clusters** = strong archetype. **Spread-out clusters** = diverse group.
- **Overlap** between clusters means borderline players.
- Use the **Elbow Method** chart to find the optimal k (where the curve bends).
""")
