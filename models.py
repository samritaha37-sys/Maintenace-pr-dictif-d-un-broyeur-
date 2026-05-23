"""Multi-model training, comparison, persistence."""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    IsolationForest,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

from config import (
    INPUT_FEATURES,
    MODELS_DIR,
    REGRESSION_TARGETS,
    TARGET_STATE,
)

warnings.filterwarnings("ignore")

# Optional libraries
try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGB = True
except Exception:
    HAS_XGB = False

try:
    from lightgbm import LGBMClassifier, LGBMRegressor
    HAS_LGBM = True
except Exception:
    HAS_LGBM = False


CLF_PATH = os.path.join(MODELS_DIR, "classifier.joblib")
REG_PATH = os.path.join(MODELS_DIR, "regressor.joblib")
ISO_PATH = os.path.join(MODELS_DIR, "isoforest.joblib")
META_PATH = os.path.join(MODELS_DIR, "meta.json")


# =============================================================================
# Container
# =============================================================================


@dataclass
class TrainedBundle:
    """All trained models plus their evaluation metadata."""

    clf: Any
    reg: Any
    iso: IsolationForest
    meta: dict = field(default_factory=dict)

    # quick accessors
    @property
    def clf_name(self) -> str:
        return self.meta.get("clf_name", type(self.clf).__name__)

    @property
    def reg_name(self) -> str:
        return self.meta.get("reg_name", type(self.reg).__name__)


# =============================================================================
# Training
# =============================================================================


def _classifier_candidates() -> dict[str, Any]:
    cands: dict[str, Any] = {
        "RandomForest": RandomForestClassifier(
            n_estimators=200, random_state=42, n_jobs=-1, class_weight="balanced"
        ),
    }
    if HAS_XGB:
        cands["XGBoost"] = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
            verbosity=0,
        )
    if HAS_LGBM:
        cands["LightGBM"] = LGBMClassifier(
            n_estimators=200, random_state=42, n_jobs=-1, verbose=-1,
            class_weight="balanced",
        )
    return cands


def _regressor_candidates() -> dict[str, Any]:
    cands: dict[str, Any] = {
        "RandomForest": RandomForestRegressor(
            n_estimators=200, random_state=42, n_jobs=-1
        ),
    }
    if HAS_XGB:
        from sklearn.multioutput import MultiOutputRegressor

        cands["XGBoost"] = MultiOutputRegressor(
            XGBRegressor(
                n_estimators=200, max_depth=6, learning_rate=0.1,
                random_state=42, n_jobs=-1, verbosity=0,
            )
        )
    return cands


def _safe_cv_f1(model, X, y, n_splits: int = 5) -> float:
    """5-fold stratified CV F1; falls back gracefully if dataset is tiny/imbalanced."""
    classes = np.unique(y)
    min_class = int(pd.Series(y).value_counts().min())
    n_splits = max(2, min(n_splits, min_class))
    if min_class < 2 or len(classes) < 2:
        # Degenerate — can't CV. Train/test split fallback.
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
        model.fit(Xtr, ytr)
        return float(f1_score(yte, model.predict(Xte), average="weighted", zero_division=0))
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=skf, scoring="f1_weighted", n_jobs=1)
    return float(np.mean(scores))


