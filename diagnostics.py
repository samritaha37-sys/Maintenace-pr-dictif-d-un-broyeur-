"""Rule-based root-cause analysis. Easy to extend by adding entries to RULES."""

from __future__ import annotations

from dataclasses import dataclass

from recommendations import VarReference


# =============================================================================
# Rule definition
# =============================================================================


@dataclass
class Diagnosis:
    rule_id: str
    component: str
    severity: str           # "low" | "medium" | "high" | "critical"
    text_en: str
    text_fr: str
    text_ar: str


def _high(value: float, ref: VarReference) -> bool:
    return value > ref.soft_max


def _very_high(value: float, ref: VarReference) -> bool:
    return value > ref.hard_max


def _low(value: float, ref: VarReference) -> bool:
    return value < ref.soft_min


def _very_low(value: float, ref: VarReference) -> bool:
    return value < ref.hard_min


# Each rule = predicate(inputs, refs) -> Diagnosis | None
def _r_bearing(inputs, refs) -> Diagnosis | None:
    if _high(inputs["Vibration_mm_s"], refs["Vibration_mm_s"]) and _high(
        inputs["Puissance_moteur_kW"], refs["Puissance_moteur_kW"]
    ):
        sev = "critical" if _very_high(inputs["Vibration_mm_s"], refs["Vibration_mm_s"]) else "high"
        return Diagnosis(
            rule_id="bearing_wear",
            component="Bearings",
            severity=sev,
            text_en="High vibration combined with high motor power — likely bearing wear or unbalanced load.",
            text_fr="Vibration élevée et puissance moteur élevée — usure de palier ou charge déséquilibrée probable.",
            text_ar="اهتزاز عال مع قدرة محرك مرتفعة — احتمال تآكل المحامل أو حمل غير متوازن.",
        )
    return None


def _r_cooling(inputs, refs) -> Diagnosis | None:
    if _high(inputs["Temperature_actuelle_C"], refs["Temperature_actuelle_C"]) and _high(
        inputs["Pression_actuelle_bar"], refs["Pression_actuelle_bar"]
    ):
        sev = "high" if _very_high(inputs["Temperature_actuelle_C"], refs["Temperature_actuelle_C"]) else "medium"
        return Diagnosis(
            rule_id="cooling_issue",
            component="Hydraulics",
            severity=sev,
            text_en="High temperature with high pressure — possible cooling-system issue or excessive grinding force.",
            text_fr="Température et pression élevées — problème de refroidissement ou force de broyage excessive.",
            text_ar="درجة حرارة وضغط مرتفعان — احتمال خلل في التبريد أو قوة طحن مفرطة.",
        )
    return None


def _r_wet_material(inputs, refs) -> Diagnosis | None:
    if _high(inputs["Humidite_matiere_pct"], refs["Humidite_matiere_pct"]) and _high(
        inputs["Finesse_refus_pct"], refs["Finesse_refus_pct"]
    ):
        return Diagnosis(
            rule_id="wet_material",
            component="Feed_System",
            severity="medium",
            text_en="High humidity with high fineness reject — wet material reducing grinding efficiency. Check pre-drying.",
            text_fr="Humidité élevée et finesse de refus élevée — matière humide réduisant l'efficacité du broyage. Vérifier le pré-séchage.",
            text_ar="رطوبة عالية مع رفض ناعم مرتفع — مادة رطبة تقلل كفاءة الطحن. افحص التجفيف الأولي.",
        )
    return None


def _r_slippage(inputs, refs) -> Diagnosis | None:
    if _low(inputs["Puissance_moteur_kW"], refs["Puissance_moteur_kW"]) and not _low(
        inputs["Debit_actuel_t_h"], refs["Debit_actuel_t_h"]
    ):
        return Diagnosis(
            rule_id="drive_slippage",
            component="Motor",
            severity="high",
            text_en="Low motor power despite normal feed rate — possible slippage in drive system or coupling.",
            text_fr="Puissance moteur faible malgré un débit normal — glissement possible dans la transmission.",
            text_ar="قدرة محرك منخفضة رغم تغذية طبيعية — احتمال انزلاق في نظام النقل.",
        )
    return None


def _r_overload(inputs, refs) -> Diagnosis | None:
    if _very_high(inputs["Debit_actuel_t_h"], refs["Debit_actuel_t_h"]) and _high(
        inputs["Puissance_moteur_kW"], refs["Puissance_moteur_kW"]
    ):
        return Diagnosis(
            rule_id="overload",
            component="Feed_System",
            severity="high",
            text_en="Feed rate above safe band with high motor power — mill is overloaded. Reduce feed.",
            text_fr="Débit au-dessus de la plage sûre avec puissance moteur élevée — broyeur en surcharge. Réduire le débit.",
            text_ar="معدل التغذية أعلى من النطاق الآمن مع قدرة محرك مرتفعة — حمل زائد. خفّض التغذية.",
        )
    return None


def _r_low_pressure(inputs, refs) -> Diagnosis | None:
    if _very_low(inputs["Pression_actuelle_bar"], refs["Pression_actuelle_bar"]):
        return Diagnosis(
            rule_id="hydraulic_leak",
            component="Hydraulics",
            severity="high",
            text_en="Pressure dangerously low — possible hydraulic leak or pump failure.",
            text_fr="Pression dangereusement basse — fuite hydraulique ou défaillance de pompe possible.",
            text_ar="ضغط منخفض بشكل خطر — احتمال تسرب هيدروليكي أو خلل في المضخة.",
        )
    return None


RULES = [_r_bearing, _r_cooling, _r_wet_material, _r_slippage, _r_overload, _r_low_pressure]


# =============================================================================
# Entry point
# =============================================================================


def diagnose(
    inputs: dict[str, float],
    refs: dict[str, VarReference],
) -> list[Diagnosis]:
    """Run every rule and return the list of triggered diagnoses."""
    out: list[Diagnosis] = []
    for rule in RULES:
        try:
            diag = rule(inputs, refs)
        except Exception:
            continue
        if diag is not None:
            out.append(diag)
    return out


def diagnosis_text(d: Diagnosis, lang: str = "en") -> str:
    return {"en": d.text_en, "fr": d.text_fr, "ar": d.text_ar}.get(lang, d.text_en)


SEVERITY_COLOR = {
    "low":      "#16a34a",
    "medium":   "#eab308",
    "high":     "#f97316",
    "critical": "#dc2626",
}
