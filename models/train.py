"""
Model Training - XGBoost classifier to predict player performance tier
Uses StratifiedKFold cross-validation (no time-leakage on cross-sectional data)
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
)
from sklearn.preprocessing import LabelEncoder

from models.feature_engineering import (
    ML_TARGET,
    TIER_LABELS,
    get_available_features,
)

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pipeline", "models")

def get_model_paths(nickname: str = "static") -> Tuple[str, str]:
    """Get paths for model and metadata files based on nickname."""
    model_name = "player_tier_model"
    if nickname != "static":
        model_name = f"player_tier_model_{nickname}"
    
    model_file = os.path.join(MODEL_DIR, f"{model_name}.json")
    meta_file = os.path.join(MODEL_DIR, f"{model_name}_meta.json")
    return model_file, meta_file


def get_model_status(nickname: str = "static") -> dict:
    """Check if a trained model exists."""
    model_file, meta_file = get_model_paths(nickname)
    if not os.path.exists(model_file):
        return {"exists": False, "path": model_file}
    try:
        with open(meta_file) as f:
            meta = json.load(f)
        return {"exists": True, "path": model_file, **meta}
    except Exception:
        return {"exists": True, "path": model_file}


def train_model(
    df_gold: pd.DataFrame, 
    feature_names: Optional[List[str]] = None,
    nickname: str = "static"
) -> Dict:
    """
    Train an XGBoost classifier on Gold-layer data.

    Args:
        df_gold: Gold-layer DataFrame with `tier_encoded` column
        feature_names: Optional list of features to use. If None, uses get_available_features.
        nickname: Unique identifier for this model variant (e.g. 'static', 'dynamic').

    Returns:
        dict with accuracy, report, confusion_matrix, feature_names, model_path

    Raises:
        ImportError: If xgboost is not installed
        ValueError: If insufficient data or features
    """
    if not XGBOOST_AVAILABLE:
        raise ImportError(
            "xgboost is not installed. Run: pip install xgboost"
        )

    if ML_TARGET not in df_gold.columns:
        raise ValueError(
            f"Target column '{ML_TARGET}' not found. Run the pipeline first."
        )

    if feature_names is not None:
        feature_cols = [f for f in feature_names if f in df_gold.columns]
    else:
        feature_cols = get_available_features(df_gold)
    if len(feature_cols) < 3:
        raise ValueError(
            f"Too few features available ({len(feature_cols)}). "
            "Ensure pipeline has been run and data contains per-90 stats."
        )

    # Prepare X/y — drop rows with NaN in features or target
    df_ml = df_gold[feature_cols + [ML_TARGET]].dropna()
    if len(df_ml) < 20:
        raise ValueError(
            f"Too few samples for training ({len(df_ml)}). "
            "Load more data via the global filters."
        )

    X = df_ml[feature_cols].values.astype(np.float32)
    y = df_ml[ML_TARGET].values.astype(int)

    # XGBoost classifier
    model = XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42,
        verbosity=0,
    )

    # 5-fold stratified CV
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")

    # Final fit on full dataset
    model.fit(X, y)

    # Evaluation
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    labels_present = sorted(np.unique(y).tolist())
    label_names = [TIER_LABELS.get(i, str(i)) for i in labels_present]
    report = classification_report(
        y, y_pred, labels=labels_present, target_names=label_names, output_dict=True
    )
    cm = confusion_matrix(y, y_pred, labels=labels_present)

    # Save model and metadata
    model_file, meta_file = get_model_paths(nickname)
    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save_model(model_file)

    # Save metadata
    import datetime
    meta = {
        "accuracy": float(accuracy),
        "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std()),
        "n_samples": int(len(df_ml)),
        "n_features": len(feature_cols),
        "feature_names": feature_cols,
        "trained_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tier_labels": TIER_LABELS,
        "nickname": nickname,
    }
    with open(meta_file, "w") as f:
        json.dump(meta, f, indent=2)

    return {
        "accuracy": accuracy,
        "cv_mean": cv_scores.mean(),
        "cv_std": cv_scores.std(),
        "report": report,
        "confusion_matrix": cm.tolist(),
        "confusion_labels": label_names,
        "feature_names": feature_cols,
        "feature_importances": model.feature_importances_.tolist(),
        "model_path": model_file,
        "n_samples": len(df_ml),
    }
