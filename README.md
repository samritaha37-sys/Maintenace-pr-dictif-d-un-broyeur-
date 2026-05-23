# Pebble Mill AI Monitoring Dashboard

An industrial-grade Streamlit dashboard that monitors a pebble mill, predicts its state, recommends optimal operating parameters, performs root-cause analysis and exports PDF reports.

---

## 🚀 How to run (for non-technical users)

**Step 1.** Make sure your data file is at:
```
C:\Users\Taha Samri\PyCharmMiscProject\dataset.xlsx
```
The file must contain a sheet called `Data_IA_1000`.

**Step 2.** Double-click `run_dashboard.bat` in this folder.

**Step 3.** A black window opens and starts the server. After ~10 seconds, your default browser automatically opens at:
```
http://localhost:8501
```
If it does not, open Chrome/Edge/Firefox and paste that address.

**Step 4.** Use the dashboard. To stop it, close the black window or press `Ctrl + C` in it.

---

## ✨ Features

| Tab | What it shows |
|-----|--------------|
| 🔮 **Live Prediction** | Sliders for the 7 sensor inputs, AI diagnosis (NORMAL / ANOMALY) with confidence, degradation score gauge (0–100), 4 component-risk gauges (Motor / Bearings / Hydraulics / Feed), time-to-failure verdict, session trend, recommended setpoints + acceptable ranges, prioritized corrective action plan, rule-based root-cause diagnosis, SHAP explanation, PDF export. |
| 📊 **Data Overview** | KPIs, state distribution pie, violin plots per variable by state, correlation matrix, raw data viewer. |
| 🎯 **Model Performance** | Best classifier name + CV F1, test accuracy/F1, confusion matrix, ROC curve, feature importance, regressor R²/MAE/RMSE per target, predicted-vs-actual scatter, candidate-model comparison table. |
| 🔬 **Exploration** | Free scatter plot (X / Y / color / size), grouped box plots. |
| 📜 **History & Logs** | All predictions made in this session, downloadable as CSV, anomaly log with diagnoses. |

### Other capabilities
- **Multi-language UI** — English / French / Arabic (Arabic uses RTL layout).
- **Model persistence** — joblib snapshots in `./models/`. Models retrain automatically only if the dataset changes (SHA-256 hash check) or you click "🔁 Retrain models".
- **Multi-model selection** — compares RandomForest, XGBoost, LightGBM (classifier) and RandomForest vs XGBoost (regressor), keeps the best by 5-fold CV.
- **Second-opinion anomaly detection** — IsolationForest trained on NORMAL rows fuses with the classifier into the degradation score.
- **PDF reports** — generated in `./reports/` with operator + mill identifier from the sidebar.

---

## 📁 Project structure

```
PyCharmMiscProject/
├─ app.py                  ← Streamlit entry point
├─ dataset.xlsx            ← your data (required)
├─ run_dashboard.bat       ← one-click launcher
├─ requirements.txt
├─ README.md
├─ modules/
│  ├─ config.py            ← paths, columns, colors, thresholds
│  ├─ data_loader.py       ← load/save/hash dataset
│  ├─ models.py            ← multi-model training + joblib persistence
│  ├─ predictor.py         ← end-to-end prediction + degradation score
│  ├─ recommendations.py   ← target ranges + corrective action plan
│  ├─ diagnostics.py       ← rule-based root-cause analysis
│  ├─ explainability.py    ← SHAP wrappers
│  ├─ reporting.py         ← PDF report generation
│  ├─ i18n.py              ← EN/FR/AR translations
│  └─ ui_components.py     ← reusable cards, gauges, CSS
├─ models/                 ← saved models (created at first launch)
└─ reports/                ← generated PDFs (created on first export)
```

---

## 🔄 Replacing the dataset

Two ways:

1. **From the dashboard** — open the sidebar → expand **"🔄 Replace dataset"** → upload your new `.xlsx`. The file is saved over the existing `dataset.xlsx` and the models retrain automatically.
2. **Manually** — copy your new file as `dataset.xlsx` in this folder, then in the sidebar click **"🔁 Retrain models"**.

The required column schema is:

| Type | Columns |
|------|---------|
| Inputs (7) | `Debit_actuel_t_h`, `Pression_actuelle_bar`, `Temperature_actuelle_C`, `Puissance_moteur_kW`, `Vibration_mm_s`, `Humidite_matiere_pct`, `Finesse_refus_pct` |
| Target (classification) | `Etat_broyeur` (0 = NORMAL, 1 = ANOMALY) |
| Targets (regression) | `Debit_recommande_t_h`, `Pression_recommandee_bar`, `Temperature_recommandee_C` |

---

## 🛠 Manual install (if the `.bat` file is not used)

```powershell
cd "C:\Users\Taha Samri\PyCharmMiscProject"
pip install -r requirements.txt
streamlit run app.py
```

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| Browser doesn't open | Manually visit http://localhost:8501 |
| "Dataset not found" | Place `dataset.xlsx` in this folder, or upload via the sidebar |
| Models look wrong | Click **🔁 Retrain models** in the sidebar |
| Black window closes immediately | Open PowerShell in this folder and run `python -m streamlit run app.py` to see the error |
| Port 8501 already in use | Close any other Streamlit instance, or run `streamlit run app.py --server.port 8502` |

---

## Tech

Python · Streamlit · scikit-learn · XGBoost · LightGBM · IsolationForest · SHAP · Plotly · ReportLab · joblib · openpyxl
