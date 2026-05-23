"""SHAP wrappers for the classifier."""

from __future__ import annotations

import warnings
from typing import Any

import numpy as np
import pandas as pd

from config import INPUT_FEATURES

warnings.filterwarnings("ignore")

try:
    import shap
    HAS_SHAP = True
except Exception:
    HAS_SHAP = False


_EXPLAINER_CACHE: dict[int, Any] = {}


def get_explainer(clf):
    """Return (and cache) a SHAP TreeExplainer for *clf*. None on failure."""
    if not HAS_SHAP:
        return None
    key = id(clf)
    if key in _EXPLAINER_CACHE:
        return _EXPLAINER_CACHE[key]
    try:
        explainer = shap.TreeExplainer(clf)
    except Exception:
        return None
    _EXPLAINER_CACHE[key] = explainer
    return explainer


def explain_prediction(clf, x_row: pd.DataFrame) -> dict[str, float] | None:
    """Return a dict {feature: shap_value} for the positive (anomaly) class.

    Returns None if SHAP is unavailable or fails.
    """
    explainer = get_explainer(clf)
    if explainer is None:
        return None
    try:
        sv = explainer.shap_values(x_row)
    except Exception:
        return None

    # Normalise to a 1D array aligned to INPUT_FEATURES for the positive class
    arr = sv
    if isinstance(arr, list):  # binary clf returns list of two arrays (rf, xgb in some versions)
        arr = arr[1] if len(arr) > 1 else arr[0]
    arr = np.asarray(arr)
    if arr.ndim == 3:  # (samples, features, classes)
        arr = arr[..., -1]
    if arr.ndim == 2:
        arr = arr[0]
    arr = np.asarray(arr).flatten()
    if arr.size != len(INPUT_FEATURES):
        return None
    return {f: float(arr[i]) for i, f in enumerate(INPUT_FEATURES)}


def expected_value(clf) -> float | None:
    """Return the explainer expected value for the positive class."""
    explainer = get_explainer(clf)
    if explainer is None:
        return None
    try:
        ev = explainer.expected_value
        if isinstance(ev, (list, np.ndarray)):
            ev = ev[1] if len(ev) > 1 else ev[0]
        return float(ev)
    except Exception:
        return None
