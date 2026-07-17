# Corpus Summary

Reference run after Phase 1 ingest. Source of truth: `reports/2026-07-16-weekly/quality_report.json`.

## Latest reference run (`2026-07-16-weekly`)

| Field | Value |
|-------|-------|
| Run ID | `2026-07-16-weekly` |
| Schema version | `1.0.0` |
| Sources in cleaned corpus | All seven |
| Collection date range | **2025-07-16 → 2026-07-15** (12 months) |
| Raw input | 1106 |
| Dropped empty | 7 |
| Dropped duplicate | 5 |
| Quarantined (kept flagged) | 8 |
| Cleaned records | **1094** (>= 1000 target) |
| Non-quarantined | 1086 |

## Per-source cleaned kept

| Source | Input | Kept |
|--------|------:|-----:|
| play_store | 159 | 157 |
| app_store | 158 | 156 |
| reddit | 157 | 156 |
| product_reviews | 158 | 156 |
| social_media | 159 | 157 |
| community_forums | 157 | 156 |
| quick_commerce_discussions | 158 | 156 |

## Regenerating fixtures

```bash
cd phase1
python scripts/generate_fixtures.py
python scripts/run_ingest.py --run-id 2026-07-16-weekly
```

`ROWS_PER_SOURCE` in `scripts/generate_fixtures.py` controls volume (default 155 × 7 sources).

## Coverage rule

Exit criterion satisfied: all seven sources appear in the cleaned corpus with **>= 1000** cleaned rows for analysis.
