"""PDF report generation (ReportLab)."""

from __future__ import annotations

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config import APP_VERSION, INPUT_FEATURES, REPORTS_DIR, VAR_META


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(
        name="Title2",
        parent=s["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=colors.HexColor("#0a1b3a"),
        spaceAfter=4,
    ))
    s.add(ParagraphStyle(
        name="Sub",
        parent=s["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#555"),
        spaceAfter=10,
    ))
    s.add(ParagraphStyle(
        name="H2",
        parent=s["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#102554"),
        spaceBefore=10,
        spaceAfter=6,
    ))
    s.add(ParagraphStyle(name="Body", parent=s["Normal"], fontSize=9.5, leading=13))
    return s


def _status_color(status: str):
    return {
        "green":  colors.HexColor("#16a34a"),
        "yellow": colors.HexColor("#eab308"),
        "orange": colors.HexColor("#f97316"),
        "red":    colors.HexColor("#dc2626"),
    }.get(status, colors.grey)


def generate_pdf_report(
    *,
    operator: str,
    mill_id: str,
    inputs: dict[str, float],
    prediction,                  # PredictionResult
    recommendations: list[dict],
    action_plan: list,           # list[ActionStep]
    diagnoses: list,             # list[Diagnosis]
    bundle_meta: dict,
    output_dir: str = REPORTS_DIR,
) -> str:
    """Build the PDF and return its absolute path."""
    os.makedirs(output_dir, exist_ok=True)
    fname = f"mill_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    path = os.path.join(output_dir, fname)

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=1.6*cm, rightMargin=1.6*cm,
        topMargin=1.4*cm, bottomMargin=1.4*cm,
        title=f"Mill Report — {mill_id or 'N/A'}",
    )
    st = _styles()
    story = []

    # ---- Header ----
    story.append(Paragraph("Pebble Mill — AI Diagnostic Report", st["Title2"]))
    header_meta = (
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} &nbsp;|&nbsp; "
        f"Operator: <b>{operator or 'N/A'}</b> &nbsp;|&nbsp; Mill: <b>{mill_id or 'N/A'}</b>"
    )
    story.append(Paragraph(header_meta, st["Sub"]))

    # ---- Diagnosis summary ----
    state_text = "ANOMALY" if prediction.is_anomaly else "NORMAL"
    state_color = "#dc2626" if prediction.is_anomaly else "#16a34a"
    story.append(Paragraph("Diagnosis", st["H2"]))
    diag_table = Table(
        [
            ["Predicted state", state_text],
            ["Confidence", f"{prediction.confidence*100:.1f} %"],
            ["Anomaly probability", f"{prediction.proba_anomaly*100:.1f} %"],
            ["Degradation score", f"{prediction.degradation_score:.1f} / 100"],
            ["Verdict", prediction.band.get("key", "")],
        ],
        colWidths=[5*cm, 11*cm],
    )
    diag_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2f8")),
        ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor(state_color)),
        ("FONT", (1, 0), (1, 0), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(diag_table)

    # ---- Component risks ----
    story.append(Paragraph("Component risks", st["H2"]))
    comp_rows = [["Component", "Risk (0–100)"]]
    for c, v in prediction.component_risks.items():
        comp_rows.append([c.replace("_", " "), f"{v:.1f}"])
    comp_table = Table(comp_rows, colWidths=[8*cm, 8*cm])
    comp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102554")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ]))
    story.append(comp_table)

    # ---- Input values ----
    story.append(Paragraph("Operating inputs", st["H2"]))
    in_rows = [["Variable", "Value"]]
    for v in INPUT_FEATURES:
        meta = VAR_META.get(v, {})
        in_rows.append([f"{meta.get('label_en', v)} ({meta.get('unit', '')})", f"{inputs[v]:.2f}"])
    in_table = Table(in_rows, colWidths=[10*cm, 6*cm])
    in_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102554")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ]))
    story.append(in_table)

    # ---- Recommendations ----
    story.append(Paragraph("Recommendations & ranges", st["H2"]))
    rec_rows = [["Variable", "Current", "Target", "Range (Q1–Q3)", "Status"]]
    rec_styles = []
    for i, row in enumerate(recommendations, start=1):
        meta = VAR_META.get(row["variable"], {})
        unit = meta.get("unit", "")
        rec_rows.append([
            meta.get("label_en", row["variable"]),
            f"{row['current']:.2f} {unit}",
            f"{row['recommended']:.2f} {unit}",
            f"{row['soft_min']:.2f} – {row['soft_max']:.2f}",
            row["status"].upper(),
        ])
        rec_styles.append(("TEXTCOLOR", (4, i), (4, i), _status_color(row["status"])))
        rec_styles.append(("FONT", (4, i), (4, i), "Helvetica-Bold"))
    rec_table = Table(rec_rows, colWidths=[4*cm, 3*cm, 3*cm, 4*cm, 2*cm])
    base_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102554")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ] + rec_styles
    rec_table.setStyle(TableStyle(base_style))
    story.append(rec_table)

    # ---- Action plan ----
    if action_plan:
        story.append(Paragraph("Prioritized action plan", st["H2"]))
        for step in action_plan:
            text = f"<b>Step {step.step}.</b> {step.text}"
            story.append(Paragraph(text, st["Body"]))
            story.append(Spacer(1, 3))

    # ---- Root cause ----
    if diagnoses:
        story.append(Paragraph("Root cause analysis", st["H2"]))
        for d in diagnoses:
            line = f"<b>[{d.severity.upper()} · {d.component}]</b> {d.text_en}"
            story.append(Paragraph(line, st["Body"]))
            story.append(Spacer(1, 3))

    # ---- Footer ----
    story.append(Spacer(1, 14))
    footer = (
        f"<font color='#777' size='8'>Model: {bundle_meta.get('clf_name', '?')} · "
        f"Trained: {bundle_meta.get('trained_at', '?')} · "
        f"Dataset hash: {bundle_meta.get('dataset_hash', '?')} · "
        f"App v{APP_VERSION}</font>"
    )
    story.append(Paragraph(footer, st["Sub"]))

    doc.build(story)
    return path
