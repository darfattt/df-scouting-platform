"""
AI Intelligence Page - Main Streamlit page with 4 tabs:
  🔧 Data Pipeline  |  🤖 ML Model  |  📊 Design  |  🧠 AI Analyst
Inspired by BaseballIQ (baseball → football adaptation)
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from config.role_definitions import get_all_roles
from config.registry import get_roles_for_position, get_responsibilities_for_position
from typing import Optional


# ── Lazy imports (graceful degradation) ──────────────────────────────────────

def import_pipeline():
    from pipeline.pipeline_runner import run_pipeline, get_pipeline_status
    from pipeline.gold_layer import load_gold, save_gold, TIER_COLORS, TIER_ORDER
    return run_pipeline, get_pipeline_status, load_gold, save_gold, TIER_COLORS, TIER_ORDER


def import_models():
    import importlib
    import models.train
    import models.predict
    importlib.reload(models.train)
    importlib.reload(models.predict)
    from models.train import train_model, get_model_status
    from models.predict import predict_dataframe, compute_shap_values, predict_player
    from models.feature_engineering import TIER_LABELS, TIER_COLORS
    return train_model, get_model_status, predict_dataframe, compute_shap_values, predict_player, TIER_LABELS, TIER_COLORS


def import_enrichment():
    from enrichment.ai_client import generate_scouting_report, is_configured
    from enrichment.prompt_templates import build_player_scouting_prompt
    return generate_scouting_report, is_configured, build_player_scouting_prompt


# ── Helper ────────────────────────────────────────────────────────────────────

BG_COLOR = "#ffffff"
ACCENT_COLORS = {"Elite": "#007d48", "Good": "#1151ff", "Average": "#0a7281", "Below Average": "#d30005"}
from styles.design_system import CANVAS, SOFT_CLOUD, INK, MUTE, HAIRLINE, SUCCESS, ALERT, INFO, apply_nike_style


def _layer_status_card(label: str, icon: str, meta: dict, col):
    """Render a pipeline layer status card in a column."""
    with col:
        if meta.get("exists"):
            st.markdown(
                f"""<div style='background:#e6f4ed;border:1px solid #007d48;border-radius:0;padding:14px'>
                <b>{icon} {label}</b><br>
                ✅ <b>{meta.get('row_count', 0):,}</b> rows · {meta.get('col_count', meta.get('col_count', '?'))} cols<br>
                <small>🕐 {meta.get('last_modified', meta.get('timestamp', 'N/A'))}</small>
                </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""<div style='background:#fce6e6;border:1px solid #d30005;border-radius:0;padding:14px'>
                <b>{icon} {label}</b><br>
                ❌ Not yet generated
                </div>""",
                unsafe_allow_html=True,
            )


# ── Tab 1: Data Pipeline ──────────────────────────────────────────────────────

def _render_pipeline_tab(df_filtered: pd.DataFrame):
    st.markdown("### 🔧 Data Engineering Pipeline")
    st.caption(
        "Runs a **Bronze → Silver → Gold** medallion architecture on your current filtered data. "
        "Inspired by production data engineering practices."
    )

    run_pipeline, get_pipeline_status, load_gold, save_gold, TIER_COLORS, TIER_ORDER = import_pipeline()

    # Status cards
    status = get_pipeline_status()
    c1, c2, c3 = st.columns(3)
    _layer_status_card("Bronze Layer", "📦", status["bronze"], c1)
    _layer_status_card("Silver Layer", "🥈", status["silver"], c2)
    _layer_status_card("Gold Layer", "🥇", status["gold"], c3)

    st.markdown("")

    # Architecture diagram
    with st.expander("📐 Architecture Overview", expanded=False):
        st.markdown("""
