# Phase 0 — Foundations & Decisions

Implements Phase 0 from [`docs/phasewiseimplementationplan.md`](../docs/phasewiseimplementationplan.md).

## Objective

Lock implementation choices and project structure so later phases do not rework core contracts.

## Folder layout

```text
phase0/
├── README.md                          ← this file
├── decisions/
│   └── decision-log.md                ← 0.1–0.5, 0.7 resolved decisions
├── schema/
│   ├── canonical_feedback_schema.md   ← human-readable schema spec
│   └── canonical_feedback_schema.json ← machine-readable JSON Schema
├── taxonomy/
│   ├── theme_taxonomy_v0.md
│   └── theme_taxonomy_v0.json
├── model_docs/
│   └── model_documentation_outline.md ← sections filled in later phases
├── config/
│   ├── settings.example.yaml
│   └── .env.example                   ← secrets template (no real secrets)
├── project_skeleton/                  ← planned repo layout for Phases 1–5
│   ├── data/
│   ├── src/
│   │   ├── ingest/
│   │   ├── analysis/
│   │   ├── validation/
│   │   └── common/
│   ├── dashboard/
│   └── docs/
├── pipeline/
│   └── smoke_test.py                  ← no-op end-to-end smoke test
└── requirements.txt
```

## Tasks completed

| ID | Task | Artifact |
|----|------|----------|
| 0.1 | Embedding / LLM stack | `decisions/decision-log.md` |
| 0.2 | Storage stack | `decisions/decision-log.md` |
| 0.3 | Dashboard platform | `decisions/decision-log.md` |
| 0.4 | v1 languages | `decisions/decision-log.md` |
| 0.5 | Batch cadence | `decisions/decision-log.md` |
| 0.6 | Canonical schema | `schema/` |
| 0.7 | Source priority order | `decisions/decision-log.md` |
| 0.8 | Project skeleton | `project_skeleton/` |
| 0.9 | Theme taxonomy v0 | `taxonomy/` |
| 0.10 | Model documentation skeleton | `model_docs/` |

## Exit criteria

- [x] All architecture open decisions resolved or explicitly deferred with owner/date
- [x] Canonical schema reviewed and frozen for Phase 1
- [x] Empty pipeline can run end-to-end as a no-op smoke test

## How to run the smoke test

```bash
cd phase0
pip install -r requirements.txt
python pipeline/smoke_test.py
```

Expected result: all steps pass (`collect → normalize → prepare → represent → theme → enrich → answer → synthesize → validate → publish`).

## Next phase

Proceed to **Phase 1 — Ingestion & Cleaned Corpus** using the frozen schema and skeleton under `project_skeleton/`.
