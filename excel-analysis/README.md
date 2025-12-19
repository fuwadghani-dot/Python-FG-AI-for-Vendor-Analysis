# Excel Analysis — Vendor Analysis 📊

A compact Python project to analyze vendor/supplier Excel files, generate styled multi-sheet Excel reports with embedded charts, and expose a Streamlit web UI plus an optional FastAPI-based service for scheduled runs and alerts.

---

## 🔍 What's included

- Data loading & cleaning utilities (parse percent strings, split condition codes, coerce numeric-like columns).
- Analysis helpers: supplier aggregation, material pivots, plant summaries, and top-materials per plant.
- Plotly-based visualizations embedded into Excel reports (via Kaleido/Pillow + openpyxl).
- Streamlit UI for interactive exploration and running reports.
- FastAPI service & APScheduler integration for recurring runs and email notifications.
- Tests (pytest) and basic CI workflow.


## 🚀 Quickstart — run locally

1. Clone and checkout the UI branch (recommended):

```bash
git clone https://github.com/fuwadghani-dot/Python-FG-AI-for-Vendor-Analysis.git
cd Python-FG-AI-for-Vendor-Analysis
git checkout supplier-analysis
```

2. Setup virtualenv and install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the Streamlit app (opens at http://localhost:8501):

```bash
streamlit run app.py
```

4. Use the **Run & Reports** tab to upload/select a workbook and generate a report, or use the CLI script below.


## 🧾 Generate a report (CLI)

```bash
python scripts/generate_report.py "path/to/your_workbook.xlsx"
# output saved to: reports/exports/vendor_report.xlsx
```

Or use the package API:

```py
from pathlib import Path
from excel_analysis.report import generate
out_path = generate(Path("path/to/workbook.xlsx"))
```


## ⚙️ Service & scheduling (optional)

Run the FastAPI service:

```bash
uvicorn src.scripts.service:app --host 0.0.0.0 --port 8000
```

Endpoints include `/run`, `/schedule`, `/status`, and `/jobs`. Protect API requests with the `SERVICE_TOKEN` environment variable.


## 🔑 Environment variables (important)

- `SERVICE_TOKEN` — Bearer token for the FastAPI endpoints.
- SMTP configuration for alerts (optional): `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `ALERT_FROM`, `ALERT_TO`.
- `REPORT_BASE_URL` — Optional; used to create public links to reports in email alerts.

> Never commit secrets; use your host's secrets manager (Streamlit Cloud, Render, GitHub Secrets) or a local `.env` file and a `.env.example` in the repo.


## 🐳 Docker (optional)

There is a Dockerfile for containerized runs. Example:

```bash
# build
docker build -t excel-analysis:latest .

# run (Streamlit)
docker run -p 8501:8501 -e SERVICE_TOKEN=token excel-analysis:latest
```


## 🧪 Tests

Run the test suite:

```bash
python -m pytest -q
```


## 📁 Artifacts & locations

- Generated reports: `reports/exports/vendor_report.xlsx`
- Run metadata: `reports/status.json`
- Uploaded sample workbooks: `data_samples/`


## 📝 Contributing & next steps

- Add a `LICENSE` if you want to publish. MIT is a good starting point.
- Consider adding a GitHub Actions workflow to auto-deploy to Streamlit Cloud or Render on push.

---

If you'd like, I can also:
- Make the repo public, or
- Set up a Streamlit Cloud deployment, or
- Create a GitHub Release attaching the latest report (`reports/exports/vendor_report.xlsx`).

Tell me which of the above you'd like me to do next.