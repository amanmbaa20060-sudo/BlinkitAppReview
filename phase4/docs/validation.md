# How Insight Quality Was Validated (Phase 4)

Fills model documentation section: **How you validated the quality of the insights**.  
Outline: [`phase0/model_docs/model_documentation_outline.md`](../../phase0/model_docs/model_documentation_outline.md)

---

## 1. Validation workflow

```text
Phase 2 enriched corpus + Phase 3 draft insights
  → Coverage check
  → Sampling QA (Groq LLM-as-judge + heuristic fallback)
  → Faithfulness check (insight vs cited quotes)
  → Cross-source consistency weighting
  → Stability holdout check
  → Drift baseline snapshot
  → Confidence finalization
  → Publish gate (draft → published only if thresholds met)
  → Validation report + stakeholder spot-check list
```

Governance thresholds: `config/governance.yaml`.

---

## 2. Coverage check

- Metric: % of analyzed records with ≥1 non-`theme.other` theme.
- Pass bar: `coverage.min_theme_coverage_pct` (default 70%).
- Results: `reports/{run_id}/validation_report.json → checks.coverage`.

---

## 3. Sampling QA (theme assignment precision)

- Random sample of analyzed records (`sampling_qa.sample_size`).
- Judge: Groq LLM (`use_llm_judge: true`) with heuristic fallback.
- Precision = fraction of assigned themes judged correct / supported.
- Pass bar: `sampling_qa.min_precision` (default 0.70).

---

## 4. Faithfulness (insight vs quotes)

- For each draft insight, verify headline/implication are entailed by `evidence_pack` quotes.
- Judge: Groq LLM with heuristic overlap fallback.
- Pass bar: `faithfulness.min_pass_rate` (default 0.80).
- Failed faithfulness blocks publish (`require_faithfulness_pass`).

---

## 5. Cross-source consistency

- Themes appearing in only one source receive a confidence penalty (`single_source_penalty`).
- Multi-source themes keep full weight.
- Applied during confidence finalization.

---

## 6. Stability / holdout

- Split analyzed corpus into train vs holdout.
- Compare top-K theme sets (Jaccard overlap).
- Pass bar: `stability.min_top_theme_overlap`.

---

## 7. Drift baseline

- Current theme-mix shares saved to `reports/{run_id}/drift_baseline.json`.
- Future runs can compare against this baseline after pipeline/model changes.

---

## 8. Publish gate

An insight is promoted `draft → published` only if **all** apply:

| Rule | Default |
|------|---------|
| Final confidence ≥ min | 0.60 |
| Evidence count ≥ min | 1 |
| Source diversity ≥ min | 2 |
| Faithfulness pass | required |
| Not marked insufficient_evidence | required |

Otherwise it remains `draft` with explicit `publish_blockers`.  
No silent promotion of low-confidence insights.

Outputs:

- `data/insights/{run_id}/insights_published.jsonl`
- `data/insights/{run_id}/insights_draft.jsonl`
- `data/insights/{run_id}/insights_all.jsonl`

---

## 9. Stakeholder spot-check

- Checklist generated at `reports/{run_id}/stakeholder_spotcheck.md`.
- Status starts as `pending_human_review` (Phase 0: human spot-check of published insights).

---

## 10. Reproduce

```bash
cd phase4
python scripts/run_phase4.py --run-id 2026-07-16-weekly
```
