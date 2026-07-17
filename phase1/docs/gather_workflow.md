# How the Workflow Gathers Data (Phase 1)

Fills model documentation section: **How your workflow gathers and analyzes data** (gather portion).  
Outline: [`phase0/model_docs/model_documentation_outline.md`](../../phase0/model_docs/model_documentation_outline.md)

---

## 1. Purpose

Phase 1 builds a multi-source ingestion pipeline that:

1. Loads feedback from seven sources (fixture/export files in v1)
2. Persists immutable raw payloads
3. Maps each record to Canonical Feedback Schema `v1.0.0`
4. Applies quality gates (empty drop, dedupe, spam/bot quarantine)
5. Detects language
6. Writes a cleaned corpus tagged with `run_id`
7. Emits an ingest quality report

Analysis (embeddings, themes, insights) starts in Phase 2+.

---

## 2. Sources and adapters

| Source enum | Adapter | Fixture / export |
|-------------|---------|------------------|
| `play_store` | `PlayStoreAdapter` | `data/fixtures/play_store.jsonl` |
| `app_store` | `AppStoreAdapter` | `data/fixtures/app_store.jsonl` |
| `reddit` | `RedditAdapter` | `data/fixtures/reddit.jsonl` |
| `product_reviews` | `ProductReviewsAdapter` | `data/fixtures/product_reviews.jsonl` |
| `social_media` | `SocialMediaAdapter` | `data/fixtures/social_media.jsonl` |
| `community_forums` | `CommunityForumsAdapter` | `data/fixtures/community_forums.jsonl` |
| `quick_commerce_discussions` | `QuickCommerceAdapter` | `data/fixtures/quick_commerce_discussions.jsonl` |

**Access method (v1):** offline JSONL fixtures simulating API/CSV exports (ToS-safe fallback from the implementation plan). Live API connectors can replace fixture paths without changing the canonical schema.

**Batch cadence:** weekly (`run_id` default `YYYY-MM-DD-weekly`), per Phase 0 decision.

**Priority order:** Play Store → App Store → Reddit → Product reviews → Social → Forums → Quick-commerce discussions.

---

## 3. Raw store layout

```text
data/raw/{source}/{run_id}/raw.jsonl
data/raw/{source}/{run_id}/meta.json
```

Raw payloads are written **before** quality gates and are treated as immutable audit inputs.

---

## 4. Canonical mapping

Each adapter implements `to_canonical(raw) → CanonicalFeedback` using Phase 0 frozen fields:

- Required: `feedback_id`, `source`, `created_at`, `text`, `ingested_at`, `raw_payload`
- Optional: `rating`, `language`, `url_or_ref`, `author_handle`, `engagement`, `thread_id`, `parent_id`, `run_id`, quarantine fields

Threaded sources (Reddit, forums) preserve `thread_id` / `parent_id`.  
Product reviews keep `product_id` / `category` inside `engagement`.

Schema reference: `phase0/schema/canonical_feedback_schema.json`.

---

## 5. Quality gates

Applied in order:

1. **Empty text** — drop (not written to cleaned)
2. **Near-duplicate** — same source + identical normalized text fingerprint within `dedupe_window_days` (default 30) → drop
3. **Spam / bot quarantine** — keyword and regex checks → keep in cleaned with `is_quarantined=true` and `quarantine_reason`

---

## 6. Language detection

- Library: `langdetect` (heuristic fallback if unavailable)
- All cleaned records store `language`
- Phase 0 policy: non-English remains in cleaned corpus but is excluded from themeing/insights in Phase 2+ unless translated

---

## 7. Cleaned corpus outputs

```text
data/cleaned/{run_id}/feedback.jsonl
data/cleaned/{run_id}/feedback.csv
reports/{run_id}/quality_report.json
```

---

## 8. How to reproduce a gather run

```bash
cd phase1
pip install -r requirements.txt
python scripts/run_ingest.py --run-id 2026-07-16-weekly
```

---

## 9. Analyze (later phases)

Gather ends at the cleaned corpus. Analyze continues as:

`prepare → represent → theme → enrich → answer → synthesize → validate → publish` (Phases 2–5).
