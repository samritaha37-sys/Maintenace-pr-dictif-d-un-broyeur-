"""High-level prediction pipeline: state, degradation, component risks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from config import (
    COMPONENT_VARS,
    DEGRADATION_BANDS,
    INPUT_FEATURES,
    REGRESSION_TARGETS,
)
from recommendations import VarReference


@dataclass
class PredictionResult:
    """Container for every output of a single prediction run."""

    inputs: dict[str, float]
    is_anomaly: int                       # 0 or 1
    confidence: float                     # confidence of the predicted class (0–1)
    proba_anomaly: float                  # probability of anomaly (0–1)
    iso_score: float                      # IsolationForest score, normalised 0–1 (higher = more anomalous)
    degradation_score: float              # 0–100
    band: dict                            # entry from DEGRADATION_BANDS
    component_risks: dict[str, float]     # {component: score 0–100}
    regression_recommendation: dict[str, float]   # raw regressor output


def _classifier_predict(clf, x_row: pd.DataFrame) -> tuple[int, float, float]:
    pred = int(clf.predict(x_row)[0])
    try:
        proba = clf.predict_proba(x_row)[0]
        # classes_ may not be [0,1] in some weird cases, but standard for our clf
        if hasattr(clf, "classes_"):
            classes = list(clf.classes_)
            p_anom = float(proba[classes.index(1)]) if 1 in classes else float(proba[-1])
            p_pred = float(proba[classes.index(pred)]) if pred in classes else float(proba.max())
        else:
            p_anom = float(proba[1]) if len(proba) > 1 else 0.0
            p_pred = float(proba.max())
        return pred, p_pred, p_anom
    except Exception:
        return pred, 1.0, float(pred)


def _iso_score(iso, x_row: pd.DataFrame) -> float:
    """Normalised anomaly score in [0,1] (1 = strongly anomalous)."""
    try:
        # higher score_samples = more normal. Negate, then sigmoid-like squash.
        raw = float(-iso.score_samples(x_row)[0])
        # Clamp using tanh-ish: map roughly to [0,1]
        return float(1.0 / (1.0 + np.exp(-raw)))
    except Exception:
        return 0.5


def _normalised_distance(value: float, ref: VarReference) -> float:
    """Distance from normal median in IQR units, capped at 3, then mapped to [0,1]."""
    iqr = ref.iqr if ref.iqr > 0 else 1.0
    d = abs(value - ref.target) / iqr
    return float(min(d, 3.0) / 3.0)


def _regressor_predict(reg, x_row_with_state: pd.DataFrame) -> dict[str, float]:
    try:
        pred = reg.predict(x_row_with_state)[0]
        return {t: float(pred[i]) for i, t in enumerate(REGRESSION_TARGETS)}
    except Exception:
        return {t: float("nan") for t in REGRESSION_TARGETS}


def _band_for(score: float) -> dict:
    for b in DEGRADATION_BANDS:
        if b["min"] <= score < b["max"]:
            return b
    return DEGRADATION_BANDS[-1]


def _component_risk(component_features: list[str], inputs: dict[str, float],
                    refs: dict[str, VarReference]) -> float:
    """Average normalised distance across the component's features → 0–100."""
    if not component_features:
        return 0.0
    distances = [_normalised_distance(inputs[v], refs[v]) for v in component_features if v in refs]
    if not distances:
        return 0.0
    return float(np.mean(distances) * 100.0)


def run_prediction(
    bundle,
    inputs: dict[str, float],
    refs: dict[str, VarReference],
    weights: tuple[float, float, float] = (0.5, 0.2, 0.3),
) -> PredictionResult:
    """End-to-end prediction. *weights* = (classifier, iso, distance) for the degradation score."""
    x_row = pd.DataFrame([{f: inputs[f] for f in INPUT_FEATURES}])

    pred, conf, p_anom = _classifier_predict(bundle.clf, x_row)
    iso = _iso_score(bundle.iso, x_row)

    # Distance component
    dists = [_normalised_distance(inputs[v], refs[v]) for v in INPUT_FEATURES if v in refs]
    distance_score = float(np.mean(dists)) if dists else 0.0

    w_clf, w_iso, w_dist = weights
    total_w = w_clf + w_iso + w_dist
    degradation = (w_clf * p_anom + w_iso * iso + w_dist * distance_score) / total_w * 100.0
    degradation = float(max(0.0, min(100.0, degradation)))

    band = _band_for(degradation)
    comp_risks = {
        comp: _component_risk(vars_, inputs, refs)
        for comp, vars_ in COMPONENT_VARS.items()
    }

    # Regressor: needs the state feature
    x_with_state = x_row.copy()
    x_with_state["Etat_broyeur"] = pred
    reg_pred = _regressor_predict(bundle.reg, x_with_state)

    return PredictionResult(
        inputs=inputs,
        is_anomaly=pred,
        confidence=conf,
        proba_anomaly=p_anom,
        iso_score=iso,
        degradation_score=degradation,
        band=band,
        component_risks=comp_risks,
        regression_recommendation=reg_pred,
    )


def trend_slope(scores: list[float], window: int = 10) -> float:
    """Linear-regression slope on the last *window* scores. 0 if insufficient data."""
    if len(scores) < 3:
        return 0.0
    s = scores[-window:]
    x = np.arange(len(s))
    return float(np.polyfit(x, s, 1)[0])
