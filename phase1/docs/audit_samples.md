# Audit Path: Raw → Cleaned

Demonstrates that every cleaned record retains an audit trail to its raw payload.

## Path

```text
Fixture export
  → data/raw/{source}/{run_id}/raw.jsonl          (immutable raw)
  → adapter.to_canonical(...)
  → language detection
  → quality gates
  → data/cleaned/{run_id}/feedback.jsonl         (canonical + raw_payload)
```

## How to audit a sample

1. Pick a `feedback_id` from `data/cleaned/{run_id}/feedback.jsonl`.
2. Read its `raw_payload` field (full original export object).
3. Confirm the same object exists in `data/raw/{source}/{run_id}/raw.jsonl`.
4. Confirm `run_id`, `source`, and `ingested_at` are populated.

## Example (after ingest)

| Field | Example |
|-------|---------|
| `feedback_id` | `play_store:ps-1001` |
| `source` | `play_store` |
| Raw file | `data/raw/play_store/{run_id}/raw.jsonl` |
| Cleaned file | `data/cleaned/{run_id}/feedback.jsonl` |
| Audit key | `raw_payload.review_id == "ps-1001"` |

## Dropped vs quarantined

| Outcome | In raw store? | In cleaned corpus? |
|---------|---------------|--------------------|
| Empty text | Yes | No |
| Duplicate | Yes | No |
| Spam/bot | Yes | Yes (`is_quarantined=true`) |
| Kept | Yes | Yes |

Raw always retains what was collected; cleaned is the analysis-ready view with quarantine flags.
