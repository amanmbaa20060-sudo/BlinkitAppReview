# Phase 5 — Insight Dashboard & Stakeholder Delivery

Implements Phase 5 from `docs/phasewiseimplementationplan.md`.

## Objective

Ship a stakeholder-facing dashboard that exposes all published insights, supports evidence click-through, and summarizes methodology and validation in one place.

## Folder layout

```text
phase5/
├── README.md
├── index.html
├── styles.css
├── app.js
├── dashboard-data.js
├── assets/
│   ├── overview.png
│   ├── theme-explorer.png
│   ├── discovery-qna.png
│   ├── segment-lens.png
│   ├── frustration-monitor.png
│   ├── evidence-browser.png
│   └── components.png
├── docs/
│   ├── dashboard_implementation.md
│   └── uat_notes.md
└── scripts/
    └── build_dashboard_data.py
```

## What the dashboard includes

- Executive Overview
- Theme Explorer
- Discovery Q&A board
- Segment Lens
- Frustration Monitor
- Evidence Browser
- Methodology

## Data sources consumed

- `phase2/data/themes/v1/2026-07-16-weekly/metrics.json`
- `phase2/data/enriched/2026-07-16-weekly/enriched_feedback.jsonl`
- `phase4/data/insights/2026-07-16-weekly/insights_published.jsonl`
- `phase4/reports/2026-07-16-weekly/validation_report.json`
- `phase4/reports/2026-07-16-weekly/drift_baseline.json`

## How to run

From the repo root (recommended):

```bash
python phase5/scripts/run_dashboard.py
```

On Windows you can also double-click:

```text
start_dashboard.bat
```

The launcher builds data, picks a free port (default `8501`), and opens the browser at:

```text
http://127.0.0.1:8501/
```

If port `8501` is busy, the script automatically uses the next free port and prints the URL.

Do **not** use `http://localhost:8000/phase5/` unless you started a separate server on port `8000`.  
Do **not** double-click `index.html`.

## Notes

- The dashboard is static by design for Phase 5 v1: no backend service is required (local environment blocks Streamlit/numpy DLLs).
- The `dashboard-data.js` bundle is regenerated from Phase 2–4 outputs.
- The provided design images are copied into `phase5/assets/` and used as the visual reference layer inside the UI.
