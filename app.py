"""
Pebble Mill AI Monitoring Dashboard — entry point.

Run with:   streamlit run app.py
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import data_loader
import diagnostics
import explainability
import models
import predictor
import recommendations
import reporting
import styles
import ui_components as ui
from config import (
    APP_VERSION,
    CHART_COLORWAY,
    COMPONENT_VARS,
    INPUT_FEATURES,
    REGRESSION_TARGETS,
    SESSION_HISTORY_MAX,
    STATUS,
    TARGET_STATE,
    TREND_SLOPE_WARNING,
    VAR_META,
    get_theme,
)
from i18n import LANGUAGES, is_rtl, t, var_label

# =============================================================================
# Page setup
# =============================================================================

st.set_page_config(
    page_title="Pebble Mill AI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ss = st.session_state
ss.setdefault("lang", "en")
ss.setdefault("theme", "light")
ss.setdefault("operator", "")
ss.setdefault("mill_id", "MILL-01")
ss.setdefault("history", [])
ss.setdefault("score_buffer", [])
ss.setdefault("confirm_clear", False)
ss.setdefault("retrain_token", 0)

# Inject CSS *first* so everything below is styled correctly
styles.inject_css(theme_name=ss.theme, rtl=is_rtl(ss.lang))
P = get_theme(ss.theme)  # current palette

# =============================================================================
# Sidebar — branding, theme, language, operator, dataset, models
# =============================================================================

with st.sidebar:
    ui.sidebar_logo(APP_VERSION)

    # ----- Theme toggle -----
    ui.sidebar_section("🎨 " + ("Apparence" if ss.lang == "fr" else
                                  "المظهر" if ss.lang == "ar" else "Appearance"))
    theme_label_light = {"en": "Light", "fr": "Clair",  "ar": "فاتح"}[ss.lang]
    theme_label_dark  = {"en": "Dark",  "fr": "Sombre", "ar": "داكن"}[ss.lang]
    new_theme = st.radio(
        "Theme",
        ["light", "dark"],
        format_func=lambda k: theme_label_light if k == "light" else theme_label_dark,
        index=0 if ss.theme == "light" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key="theme_radio",
    )
    if new_theme != ss.theme:
        ss.theme = new_theme
        st.rerun()

    # ----- Language -----
    ui.sidebar_section("🌐 " + t("language", ss.lang))
    lang_keys = list(LANGUAGES.keys())
    lang = st.selectbox(
        t("language", ss.lang),
        lang_keys,
        index=lang_keys.index(ss.lang),
        format_func=lambda k: LANGUAGES[k],
        label_visibility="collapsed",
    )
    if lang != ss.lang:
        ss.lang = lang
        st.rerun()

    # ----- Operator + mill ID -----
    ui.sidebar_section("👤 " + ("Opérateur" if ss.lang == "fr" else
                                  "المشغل" if ss.lang == "ar" else "Operator"))
    ss.operator = st.text_input(t("operator_name", ss.lang), ss.operator)
    ss.mill_id  = st.text_input(t("mill_id", ss.lang),       ss.mill_id)

# =============================================================================
# Dataset load (auto from disk, with upload fallback + replace)
# =============================================================================


def _load_or_prompt() -> pd.DataFrame | None:
    if data_loader.dataset_exists():
        try:
            return data_loader.load_dataset()
        except Exception as exc:
            st.sidebar.error(f"⚠ {exc}")
    st.warning(t("no_dataset", ss.lang))
    up = st.file_uploader(t("upload_help", ss.lang), type=["xlsx"], key="initial_upload")
    if up is not None:
        try:
            data_loader.save_uploaded_dataset(up.getvalue())
            st.success("✓ Dataset saved.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
    return None


with st.sidebar:
    ui.sidebar_section("📁 " + t("dataset_info", ss.lang))
    if data_loader.dataset_exists():
        st.caption(f"`{data_loader.dataset_filename()}`")
        st.caption(f"📅 {data_loader.dataset_modified()}")

    with st.expander(t("replace_dataset", ss.lang), expanded=False):
        replace = st.file_uploader(
            t("upload_help", ss.lang), type=["xlsx"], key="replace_upload",
            label_visibility="collapsed",
        )
        if replace is not None:
            try:
                data_loader.save_uploaded_dataset(replace.getvalue())
                st.success("✓ Replaced.")
                st.cache_data.clear()
                st.cache_resource.clear()
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

data = _load_or_prompt()
if data is None:
    st.stop()

with st.sidebar:
    st.caption(f"🗂  {len(data):,} {t('samples', ss.lang)} · {data.shape[1]} cols".replace(",", " "))

# =============================================================================
# Models
# =============================================================================


@st.cache_resource(show_spinner=False)
def _ref_table(_df_hash: str, df: pd.DataFrame):
    return recommendations.build_references(df)


@st.cache_resource(show_spinner=False)
def _get_bundle(dataset_hash_str: str, retrain_token: int, _df: pd.DataFrame):
    bundle = models.load_bundle()
    if bundle is not None and not models.need_retrain(dataset_hash_str):
        return bundle
    bundle = models.train_all(_df, dataset_hash_str=dataset_hash_str)
    try:
        models.save_bundle(bundle)
    except Exception:
        pass
    return bundle


ds_hash = data_loader.dataset_hash()

with st.sidebar:
    if st.button(t("retrain_models", ss.lang), use_container_width=True):
        import os
        for path in (models.CLF_PATH, models.REG_PATH, models.ISO_PATH, models.META_PATH):
            try: os.remove(path)
            except OSError: pass
        ss.retrain_token += 1
        st.cache_resource.clear()
        st.rerun()

try:
    with st.spinner(t("training_in_progress", ss.lang)):
        bundle = _get_bundle(ds_hash, ss.retrain_token, data)
except Exception as exc:
    st.error(t("model_load_err", ss.lang))
    st.exception(exc)
    st.stop()

refs = _ref_table(ds_hash, data)

with st.sidebar:
    ui.sidebar_section("🧠 " + t("model_perf_brief", ss.lang))
    clf_eval = bundle.meta.get("clf_eval", {})
    reg_eval = bundle.meta.get("reg_eval", {})
    st.caption(f"{t('best_classifier', ss.lang)}: **{bundle.clf_name}**"
               f" · F1 {clf_eval.get('cv_f1', float('nan')):.3f}")
    st.caption(f"{t('best_regressor', ss.lang)}: **{bundle.reg_name}**"
               f" · R² {reg_eval.get('cv_r2', float('nan')):.3f}")
    st.caption(f"{t('last_training', ss.lang)}: {bundle.meta.get('trained_at', '—')}")
    st.caption(f"{t('dataset_hash', ss.lang)}: `{bundle.meta.get('dataset_hash', '—')}`")

    with st.expander("ℹ " + t("about", ss.lang)):
        st.caption(
            "Industrial AI dashboard for pebble mill monitoring. "
            "Combines a supervised classifier, isolation forest, normal-band statistics, "
            "and rule-based diagnostics to give operators actionable recommendations."
        )

# =============================================================================
# Top header
# =============================================================================

ui.app_header(
    title=f"⚙ {t('app_title', ss.lang)}",
    subtitle=f"{t('app_subtitle', ss.lang)} · {bundle.clf_name} · {len(data):,} {t('samples', ss.lang)}".replace(",", " "),
    live=True,
    live_text="LIVE",
)

# =============================================================================
# Tabs
# =============================================================================

tab_live, tab_data, tab_perf, tab_explore, tab_history = st.tabs([
    t("tab_live",    ss.lang),
    t("tab_data",    ss.lang),
    t("tab_perf",    ss.lang),
    t("tab_explore", ss.lang),
    t("tab_history", ss.lang),
])

# =============================================================================
# TAB 1 — LIVE PREDICTION
# =============================================================================

with tab_live:
    col_in, col_out = st.columns([1, 1.5], gap="large")

    # ----- Inputs -----
    with col_in:
        ui.section_header("🎚", t("sensor_inputs", ss.lang))
        inputs: dict[str, float] = {}
        for v in INPUT_FEATURES:
            meta = VAR_META[v]
            unit = meta["unit"]
            vmin = float(data[v].min())
            vmax = float(data[v].max())
            default = float(data[v].median())
            step = max((vmax - vmin) / 200.0, 0.01)
            inputs[v] = st.slider(
                f"{var_label(v, ss.lang)} ({unit})",
                vmin, vmax, default, step=step, key=f"in_{v}",
            )

    # Run pipeline
    try:
        result = predictor.run_prediction(bundle, inputs, refs)
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
        st.stop()

    shap_vals = explainability.explain_prediction(
        bundle.clf, pd.DataFrame([{f: inputs[f] for f in INPUT_FEATURES}])
    )
    expected_v = explainability.expected_value(bundle.clf)
    diag_list  = diagnostics.diagnose(inputs, refs)
    rec_rows   = recommendations.build_recommendation_table(
        inputs, result.regression_recommendation, refs
    )
    action_plan = recommendations.build_action_plan(
        inputs, rec_rows, shap_vals, bool(result.is_anomaly)
    )

    ss.score_buffer.append(result.degradation_score)
    ss.score_buffer = ss.score_buffer[-SESSION_HISTORY_MAX:]
    ss.history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **inputs,
        "predicted_state": "ANOMALY" if result.is_anomaly else "NORMAL",
        "confidence": round(result.confidence, 3),
        "degradation_score": round(result.degradation_score, 1),
        "diagnoses": "; ".join(d.rule_id for d in diag_list) or "—",
    })
    ss.history = ss.history[-SESSION_HISTORY_MAX:]

    # ----- Diagnosis column -----
    with col_out:
        ui.section_header("🩺", t("diagnosis", ss.lang))
        ui.status_card(bool(result.is_anomaly), result.confidence, ss.lang)

        st.markdown("")
        gd1, gd2 = st.columns([1, 1], gap="medium")
        with gd1:
            st.plotly_chart(
                ui.degradation_gauge(result.degradation_score, t("degradation", ss.lang)),
                use_container_width=True, config={"displayModeBar": False},
            )
        with gd2:
            band = result.band
            ui.verdict_card(
                label=t("time_to_failure", ss.lang),
                text=t(band["key"], ss.lang),
                color=band["color"],
            )
            slope = predictor.trend_slope(ss.score_buffer)
            if slope > TREND_SLOPE_WARNING:
                st.markdown(
                    f"""
                    <div style="margin-top:10px; padding:10px 14px;
                                background: rgba(220,38,38,0.10);
                                border:1px solid {STATUS['red']};
                                border-radius:10px; color:{STATUS['red']};
                                font-weight:600;">
                        {t('trend_warning', ss.lang)} (Δ = +{slope:.2f}/step)
                    </div>
                    """, unsafe_allow_html=True,
                )

    # ----- Component risks -----
    ui.section_header("🔧", t("component_risks", ss.lang))
    ccols = st.columns(len(COMPONENT_VARS), gap="medium")
    for col, comp in zip(ccols, COMPONENT_VARS.keys()):
        with col:
            st.plotly_chart(
                ui.small_gauge(result.component_risks[comp], comp.replace("_", " ")),
                use_container_width=True, config={"displayModeBar": False},
            )

    # ----- Trend -----
    ui.section_header("📈", t("trend", ss.lang))
    if len(ss.score_buffer) >= 2:
        trend_df = pd.DataFrame({
            "step": range(1, len(ss.score_buffer) + 1),
            "score": ss.score_buffer,
        })
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_df["step"], y=trend_df["score"],
            mode="lines+markers",
            line=dict(color=P["accent"], width=2.5, shape="spline"),
            marker=dict(size=7, color=P["accent"],
                        line=dict(color="white", width=1.5)),
            fill="tozeroy", fillcolor=P["accent_tint"],
            name="Score",
        ))
        for b in [25, 50, 75]:
            fig_trend.add_hline(y=b, line=dict(color=P["chart_grid"], dash="dot", width=1))
        fig_trend.update_layout(
            height=240, yaxis_range=[0, 100],
            xaxis_title="Prediction #", yaxis_title="Score (0–100)",
        )
        st.plotly_chart(ui.apply_chart_theme(fig_trend), use_container_width=True,
                        config={"displayModeBar": False})
    else:
        st.caption("Run a few predictions to see the trend.")

    # ----- Recommendation table -----
    ui.section_header("📋", t("recommendations", ss.lang))
    table_rows = []
    for r in rec_rows:
        meta = VAR_META[r["variable"]]
        unit = meta["unit"]
        table_rows.append({
            "variable":    var_label(r["variable"], ss.lang),
            "current":     f"{r['current']:.2f} {unit}",
            "recommended": f"{r['recommended']:.2f} {unit}",
            "range":       f"{r['soft_min']:.2f} – {r['soft_max']:.2f}",
            "status":      r["status"].upper(),
            "status_key":  r["status"],
        })
    ui.styled_recommendation_table(
        table_rows,
        headers={
            "variable":    t("variable", ss.lang),
            "current":     t("current", ss.lang),
            "recommended": t("recommended", ss.lang),
            "range":       t("range", ss.lang),
            "status":      t("status", ss.lang),
        },
    )

    # ----- Action plan -----
    ui.section_header("📌", t("action_plan", ss.lang))
    if not result.is_anomaly:
        st.success(t("all_normal", ss.lang))
    elif not action_plan:
        st.info("—")
    else:
        for step in action_plan:
            ui.action_step(step.step, step.text, step.severity)

    # ----- Root cause -----
    ui.section_header("🔍", t("root_cause", ss.lang))
    if not diag_list:
        st.caption("No rule triggered.")
    else:
        for d in diag_list:
            ui.diag_card(d.severity, d.component.replace("_", " "),
                         diagnostics.diagnosis_text(d, ss.lang))

    # ----- SHAP -----
    ui.section_header("🧩", t("shap_explain", ss.lang))
    if shap_vals is None:
        st.caption("SHAP unavailable for this model.")
    else:
        items = sorted(shap_vals.items(), key=lambda kv: -abs(kv[1]))
        sv_df = pd.DataFrame({
            "feature": [var_label(f, ss.lang) for f, _ in items],
            "shap":    [v for _, v in items],
        })
        sv_df["color"] = sv_df["shap"].apply(
            lambda v: STATUS["red"] if v > 0 else STATUS["green"]
        )
        fig_sh = go.Figure(go.Bar(
            x=sv_df["shap"], y=sv_df["feature"],
            orientation="h", marker_color=sv_df["color"],
            text=[f"{v:+.3f}" for v in sv_df["shap"]],
            textposition="outside",
        ))
        fig_sh.update_layout(
            height=340, xaxis_title="SHAP value (→ pushes toward ANOMALY)",
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(ui.apply_chart_theme(fig_sh), use_container_width=True,
                        config={"displayModeBar": False})
        if expected_v is not None:
            st.caption(f"Baseline expected value: {expected_v:+.3f}")

    # ----- Export PDF -----
    st.markdown("")
    if st.button(t("export_pdf", ss.lang), key="export_pdf_btn"):
        try:
            path = reporting.generate_pdf_report(
                operator=ss.operator, mill_id=ss.mill_id,
                inputs=inputs, prediction=result, recommendations=rec_rows,
                action_plan=action_plan, diagnoses=diag_list,
                bundle_meta=bundle.meta,
            )
            st.success(f"{t('report_saved', ss.lang)}: `{path}`")
            with open(path, "rb") as f:
                st.download_button(
                    "⬇ Download PDF", f.read(),
                    file_name=path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1],
                    mime="application/pdf",
                )
        except Exception as exc:
            st.error(f"PDF generation failed: {exc}")

# =============================================================================
# TAB 2 — DATA OVERVIEW
# =============================================================================

with tab_data:
    n = len(data)
    n_anom = int((data[TARGET_STATE] == 1).sum())
    n_norm = n - n_anom
    pct_a = n_anom / n * 100
    pct_n = n_norm / n * 100

    ui.section_header("📊", t("tab_data", ss.lang))
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1: ui.styled_metric(t("total_samples", ss.lang), f"{n:,}".replace(",", " "), status="green")
    with k2: ui.styled_metric(t("pct_anomaly", ss.lang), f"{pct_a:.1f}", "%",
                               status="red" if pct_a > 30 else "orange")
    with k3: ui.styled_metric(t("pct_normal", ss.lang), f"{pct_n:.1f}", "%", status="green")
    with k4: ui.styled_metric("Variables", f"{data.shape[1]}", "cols", status="")

    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        ui.section_header("🎯", t("state_dist", ss.lang))
        edf = pd.DataFrame({
            "Etat": [t("normal", ss.lang), t("anomaly", ss.lang)],
            "n":    [n_norm, n_anom],
        })
        fig = px.pie(edf, names="Etat", values="n", hole=0.6,
                     color="Etat",
                     color_discrete_map={
                         t("normal", ss.lang):  STATUS["green"],
                         t("anomaly", ss.lang): STATUS["red"],
                     })
        fig.update_traces(textinfo="percent+label", textfont_size=14,
                          marker=dict(line=dict(color=P["bg"], width=2)))
        st.plotly_chart(ui.apply_chart_theme(fig), use_container_width=True,
                        config={"displayModeBar": False})
    with c2:
        ui.section_header("📈", t("stats", ss.lang))
        st.dataframe(data[INPUT_FEATURES].describe().round(2),
                     use_container_width=True, height=320)

    ui.section_header("📉", t("dist_by_state", ss.lang))
    var = st.selectbox(t("variable", ss.lang), INPUT_FEATURES,
                       index=INPUT_FEATURES.index("Puissance_moteur_kW"),
                       format_func=lambda v: var_label(v, ss.lang))
    dfp = data.copy()
    dfp["_st"] = dfp[TARGET_STATE].map({0: t("normal", ss.lang), 1: t("anomaly", ss.lang)})
    fig_v = px.violin(dfp, x="_st", y=var, color="_st", box=True, points="outliers",
                      color_discrete_map={
                          t("normal", ss.lang):  STATUS["green"],
                          t("anomaly", ss.lang): STATUS["red"],
                      })
    fig_v.update_layout(height=380, showlegend=False)
    st.plotly_chart(ui.apply_chart_theme(fig_v), use_container_width=True,
                    config={"displayModeBar": False})

    ui.section_header("🔗", t("correlation", ss.lang))
    corr = data[INPUT_FEATURES + [TARGET_STATE]].corr().round(2)
    fig_c = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                      zmin=-1, zmax=1, aspect="auto")
    fig_c.update_layout(height=500)
    st.plotly_chart(ui.apply_chart_theme(fig_c), use_container_width=True,
                    config={"displayModeBar": False})

    with st.expander(t("raw_data", ss.lang)):
        st.dataframe(data, use_container_width=True, height=380)

# =============================================================================
# TAB 3 — MODEL PERFORMANCE
# =============================================================================

with tab_perf:
    clf_eval = bundle.meta.get("clf_eval", {})
    reg_eval = bundle.meta.get("reg_eval", {})

    ui.section_header("🤖", f"Classifier · {clf_eval.get('name', '?')}")
    cp1, cp2, cp3 = st.columns(3, gap="medium")
    with cp1: ui.styled_metric("CV F1",         f"{clf_eval.get('cv_f1', float('nan')):.3f}",       status="green")
    with cp2: ui.styled_metric("Test accuracy", f"{clf_eval.get('test_accuracy', float('nan'))*100:.2f}", "%")
    with cp3: ui.styled_metric("Test F1",       f"{clf_eval.get('test_f1', float('nan')):.3f}")

    cm = clf_eval.get("confusion_matrix") or [[0, 0], [0, 0]]
    cm_cols = st.columns(2, gap="medium")
    with cm_cols[0]:
        ui.section_header("🎯", t("confusion_matrix", ss.lang))
        fig_cm = px.imshow(cm, text_auto=True,
                           x=["Pred Normal", "Pred Anomaly"],
                           y=["Real Normal", "Real Anomaly"],
                           color_continuous_scale="Blues", aspect="auto")
        fig_cm.update_layout(height=320)
        st.plotly_chart(ui.apply_chart_theme(fig_cm), use_container_width=True,
                        config={"displayModeBar": False})
    with cm_cols[1]:
        ui.section_header("📈", t("roc_curve", ss.lang))
        roc = clf_eval.get("roc", {})
        if roc.get("fpr"):
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(x=roc["fpr"], y=roc["tpr"], mode="lines",
                                          line=dict(color=P["accent"], width=3),
                                          name=f"AUC = {roc.get('auc', float('nan')):.3f}"))
            fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines",
                                          line=dict(color=P["chart_grid"], dash="dash"),
                                          showlegend=False))
            fig_roc.update_layout(height=320, xaxis_title="FPR", yaxis_title="TPR")
            st.plotly_chart(ui.apply_chart_theme(fig_roc), use_container_width=True,
                            config={"displayModeBar": False})
        else:
            st.caption("ROC unavailable (single class in test split).")

    fi = clf_eval.get("feature_importance") or {}
    if fi:
        ui.section_header("🏷", t("feat_importance", ss.lang))
        fi_df = pd.DataFrame({"feature": list(fi.keys()), "imp": list(fi.values())})
        fi_df = fi_df.sort_values("imp")
        fi_df["label"] = fi_df["feature"].apply(lambda v: var_label(v, ss.lang))
        fig_fi = px.bar(fi_df, x="imp", y="label", orientation="h")
        fig_fi.update_traces(marker_color=P["accent"])
        fig_fi.update_layout(height=360)
        st.plotly_chart(ui.apply_chart_theme(fig_fi), use_container_width=True,
                        config={"displayModeBar": False})
    if clf_eval.get("candidates"):
        ui.section_header("🏆", t("cv_results", ss.lang))
        st.dataframe(pd.DataFrame(clf_eval["candidates"]).round(4),
                     use_container_width=True, hide_index=True)

    ui.section_header("📐", f"Regressor · {reg_eval.get('name', '?')}")
    r1, r2, r3, r4 = st.columns(4, gap="medium")
    with r1: ui.styled_metric("CV R²",   f"{reg_eval.get('cv_r2', float('nan')):.3f}", status="green")
    with r2: ui.styled_metric("Test R²", f"{reg_eval.get('test_r2', float('nan')):.3f}")
    with r3: ui.styled_metric("MAE",     f"{reg_eval.get('test_mae', float('nan')):.3f}")
    with r4: ui.styled_metric("RMSE",    f"{reg_eval.get('test_rmse', float('nan')):.3f}")

    per_t = reg_eval.get("per_target", {})
    if per_t:
        st.dataframe(pd.DataFrame(per_t).T.round(4), use_container_width=True)

    targ = st.selectbox(t("predicted", ss.lang) + " / " + t("actual", ss.lang),
                        REGRESSION_TARGETS, key="reg_scatter_target")
    yts = reg_eval.get("y_test_sample", {}).get(targ, [])
    yps = reg_eval.get("y_pred_sample", {}).get(targ, [])
    if yts and yps:
        sc_df = pd.DataFrame({"Real": yts, "Pred": yps})
        fig_sc = px.scatter(sc_df, x="Real", y="Pred", opacity=0.65)
        fig_sc.update_traces(marker=dict(color=P["accent"], size=7))
        lim_min = min(sc_df["Real"].min(), sc_df["Pred"].min())
        lim_max = max(sc_df["Real"].max(), sc_df["Pred"].max())
        fig_sc.add_shape(type="line", x0=lim_min, y0=lim_min, x1=lim_max, y1=lim_max,
                         line=dict(color=STATUS["green"], dash="dash", width=2))
        fig_sc.update_layout(height=420, title=targ)
        st.plotly_chart(ui.apply_chart_theme(fig_sc), use_container_width=True,
                        config={"displayModeBar": False})

    if reg_eval.get("candidates"):
        st.dataframe(pd.DataFrame(reg_eval["candidates"]).round(4),
                     use_container_width=True, hide_index=True)

# =============================================================================
# TAB 4 — EXPLORATION
# =============================================================================

with tab_explore:
    all_num = INPUT_FEATURES + REGRESSION_TARGETS

    ui.section_header("🔍", "Configurable scatter plot")
    e1, e2, e3, e4 = st.columns(4, gap="medium")
    with e1: xv = st.selectbox("X", all_num, index=0,
                                format_func=lambda v: var_label(v, ss.lang))
    with e2: yv = st.selectbox("Y", all_num, index=3,
                                format_func=lambda v: var_label(v, ss.lang))
    with e3: cv = st.selectbox("Color", [TARGET_STATE] + all_num, index=0,
                                format_func=lambda v: var_label(v, ss.lang) if v != TARGET_STATE else "State")
    with e4: sv = st.selectbox("Size", ["(none)"] + all_num, index=0,
                                format_func=lambda v: var_label(v, ss.lang) if v != "(none)" else "(none)")
    dfx = data.copy()
    size_arg = None if sv == "(none)" else sv
    if cv == TARGET_STATE:
        dfx["_c"] = dfx[TARGET_STATE].map({0: t("normal", ss.lang), 1: t("anomaly", ss.lang)})
        fig = px.scatter(dfx, x=xv, y=yv, color="_c", size=size_arg,
                         color_discrete_map={t("normal", ss.lang): STATUS["green"],
                                              t("anomaly", ss.lang): STATUS["red"]},
                         opacity=0.75, size_max=18)
    else:
        fig = px.scatter(dfx, x=xv, y=yv, color=cv, size=size_arg,
                         color_continuous_scale="Viridis", opacity=0.75, size_max=18)
    fig.update_layout(height=520)
    st.plotly_chart(ui.apply_chart_theme(fig), use_container_width=True,
                    config={"displayModeBar": False})

    ui.section_header("📦", "Box plots by state")
    bvars = st.multiselect("Variables", INPUT_FEATURES,
                            default=["Puissance_moteur_kW", "Vibration_mm_s",
                                    "Temperature_actuelle_C"],
                            format_func=lambda v: var_label(v, ss.lang))
    if bvars:
        df_b = data[bvars + [TARGET_STATE]].copy()
        df_b["_st"] = df_b[TARGET_STATE].map({0: t("normal", ss.lang), 1: t("anomaly", ss.lang)})
        dl = df_b.melt(id_vars="_st", value_vars=bvars, var_name="Variable", value_name="Value")
        dl["Variable"] = dl["Variable"].apply(lambda v: var_label(v, ss.lang))
        fig_b = px.box(dl, x="Variable", y="Value", color="_st",
                       color_discrete_map={t("normal", ss.lang): STATUS["green"],
                                            t("anomaly", ss.lang): STATUS["red"]})
        fig_b.update_layout(height=440)
        st.plotly_chart(ui.apply_chart_theme(fig_b), use_container_width=True,
                        config={"displayModeBar": False})

# =============================================================================
# TAB 5 — HISTORY
# =============================================================================

with tab_history:
    ui.section_header("📜", t("tab_history", ss.lang))
    if not ss.history:
        st.info(t("no_history", ss.lang))
    else:
        hist_df = pd.DataFrame(ss.history)
        st.dataframe(hist_df, use_container_width=True, hide_index=True, height=420)

        c1, c2, _ = st.columns([1, 1, 4], gap="medium")
        with c1:
            st.download_button(t("download_csv", ss.lang),
                                hist_df.to_csv(index=False).encode("utf-8"),
                                file_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                mime="text/csv")
        with c2:
            if ss.confirm_clear:
                if st.button("⚠ " + t("clear_history", ss.lang), key="clr_confirm"):
                    ss.history = []
                    ss.score_buffer = []
                    ss.confirm_clear = False
                    st.rerun()
            else:
                if st.button(t("clear_history", ss.lang), key="clr_btn"):
                    ss.confirm_clear = True
                    st.caption(t("confirm_clear", ss.lang))

        anom = hist_df[hist_df["predicted_state"] == "ANOMALY"]
        if not anom.empty:
            ui.section_header("⚠", "Anomalies (session)")
            st.dataframe(anom[["timestamp", "degradation_score", "confidence", "diagnoses"]],
                         use_container_width=True, hide_index=True)

# =============================================================================
# Footer
# =============================================================================

ui.app_footer(
    version=APP_VERSION,
    extra=f"{t('system_online', ss.lang)} · {datetime.now().strftime('%H:%M:%S')}",
)
