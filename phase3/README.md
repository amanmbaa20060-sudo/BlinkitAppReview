# Phase 3 — Discovery Question Modules & Draft Insights

Implements Phase 3 from [`docs/phasewiseimplementationplan.md`](../docs/phasewiseimplementationplan.md).

**Inputs**
- Phase 2 enriched feedback: `phase2/data/enriched/{run_id}/enriched_feedback.jsonl`
- Phase 2 Theme Store metrics: `phase2/data/themes/v1/{run_id}/metrics.json`
- Taxonomy map: `phase2/taxonomy/theme_taxonomy_v1.json`

## Objective

Produce draft, evidence-linked insights for every discovery question (Q1–Q8).

## Folder layout

```text
phase3/
├── README.md
├── docs/
│   ├── insight_generation.md
│   └── phase3_run_summary.md
├── data/insights/{run_id}/
│   ├── insights.jsonl
│   └── insights_by_question.json
├── reports/{run_id}/phase3_report.json
├── scripts/run_phase3.py
└── src/
    ├── evidence.py
    ├── synthesis.py
    ├── modules/   # Q1–Q8
    └── pipeline.py
```

## How to run

```bash
cd phase3
python scripts/run_phase3.py --run-id 2026-07-16-weekly
```

## Exit criteria

- [x] Every discovery question has ≥1 draft insight
- [x] Every draft insight cites evidence IDs
- [x] Implications relate to new-category purchase behavior among MACs
- [x] No orphan insights without question mapping

## Next phase

**Phase 4** validates draft insights and applies the publish gate.
