# Phase 1 — Ingestion & Cleaned Corpus

Implements Phase 1 from [`docs/phasewiseimplementationplan.md`](../docs/phasewiseimplementationplan.md).

Uses the frozen Phase 0 canonical schema: [`phase0/schema/canonical_feedback_schema.json`](../phase0/schema/canonical_feedback_schema.json).

## Objective

Collect feedback from all seven sources, normalize into the canonical schema, and produce a cleaned, auditable corpus.

## Folder layout

```text
phase1/
├── README.md
├── requirements.txt
├── config/
│   └── settings.example.yaml
├── data/
│   ├── fixtures/          # Offline export samples (API/CSV fallback)
│   ├── raw/{source}/{run_id}/
│   └── cleaned/{run_id}/
├── docs/
│   ├── gather_workflow.md
│   ├── corpus_summary.md
│   └── audit_samples.md
├── reports/               # Generated quality reports per run
├── scripts/
│   └── run_ingest.py
└── src/
    ├── adapters/          # Seven source adapters
    ├── quality/           # Empty drop, dedupe, quarantine, language
    ├── storage/           # Raw + cleaned persistence
    └── pipeline/          # Ingest orchestration
```

## Sources (all in scope)

| Priority | Source | Adapter |
|----------|--------|---------|
| 1A | Play Store | `src/adapters/play_store.py` |
| 1A | App Store | `src/adapters/app_store.py` |
| 1B | Reddit | `src/adapters/reddit.py` |
| 1B | Product reviews | `src/adapters/product_reviews.py` |
| 1C | Social media | `src/adapters/social_media.py` |
| 1C | Community forums | `src/adapters/community_forums.py` |
| 1C | Quick-commerce discussions | `src/adapters/quick_commerce.py` |

Adapters read **fixture/export files** by default (ToS-safe offline path). Swap fixture paths for live API/export dumps without changing the canonical schema.

## How to run

```bash
cd phase1
pip install -r requirements.txt
python scripts/run_ingest.py
```

Optional:

```bash
python scripts/run_ingest.py --run-id 2026-07-16-weekly
python scripts/run_ingest.py --sources play_store,app_store   # slice 1A only
```

## Exit criteria

- [x] All seven sources represented in the cleaned corpus
- [x] Deduplication and empty-text gates active
- [x] Audit path raw → cleaned documented (`docs/audit_samples.md`)
- [x] Corpus volume and date range documented (`docs/corpus_summary.md`)

## Deliverables

| Deliverable | Location |
|-------------|----------|
| Seven source adapters | `src/adapters/` |
| Raw store | `data/raw/` |
| Cleaned corpus | `data/cleaned/{run_id}/feedback.jsonl` (+ CSV) |
| Quality report | `reports/{run_id}/quality_report.json` |
| Gather workflow (model docs) | `docs/gather_workflow.md` |

## Next phase

**Phase 2 — Representation, Themeing & Enrichment** consumes `data/cleaned/{run_id}/`.
