# Phase 2 — Representation, Themeing & Enrichment

Implements Phase 2 from [`docs/phasewiseimplementationplan.md`](../docs/phasewiseimplementationplan.md).

**Input:** Phase 1 cleaned corpus (`phase1/data/cleaned/{run_id}/feedback.jsonl`)  
**Seed taxonomy:** [`phase0/taxonomy/theme_taxonomy_v0.json`](../phase0/taxonomy/theme_taxonomy_v0.json)

## Objective

Turn the cleaned corpus into embeddings, a versioned Theme Store, sentiment scores, and lightweight segment tags.

## Folder layout

```text
phase2/
├── README.md
├── requirements.txt
├── config/
├── taxonomy/
│   ├── theme_taxonomy_v1.json
│   └── theme_taxonomy_v1.md
├── data/
│   ├── prepared/{run_id}/
│   ├── embeddings/{run_id}/
│   ├── enriched/{run_id}/
│   └── themes/v1/{run_id}/
├── samples/
│   └── theme_assignments_sample.json
├── docs/
│   ├── theme_identification.md
│   └── phase2_run_summary.md
├── reports/{run_id}/
├── scripts/run_phase2.py
└── src/   # prepare, embed, enrich, theme, sentiment, segments, metrics, pipeline
```

## How to run

```bash
cd phase2
pip install -r requirements.txt
python scripts/run_phase2.py --run-id 2026-07-16-weekly
```

## Exit criteria

- [x] Every cleaned record processed for embedding (or skipped with reason)
- [x] Theme coverage measured (% with ≥1 non-other theme)
- [x] Taxonomy definitions written for all active themes (`taxonomy/theme_taxonomy_v1.*`)
- [x] Sample theme assignments reviewable (`samples/theme_assignments_sample.json`)

## Next phase

**Phase 3** consumes Theme Store + enriched records to answer the eight discovery questions.
