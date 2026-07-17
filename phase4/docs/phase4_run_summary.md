# Phase 4 Run Summary

## Reference run: `2026-07-16-weekly`

| Check | Result |
|-------|--------|
| Coverage | Passed (100% theme coverage) |
| Sampling QA (LLM-as-judge) | See validation report |
| Faithfulness | Passed (all draft insights) |
| Cross-source consistency | Applied as confidence weights |
| Stability holdout | See validation report |
| Drift baseline | Written |
| Publish gate | Enforced |

## Publish outcomes

| Metric | Value |
|--------|------:|
| Published insights | 8 (Q1–Q8) |
| Remaining drafts | 0 |
| Gaps documented | none (all questions published) |

## Deliverables

| Deliverable | Path |
|-------------|------|
| Governance config | `config/governance.yaml` |
| Published Insight Store | `data/insights/{run_id}/insights_published.jsonl` |
| Draft Insight Store | `data/insights/{run_id}/insights_draft.jsonl` |
| Validation report | `reports/{run_id}/validation_report.json` |
| Drift baseline | `reports/{run_id}/drift_baseline.json` |
| Stakeholder spot-check | `reports/{run_id}/stakeholder_spotcheck.md` |
| Validation docs | `docs/validation.md` |

## Exit criteria

- [x] All four model-doc pillars have content
- [x] Published insights for Q1–Q8 (gaps would be documented if any)
- [x] Publish rule enforced (no silent promotion)

## Reproduce

```bash
cd phase4
python scripts/run_phase4.py --run-id 2026-07-16-weekly
```
