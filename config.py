"""Project-wide constants: paths, columns, thresholds, colors."""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Paths (resolved relative to project root = parent of this modules/ folder)
# ---------------------------------------------------------------------------

PROJECT_ROOT: str = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH: str = os.path.join(PROJECT_ROOT, "dataset.xlsx")
MODELS_DIR: str = os.path.join(PROJECT_ROOT, "models")
REPORTS_DIR: str = os.path.join(PROJECT_ROOT, "reports")
SHEET_NAME: str = "Data_IA_1000"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

INPUT_FEATURES: list[str] = [
    "Debit_actuel_t_h",
    "Pression_actuelle_bar",
    "Temperature_actuelle_C",
    "Puissance_moteur_kW",
    "Vibration_mm_s",
    "Humidite_matiere_pct",
    "Finesse_refus_pct",
]

# Operator-controlled (sliders)
OPERATOR_VARS: list[str] = [
    "Debit_actuel_t_h",
    "Pression_actuelle_bar",
    "Temperature_actuelle_C",
]

# Outcome variables (not directly set — derived targets/ranges from normals)
OUTCOME_VARS: list[str] = [
    "Puissance_moteur_kW",
    "Vibration_mm_s",
    "Humidite_matiere_pct",
    "Finesse_refus_pct",
]

TARGET_STATE: str = "Etat_broyeur"

REGRESSION_TARGETS: list[str] = [
    "Debit_recommande_t_h",
    "Pression_recommandee_bar",
    "Temperature_recommandee_C",
]

# Friendly labels (key -> (label_en, unit))
VAR_META: dict[str, dict[str, str]] = {
    "Debit_actuel_t_h":        {"label_en": "Feed rate",      "label_fr": "Débit",          "label_ar": "معدل التغذية",   "unit": "t/h"},
    "Pression_actuelle_bar":   {"label_en": "Pressure",       "label_fr": "Pression",       "label_ar": "الضغط",          "unit": "bar"},
    "Temperature_actuelle_C":  {"label_en": "Temperature",    "label_fr": "Température",    "label_ar": "درجة الحرارة",    "unit": "°C"},
    "Puissance_moteur_kW":     {"label_en": "Motor power",    "label_fr": "Puissance",      "label_ar": "قدرة المحرك",     "unit": "kW"},
    "Vibration_mm_s":          {"label_en": "Vibration",      "label_fr": "Vibration",      "label_ar": "الاهتزاز",        "unit": "mm/s"},
    "Humidite_matiere_pct":    {"label_en": "Material humidity", "label_fr": "Humidité",   "label_ar": "رطوبة المادة",     "unit": "%"},
    "Finesse_refus_pct":       {"label_en": "Fineness reject", "label_fr": "Finesse refus", "label_ar": "نسبة الرفض",      "unit": "%"},
}

# Component mapping for component-level risk
COMPONENT_VARS: dict[str, list[str]] = {
    "Motor":       ["Puissance_moteur_kW"],
    "Bearings":    ["Vibration_mm_s"],
    "Hydraulics":  ["Pression_actuelle_bar", "Temperature_actuelle_C"],
    "Feed_System": ["Debit_actuel_t_h", "Humidite_matiere_pct", "Finesse_refus_pct"],
}

# ---------------------------------------------------------------------------
# Colors — light & dark theme palettes
# ---------------------------------------------------------------------------

# Status colors (theme-independent)
STATUS = {
    "green":  "#16a34a",   # healthy / normal
    "yellow": "#eab308",   # watch
    "orange": "#f97316",   # risk
    "red":    "#dc2626",   # critical
    "info":   "#2563eb",
}

