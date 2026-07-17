# Phase 2 Run Summary

## Reference run: `2026-07-16-weekly`

| Metric | Value |
|--------|------:|
| Input cleaned records | 1094 |
| Prepared | 1094 |
| Embedded (incl. non-English audit embeds) | 1086 |
| Skipped quarantined | 8 |
| Excluded from themeing (non-English) | 16 |
| Analyzed (themed) | 1070 |
| Theme coverage (non-other) | **100%** |
| Taxonomy version | v1 |
| Embedding model | `local_hashing_dim256` |
| Discovered residual clusters | 0 |

## Deliverables

| Deliverable | Path |
|-------------|------|
| Embeddings index | `data/embeddings/2026-07-16-weekly/vectors.jsonl` |
| Taxonomy v1 | `taxonomy/theme_taxonomy_v1.json` |
| Theme Store | `data/themes/v1/2026-07-16-weekly/` |
| Enriched records | `data/enriched/2026-07-16-weekly/enriched_feedback.jsonl` |
| QA sample | `samples/theme_assignments_sample.json` |
| Themeing docs | `docs/theme_identification.md` |
| Run report | `reports/2026-07-16-weekly/phase2_report.json` |

## Exit criteria

- [x] Every cleaned record embedded or skipped with reason
- [x] Theme coverage measured
- [x] Taxonomy definitions written for active themes
- [x] Sample assignments reviewable for Phase 4 QA
