"""
Complete CSS stylesheet for the dashboard.

The single entry point is `inject_css(theme_name)`. Call it once per
Streamlit run (before rendering anything), passing 'light' or 'dark'.
"""

from __future__ import annotations

import streamlit as st

from config import STATUS, get_theme


def inject_css(theme_name: str = "light", rtl: bool = False) -> None:
    """Inject the full stylesheet for the chosen *theme_name*."""
    p = get_theme(theme_name)
    is_dark = theme_name == "dark"
    direction = "rtl" if rtl else "ltr"
    text_align = "right" if rtl else "left"

    # ---- Theme-conditional helpers ----
    sidebar_bg = (
        "linear-gradient(180deg, #0f1626 0%, #0a0e1a 100%)" if is_dark
        else "linear-gradient(180deg, #e7ebf2 0%, #dde3ec 100%)"
    )
    sidebar_border = p["border"]
    sidebar_text = p["text"]
    sidebar_text_dim = p["text_dim"]
    # Inputs: white in light mode is OK (contrast against grey-blue bg)
    input_bg = "rgba(255,255,255,0.04)" if is_dark else "#ffffff"
    input_border = p["border"]
    table_head    = p["table_head"]
    table_row     = p["table_row"]
    table_row_alt = p["table_row_alt"]

    css = f"""
<style>
/* ============================================================
   Google Font
============================================================ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ============================================================
   Globals — force Inter font everywhere with high specificity.
   Exclude Material icon containers so chevrons / arrows render as icons,
   not as raw text like "keyboard_arrow_down".
============================================================ */
html, body, [class*="css"], .stApp, .stMarkdown, .main,
button, input, textarea, select,
h1, h2, h3, h4, h5, h6,
p, span, div, label, td, th, li, a,
[class*="st-"], [class*="css-"], [data-testid] {{
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
}}

/* Keep Material icon fonts intact — these elements must use the icon font,
   not Inter, otherwise the ligature name shows as raw text. */
.material-icons,
.material-icons-outlined,
[class*="material-symbols"],
[data-testid="stIconMaterial"],
[data-testid="stExpanderToggleIcon"],
[data-testid="stExpanderIcon"],
[data-testid="StyledFullScreenButton"] svg,
[data-baseweb="icon"],
i.material-icons,
span.material-symbols-rounded,
span.material-symbols-outlined,
span.material-symbols-sharp,
[class*="iconMaterial"],
[class*="MaterialIcon"] {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined',
                 'Material Icons', 'Material Icons Outlined' !important;
    font-feature-settings: 'liga' !important;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    letter-spacing: 0 !important;
    text-transform: none !important;
    line-height: 1 !important;
}}

html, body, .stApp {{
    direction: {direction};
    text-align: {text_align};
    color: {p['text']};
    letter-spacing: -0.01em;
}}

.stApp {{
    background: {p['bg']} !important;
    background-image: {p['bg_gradient']} !important;
    background-attachment: fixed;
}}

.main .block-container {{
    max-width: 1400px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}}

/* Hide Streamlit chrome — but KEEP the sidebar toggle visible */
#MainMenu, footer {{ visibility: hidden; height: 0; }}
header[data-testid="stHeader"] {{
    background: transparent !important;
    height: auto !important;
}}
[data-testid="stToolbar"] {{ display: none !important; }}

/* Make the sidebar-collapse / expand control clearly visible */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
[data-testid="stExpandSidebarButton"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
    background: {p['surface']} !important;
    border: 1px solid {p['border']} !important;
    border-radius: 10px !important;
    box-shadow: {p['shadow']};
    color: {p['accent']} !important;
}}
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="stSidebarCollapseButton"] button {{
    color: {p['accent']} !important;
}}

/* Typography weights */
h1, h2, h3, h4, h5 {{
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
    color: {p['text']} !important;
}}
p, span, div, label, li {{ color: {p['text']}; font-weight: 400; }}
strong, b {{ font-weight: 700; }}
/* Numbers / metric values */
.metric-value, .state-value, .verdict-text, .step-circle,
[data-testid="stMetricValue"] {{
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}}

/* Smooth transitions on most things */
button, .stButton button, .stDownloadButton button,
[data-baseweb="select"], input, textarea,
.metric-card, .status-card, .action-step-card,
.section-pill, .stTabs [data-baseweb="tab"] {{
    transition: all 0.2s ease !important;
}}

/* Custom scrollbar */
::-webkit-scrollbar       {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
    background: {p['scrollbar']};
    border-radius: 999px;
    border: 2px solid transparent;
    background-clip: content-box;
}}
::-webkit-scrollbar-thumb:hover {{ background: {p['accent']}; background-clip: content-box; }}

/* ============================================================
   App header (gradient title)
============================================================ */
.app-header {{
    margin: 0 0 24px 0;
    padding: 6px 0 20px 0;
    border-bottom: 1px solid {p['border']};
}}
.app-title {{
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0;
    background: {p['accent_grad']};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}}
.app-subtitle {{
    color: {p['text_dim']};
    font-size: 14px;
    margin-top: 6px;
    font-weight: 500;
}}
.live-pill {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(22,163,74,0.12);
    color: {STATUS['green']};
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}
.live-pill .dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: {STATUS['green']};
    box-shadow: 0 0 8px {STATUS['green']};
    animation: live-pulse 1.8s ease-in-out infinite;
}}
@keyframes live-pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%      {{ opacity: 0.55; transform: scale(0.85); }}
}}

/* ============================================================
   Section header
============================================================ */
.section-header {{
    display: flex; align-items: center; gap: 10px;
    margin: 22px 0 12px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid {p['border']};
}}
.section-header .icon {{
    font-size: 18px;
    width: 32px; height: 32px;
    display: inline-flex; align-items: center; justify-content: center;
    background: {p['accent_tint']};
    border-radius: 8px;
}}
.section-header .title {{
    font-weight: 700; font-size: 15px;
    color: {p['text']};
    letter-spacing: -0.01em;
}}

/* ============================================================
   Sidebar
============================================================ */
[data-testid="stSidebar"] > div:first-child {{
    background: {sidebar_bg} !important;
    border-right: 1px solid {sidebar_border};
    padding-top: 12px;
}}
[data-testid="stSidebar"] * {{
    color: {sidebar_text};
}}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stCaption {{
    color: {sidebar_text_dim} !important;
    font-size: 12px !important;
    font-weight: 500;
}}
.sidebar-logo {{
    text-align: center;
    padding: 6px 0 18px 0;
}}
.sidebar-logo .gear {{
    font-size: 38px;
    background: {p['accent_grad']};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}}
.sidebar-logo .brand {{
    font-weight: 800; font-size: 14px; letter-spacing: 0.5px;
    margin-top: 6px;
    color: {sidebar_text};
}}
.sidebar-logo .version {{
    display: inline-block;
    margin-top: 6px;
    padding: 2px 10px;
    background: {p['accent_tint']};
    color: {p['accent']};
    border-radius: 999px;
    font-size: 10px;
    font-weight: 600;
}}
.sidebar-section-title {{
    font-size: 11px;
    font-weight: 700;
    color: {sidebar_text_dim};
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin: 14px 0 8px 0;
}}

/* Sidebar inputs */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {{
    background: {input_bg} !important;
    border: 1px solid {input_border} !important;
    border-radius: 10px !important;
    color: {sidebar_text} !important;
    font-weight: 500;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
[data-testid="stSidebar"] input:focus {{
    border-color: {p['accent']} !important;
    box-shadow: 0 0 0 3px {p['accent_tint']} !important;
}}

/* ============================================================
   KPI / Metric Card
============================================================ */
.metric-card {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: {p['shadow']};
    position: relative;
    overflow: hidden;
    animation: fade-up 0.35s ease both;
    height: 100%;
}}
.metric-card::before {{
    content: '';
    position: absolute; left: 0; top: 0; bottom: 0;
    width: 3px;
    background: {p['accent_grad']};
    border-radius: 0 3px 3px 0;
    opacity: 0.95;
}}
.metric-card.green::before    {{ background: {STATUS['green']}; }}
.metric-card.yellow::before   {{ background: {STATUS['yellow']}; }}
.metric-card.orange::before   {{ background: {STATUS['orange']}; }}
.metric-card.red::before      {{ background: {STATUS['red']}; }}

.metric-card:hover {{
    transform: translateY(-3px);
    border-color: {p['accent']};
    box-shadow: {p['shadow_hover']};
}}
.metric-label {{
    color: {p['text_dim']};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}}
.metric-value {{
    font-weight: 800;
    font-size: 28px;
    color: {p['text']};
    line-height: 1.1;
    letter-spacing: -0.025em;
    display: flex; align-items: baseline; gap: 4px;
    flex-wrap: wrap;
}}
.metric-unit {{
    font-weight: 600; font-size: 13px;
    color: {p['text_dim']};
}}
.metric-delta {{
    font-size: 12px; font-weight: 600;
    margin-top: 6px;
    display: inline-flex; align-items: center; gap: 4px;
}}
.metric-delta.up    {{ color: {STATUS['red']}; }}
.metric-delta.down  {{ color: {STATUS['green']}; }}
.metric-delta.flat  {{ color: {p['text_muted']}; }}
.metric-sub {{
    color: {p['text_dim']};
    font-size: 12px;
    margin-top: 6px;
}}

@keyframes fade-up {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ============================================================
   Status card (NORMAL / ANOMALY)
============================================================ */
.status-card {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 20px;
    padding: 28px 32px;
    box-shadow: {p['shadow']};
    position: relative;
    overflow: hidden;
    animation: fade-up 0.4s ease both;
}}
.status-card.normal {{
    border-color: rgba(22,163,74,0.45);
    background: linear-gradient(135deg, rgba(22,163,74,0.06), {p['surface_alt'] if not is_dark else 'rgba(22,163,74,0.02)'} 60%);
}}
.status-card.anomaly {{
    border-color: rgba(220,38,38,0.55);
    background: linear-gradient(135deg, rgba(220,38,38,0.07), {p['surface_alt'] if not is_dark else 'rgba(220,38,38,0.03)'} 60%);
    animation: pulse-glow 2.4s ease-in-out infinite, fade-up 0.4s ease both;
}}
@keyframes pulse-glow {{
    0%, 100% {{ box-shadow: {p['shadow']}; }}
    50%      {{ box-shadow: 0 0 0 6px rgba(220,38,38,0.10), {p['shadow']}; }}
}}
.status-card .row {{
    display: flex; align-items: center; gap: 18px;
}}
.status-card .icon {{
    font-size: 44px; line-height: 1;
}}
.status-card .col {{ flex: 1; min-width: 0; }}
.status-card .state-label {{
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.8px;
    color: {p['text_dim']};
}}
.status-card .state-value {{
    font-size: 30px; font-weight: 800;
    margin-top: 2px;
    letter-spacing: -0.025em;
}}
.status-card.normal .state-value  {{ color: {STATUS['green']}; }}
.status-card.anomaly .state-value {{ color: {STATUS['red']}; }}
.status-card .conf {{
    color: {p['text_dim']};
    font-size: 13px; font-weight: 500; margin-top: 4px;
}}
.status-card .conf b {{
    color: {p['text']};
    font-weight: 700; font-size: 15px;
}}

/* ============================================================
   Action step card
============================================================ */
.action-step-card {{
    display: flex; align-items: flex-start; gap: 14px;
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-left: 4px solid {p['accent']};
    border-radius: 12px;
    padding: 14px 16px;
    margin: 8px 0;
    box-shadow: {p['shadow']};
    animation: fade-up 0.3s ease both;
}}
.action-step-card.red    {{ border-left-color: {STATUS['red']}; }}
.action-step-card.orange {{ border-left-color: {STATUS['orange']}; }}
.action-step-card.yellow {{ border-left-color: {STATUS['yellow']}; }}
.action-step-card.green  {{ border-left-color: {STATUS['green']}; }}
.action-step-card .step-circle {{
    flex-shrink: 0;
    width: 32px; height: 32px;
    background: {p['accent_grad']};
    color: white;
    border-radius: 999px;
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 13px;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25);
}}
.action-step-card .step-body {{
    flex: 1; font-size: 14px; line-height: 1.5;
    color: {p['text']};
}}

/* ============================================================
   Diagnosis card
============================================================ */
.diag-card {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-left: 4px solid {STATUS['orange']};
    border-radius: 12px;
    padding: 14px 16px;
    margin: 8px 0;
    box-shadow: {p['shadow']};
    animation: fade-up 0.3s ease both;
}}
.diag-card.critical {{ border-left-color: {STATUS['red']}; }}
.diag-card.high     {{ border-left-color: {STATUS['orange']}; }}
.diag-card.medium   {{ border-left-color: {STATUS['yellow']}; }}
.diag-card.low      {{ border-left-color: {STATUS['green']}; }}
.diag-card .diag-head {{
    display: flex; align-items: center; gap: 8px; margin-bottom: 4px;
}}
.diag-tag {{
    display: inline-block;
    padding: 3px 10px; border-radius: 999px;
    font-size: 10px; font-weight: 700; letter-spacing: 0.6px;
    text-transform: uppercase;
}}
.diag-tag.critical {{ background: rgba(220,38,38,0.12); color: {STATUS['red']}; }}
.diag-tag.high     {{ background: rgba(249,115,22,0.12); color: {STATUS['orange']}; }}
.diag-tag.medium   {{ background: rgba(234,179,8,0.18); color: {STATUS['yellow']}; }}
.diag-tag.low      {{ background: rgba(22,163,74,0.12); color: {STATUS['green']}; }}
.diag-card .component {{
    font-weight: 700; font-size: 13px; color: {p['text']};
}}
.diag-card .text {{
    color: {p['text_dim']}; font-size: 13px; line-height: 1.5;
}}

/* ============================================================
   Verdict / time-to-failure card
============================================================ */
.verdict-card {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 16px;
    padding: 20px 22px;
    box-shadow: {p['shadow']};
    animation: fade-up 0.35s ease both;
}}
.verdict-label {{
    color: {p['text_dim']}; font-size: 11px;
    font-weight: 600; letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 8px;
}}
.verdict-text {{
    font-size: 17px; font-weight: 700; line-height: 1.4;
    letter-spacing: -0.01em;
}}

/* ============================================================
   Tabs (pill-style)
============================================================ */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background: {p['surface_alt']};
    border: 1px solid {p['border']};
    border-radius: 14px;
    padding: 6px;
    margin-bottom: 14px;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    border: none;
    border-radius: 10px !important;
    color: {p['text_dim']};
    font-weight: 600;
    font-size: 13px;
    padding: 10px 18px !important;
    letter-spacing: 0.1px;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: {p['text']};
    background: {p['accent_tint']};
}}
.stTabs [aria-selected="true"] {{
    background: {p['accent_grad']} !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.25);
}}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{ display: none; }}

/* ============================================================
   Sliders
============================================================ */
.stSlider [data-baseweb="slider"] [role="slider"] {{
    background: {p['accent']} !important;
    border: 2px solid white !important;
    box-shadow: 0 2px 8px {p['accent_tint']};
    width: 18px !important; height: 18px !important;
}}
.stSlider [data-baseweb="slider"] > div > div > div {{
    background: {p['accent']} !important;
    height: 6px !important;
}}

/* ============================================================
   Buttons
============================================================ */
.stButton button, .stDownloadButton button {{
    background: {p['accent_grad']} !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    letter-spacing: 0.1px;
    box-shadow: 0 2px 8px rgba(37,99,235,0.18);
}}
.stButton button:hover, .stDownloadButton button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(37,99,235,0.32);
    filter: brightness(1.05);
}}
.stButton button:active {{ transform: translateY(0); }}

/* ============================================================
   Inputs (main area)
============================================================ */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input, .stNumberInput input, textarea {{
    background: {input_bg} !important;
    border: 1px solid {input_border} !important;
    border-radius: 10px !important;
    color: {p['text']} !important;
}}
.stSelectbox [data-baseweb="select"] > div:hover,
.stTextInput input:focus, .stNumberInput input:focus, textarea:focus {{
    border-color: {p['accent']} !important;
    box-shadow: 0 0 0 3px {p['accent_tint']} !important;
}}

/* ============================================================
   Recommendation table (custom)
============================================================ */
.rec-table {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 14px;
    overflow: hidden;
    box-shadow: {p['shadow']};
    animation: fade-up 0.3s ease both;
}}
.rec-table table {{
    width: 100%; border-collapse: collapse;
}}
.rec-table thead th {{
    background: {table_head};
    color: {p['text']};
    font-weight: 700; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.6px;
    padding: 12px 14px;
    text-align: {text_align};
    border-bottom: 1px solid {p['border']};
}}
.rec-table tbody td {{
    padding: 12px 14px;
    font-size: 13.5px;
    color: {p['text']};
    border-bottom: 1px solid {p['border_soft']};
    background: {table_row};
}}
.rec-table tbody tr:nth-child(even) td {{ background: {table_row_alt}; }}
.rec-table tbody tr:last-child td       {{ border-bottom: none; }}
.rec-table tbody tr:hover td            {{ background: {p['accent_tint']}; }}
.status-pill {{
    display: inline-block; padding: 3px 10px;
    border-radius: 999px; font-size: 11px;
    font-weight: 700; letter-spacing: 0.4px;
}}
.status-pill.green  {{ background: rgba(22,163,74,0.15); color: {STATUS['green']}; }}
.status-pill.orange {{ background: rgba(249,115,22,0.18); color: {STATUS['orange']}; }}
.status-pill.red    {{ background: rgba(220,38,38,0.15);  color: {STATUS['red']}; }}

/* ============================================================
   Native Streamlit dataframe (fallback)
============================================================ */
[data-testid="stDataFrame"] {{
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid {p['border']};
}}

/* ============================================================
   File uploader
============================================================ */
[data-testid="stFileUploader"] section {{
    background: {p['surface_alt']};
    border: 1px dashed {p['border']};
    border-radius: 12px;
}}
[data-testid="stFileUploader"] section:hover {{
    border-color: {p['accent']};
}}

/* ============================================================
   Alerts (info / success / warning / error)
============================================================ */
[data-testid="stAlert"] {{
    border-radius: 12px;
    border-width: 1px;
}}

/* Streamlit metric — only used as fallback */
[data-testid="stMetricValue"] {{
    font-weight: 800 !important; color: {p['text']} !important;
    letter-spacing: -0.02em;
}}
[data-testid="stMetricLabel"] {{
    color: {p['text_dim']} !important;
    font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.6px;
}}

/* Chart container wrapper */
.chart-wrap {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 16px;
    padding: 14px 16px 8px 16px;
    box-shadow: {p['shadow']};
    margin-bottom: 12px;
}}

/* Footer */
.app-footer {{
    text-align: center;
    color: {p['text_dim']};
    font-size: 11px;
    padding: 24px 0 10px 0;
    border-top: 1px solid {p['border']};
    margin-top: 32px;
    letter-spacing: 0.4px;
}}

hr {{ border-color: {p['border']} !important; }}
</style>
    """
    st.markdown(css, unsafe_allow_html=True)


# Backwards-compat helper used by older modules
def _ensure_rtl_helper():
    """Make sure config.is_rtl_aware exists (kept for forward compat)."""
    pass