THEMES: dict[str, dict[str, str]] = {
    "light": {
        # Surfaces  — soft grey-blue, never pure white
        "bg":            "#eef1f6",
        "bg_gradient":   "linear-gradient(180deg, #eef1f6 0%, #e7ebf2 100%)",
        "surface":       "#f8fafc",          # cards
        "surface_alt":   "#e7ebf2",          # sidebar / subtle panels
        "border":        "#dde3ec",
        "border_soft":   "#d8dfe9",
        # Text
        "text":          "#1e293b",          # dark slate (not pure black)
        "text_dim":      "#64748b",
        "text_muted":    "#94a3b8",
        # Brand
        "accent":        "#2563eb",
        "accent_2":      "#4f46e5",
        "accent_grad":   "linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)",
        "accent_tint":   "rgba(37, 99, 235, 0.10)",
        # Shadows — softer / subtler
        "shadow":        "0 2px 12px rgba(15,23,42,0.06)",
        "shadow_hover":  "0 4px 18px rgba(15,23,42,0.10), 0 8px 28px rgba(37,99,235,0.08)",
        # Plotly
        "chart_grid":    "rgba(15,23,42,0.06)",
        "chart_paper":   "rgba(0,0,0,0)",
        "chart_plot":    "rgba(0,0,0,0)",
        "chart_text":    "#475569",
        "chart_text_dim":"#64748b",
        "scrollbar":     "#cbd5e1",
        # Table-specific
        "table_head":    "#e3e8f0",
        "table_row":     "#f8fafc",
        "table_row_alt": "#f1f4f9",
    },
    "dark": {
        # Surfaces
        "bg":            "#0a0e1a",
        "bg_gradient":   "linear-gradient(135deg, #0a0e1a 0%, #131a2e 100%)",
        "surface":       "linear-gradient(145deg, #1a2235 0%, #141b2b 100%)",
        "surface_alt":   "#141b2b",
        "border":        "rgba(255,255,255,0.08)",
        "border_soft":   "rgba(255,255,255,0.04)",
        # Text
        "text":          "#f1f5f9",
        "text_dim":      "#94a3b8",
        "text_muted":    "#64748b",
        # Brand
        "accent":        "#38bdf8",
        "accent_2":      "#6366f1",
        "accent_grad":   "linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)",
        "accent_tint":   "rgba(56, 189, 248, 0.12)",
        # Shadows
        "shadow":        "0 1px 3px rgba(0,0,0,0.25), 0 6px 24px rgba(0,0,0,0.35)",
        "shadow_hover":  "0 4px 12px rgba(0,0,0,0.35), 0 12px 32px rgba(56,189,248,0.18)",
        # Plotly
        "chart_grid":    "rgba(255,255,255,0.06)",
        "chart_paper":   "rgba(0,0,0,0)",
        "chart_plot":    "rgba(0,0,0,0)",
        "chart_text":    "#e2e8f0",
        "chart_text_dim":"#94a3b8",
        "scrollbar":     "rgba(255,255,255,0.15)",
        # Table-specific
        "table_head":    "rgba(56,189,248,0.10)",
        "table_row":     "rgba(255,255,255,0.02)",
        "table_row_alt": "rgba(255,255,255,0.04)",
    },
}

# Plotly colorway used everywhere
CHART_COLORWAY = ["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f87171", "#c084fc"]

# Backwards-compat shim: legacy COLORS dict resolves to light theme + status
COLORS = {
    "green":  STATUS["green"],
    "yellow": STATUS["yellow"],
    "orange": STATUS["orange"],
    "red":    STATUS["red"],
    "blue":   STATUS["info"],
    "bg_dark":   THEMES["dark"]["bg"],
    "bg_panel":  THEMES["dark"]["surface_alt"],
    "bg_panel2": THEMES["dark"]["surface_alt"],
    "border":    THEMES["light"]["border"],
    "text":      THEMES["light"]["text"],
    "text_dim":  THEMES["light"]["text_dim"],
    "accent":    THEMES["light"]["accent"],
}


def get_theme(name: str) -> dict[str, str]:
    """Return the palette dict for *name* ('light' or 'dark')."""
    return THEMES.get(name, THEMES["light"])

# ---------------------------------------------------------------------------
# Degradation score bands
# ---------------------------------------------------------------------------

DEGRADATION_BANDS = [
    {"min": 0,  "max": 25,  "color": COLORS["green"],  "key": "band_healthy"},
    {"min": 25, "max": 50,  "color": COLORS["yellow"], "key": "band_watch"},
    {"min": 50, "max": 75,  "color": COLORS["orange"], "key": "band_risk"},
    {"min": 75, "max": 101, "color": COLORS["red"],    "key": "band_critical"},
]

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

APP_VERSION: str = "3.0"
SESSION_HISTORY_MAX: int = 50
TREND_SLOPE_WARNING: float = 1.5  # score points per step
