"""Reusable, theme-aware UI components for the dashboard."""

from __future__ import annotations

import html

import plotly.graph_objects as go
import streamlit as st

from config import CHART_COLORWAY, STATUS, get_theme
from i18n import t
from styles import inject_css  # noqa: F401 (re-exported for backwards compat)


# =============================================================================
# Theme accessor
# =============================================================================


def current_theme_name() -> str:
    """Return 'light' or 'dark' from session_state, defaulting to 'light'."""
    return st.session_state.get("theme", "light")


def current_palette() -> dict[str, str]:
    return get_theme(current_theme_name())


# =============================================================================
# Section helpers
# =============================================================================


def section_header(icon: str, title: str) -> None:
    """Small section banner: icon chip + title + divider."""
    st.markdown(
        f"""
        <div class="section-header">
            <span class="icon">{html.escape(icon)}</span>
            <span class="title">{html.escape(title)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def app_header(title: str, subtitle: str, live: bool = True, live_text: str = "LIVE") -> None:
    """Top page header with gradient title."""
    live_html = (
        f'<div class="live-pill"><span class="dot"></span>{html.escape(live_text)}</div>'
        if live else ""
    )
    st.markdown(
        f"""
        <div class="app-header" style="display:flex; align-items:flex-end; justify-content:space-between; flex-wrap:wrap; gap:14px;">
            <div>
                <h1 class="app-title">{html.escape(title)}</h1>
                <div class="app-subtitle">{html.escape(subtitle)}</div>
            </div>
            <div>{live_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# KPI / metric card
# =============================================================================


def styled_metric(
    label: str,
    value: str,
    unit: str = "",
    delta: str | None = None,
    delta_dir: str = "flat",      # 'up' | 'down' | 'flat'
    sub: str | None = None,
    status: str = "",             # '' | 'green' | 'yellow' | 'orange' | 'red'
) -> None:
    """Render a clean rounded KPI card."""
    arrow = ""
    if delta:
        arrow = {"up": "▲", "down": "▼", "flat": "•"}.get(delta_dir, "•")
    delta_html = (
        f'<div class="metric-delta {delta_dir}">{arrow} {html.escape(delta)}</div>'
        if delta else ""
    )
    sub_html = f'<div class="metric-sub">{html.escape(sub)}</div>' if sub else ""
    unit_html = f'<span class="metric-unit">{html.escape(unit)}</span>' if unit else ""

    cls = f"metric-card {status}".strip()
    st.markdown(
        f"""
        <div class="{cls}">
            <div class="metric-label">{html.escape(label)}</div>
            <div class="metric-value">{html.escape(value)} {unit_html}</div>
            {delta_html}
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# Backwards-compat alias
def kpi_card(label, value, unit="", sub="", status="") -> None:
    styled_metric(label=label, value=value, unit=unit, sub=sub, status=status)


# =============================================================================
# Status card (NORMAL / ANOMALY)
# =============================================================================


def status_card(is_anomaly: bool, confidence: float, lang: str = "en") -> None:
    """Big rounded status card for the live tab."""
    if is_anomaly:
        cls, icon, label = "anomaly", "🚨", t("anomaly", lang)
    else:
        cls, icon, label = "normal", "✅", t("normal", lang)
    conf_text = f'{t("confidence", lang)}: <b>{confidence*100:.1f}%</b>'
    st.markdown(
        f"""
        <div class="status-card {cls}">
            <div class="row">
                <div class="icon">{icon}</div>
                <div class="col">
                    <div class="state-label">{t('state', lang)}</div>
                    <div class="state-value">{html.escape(label)}</div>
                    <div class="conf">{conf_text}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Backwards-compat alias
status_banner = status_card


# =============================================================================
# Verdict / time-to-failure card
# =============================================================================


def verdict_card(label: str, text: str, color: str) -> None:
    st.markdown(
        f"""
        <div class="verdict-card" style="border-left: 4px solid {color};">
            <div class="verdict-label">{html.escape(label)}</div>
            <div class="verdict-text" style="color:{color};">{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Action step
# =============================================================================


def action_step(number: int, text: str, severity: str = "yellow") -> None:
    """Numbered action card with a gradient badge."""
    sev = severity if severity in {"red", "orange", "yellow", "green"} else "yellow"
    st.markdown(
        f"""
        <div class="action-step-card {sev}">
            <div class="step-circle">{int(number)}</div>
            <div class="step-body">{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Diagnosis card
# =============================================================================


def diag_card(severity: str, component: str, text: str) -> None:
    sev = severity if severity in {"critical", "high", "medium", "low"} else "medium"
    st.markdown(
        f"""
        <div class="diag-card {sev}">
            <div class="diag-head">
                <span class="diag-tag {sev}">{html.escape(severity.upper())}</span>
                <span class="component">{html.escape(component)}</span>
            </div>
            <div class="text">{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Recommendation table (custom HTML)
# =============================================================================


def styled_recommendation_table(rows: list[dict], headers: dict[str, str]) -> None:
    """Render an HTML table for the live-tab recommendation block.

    *rows*: each dict has keys 'variable', 'current', 'recommended',
            'range', 'status' (already pre-formatted strings) and 'status_key'.
    *headers*: {'variable': 'Variable', 'current': 'Current', ...}
    """
    head_html = "".join(f"<th>{html.escape(headers[k])}</th>"
                        for k in ["variable", "current", "recommended", "range", "status"])
    body_html = ""
    for r in rows:
        pill_cls = r.get("status_key", "green")
        body_html += (
            "<tr>"
            f"<td><b>{html.escape(str(r['variable']))}</b></td>"
            f"<td>{html.escape(str(r['current']))}</td>"
            f"<td>{html.escape(str(r['recommended']))}</td>"
            f"<td>{html.escape(str(r['range']))}</td>"
            f"<td><span class='status-pill {pill_cls}'>{html.escape(str(r['status']))}</span></td>"
            "</tr>"
        )
    st.markdown(
        f"""
        <div class="rec-table">
            <table>
                <thead><tr>{head_html}</tr></thead>
                <tbody>{body_html}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Sidebar logo
# =============================================================================


def sidebar_logo(version: str) -> None:
    st.markdown(
        f"""
        <div class="sidebar-logo">
            <div class="gear">⚙</div>
            <div class="brand">PEBBLE MILL AI</div>
            <div class="version">v{html.escape(version)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_section(title: str) -> None:
    st.markdown(
        f'<div class="sidebar-section-title">{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# Footer
# =============================================================================


def app_footer(version: str, extra: str = "") -> None:
    st.markdown(
        f'<div class="app-footer">PEBBLE MILL AI · v{html.escape(version)} '
        f'· {html.escape(extra)}</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# Plotly theme application
# =============================================================================


def apply_chart_theme(fig, theme_name: str | None = None):
    """Apply the current theme (paper, plot, fonts, gridlines, colorway) to *fig*."""
    name = theme_name or current_theme_name()
    p = get_theme(name)
    fig.update_layout(
        paper_bgcolor=p["chart_paper"],
        plot_bgcolor=p["chart_plot"],
        font=dict(family="Inter, sans-serif", color=p["chart_text"], size=12),
        margin=dict(l=40, r=20, t=50, b=40),
        colorway=CHART_COLORWAY,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=p["chart_text"])),
    )
    fig.update_xaxes(
        gridcolor=p["chart_grid"], zerolinecolor=p["chart_grid"],
        linecolor=p["chart_grid"], tickfont=dict(color=p["chart_text_dim"]),
        title_font=dict(color=p["chart_text_dim"]),
    )
    fig.update_yaxes(
        gridcolor=p["chart_grid"], zerolinecolor=p["chart_grid"],
        linecolor=p["chart_grid"], tickfont=dict(color=p["chart_text_dim"]),
        title_font=dict(color=p["chart_text_dim"]),
    )
    return fig


# Backwards-compat alias
styled = apply_chart_theme


# =============================================================================
# Gauges
# =============================================================================


def _band_color_for(score: float) -> str:
    if score < 25:  return STATUS["green"]
    if score < 50:  return STATUS["yellow"]
    if score < 75:  return STATUS["orange"]
    return STATUS["red"]


def degradation_gauge(score: float, title: str = "Degradation"):
    """Big, clean degradation gauge — number is below the arc."""
    p = current_palette()
    band = _band_color_for(score)

    fig = go.Figure(go.Indicator(
        mode="gauge",
        value=score,
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickvals": [0, 25, 50, 75, 100],
                "tickfont": {"size": 10, "color": p["chart_text_dim"]},
                "tickcolor": p["chart_text_dim"],
            },
            "bar":      {"color": "rgba(0,0,0,0)", "thickness": 0.0},   # invisible bar
            "bgcolor":  "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  25],  "color": STATUS["green"]},
                {"range": [25, 50],  "color": STATUS["yellow"]},
                {"range": [50, 75],  "color": STATUS["orange"]},
                {"range": [75, 100], "color": STATUS["red"]},
            ],
            "threshold": {
                "line": {"color": p["text"], "width": 4},
                "thickness": 0.88,
                "value": score,
            },
        },
        domain={"x": [0, 1], "y": [0.32, 1.0]},
    ))

    fig.add_annotation(
        x=0.5, y=0.06, xref="paper", yref="paper",
        text=(f"<span style='font-family:Inter; font-size:42px; font-weight:800;"
              f" color:{band};'>{score:.1f}</span>"
              f"<span style='font-family:Inter; font-size:16px; color:{p['text_dim']};"
              f" font-weight:600;'> / 100</span>"),
        showarrow=False, align="center",
    )
    fig.add_annotation(
        x=0.5, y=1.06, xref="paper", yref="paper",
        text=(f"<span style='font-family:Inter; font-size:11px; "
              f"font-weight:700; letter-spacing:0.8px; "
              f"color:{p['text_dim']}; text-transform:uppercase;'>{title}</span>"),
        showarrow=False, align="center",
    )

    fig.update_layout(
        height=290,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        margin=dict(l=10, r=10, t=46, b=44),
    )
    return fig


def small_gauge(value: float, label: str, color: str | None = None):
    """Compact gauge used for component risks."""
    p = current_palette()
    if color is None:
        color = _band_color_for(value)

    fig = go.Figure(go.Indicator(
        mode="gauge",
        value=value,
        gauge={
            "axis": {
                "range": [0, 100],
                "tickfont": {"size": 9, "color": p["chart_text_dim"]},
                "tickcolor": p["chart_text_dim"],
                "tickvals": [0, 50, 100],
            },
            "bar":     {"color": "rgba(0,0,0,0)", "thickness": 0.0},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 25],   "color": "rgba(22,163,74,0.28)"},
                {"range": [25, 50],  "color": "rgba(234,179,8,0.32)"},
                {"range": [50, 75],  "color": "rgba(249,115,22,0.32)"},
                {"range": [75, 100], "color": "rgba(220,38,38,0.32)"},
            ],
            "threshold": {
                "line": {"color": p["text"], "width": 3},
                "thickness": 0.85, "value": value,
            },
        },
        domain={"x": [0, 1], "y": [0.30, 1.0]},
    ))
    fig.add_annotation(
        x=0.5, y=0.08, xref="paper", yref="paper",
        text=(f"<span style='font-family:Inter; font-size:24px; font-weight:800;"
              f" color:{color};'>{value:.0f}</span>"
              f"<span style='font-family:Inter; font-size:11px; color:{p['text_dim']};'> / 100</span>"),
        showarrow=False, align="center",
    )
    fig.add_annotation(
        x=0.5, y=1.08, xref="paper", yref="paper",
        text=(f"<span style='font-family:Inter; font-size:11px; font-weight:700; "
              f"letter-spacing:0.6px; color:{p['text_dim']}; "
              f"text-transform:uppercase;'>{label}</span>"),
        showarrow=False, align="center",
    )
    fig.update_layout(
        height=200,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        margin=dict(l=10, r=10, t=36, b=30),
    )
    return fig


# =============================================================================
# Legacy panel wrappers (kept so older code paths still render)
# =============================================================================


def panel_open(title: str) -> None:
    """Legacy: emit a section header (the new design uses cards, not panels)."""
    section_header("▸", title)


def panel_close() -> None:
    """Legacy no-op (panels are no longer wrapped)."""
    pass
