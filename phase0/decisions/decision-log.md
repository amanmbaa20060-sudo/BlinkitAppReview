# Decision Log (Phase 0)

All architecture open decisions are resolved or deferred below.  
Owner: Project team · Date frozen: 2026-07-16 · Status: **Frozen for Phase 1**

---

## 0.1 Embedding / LLM stack

| Item | Decision |
|------|----------|
| **Status** | Resolved |
| **Embeddings** | OpenAI-compatible embedding API (`text-embedding-3-small` or equivalent) behind a thin `EmbeddingClient` interface |
| **Classification / theme assignment** | LLM classification against taxonomy definitions via `LLMClient` interface |
| **Insight synthesis** | Same `LLMClient` with retrieval-constrained prompts (evidence-only) |
| **Local/dev fallback** | Optional sentence-transformers model for offline smoke tests only |
| **Rationale** | Interface isolation avoids provider lock-in (architecture risk mitigation) |
| **Deferred** | Exact production model version may be upgraded without schema changes |

**Interface locations (skeleton):**

- `project_skeleton/src/common/embeddings.py`
- `project_skeleton/src/common/llm.py`

---

## 0.2 Storage stack

| Item | Decision |
|------|----------|
| **Status** | Resolved |
| **Raw store** | Local filesystem / object-store layout: `data/raw/{source}/{run_id}/` (JSONL or JSON payloads) |
| **Cleaned corpus** | Tabular files first: `data/cleaned/{run_id}/feedback.parquet` (CSV acceptable in early Phase 1) |
| **Embeddings index** | Vector store behind `VectorIndex` interface; default v1 = Chroma (local persistent) |
| **Theme store** | `data/themes/{taxonomy_version}/` — JSON/Parquet membership + metrics |
| **Insight store** | `data/insights/{run_id}/insights.jsonl` |
| **Rationale** | File-first keeps Phase 1–3 simple; interfaces allow warehouse/vector DB swap later |
| **Deferred** | Cloud warehouse (e.g., BigQuery/Snowflake) and managed vector DB until volume requires it |

---

## 0.3 Dashboard platform

| Item | Decision |
|------|----------|
| **Status** | Resolved |
| **Platform** | Internal web app using **Streamlit** for v1 |
| **Rationale** | Fast path for filters, charts, evidence drill-down; aligns with analytics deliverable |
| **Deferred** | Migration to a custom React app if stakeholder UX requires it post-v1 |
| **Location** | `project_skeleton/dashboard/` |

---

## 0.4 v1 languages

| Item | Decision |
|------|----------|
| **Status** | Resolved |
| **Primary** | English |
| **Ingest policy** | Detect and store `language` for all records; non-English kept in raw/cleaned but **excluded from themeing/insights in v1** unless translated |
| **Rationale** | Avoid over-scoping languages in v1 (architecture risk mitigation) |
| **Deferred** | Hindi and other major Indian languages for a later iteration |

---

## 0.5 Batch cadence

| Item | Decision |
|------|----------|
| **Status** | Resolved |
| **Cadence** | **Weekly** batch runs for v1 |
| **Rationale** | Matches architecture recommendation; enough for trend views without streaming complexity |
| **Deferred** | Daily cadence if source volume or stakeholder need increases |

---

## 0.7 Source priority order

| Priority | Source | `source` enum value |
|----------|--------|---------------------|
| 1 | Play Store reviews | `play_store` |
| 2 | App Store reviews | `app_store` |
| 3 | Reddit discussions | `reddit` |
| 4 | Product reviews | `product_reviews` |
| 5 | Social media conversations | `social_media` |
| 6 | Community forums | `community_forums` |
| 7 | Quick-commerce discussions | `quick_commerce_discussions` |

**Phase 1 rollout slices (from plan):**

- **1A:** `play_store`, `app_store`
- **1B:** `reddit`, `product_reviews`
- **1C:** `social_media`, `community_forums`, `quick_commerce_discussions`

All seven remain in final scope.

---

## QA depth (architecture open decision)

| Item | Decision |
|------|----------|
| **Status** | Resolved |
| **Approach** | LLM-as-judge on random theme-assignment samples **plus** human spot-check of all **published** insights |
| **Publish gate** | Insights below configured confidence stay `draft` |
| **Deferred** | Full dual human inter-rater labeling program |

---

## Summary table

| Decision area | Choice | Status |
|---------------|--------|--------|
| Embeddings / LLM | OpenAI-compatible APIs behind thin interfaces | Resolved |
| Storage | Filesystem raw + Parquet cleaned + Chroma vectors | Resolved |
| Dashboard | Streamlit internal web app | Resolved |
| Languages | English primary for analysis v1 | Resolved |
| Batch cadence | Weekly | Resolved |
| Source priority | Play → App → Reddit → Product → Social → Forums → Q-commerce | Resolved |
| QA depth | LLM-judge + human spot-check on published insights | Resolved |
| Managed warehouse / multi-language / daily / React UI | — | Deferred (see above) |
