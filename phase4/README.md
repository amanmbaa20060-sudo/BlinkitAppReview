# Phase 4 — Validation, Governance & Publish Gate

Implements Phase 4 from [`docs/phasewiseimplementationplan.md`](../docs/phasewiseimplementationplan.md).

**Inputs**
- Phase 2 enriched feedback + Theme Store metrics + QA sample
- Phase 3 draft insights

## Objective

Validate theme and insight quality, apply confidence gating, and produce a publishable insight set for the dashboard.

## Folder layout

```text
phase4/
├── README.md
├── config/governance.yaml
├── docs/validation.md
├── data/insights/{run_id}/
│   ├── insights_published.jsonl
│   ├── insights_draft.jsonl
│   └── insights_all.jsonl
├── reports/{run_id}/
│   ├── validation_report.json
│   ├── drift_baseline.json
│   └── stakeholder_spotcheck.md
├── scripts/run_phase4.py
└── src/   # checks + pipeline
```

## How to run

```bash
cd phase4
python scripts/run_phase4.py --run-id 2026-07-16-weekly
```

Uses Groq (`GROQ_API_KEY` in repo-root `.env`) for LLM-as-judge sampling QA and faithfulness checks.

## Exit criteria

- [x] Model-doc validation pillar filled
- [x] Published insights for Q1–Q8 where evidence allows; gaps documented
- [x] Publish rule enforced (no silent promotion of low-confidence insights)

## Next phase

**Phase 5** dashboard consumes published insights + Theme Store.
