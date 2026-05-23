"""Translations for the dashboard (EN / FR / AR)."""

from __future__ import annotations

LANGUAGES: dict[str, str] = {"en": "English", "fr": "Français", "ar": "العربية"}

# All UI strings. Use t(key) to fetch the translation for the active language.
TRANSLATIONS: dict[str, dict[str, str]] = {
    # ---- App ----
    "app_title":       {"en": "Pebble Mill AI Monitoring",         "fr": "Supervision IA Broyeur à Galets",       "ar": "مراقبة المطحنة بالذكاء الاصطناعي"},
    "app_subtitle":    {"en": "Industrial diagnostics & optimization", "fr": "Diagnostic et optimisation industriels", "ar": "التشخيص والتحسين الصناعي"},
    "system_online":   {"en": "System Online",                     "fr": "Système en ligne",                      "ar": "النظام متصل"},
    # ---- Sidebar ----
    "sidebar_title":   {"en": "Control Panel",                     "fr": "Panneau de contrôle",                   "ar": "لوحة التحكم"},
    "language":        {"en": "Language",                          "fr": "Langue",                                "ar": "اللغة"},
    "operator_name":   {"en": "Operator name",                     "fr": "Nom de l'opérateur",                    "ar": "اسم المشغل"},
    "mill_id":         {"en": "Mill identifier",                   "fr": "Identifiant broyeur",                   "ar": "معرف المطحنة"},
    "dataset_info":    {"en": "Dataset",                           "fr": "Jeu de données",                        "ar": "مجموعة البيانات"},
    "samples":         {"en": "samples",                           "fr": "échantillons",                          "ar": "عينات"},
    "last_modified":   {"en": "Last modified",                     "fr": "Dernière modification",                 "ar": "آخر تعديل"},
    "replace_dataset": {"en": "🔄 Replace dataset",                "fr": "🔄 Remplacer le jeu de données",         "ar": "🔄 استبدال البيانات"},
    "retrain_models":  {"en": "🔁 Retrain models",                 "fr": "🔁 Réentraîner les modèles",             "ar": "🔁 إعادة تدريب النماذج"},
    "dark_mode":       {"en": "Dark mode",                         "fr": "Mode sombre",                           "ar": "الوضع الداكن"},
    "model_perf_brief":{"en": "Model performance",                 "fr": "Performance des modèles",               "ar": "أداء النماذج"},
    "best_classifier": {"en": "Best classifier",                   "fr": "Meilleur classifieur",                  "ar": "أفضل مصنف"},
    "best_regressor":  {"en": "Best regressor",                    "fr": "Meilleur régresseur",                   "ar": "أفضل ممي"},
    "last_training":   {"en": "Last training",                     "fr": "Dernier entraînement",                  "ar": "آخر تدريب"},
    "dataset_hash":    {"en": "Dataset hash",                      "fr": "Hash du jeu",                           "ar": "بصمة البيانات"},
    "about":           {"en": "About",                             "fr": "À propos",                              "ar": "حول"},
    "help":            {"en": "Help",                              "fr": "Aide",                                  "ar": "مساعدة"},
    # ---- Tabs ----
    "tab_live":        {"en": "🔮 Live Prediction",                "fr": "🔮 Prédiction live",                     "ar": "🔮 التنبؤ المباشر"},
    "tab_data":        {"en": "📊 Data Overview",                  "fr": "📊 Vue des données",                     "ar": "📊 نظرة على البيانات"},
    "tab_perf":        {"en": "🎯 Model Performance",              "fr": "🎯 Performance des modèles",             "ar": "🎯 أداء النموذج"},
    "tab_explore":     {"en": "🔬 Exploration",                    "fr": "🔬 Exploration",                         "ar": "🔬 الاستكشاف"},
    "tab_history":     {"en": "📜 History & Logs",                 "fr": "📜 Historique",                          "ar": "📜 السجل"},
    # ---- Live tab ----
    "sensor_inputs":   {"en": "Sensor inputs",                     "fr": "Entrées capteurs",                      "ar": "مدخلات الحساسات"},
    "diagnosis":       {"en": "AI Diagnosis",                      "fr": "Diagnostic IA",                         "ar": "تشخيص الذكاء الاصطناعي"},
    "state":           {"en": "State",                             "fr": "État",                                  "ar": "الحالة"},
    "normal":          {"en": "NORMAL",                            "fr": "NORMAL",                                "ar": "طبيعي"},
    "anomaly":         {"en": "ANOMALY",                           "fr": "ANOMALIE",                              "ar": "خلل"},
    "confidence":      {"en": "Confidence",                        "fr": "Confiance",                             "ar": "الثقة"},
    "degradation":     {"en": "Degradation score",                 "fr": "Score de dégradation",                  "ar": "درجة التدهور"},
    "component_risks": {"en": "Component risks",                   "fr": "Risques par composant",                 "ar": "مخاطر المكونات"},
    "time_to_failure": {"en": "Time-to-failure verdict",           "fr": "Pronostic temps avant défaillance",     "ar": "الوقت قبل العطل"},
    "recommendations": {"en": "Recommendations",                   "fr": "Recommandations",                       "ar": "التوصيات"},
    "action_plan":     {"en": "Corrective action plan",            "fr": "Plan d'action correctif",               "ar": "خطة الإجراءات التصحيحية"},
    "root_cause":      {"en": "Root cause analysis",               "fr": "Analyse cause racine",                  "ar": "تحليل السبب الجذري"},
    "shap_explain":    {"en": "AI explanation (SHAP)",             "fr": "Explication IA (SHAP)",                 "ar": "شرح الذكاء الاصطناعي"},
    "trend":           {"en": "Session trend (last predictions)",  "fr": "Tendance session (dernières prédictions)", "ar": "اتجاه الجلسة"},
    "export_pdf":      {"en": "📄 Export PDF report",              "fr": "📄 Exporter rapport PDF",                "ar": "📄 تصدير تقرير PDF"},
    "current":         {"en": "Current",                           "fr": "Actuel",                                "ar": "الحالي"},
    "recommended":     {"en": "Recommended",                       "fr": "Recommandé",                            "ar": "موصى به"},
    "range":           {"en": "Range",                             "fr": "Plage",                                 "ar": "المدى"},
    "status":          {"en": "Status",                            "fr": "Statut",                                "ar": "الحالة"},
    "variable":        {"en": "Variable",                          "fr": "Variable",                              "ar": "المتغير"},
    "target":          {"en": "Target",                            "fr": "Cible",                                 "ar": "الهدف"},
    "all_normal":      {"en": "All parameters are in normal range. No action required.",
                        "fr": "Tous les paramètres sont dans la plage normale. Aucune action requise.",
                        "ar": "جميع المعلمات ضمن المدى الطبيعي. لا حاجة لأي إجراء."},
    "trend_warning":   {"en": "⚠ Conditions degrading rapidly.",   "fr": "⚠ Conditions en dégradation rapide.",    "ar": "⚠ الظروف تتدهور بسرعة."},
    # ---- Degradation bands ----
    "band_healthy":  {"en": "HEALTHY — Next inspection in normal maintenance cycle (~7 days)",
                      "fr": "SAIN — Prochaine inspection dans le cycle normal (~7 jours)",
                      "ar": "سليم — الفحص التالي ضمن الدورة العادية (~7 أيام)"},
    "band_watch":    {"en": "WATCH — Inspect within 48 hours",
                      "fr": "VIGILANCE — Inspecter sous 48 heures",
                      "ar": "تنبه — افحص خلال 48 ساعة"},
    "band_risk":     {"en": "RISK — Inspect within 24 hours, prepare intervention",
                      "fr": "RISQUE — Inspecter sous 24 h, préparer l'intervention",
                      "ar": "خطر — افحص خلال 24 ساعة وحضّر التدخل"},
    "band_critical": {"en": "CRITICAL — Stop and inspect immediately",
                      "fr": "CRITIQUE — Arrêter et inspecter immédiatement",
                      "ar": "حرج — أوقف وافحص فوراً"},
    # ---- Data tab ----
    "total_samples":  {"en": "Total samples",   "fr": "Total échantillons", "ar": "إجمالي العينات"},
    "pct_anomaly":    {"en": "% Anomalies",     "fr": "% Anomalies",       "ar": "% الخلل"},
    "pct_normal":     {"en": "% Normal",        "fr": "% Normal",          "ar": "% الطبيعي"},
    "state_dist":     {"en": "State distribution", "fr": "Répartition des états", "ar": "توزيع الحالات"},
    "stats":          {"en": "Descriptive statistics", "fr": "Statistiques descriptives", "ar": "إحصاءات وصفية"},
    "dist_by_state":  {"en": "Distribution by state",  "fr": "Distribution par état",     "ar": "التوزيع حسب الحالة"},
    "correlation":    {"en": "Correlation matrix",     "fr": "Matrice de corrélation",    "ar": "مصفوفة الارتباط"},
    "raw_data":       {"en": "Raw data",               "fr": "Données brutes",            "ar": "البيانات الخام"},
    # ---- Perf tab ----
    "confusion_matrix": {"en": "Confusion matrix",      "fr": "Matrice de confusion",      "ar": "مصفوفة الالتباس"},
    "roc_curve":        {"en": "ROC curve",             "fr": "Courbe ROC",                "ar": "منحنى ROC"},
    "feat_importance":  {"en": "Feature importance",    "fr": "Importance des variables",  "ar": "أهمية المتغيرات"},
    "cv_results":       {"en": "Cross-validation results", "fr": "Résultats validation croisée", "ar": "نتائج التحقق المتقاطع"},
    "predicted":        {"en": "Predicted",             "fr": "Prédit",                    "ar": "المتوقع"},
    "actual":           {"en": "Actual",                "fr": "Réel",                      "ar": "الفعلي"},
    # ---- History ----
    "no_history":     {"en": "No predictions yet in this session.", "fr": "Aucune prédiction dans cette session.", "ar": "لا توجد تنبؤات بعد."},
    "clear_history":  {"en": "Clear history",            "fr": "Effacer l'historique",      "ar": "مسح السجل"},
    "download_csv":   {"en": "Download CSV",             "fr": "Télécharger CSV",          "ar": "تنزيل CSV"},
    "confirm_clear":  {"en": "Click again to confirm clear", "fr": "Cliquez à nouveau pour confirmer", "ar": "اضغط مرة أخرى للتأكيد"},
    # ---- Errors ----
    "no_dataset":     {"en": "Dataset not found. Please upload one.",
                       "fr": "Jeu de données introuvable. Veuillez en charger un.",
                       "ar": "لم يتم العثور على البيانات. الرجاء التحميل."},
    "upload_help":    {"en": "Upload an .xlsx file with sheet 'Data_IA_1000'",
                       "fr": "Chargez un fichier .xlsx avec la feuille « Data_IA_1000 »",
                       "ar": "ارفع ملف .xlsx بورقة « Data_IA_1000 »"},
    "model_load_err": {"en": "Failed to load models. Click 'Retrain models' below.",
                       "fr": "Échec du chargement des modèles. Cliquez sur « Réentraîner ».",
                       "ar": "فشل تحميل النماذج. اضغط على إعادة التدريب."},
    "report_saved":   {"en": "Report saved to",          "fr": "Rapport enregistré dans",   "ar": "تم حفظ التقرير في"},
    "training_done":  {"en": "Training complete",        "fr": "Entraînement terminé",      "ar": "اكتمل التدريب"},
    "training_in_progress": {"en": "Training models...", "fr": "Entraînement en cours...",  "ar": "جاري التدريب..."},
}


def t(key: str, lang: str = "en") -> str:
    """Return the translation for *key* in *lang*, falling back to English then to the key."""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(lang) or entry.get("en") or key


def var_label(var: str, lang: str = "en") -> str:
    """Return the localised label for a variable column, falling back to the column name."""
    from .config import VAR_META

    meta = VAR_META.get(var)
    if not meta:
        return var
    return meta.get(f"label_{lang}", meta.get("label_en", var))


def is_rtl(lang: str) -> bool:
    return lang == "ar"