def _safe_cv_r2(model, X, Y, n_splits: int = 5) -> float:
    from sklearn.model_selection import KFold

    n_splits = max(2, min(n_splits, len(X) // 10 or 2))
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, Y, cv=kf, scoring="r2", n_jobs=1)
    return float(np.mean(scores))


def train_all(data: pd.DataFrame, dataset_hash_str: str = "") -> TrainedBundle:
    """Train classifier + regressor + isolation forest. Picks best by CV."""

    # -------- Classifier --------
    Xc = data[INPUT_FEATURES].copy()
    yc = data[TARGET_STATE].astype(int).copy()

    clf_results: list[dict] = []
    best_clf_name, best_clf, best_clf_score = None, None, -np.inf
    for name, mdl in _classifier_candidates().items():
        try:
            score = _safe_cv_f1(mdl, Xc, yc)
        except Exception as e:
            score = float("nan")
            clf_results.append({"model": name, "f1_cv": score, "error": str(e)})
            continue
        clf_results.append({"model": name, "f1_cv": score})
        if score > best_clf_score:
            best_clf_score, best_clf_name, best_clf = score, name, mdl

    # Fit best on full data
    Xc_tr, Xc_te, yc_tr, yc_te = train_test_split(
        Xc, yc, test_size=0.2, random_state=42,
        stratify=yc if yc.nunique() > 1 and yc.value_counts().min() >= 2 else None,
    )
    best_clf.fit(Xc_tr, yc_tr)
    yc_pred = best_clf.predict(Xc_te)
    try:
        yc_proba = best_clf.predict_proba(Xc_te)[:, 1]
        roc_auc = float(roc_auc_score(yc_te, yc_proba)) if yc_te.nunique() > 1 else float("nan")
        fpr, tpr, _ = roc_curve(yc_te, yc_proba) if yc_te.nunique() > 1 else (np.array([0,1]), np.array([0,1]), None)
        roc = {"fpr": fpr.tolist(), "tpr": tpr.tolist(), "auc": roc_auc}
    except Exception:
        roc = {"fpr": [], "tpr": [], "auc": float("nan")}

    clf_eval = {
        "name": best_clf_name,
        "cv_f1": float(best_clf_score),
        "test_accuracy": float(accuracy_score(yc_te, yc_pred)),
        "test_f1": float(f1_score(yc_te, yc_pred, average="weighted", zero_division=0)),
        "confusion_matrix": confusion_matrix(yc_te, yc_pred).tolist(),
        "roc": roc,
        "feature_importance": _feature_importance(best_clf, INPUT_FEATURES),
        "candidates": clf_results,
    }

    # Refit on FULL data for production use
    best_clf.fit(Xc, yc)

    # -------- Regressor --------
    Xr = data[INPUT_FEATURES + [TARGET_STATE]].copy()
    Yr = data[REGRESSION_TARGETS].copy()

    reg_results: list[dict] = []
    best_reg_name, best_reg, best_reg_score = None, None, -np.inf
    for name, mdl in _regressor_candidates().items():
        try:
            score = _safe_cv_r2(mdl, Xr, Yr)
        except Exception as e:
            score = float("nan")
            reg_results.append({"model": name, "r2_cv": score, "error": str(e)})
            continue
        reg_results.append({"model": name, "r2_cv": score})
        if score > best_reg_score:
            best_reg_score, best_reg_name, best_reg = score, name, mdl

    Xr_tr, Xr_te, Yr_tr, Yr_te = train_test_split(Xr, Yr, test_size=0.2, random_state=42)
    best_reg.fit(Xr_tr, Yr_tr)
    Yr_pred = best_reg.predict(Xr_te)
    reg_eval = {
        "name": best_reg_name,
        "cv_r2": float(best_reg_score),
        "test_r2": float(r2_score(Yr_te, Yr_pred)),
        "test_mae": float(mean_absolute_error(Yr_te, Yr_pred)),
        "test_rmse": float(np.sqrt(mean_squared_error(Yr_te, Yr_pred))),
        "per_target": {
            t: {
                "r2": float(r2_score(Yr_te[t], Yr_pred[:, i])),
                "mae": float(mean_absolute_error(Yr_te[t], Yr_pred[:, i])),
            }
            for i, t in enumerate(REGRESSION_TARGETS)
        },
        "candidates": reg_results,
        # Sample for scatter plots
        "y_test_sample": Yr_te.reset_index(drop=True).to_dict(orient="list"),
        "y_pred_sample": pd.DataFrame(Yr_pred, columns=REGRESSION_TARGETS).to_dict(orient="list"),
    }
    best_reg.fit(Xr, Yr)  # final fit on all data

    # -------- IsolationForest on normals only --------
    normals = data[data[TARGET_STATE] == 0][INPUT_FEATURES]
    if len(normals) < 10:
        # Fall back to all data if normals too sparse
        iso_train = data[INPUT_FEATURES]
    else:
        iso_train = normals
    iso = IsolationForest(
        n_estimators=200, contamination="auto", random_state=42, n_jobs=-1
    )
    iso.fit(iso_train)

    meta = {
        "clf_name": best_clf_name,
        "reg_name": best_reg_name,
        "clf_eval": clf_eval,
        "reg_eval": reg_eval,
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_hash": dataset_hash_str,
        "n_samples": int(len(data)),
    }
    return TrainedBundle(clf=best_clf, reg=best_reg, iso=iso, meta=meta)


def _feature_importance(model, feature_names: list[str]) -> dict[str, float]:
    if hasattr(model, "feature_importances_"):
        return dict(zip(feature_names, [float(v) for v in model.feature_importances_]))
    return {}


# =============================================================================
# Persistence
# =============================================================================


def save_bundle(bundle: TrainedBundle) -> None:
    """Persist the bundle to disk (joblib + meta.json)."""
    joblib.dump(bundle.clf, CLF_PATH, compress=3)
    joblib.dump(bundle.reg, REG_PATH, compress=3)
    joblib.dump(bundle.iso, ISO_PATH, compress=3)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(bundle.meta, f, indent=2, default=str)


def load_bundle() -> TrainedBundle | None:
    """Load a previously saved bundle, or None if any artifact is missing/corrupt."""
    if not (os.path.isfile(CLF_PATH) and os.path.isfile(REG_PATH) and os.path.isfile(ISO_PATH)):
        return None
    try:
        clf = joblib.load(CLF_PATH)
        reg = joblib.load(REG_PATH)
        iso = joblib.load(ISO_PATH)
        meta = {}
        if os.path.isfile(META_PATH):
            with open(META_PATH, "r", encoding="utf-8") as f:
                meta = json.load(f)
        return TrainedBundle(clf=clf, reg=reg, iso=iso, meta=meta)
    except Exception:
        return None


def need_retrain(current_hash: str) -> bool:
    """Return True if no saved bundle exists or its hash differs from current_hash."""
    if not os.path.isfile(META_PATH):
        return True
    try:
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        return meta.get("dataset_hash") != current_hash
    except Exception:
        return True