```
Current Filtered Data (df_filtered)
        │
        ▼
📦 BRONZE  →  Raw Parquet snapshot (immutable, timestamped)
        │      No transformations — exactly what you see in the sidebar
        ▼
🥈 SILVER  →  Cleaned + Feature Engineered Parquet
        │      Derives per-90 stats if missing, fills NaN with medians
        │      Adds team-relative z-score proxies (rolling approximation)
        ▼
🥇 GOLD    →  Aggregated Parquet with ML-ready features
               Composite score, performance tiers, position percentiles
               Input to ML Model and AI Analyst
```
        """)

    # Run pipeline button
    st.markdown("---")
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        run_clicked = st.button(
            "▶ Run Full Pipeline",
            type="primary",
            use_container_width=True,
            key="pipeline_run_btn",
        )
    with col_info:
        st.info(
            f"📊 Will process **{len(df_filtered):,} players** from your current filter selection. "
            "Takes ~5–15 seconds depending on data size."
        )

    if run_clicked:
        progress_bar = st.progress(0, text="Starting pipeline...")
        status_text = st.empty()

        def on_progress(step: int, total: int, msg: str):
            progress_bar.progress(step / total, text=msg)
            status_text.markdown(f"**{msg}**")

        # Run pipeline
        with st.spinner("Running pipeline..."):
            result = run_pipeline(df_filtered, progress_callback=on_progress)

        progress_bar.progress(1.0, text="Complete!")

        if result["overall"] == "success":
            st.success("✅ Pipeline completed successfully!")
            
            # Use ML model if exists to enrich predictions
            with st.spinner("🤖 Enriching with ML predictions..."):
                try:
                    _, get_model_status, predict_dataframe, _, _, _, _ = import_models()
                    model_meta = get_model_status(nickname="static")
                    if model_meta["exists"]:
                        df_gold = load_gold()
                        df_gold = predict_dataframe(df_gold, nickname="static")
                        save_gold(df_gold)
                        st.info("🤖 Added ML predictions and SHAP-ready features to Gold layer.")
                except Exception as e:
                    st.warning(f"⚠️ Could not run ML predictions: {e}")
            bronze = result["steps"].get("bronze", {})
            silver = result["steps"].get("silver", {})
            gold = result["steps"].get("gold", {})

            m1, m2, m3 = st.columns(3)
            m1.metric("Bronze rows", f"{bronze.get('row_count', 0):,}")
            m2.metric("Silver rows", f"{silver.get('row_count', 0):,}")
            m3.metric("Gold rows", f"{gold.get('row_count', 0):,}")

            st.balloons()
            st.rerun()
        else:
            st.error("❌ Pipeline failed.")
            for layer, res in result["steps"].items():
                if res.get("status") == "error":
                    st.code(f"{layer}: {res.get('error')}\n{res.get('trace', '')}", language="text")


# ── Tab 2: ML Model ──────────────────────────────────────────────────────────

def _render_ml_tab(df_filtered: pd.DataFrame, selected_position_group: str):
    st.markdown("### 🤖 ML Model — Player Performance Tier Prediction")
    st.caption(
        "**XGBoost** classifier predicts performance tier (Elite / Good / Average / Below Average) "
        "using per-90 stats. **SHAP** values explain each prediction."
    )

    train_model, get_model_status, predict_dataframe, compute_shap_values, predict_player, TIER_LABELS, TIER_COLORS = import_models()
    _, get_pipeline_status, load_gold, _, _ = import_pipeline()

    # Check Gold layer exists
    pipeline_status = get_pipeline_status()
    if not pipeline_status["gold"]["exists"]:
        st.warning("⚠️ Gold layer not found. Go to **Data Pipeline** tab and run the pipeline first.")
        return

    try:
        df_gold = load_gold()
    except Exception as e:
        st.error(f"Failed to load Gold layer: {e}")
        return

    # Model status
    model_meta = get_model_status(nickname="static")
    if model_meta["exists"]:
        st.success(
            f"✅ Trained model found — Accuracy: **{model_meta.get('cv_mean', 0):.1%}** (5-fold CV) "
            f"· {model_meta.get('n_samples', '?')} samples · {model_meta.get('n_features', '?')} features"
        )
    else:
        st.info("ℹ️ No trained model found. Train it below.")

    # Train button
    col_train, col_note = st.columns([1, 2])
    with col_train:
        train_clicked = st.button(
            "🎯 Train Model",
            type="primary",
            use_container_width=True,
            key="ml_train_btn",
        )
    with col_note:
        st.markdown(
            "Uses **StratifiedKFold 5-fold CV** — no data leakage. "
            "Model is saved to `data/pipeline/models/` and reused on subsequent visits."
        )

    if train_clicked:
        with st.spinner("Training XGBoost model..."):
            try:
                result = train_model(df_gold, nickname="static")
                st.success(
                    f"✅ Model trained! Accuracy: **{result['accuracy']:.1%}** "
                    f"| CV: **{result['cv_mean']:.1%} ± {result['cv_std']:.2%}** "
                    f"| {result['n_samples']:,} samples"
                )
                st.session_state["ml_train_result"] = result
                st.rerun()
            except ImportError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(f"❌ Training failed: {e}")

    if not model_meta["exists"]:
        return

    st.markdown("---")

    # Feature importance
    if "feature_names" in model_meta and model_meta["exists"]:
        try:
            result = st.session_state.get("ml_train_result")

            if result and "feature_importances" in result:
                fi = dict(zip(result["feature_names"], result["feature_importances"]))
                fi_sorted = sorted(fi.items(), key=lambda x: x[1], reverse=True)

                with st.expander("📊 Feature Importance (XGBoost)", expanded=True):
                    fig, ax = plt.subplots(figsize=(9, 4))
                    apply_nike_style(fig, ax)
                    names = [n for n, _ in fi_sorted[:12]]
                    values = [v for _, v in fi_sorted[:12]]
                    colors = [INFO] * len(names)
                    ax.barh(names[::-1], values[::-1], color=colors[::-1], edgecolor="none")
                    ax.set_xlabel("Importance Score", fontsize=9)
                    ax.set_title("Top 12 Features by XGBoost Importance", fontsize=11, fontweight="bold")
                    ax.spines["top"].set_visible(False)
                    ax.spines["right"].set_visible(False)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)
        except Exception:
            pass

    # Per-player prediction
    st.markdown("### 🔍 Player Prediction")
    player_list = sorted(df_gold["Player"].dropna().unique().tolist()) if "Player" in df_gold.columns else []
    if not player_list:
        st.warning("No players available in Gold layer.")
        return

    selected_player = st.selectbox(
        "Select a player to predict:",
        options=player_list,
        key="ml_player_select",
    )

    if st.button("🔮 Predict Tier", key="ml_predict_btn", use_container_width=False):
        player_row = df_gold[df_gold["Player"] == selected_player].iloc[0]
        try:
            pred = predict_player(player_row, feature_names=model_meta.get("feature_names"))
            tier = pred["tier_label"]
            conf = pred["confidence"]
            color = TIER_COLORS.get(tier, MUTE)
            print(f"pred {pred}")
            st.markdown(
                f"""<div style='background:{color}22;border:2px solid {color};border-radius:12px;padding:16px;margin:8px 0'>
                <h3 style='color:{color};margin:0'>{tier} ⚽</h3>
                <p style='margin:4px 0'>Confidence: <b>{conf:.1%}</b></p>
                </div>""",
                unsafe_allow_html=True,
            )

            # Probability breakdown
            proba_df = pd.DataFrame(
                [(k, f"{v:.1%}") for k, v in pred["probabilities"].items()],
                columns=["Tier", "Probability"],
            )
            st.dataframe(proba_df, use_container_width=False, hide_index=True)

            # SHAP
            with st.spinner("Computing SHAP explanations..."):
                try:
                    shap_data = compute_shap_values(df_gold, selected_player, nickname="static")
                except RuntimeError as shap_err:
                    st.warning(f"⚠️ SHAP: {shap_err}")
                    shap_data = None

            # ── SHAP Debug expander (always shown to help diagnose issues) ────
            if shap_data and "debug_info" in shap_data:
                with st.expander("🔧 SHAP Debug Info", expanded=True):
                    di = shap_data["debug_info"]
                    st.json(di)
            elif shap_data is None:
                with st.expander("🔧 SHAP Debug Info — no data returned", expanded=True):
                    st.write("shap_data is None — either no model, no player, or error before return")

            if shap_data:
                st.markdown("**🔬 SHAP Explanation (top features driving this prediction)**")
                fig, ax = plt.subplots(figsize=(8, 3.5))
                fig.patch.set_facecolor(BG_COLOR)
                ax.set_facecolor(BG_COLOR)
                shap_vals = shap_data["shap_values"]
                feat_names = shap_data["feature_names"]
                bar_colors = ["#007d48" if v > 0 else "#d30005" for v in shap_vals]
                ax.barh(feat_names[::-1], shap_vals[::-1], color=bar_colors[::-1], edgecolor="none")
                ax.axvline(0, color="gray", linewidth=0.8)
                ax.set_xlabel("SHAP value (positive = pushes toward higher tier)", fontsize=8)
                ax.set_title(f"SHAP — {selected_player}", fontsize=10, fontweight="bold")
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
                st.session_state["shap_data_for_ai"] = shap_data
            else:
                if shap_data is None:
                    st.info("💡 SHAP data available")

            st.session_state["selected_player_for_ai"] = selected_player

        except (ImportError, FileNotFoundError) as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")


# ── Tab 3: Design / Analytics ─────────────────────────────────────────────────

def _render_design_tab(df_filtered: pd.DataFrame):
    st.markdown("### 📊 Gold Layer Analytics — Design & Visualization")
    st.caption("Rich visualizations built from the Gold layer composite scores and performance tiers.")

    _, get_pipeline_status, load_gold, _, TIER_COLORS, TIER_ORDER = import_pipeline()
    pipeline_status = get_pipeline_status()

    if not pipeline_status["gold"]["exists"]:
        st.warning("⚠️ Run the Data Pipeline first to generate Gold layer data.")
        return

    try:
        df_gold = load_gold()
    except Exception as e:
        st.error(f"Failed to load Gold layer: {e}")
        return

    if "performance_tier" not in df_gold.columns:
        st.warning("Performance tier column missing. Re-run the pipeline.")
        return

    # ── Row 1: Tier distribution + Top players ────────────────────────────────
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### 🥇 Tier Distribution")
        tier_counts = df_gold["performance_tier"].value_counts()
        tiers_ordered = [t for t in TIER_ORDER if t in tier_counts.index]
        counts = [tier_counts[t] for t in tiers_ordered]
        colors = [TIER_COLORS.get(t, MUTE) for t in tiers_ordered]

        fig, ax = plt.subplots(figsize=(4, 4))
        apply_nike_style(fig, ax)
        wedges, texts, autotexts = ax.pie(
            counts,
            labels=tiers_ordered,
            autopct="%1.0f%%",
            colors=colors,
            startangle=140,
            pctdistance=0.75,
        )
        for t in texts:
            t.set_fontsize(9)
        for at in autotexts:
            at.set_fontsize(8)
            at.set_fontweight("bold")
        ax.set_title(f"Performance Tiers\n({len(df_gold):,} players)", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.markdown("#### 🏆 Top 20 Players by Composite Score")
        top_players = df_gold.nlargest(20, "composite_score")
        if "Player" in top_players.columns and "Team" in top_players.columns:
            fig, ax = plt.subplots(figsize=(8, 5))
            apply_nike_style(fig, ax)

            player_labels = [
                f"{row['Player']} ({row.get('Team', '?')})"
                for _, row in top_players.iterrows()
            ]
            bar_colors = [TIER_COLORS.get(t, INFO) for t in top_players["performance_tier"]]
            ax.barh(player_labels[::-1], top_players["composite_score"].values[::-1],
                    color=bar_colors[::-1], edgecolor="none")
            ax.set_xlabel("Composite Score", fontsize=9)
            ax.set_title("Top 20 Players — Composite Performance Score", fontsize=10, fontweight="bold")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            legend_patches = [mpatches.Patch(color=v, label=k) for k, v in TIER_COLORS.items()]
            ax.legend(handles=legend_patches, fontsize=7, loc="lower right")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    st.markdown("---")

    # ── Row 2: Score distribution + League breakdown ──────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 📈 Composite Score Distribution")
        fig, ax = plt.subplots(figsize=(5, 3.5))
        apply_nike_style(fig, ax)
        ax.hist(df_gold["composite_score"].dropna(), bins=30, color=INFO, alpha=0.8, edgecolor="white")
        for tier, threshold in [("Elite", 90), ("Good", 70)]:
            pct_val = np.percentile(df_gold["composite_score"].dropna(), threshold)
            ax.axvline(pct_val, color=TIER_COLORS[tier], linestyle="--", linewidth=1.5, label=f"{tier} threshold")
        ax.set_xlabel("Composite Score", fontsize=9)
        ax.set_ylabel("Players", fontsize=9)
        ax.set_title("Score Distribution", fontsize=10, fontweight="bold")
        ax.legend(fontsize=7)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col4:
        if "League" in df_gold.columns:
            st.markdown("#### 🌍 Elite Players by League (Top 10)")
            elite_by_league = (
                df_gold[df_gold["performance_tier"] == "Elite"]
                .groupby("League")
                .size()
                .sort_values(ascending=False)
                .head(10)
            )
            if len(elite_by_league) > 0:
                fig, ax = plt.subplots(figsize=(5, 3.5))
                fig.patch.set_facecolor(BG_COLOR)
                ax.set_facecolor(BG_COLOR)
                ax.barh(elite_by_league.index[::-1], elite_by_league.values[::-1],
                        color=TIER_COLORS["Elite"], edgecolor="none")
                ax.set_xlabel("# Elite Players", fontsize=9)
                ax.set_title("Elite Players per League", fontsize=10, fontweight="bold")
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

    # ── Row 3: Position breakdown ─────────────────────────────────────────────
    if "Primary position" in df_gold.columns:
        st.markdown("---")
        st.markdown("#### 🎯 Performance Tier by Position")
        pos_tier = df_gold.groupby(["Primary position", "performance_tier"]).size().unstack(fill_value=0)
        tier_order_cols = [t for t in TIER_ORDER if t in pos_tier.columns]
        pos_tier = pos_tier[tier_order_cols]
        top_positions = pos_tier.sum(axis=1).sort_values(ascending=False).head(12).index
        pos_tier = pos_tier.loc[top_positions]

        fig, ax = plt.subplots(figsize=(11, 4))
        apply_nike_style(fig, ax)
        bottom = np.zeros(len(pos_tier))
        for tier_col in tier_order_cols:
            vals = pos_tier[tier_col].values
            ax.bar(pos_tier.index, vals, bottom=bottom, label=tier_col,
                   color=TIER_COLORS.get(tier_col, MUTE), edgecolor="white", linewidth=0.5)
            bottom += vals
        ax.set_ylabel("Players", fontsize=9)
        ax.set_title("Tier Distribution by Position", fontsize=10, fontweight="bold")
        ax.legend(fontsize=8, loc="upper right")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # ── New Section 1: Top 20 by Selected Position ─────────────────────────────
    st.markdown("---")
    st.markdown("#### 🎯 Top 20 Players by Primary Position")
    all_positions = sorted(df_gold["Primary position"].dropna().unique().tolist())
    if all_positions:
        # Market Value Filter Setup
        mv_col = "Market value"
        max_val_found = 100000000.0#3000000
        if mv_col in df_gold.columns:
            # Convert to numeric to be safe
            mv_numeric = pd.to_numeric(df_gold[mv_col], errors='coerce').fillna(0)
            max_val_found = float(mv_numeric.max()) if not mv_numeric.empty else 1000000.0
            if max_val_found <= 0: max_val_found = 1000000.0

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            selected_positions = st.multiselect("Select Positions:", all_positions, default=[all_positions[0]], key="design_pos_multiselect")
        with c2:
            max_val_k = max_val_found / 1000.0
            mv_range_k = st.slider(
                "Market Value Range (k€):",
                min_value=0.0,
                max_value=max_val_k,
                value=(0.0, max_val_k),
                step=10.0,
                format="%.0f",
                key="design_pos_mv_slider_k"
            )
            # Convert back to full units for filtering
            mv_range = (mv_range_k[0] * 1000, mv_range_k[1] * 1000)
        with c3:
            show_expiring_pos = st.checkbox("Only soon-to-expire", key="design_pos_expiring_check", help="Expired before 31 Aug 2026")
        
        df_pos = df_gold.copy()
        if selected_positions:
            df_pos = df_pos[df_pos["Primary position"].isin(selected_positions)]
        
        # Apply Market Value Filter
        if mv_col in df_pos.columns:
            df_pos[mv_col] = pd.to_numeric(df_pos[mv_col], errors='coerce').fillna(0)
            df_pos = df_pos[(df_pos[mv_col] >= mv_range[0]) & (df_pos[mv_col] <= mv_range[1])]
        
        if show_expiring_pos and "Contract expires" in df_pos.columns:
            df_pos = df_pos[df_pos["Contract expires"].notna()]
            df_pos = df_pos[df_pos["Contract expires"] < "2026-08-31"]
            
        df_pos = df_pos.nlargest(20, "composite_score")
        
        if not df_pos.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            apply_nike_style(fig, ax)
            
            labels = [f"{r['Player']} ({int(r['Age']) if pd.notna(r['Age']) else '?'}y, {r.get('Primary position', '?')})" for _, r in df_pos.iterrows()]
            bar_colors = [TIER_COLORS.get(t, INFO) for t in df_pos["performance_tier"]]
            ax.barh(labels[::-1], df_pos["composite_score"].values[::-1], color=bar_colors[::-1])
            
            pos_label = ", ".join(selected_positions[:3]) + ("..." if len(selected_positions) > 3 else "")
            title = f"Top 20 {pos_label} by Composite Score"
            if show_expiring_pos:
                title += " (Expiring Soon)"
            ax.set_title(title, fontweight="bold")
            ax.set_xlabel("Composite Score")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            # --- New Table for df_pos in Section 1 ---
            st.markdown("##### 📋 Player list (Top 20)")
            display_cols_pos = ["Player","Full name", "Team", "Position","Primary Position", "Age", "Passport country", "Foot", "Height", "Weight", "Contract expires", "Market value", "composite_score"]
            available_cols_pos = [c for c in display_cols_pos if c in df_pos.columns]
            if available_cols_pos:
                df_table_pos = df_pos[available_cols_pos].copy()
                if "composite_score" in df_table_pos.columns:
                    df_table_pos["composite_score"] = df_table_pos["composite_score"].round(1)
                st.dataframe(df_table_pos, use_container_width=True, hide_index=True)
        else:
            st.info("No players found with the selected filters.")

    # ── New Section 2: Top 20 by Age Group ──────────────────────────────────────
    st.markdown("---")
    st.markdown("#### ⏳ Top 20 Players by Age Group")
    if "Age" in df_gold.columns:
        df_age = df_gold.copy()
        # Define age groups
        def get_age_group(age):
            if age <= 21: return "U21"
            if age <= 25: return "21-25"
            if age <= 30: return "26-30"
            return "31+"
        
        df_age["Age Group"] = df_age["Age"].apply(get_age_group)
        age_groups = ["U21", "21-25", "26-30", "31+"]
        
        c1, c2 = st.columns([2, 1])
        with c1:
            selected_age_group = st.radio("Select Age Group:", age_groups, horizontal=True, key="design_age_radio")
        with c2:
            show_expiring_age = st.checkbox("Only soon-to-expire", key="design_age_expiring_check", help="Expired before 31 Aug 2026")
        
        df_group = df_age[df_age["Age Group"] == selected_age_group]
        
        if show_expiring_age and "Contract expires" in df_group.columns:
            df_group = df_group[df_group["Contract expires"].notna()]
            df_group = df_group[df_group["Contract expires"] < "2026-08-31"]
            
        df_group = df_group.nlargest(20, "composite_score")
        
        if not df_group.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            apply_nike_style(fig, ax)
            labels = [f"{r['Player']} ({int(r['Age']) if pd.notna(r['Age']) else '?'})" for _, r in df_group.iterrows()]
            bar_colors = [TIER_COLORS.get(t, INFO) for t in df_group["performance_tier"]]
            ax.barh(labels[::-1], df_group["composite_score"].values[::-1], color=bar_colors[::-1])
            
            title = f"Top 20 {selected_age_group} Players"
            if show_expiring_age:
                title += " (Expiring Soon)"
            ax.set_title(title, fontweight="bold")
            ax.set_xlabel("Composite Score")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No players found with the selected filters.")

    # ── New Section 3: Expiring Contracts before 31 Aug 2026 ────────────────────
    if "Contract expires" in df_gold.columns:
        st.markdown("---")
        st.markdown("#### ⚠️ High-Value Expiring Contracts (Before 31 Aug 2026)")
        
        # Filter for contracts expiring before 31 Aug 2026
        # Assuming format YYYY-MM-DD
        df_expiring = df_gold[df_gold["Contract expires"].notna()].copy()
        df_expiring = df_expiring[df_expiring["Contract expires"] < "2026-08-31"]
        
        if not df_expiring.empty:
            st.caption(f"Found {len(df_expiring)} players with contracts expiring before 31 August 2026.")
            
            # Show top 20 of these by composite score
            df_expiring_top = df_expiring.nlargest(20, "composite_score")
            
            fig, ax = plt.subplots(figsize=(10, 5))
            apply_nike_style(fig, ax)
            
            labels = [f"{r['Player']} ({int(r['Age']) if pd.notna(r['Age']) else '?'}y, {r.get('Primary position', '?')})" for _, r in df_expiring_top.iterrows()]
            bar_colors = [TIER_COLORS.get(t, INFO) for t in df_expiring_top["performance_tier"]]
            ax.barh(labels[::-1], df_expiring_top["composite_score"].values[::-1], color=bar_colors[::-1])
            ax.set_title("Top 20 Players with Soon-to-Expire Contracts", fontweight="bold")
            ax.set_xlabel("Composite Score")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            
            # Annotate with expiry date and market value
            for i, (_, row) in enumerate(df_expiring_top.iterrows()):
                mv = row.get("Market value", 0)
                try:
                    mv_val = float(mv) if pd.notna(mv) else 0
                except:
                    mv_val = 0
                
                if mv_val >= 1000000:
                    mv_str = f"{mv_val/1000000:.1f}M"
                elif mv_val >= 1000:
                    mv_str = f"{int(mv_val/1000)}K"
                else:
                    mv_str = f"{int(mv_val)}" if mv_val > 0 else "?"
                
                label_text = f"{row['Contract expires']} ({mv_str})"
                ax.text(row["composite_score"] + 0.5, 19-i, label_text, va='center', fontsize=8, color="#d30005")
                
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            
            with st.expander("📄 View All Expiring Contracts Table"):
                st.dataframe(
                    df_expiring[["Player","Full name", "Team", "Position", "Age", "Passport country", "Foot", "Height", "Weight", "Contract expires", "Market value", "composite_score"]]
                    .sort_values("composite_score", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No players found with contracts expiring before 31 August 2026.")

    # ── Quick stats table ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 Gold Layer — Player Table")
    display_cols = ["Player", "Full name", "Team", "League", "Primary position", "performance_tier",
                    "composite_score", "composite_percentile", "league_rank"]
    available_cols = [c for c in display_cols if c in df_gold.columns]
    if available_cols:
        df_display = df_gold[available_cols].sort_values("composite_score", ascending=False).head(50)
        df_display["composite_score"] = df_display["composite_score"].round(1)
        df_display["composite_percentile"] = df_display["composite_percentile"].round(1)
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# ── Tab 4: AI Analyst ─────────────────────────────────────────────────────────

def render_ai_analyst_tab(df_filtered: pd.DataFrame, selected_position_group: str):
    st.markdown("### 🧠 AI Analyst — Gemini-Powered Scouting Reports")
    st.caption(
        "Google **Gemini 1.5 Flash** reads pre-computed statistics and SHAP explanations to write "
        "professional natural-language scouting reports. The LLM never computes numbers."
    )

    generate_scouting_report, is_configured, build_player_scouting_prompt = import_enrichment()
    _, get_pipeline_status, load_gold, _, _, _ = import_pipeline()
    from models.predict import compute_shap_values
    from models.train import get_model_status
    from models.feature_engineering import ML_FEATURES

    # API key check
    if not is_configured():
        st.warning(
            "⚠️ **GEMINI_API_KEY not configured.** Add it to your `.env` file:\n\n"
            "```\nGEMINI_API_KEY=your_key_here\n```\n\n"
            "Get a free key at [aistudio.google.com](https://aistudio.google.com)"
        )
        st.info("The rest of the AI Analyst tab is disabled until the key is set.")
        return

    # Gold layer check
    pipeline_status = get_pipeline_status()
    if not pipeline_status["gold"]["exists"]:
        st.warning("⚠️ Run the **Data Pipeline** first to generate Gold layer data.")
        return

    try:
        df_gold = load_gold()
    except Exception as e:
        st.error(f"Failed to load Gold layer: {e}")
        return

    # Player selector
    player_list = sorted(df_gold["Player"].dropna().unique().tolist()) if "Player" in df_gold.columns else []
    if not player_list:
        st.warning("No players in Gold layer.")
        return

    # Pre-select from ML tab if available
    default_player = st.session_state.get("selected_player_for_ai", player_list[0])
    if default_player not in player_list:
        default_player = player_list[0]

    col_sel, col_info = st.columns([2, 1])
    with col_sel:
        selected_player = st.selectbox(
            "Select Player:",
            options=player_list,
            index=player_list.index(default_player),
            key="ai_player_select",
        )

    player_row = df_gold[df_gold["Player"] == selected_player].iloc[0]

    # Build player info panel
    with col_info:
        tier = player_row.get("performance_tier", "Unknown")
        tier_color = ACCENT_COLORS.get(tier, MUTE)
        st.markdown(
            f"""<div style='background:{tier_color}22;border:1px solid {tier_color};
            border-radius:0;padding:10px;margin-top:4px'>
            <b>🏷️ {tier}</b><br>
            Score: {player_row.get('composite_score', 0):.1f}/100<br>
            Top {100 - player_row.get('composite_percentile', 50):.0f}%
            </div>""",
            unsafe_allow_html=True,
        )

    # Player stats preview
    with st.expander(f"📊 {selected_player} — Statistical Profile", expanded=True):
        stat_cols = [c for c in ML_FEATURES if c in player_row.index]
        if stat_cols:
            pairs = [(c, player_row[c]) for c in stat_cols if not pd.isna(player_row.get(c))]
            if pairs:
                display_df = pd.DataFrame(pairs, columns=["Statistic", "Value (per 90)"]).set_index("Statistic")
                display_df["Value (per 90)"] = display_df["Value (per 90)"].apply(lambda x: f"{x:.3f}")
                st.dataframe(display_df, use_container_width=False)
            else:
                st.info("No per-90 stats available for this player.")

    # SHAP preview (if model exists)
    shap_data = None
    model_meta = get_model_status()
    if model_meta["exists"]:
        with st.spinner("Loading SHAP explanations..."):
            try:
                shap_data = compute_shap_values(df_gold, selected_player)
            except RuntimeError as shap_err:
                st.caption(f"⚠️ SHAP: {shap_err}")
                shap_data = None

        if shap_data:
            with st.expander("🔬 SHAP — ML Explanation", expanded=False):
                shap_items = [
                    {"feature": f, "shap_value": v, "feature_value": fv}
                    for f, v, fv in zip(
                        shap_data["feature_names"],
                        shap_data["shap_values"],
                        shap_data["feature_values"],
                    )
                ]
                shap_df = pd.DataFrame(shap_items).rename(columns={
                    "feature": "Feature",
                    "feature_value": "Value",
                    "shap_value": "SHAP Impact",
                })
                shap_df["SHAP Impact"] = shap_df["SHAP Impact"].apply(lambda x: f"{x:+.3f}")
                shap_df["Value"] = shap_df["Value"].apply(lambda x: f"{x:.3f}")
                st.dataframe(shap_df, use_container_width=False, hide_index=True)
        else:
            st.caption("💡 Train the model and install `shap` to see ML explanations.")
            shap_data = None

    st.markdown("---")

    # Generate report button
    generate_clicked = st.button(
        "📝 Generate Scouting Report",
        type="primary",
        use_container_width=True,
        key="ai_generate_btn",
    )

    if generate_clicked:
        # Build key stats dict
        key_stats = {
            c: float(player_row[c])
            for c in ML_FEATURES
            if c in player_row.index and not pd.isna(player_row.get(c))
        }

        shap_items = None
        if shap_data:
            shap_items = [
                {"feature": f, "shap_value": float(v), "feature_value": float(fv)}
                for f, v, fv in zip(
                    shap_data["feature_names"],
                    shap_data["shap_values"],
                    shap_data["feature_values"],
                )
            ]

        # 1b. Calculate Best Role (Tactical Fit) - Filtered by position group
        all_roles = get_all_roles()
        if selected_position_group == "All":
            relevant_role_names = list(all_roles.keys())
        else:
            relevant_role_names = get_roles_for_position(selected_position_group)
        
        role_scores = {}
        # Only consider roles mapped to this position group in registry.py
        for role_name in relevant_role_names:
            if role_name in all_roles:
                role_info = all_roles[role_name]
                score = 0.0
                for comp in role_info.get("components", []):
                    stat = comp["stat"]
                    weight = comp["weight"]
                    val = player_row.get(f"{stat}_percentile", player_row.get(stat, 50.0))
                    if pd.isna(val): val = 50.0
                    score += val * weight
                role_scores[role_name] = score
        
        best_role = "N/A"
        if role_scores:
            best_role = max(role_scores, key=role_scores.get)
        
        # 1c. Find Top 5 Archetypes (from COMP_ columns) - Filtered by position group
        if selected_position_group == "All":
            comp_cols = [c for c in player_row.index if c.startswith("COMP_")]
        else:
            relevant_comp_keys = get_responsibilities_for_position(selected_position_group)
            comp_cols = [f"COMP_{k}" for k in relevant_comp_keys if f"COMP_{k}" in player_row.index]
        
        # Fallback to all COMP_ if none found for group (to be safe)
        if not comp_cols:
            comp_cols = [c for c in player_row.index if c.startswith("COMP_")]
            
        top_comp_scores = player_row[comp_cols].sort_values(ascending=False).head(5)
        top_archetypes = [c.replace("COMP_", "") for c in top_comp_scores.index]
        
        prompt = build_player_scouting_prompt(
            player_name=selected_player,
            position=str(player_row.get("Primary position", player_row.get("Position", "Unknown"))),
            team=str(player_row.get("Team", "Unknown")),
            league=str(player_row.get("League", "Unknown")),
            age=int(player_row["Age"]) if "Age" in player_row.index and not pd.isna(player_row.get("Age")) else None,
            performance_tier=str(player_row.get("performance_tier", "Unknown")),
            composite_score=float(player_row.get("composite_score", 50)),
            composite_percentile=float(player_row.get("composite_percentile", 50)),
            key_stats=key_stats,
            shap_top_features=shap_items,
            position_group=selected_position_group,
            best_role=best_role,
            top_archetypes=top_archetypes
        )

        with st.spinner(f"🧠 Gemini is analyzing {selected_player}..."):
            try:
                report = generate_scouting_report(prompt)
                st.session_state["ai_report"] = report
                st.session_state["ai_report_player"] = selected_player
            except (ImportError, ValueError) as e:
                st.error(f"❌ Configuration error: {e}")
            except RuntimeError as e:
                st.error(f"❌ API error: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")

    # Display generated report
    if st.session_state.get("ai_report") and st.session_state.get("ai_report_player") == selected_player:
        st.markdown("---")
        st.markdown(
            f"### 📋 Scouting Report — {selected_player}",
        )
        st.markdown(
            f"""<div style='background:#f5f5f5;border:1px solid #cacacb;border-radius:0;padding:20px'>""",
            unsafe_allow_html=True,
        )
        st.markdown(st.session_state["ai_report"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Copy helper
        with st.expander("📋 Copy raw text"):
            st.text_area(
                "Report text:",
                value=st.session_state["ai_report"],
                height=300,
                key="ai_report_copy",
            )

        st.caption(
            "⚠️ **Disclosure:** This report was generated by Google Gemini AI based on statistical data only. "
            "Always validate with video analysis and professional scouting."
        )


# ── Main Entry Point ──────────────────────────────────────────────────────────

def render_ai_intelligence_page(df_filtered: pd.DataFrame, selected_position_group: str):
    """
    Render the AI Intelligence page with 4 tabs.

    Args:
        df_filtered: Filtered player DataFrame (with percentiles & composite attrs)
        selected_position_group: Currently selected position group from sidebar
    """
    st.header("AI Intelligence")
    st.markdown(
        "A **data engineering + machine learning + AI** pipeline for intelligent player analysis. "
        "Architecture inspired by production sports analytics platforms."
    )

    if df_filtered is None or len(df_filtered) == 0:
        st.warning("⚠️ No player data available. Adjust global filters in the sidebar.")
        return

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔧 Data Pipeline",
        "🤖 ML Model",
        "📊 Design",
        "🧠 AI Analyst",
    ])

    with tab1:
        _render_pipeline_tab(df_filtered)

    with tab2:
        _render_ml_tab(df_filtered, selected_position_group)

    with tab3:
        _render_design_tab(df_filtered)

    with tab4:
        render_ai_analyst_tab(df_filtered, selected_position_group)
