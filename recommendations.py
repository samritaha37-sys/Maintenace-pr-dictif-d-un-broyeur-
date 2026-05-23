"""Compute targets, ranges and a prioritized corrective action plan."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from config import (
    INPUT_FEATURES,
    OPERATOR_VARS,
    OUTCOME_VARS,
    REGRESSION_TARGETS,
    TARGET_STATE,
)


# =============================================================================
# Per-variable target/range computation (from NORMAL subset)
# =============================================================================


@dataclass
class VarReference:
    """Reference statistics for a single variable, computed from NORMAL rows."""

    var: str
    target: float          # median in NORMAL
    q1: float
    q3: float
    iqr: float
    soft_min: float        # = q1
    soft_max: float        # = q3
    hard_min: float        # = q1 - 1.5*IQR
    hard_max: float        # = q3 + 1.5*IQR


def build_references(data: pd.DataFrame) -> dict[str, VarReference]:
    """Compute target & range references for every input variable from normal rows."""
    refs: dict[str, VarReference] = {}
    normals = data[data[TARGET_STATE] == 0]
    if len(normals) < 5:
        # Fall back to whole population if normals are too few
        normals = data
    for v in INPUT_FEATURES:
        s = normals[v]
        q1 = float(s.quantile(0.25))
        q3 = float(s.quantile(0.75))
        iqr = q3 - q1 if (q3 - q1) > 0 else float(s.std() or 1.0)
        refs[v] = VarReference(
            var=v,
            target=float(s.median()),
            q1=q1,
            q3=q3,
            iqr=iqr,
            soft_min=q1,
            soft_max=q3,
            hard_min=q1 - 1.5 * iqr,
            hard_max=q3 + 1.5 * iqr,
        )
    return refs


def variable_status(value: float, ref: VarReference) -> str:
    """Return one of: 'green', 'orange', 'red' for the current value."""
    if ref.soft_min <= value <= ref.soft_max:
        return "green"
    if ref.hard_min <= value <= ref.hard_max:
        return "orange"
    return "red"


# =============================================================================
# Combined recommendation row (used by the live tab table)
# =============================================================================


def build_recommendation_table(
    inputs: dict[str, float],
    reg_prediction: dict[str, float] | None,
    refs: dict[str, VarReference],
) -> list[dict]:
    """Build a list of row dicts mixing regressor outputs (for operator vars) with
    normal-band targets/ranges (for outcome vars).
    """
    rows: list[dict] = []
    rec_map = {
        "Debit_actuel_t_h":       reg_prediction.get("Debit_recommande_t_h")       if reg_prediction else None,
        "Pression_actuelle_bar":  reg_prediction.get("Pression_recommandee_bar")  if reg_prediction else None,
        "Temperature_actuelle_C": reg_prediction.get("Temperature_recommandee_C") if reg_prediction else None,
    }
    for v in INPUT_FEATURES:
        cur = float(inputs[v])
        ref = refs[v]
        recommended = rec_map.get(v, ref.target)
        if recommended is None:
            recommended = ref.target
        rows.append(
            {
                "variable": v,
                "current": cur,
                "recommended": float(recommended),
                "soft_min": ref.soft_min,
                "soft_max": ref.soft_max,
                "hard_min": ref.hard_min,
                "hard_max": ref.hard_max,
                "status": variable_status(cur, ref),
                "is_operator": v in OPERATOR_VARS,
            }
        )
    return rows


# =============================================================================
# Prioritized action plan
# =============================================================================


@dataclass
class ActionStep:
    step: int
    variable: str
    text: str
    severity: str  # green/yellow/orange/red


def build_action_plan(
    inputs: dict[str, float],
    recommendations: list[dict],
    shap_importance: dict[str, float] | None,
    is_anomaly: bool,
) -> list[ActionStep]:
    """Return an ordered list of action steps. Empty if state is normal."""
    if not is_anomaly:
        return []

    # Priority weight = |SHAP| if available, else delta magnitude / IQR
    def weight(row: dict) -> float:
        if shap_importance and row["variable"] in shap_importance:
            return abs(shap_importance[row["variable"]])
        span = max(row["soft_max"] - row["soft_min"], 1e-6)
        return abs(row["recommended"] - row["current"]) / span

    # Only act on variables that are out of range OR have non-trivial recommendation delta
    candidates = []
    for row in recommendations:
        delta = row["recommended"] - row["current"]
        rel = abs(delta) / max(abs(row["recommended"]), 1e-6)
        if row["status"] != "green" or rel > 0.02:
            candidates.append((weight(row), row, delta))
    candidates.sort(key=lambda x: -x[0])

    steps: list[ActionStep] = []
    for i, (_, row, delta) in enumerate(candidates, start=1):
        var = row["variable"]
        cur = row["current"]
        rec = row["recommended"]
        unit = _unit(var)
        pct = (delta / cur * 100) if cur != 0 else 0.0

        # Operator-controlled variable → setpoint instruction
        if var in OPERATOR_VARS:
            verb = "Reduce" if delta < 0 else "Increase"
            text = (
                f"{verb} {_human(var)} from {cur:.2f} {unit} to {rec:.2f} {unit} "
                f"({pct:+.1f}%). Wait 5 minutes, then re-check sensor readings."
            )
            severity = "orange" if abs(pct) > 5 else "yellow"
        # Outcome variable → diagnostic / monitor instruction
        else:
            if row["status"] == "red":
                severity = "red"
                text = (
                    f"{_human(var)} is critically out of band ({cur:.2f} {unit}, "
                    f"target ≈ {rec:.2f}). Schedule mechanical inspection within 24h."
                )
            elif row["status"] == "orange":
                severity = "orange"
                text = (
                    f"{_human(var)} drifting out of normal range "
                    f"({cur:.2f} {unit}, target ≈ {rec:.2f}). Monitor closely."
                )
            else:
                severity = "yellow"
                text = (
                    f"Verify {_human(var)} sensor — value {cur:.2f} {unit} differs "
                    f"from typical {rec:.2f} {unit}."
                )

        steps.append(ActionStep(step=i, variable=var, text=text, severity=severity))

    # Always add a final verification step
    steps.append(
        ActionStep(
            step=len(steps) + 1,
            variable="*",
            text="After applying all setpoints, wait 10 minutes and re-run the AI diagnosis to confirm the mill returns to NORMAL.",
            severity="yellow",
        )
    )
    return steps


# =============================================================================
# Helpers
# =============================================================================


def _human(var: str) -> str:
    from .config import VAR_META
    return VAR_META.get(var, {}).get("label_en", var)


def _unit(var: str) -> str:
    from .config import VAR_META
    return VAR_META.get(var, {}).get("unit", "")
