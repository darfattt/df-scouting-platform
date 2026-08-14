"""
Model Prediction - Load trained model and produce predictions + SHAP values
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

from models.feature_engineering import TIER_LABELS, get_available_features
from models.train import get_model_paths, MODEL_DIR


def _load_model(nickname: str = "static"):
    """Load trained XGBoost model from disk."""
    try:
        from xgboost import XGBClassifier
    except ImportError:
        raise ImportError("xgboost not installed. Run: pip install xgboost")

    model_file, _ = get_model_paths(nickname)
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"No trained model found for '{nickname}'. Train the model first.")

    model = XGBClassifier()
    model.load_model(model_file)
    return model


def _load_meta(nickname: str = "static") -> dict:
    """Load model metadata."""
    _, meta_file = get_model_paths(nickname)
    if not os.path.exists(meta_file):
        return {}
    with open(meta_file) as f:
        return json.load(f)


def _numeric_features_only(df: pd.DataFrame, feature_names: list) -> list:
    """
    Return only those feature_names whose column in df is fully numeric.
    Drops columns that contain strings or mixed types (e.g. JSON array strings).
    """
    good = []
    for f in feature_names:
        if f not in df.columns:
            continue
        try:
            col = pd.to_numeric(df[f], errors="coerce")
            # reject if more than 10% NaN after coerce (indicates string values)
            if col.isna().mean() > 0.9:
                continue
            good.append(f)
        except Exception:
            continue
    return good


def _safe_float(value) -> float:
    """
    Convert a single value to float safely.
    Returns 0.0 for anything that cannot be parsed:
    - Python lists / numpy arrays → 0.0 (JSON-array columns)
    - Strings that look like '[...]' → 0.0
    - NaN / None → 0.0
    - Normal numeric strings / ints / floats → float(value)
    """
    if isinstance(value, (list, np.ndarray)):
        return 0.0
    if value is None:
        return 0.0
    try:
        f = float(value)
        return 0.0 if np.isnan(f) else f
    except (TypeError, ValueError):
        return 0.0


def predict_player(player_row: pd.Series, feature_names=None, nickname: str = "static") -> Dict:
    """
    Predict performance tier for a single player.
    """
    model = _load_model(nickname)
    meta = _load_meta(nickname)
    
    # Wrap series in DataFrame to use the same matching logic
    df_temp = pd.DataFrame([player_row])
    X_df, features = _match_features(df_temp, model, meta)
    
    X = X_df.values.astype(np.float32)
    proba = model.predict_proba(X)[0]
    pred_class = int(np.argmax(proba))
    
    return {
        "tier": pred_class,
        "tier_label": TIER_LABELS.get(pred_class, "Unknown"),
        "confidence": float(proba[pred_class]),
        "probabilities": {
            TIER_LABELS.get(i, str(i)): float(p) for i, p in enumerate(proba)
        },
    }


def _match_features(df_gold: pd.DataFrame, model, meta: dict) -> Tuple[pd.DataFrame, list]:
    """
    Ensure df_gold matches the feature set the model was trained on.
    Pads missing features with 0.0, drops extra features, and orders correctly.
    """
    # 1. Determine expected features
    expected = []
    try:
        # Best source: The booster's own feature names (if saved)
        expected = model.get_booster().feature_names
    except Exception:
        pass
    
    if not expected:
        # Fallback: Meta file
        expected = meta.get("feature_names", [])
    
    if not expected:
        # Final fallback: current config (unreliable but better than nothing)
        expected = get_available_features(df_gold)

    # 2. Build the matrix
    X_df = pd.DataFrame(index=df_gold.index)
    for col in expected:
        if col in df_gold.columns:
            # Convert to numeric, handle potential string/array data gracefully
            X_df[col] = df_gold[col].apply(_safe_float)
        else:
            # Padding missing feature with 0.0
            X_df[col] = 0.0
            
    return X_df, expected


def predict_dataframe(df_gold: pd.DataFrame, nickname: str = "static") -> pd.DataFrame:
    """
    Run predictions on the entire Gold DataFrame.
    Adds predicted_tier and predicted_tier_label columns.
    """
    model = _load_model(nickname)
    meta = _load_meta(nickname)
    
    X_df, _ = _match_features(df_gold, model, meta)
    if X_df.empty:
        return df_gold

    X = X_df.values.astype(np.float32)
    preds = model.predict(X)
    probas = model.predict_proba(X)

    df_out = df_gold.copy()
    df_out["predicted_tier"] = preds
    df_out["predicted_tier_label"] = [TIER_LABELS.get(int(p), "Unknown") for p in preds]
    df_out["predicted_confidence"] = probas.max(axis=1)
    return df_out


def compute_shap_values(df_gold: pd.DataFrame, player_name: str, nickname: str = "static") -> Optional[Dict]:
    """
    Compute SHAP values for a single player using TreeExplainer.
    Returns debug_info dict alongside results for browser-side debugging.

    Returns:
        dict with feature_names, shap_values, base_value, debug_info — or None
    """
    try:
        print("importing shap.....")
        import shap
        print("success.....")
    except ImportError as ie:
        raise RuntimeError(f"shap import failed: {ie}")

    try:
        meta = _load_meta()
        feature_names = meta.get("feature_names", get_available_features(df_gold))
        available = [f for f in feature_names if f in df_gold.columns]

        if not available:
            raise RuntimeError("No matching feature columns found in Gold layer.")

        player_rows = df_gold[df_gold["Player"] == player_name]
        if len(player_rows) == 0:
            raise RuntimeError(f"Player '{player_name}' not found in Gold layer.")
        # Reset index for safe integer-position lookup
        df_reset = df_gold.reset_index(drop=True)
        player_rows_reset = df_reset[df_reset["Player"] == player_name]
        local_idx = int(player_rows_reset.index[0])

        # Build X column-by-column as float64 — fully immune to string/object dtype.
        # pd.to_numeric converts strings to NaN, then we numpy-cast to float64.
        # If a column still has non-numeric values after that, fill with 0.
        X_cols = []
        good_features = []
        for col in available:
            try:
                # Element-wise _safe_float handles JSON-array strings, Python list cells,
                # None, NaN, and normal numeric values — fully immune to ValueError.
                col_array = np.array([_safe_float(v) for v in df_reset[col]], dtype=np.float64)
                X_cols.append(col_array)
                good_features.append(col)
            except Exception:
                print(f"col {col} failed")
                pass  # skip columns that can't be converted at all

        if not X_cols:
            raise RuntimeError("No numeric feature columns could be built for SHAP.")

        available = good_features
        X = np.column_stack(X_cols)  # shape: (n_samples, n_features)
        debug_info = {
            "n_features": len(available),
            "n_samples": X.shape[0],
            "X_dtype": str(X.dtype),
            "X_shape": str(X.shape),
            "X_player_row_sample": {available[i]: float(X[local_idx, i]) for i in range(min(5, len(available)))},
            "local_idx": local_idx,
            "features": available,
        }
        print(f"debug_info {debug_info}")
        print(f"model {model}")
        # Predict class for this player
        pred_class = int(model.predict(X[[local_idx], :])[0])
        debug_info["pred_class"] = pred_class

        # ── Compute SHAP ───────────────────────────────────────────────────────
        explainer = None
        try:
            # Level 1: Standard TreeExplainer (Direct Model)
            explainer = shap.TreeExplainer(model)
        except (ValueError, Exception) as e_init:
            print(f"SHAP Level 1 Failed: {e_init}. Trying Level 2 (Booster Hack)...")
            try:
                # Level 2: Booster Hack (Fix string-encoded base_score)
                booster = model.get_booster()
                orig_bs = booster.attr("base_score")
                # Temporarily set to a single float to dodge SHAP parser bug
                booster.set_attr(base_score="0.5")
                explainer = shap.TreeExplainer(booster)
                # Note: expected_value might be wrong now, but explainer(X) might still work
                # We can try to restore or fix expected_value later if needed.
            except Exception as e_init2:
                print(f"SHAP Level 2 Failed: {e_init2}. Trying Level 3 (KernelExplainer)...")
                # Level 3: KernelExplainer (Robust fallback, uses black-box prediction)
                try:
                    # Summarize background data with k-means for speed
                    # Using 20 centroids is usually enough for good approximations
                    X_background = shap.kmeans(X, 20)
                    
                    def model_predict_proba(data):
                        # SHAP expects (n_samples, n_classes) for multi-class
                        return model.predict_proba(data)
                        
                    explainer = shap.KernelExplainer(model_predict_proba, X_background)
                    debug_info["explainer_type"] = "KernelExplainer"
                except Exception as e_init3:
                    raise RuntimeError(f"All SHAP initialization levels failed. Last error: {e_init3}")

        print(f"SHAP Debug: explainer_type={type(explainer)}")

        # ── Extract SHAP Values ────────────────────────────────────────────────
        # Use only the selected player row for performance (crucial for KernelExplainer)
        X_player = X[[local_idx], :]
        player_shap = None
        base_value = 0.0

        try:
            # 1. Try modern API (works for TreeExplainer, fast)
            if hasattr(explainer, "__call__") and not isinstance(explainer, shap.KernelExplainer):
                explanation = explainer(X_player)
                # explanation.values is (1, n_features, n_classes) or (1, n_features)
                vals = np.array(explanation.values)
                if vals.ndim == 3:  # (1, n_features, n_classes)
                    player_shap = vals[0, :, pred_class]
                else:  # (1, n_features)
                    player_shap = vals[0, :]
                
                ev = np.atleast_1d(explanation.base_values)
                base_value = float(ev[pred_class]) if len(ev) > pred_class else float(ev[0])
            
            # 2. Fallback to legacy API or KernelExplainer
            if player_shap is None:
                sv = explainer.shap_values(X_player)
                # For multi-class, sv is a list of arrays [n_samples, n_features]
                if isinstance(sv, list):
                    # Pick the list element matching the predicted class
                    player_shap = np.array(sv[pred_class])[0]
                else:
                    # Check for (n_samples, n_features, n_classes)
                    sv_arr = np.array(sv)
                    if sv_arr.ndim == 3:
                        player_shap = sv_arr[0, :, pred_class]
                    else:
                        player_shap = sv_arr[0]
                
                # expected_value
                ev = explainer.expected_value
                # Handle cases where ev is a string representation of a list (e.g. '[0.1, 0.2]')
                if isinstance(ev, str) and ev.startswith('[') and ev.endswith(']'):
                    try:
                        import json
                        ev = json.loads(ev)
                    except Exception:
                        pass
                
                ev_arr = np.atleast_1d(ev)
                if len(ev_arr) > pred_class:
                    base_value = _safe_float(ev_arr[pred_class])
                else:
                    base_value = _safe_float(ev_arr[0]) if hasattr(ev, '__len__') else _safe_float(ev)

        except Exception as e_extract:
            print(f"SHAP extraction failed: {e_extract}")
            raise RuntimeError(f"Could not extract SHAP values: {e_extract}")

        # Ensure numeric type
        player_shap = player_shap.astype(np.float64)

        # Sort by absolute importance
        importance_order = np.argsort(np.abs(player_shap))[::-1]
        top_n = min(10, len(available))

        return {
            "feature_names": [available[i] for i in importance_order[:top_n]],
            "shap_values": [float(player_shap[i]) for i in importance_order[:top_n]],
            "feature_values": [float(X[local_idx, i]) for i in importance_order[:top_n]],
            "base_value": base_value,
            "predicted_class": pred_class,
            "predicted_label": TIER_LABELS.get(pred_class, "Unknown"),
            "debug_info": debug_info,
        }

    except ImportError as ie:
        raise RuntimeError(f"ImportError inside SHAP: {ie}")
    except FileNotFoundError as fnf:
        raise RuntimeError(f"Model file not found: {fnf}")
    except Exception as e:
        raise RuntimeError(f"SHAP computation failed [{type(e).__name__}]: {e}")

