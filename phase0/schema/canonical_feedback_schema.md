# Canonical Feedback Schema

**Status:** Frozen for Phase 1  
**Version:** `1.0.0`  
**Frozen date:** 2026-07-16  
**Machine-readable:** [`canonical_feedback_schema.json`](./canonical_feedback_schema.json)

This is the shared contract all source adapters must map into before analysis.

---

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| `feedback_id` | string | Stable unique ID (prefer source-native ID; otherwise hash of source + permalink + created_at) |
| `source` | enum | One of the seven analysis sources (see below) |
| `created_at` | string (ISO-8601) | Original publish/post time (UTC preferred) |
| `text` | string | Normalized body text (non-empty after clean) |
| `ingested_at` | string (ISO-8601) | Pipeline ingest timestamp |
| `raw_payload` | object | Original payload for auditability |

## Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `rating` | number \| null | Star rating when available (App/Play Store, some product reviews) |
| `language` | string \| null | Detected language code (BCP-47 / ISO 639-1, e.g. `en`) |
| `url_or_ref` | string \| null | Permalink or external reference |
| `author_handle` | string \| null | Public handle when available |
| `engagement` | object \| null | Source-specific engagement metrics (likes, upvotes, replies, etc.) |
| `thread_id` | string \| null | Parent thread ID for Reddit/forums |
| `parent_id` | string \| null | Parent comment/post ID when chunked |
| `run_id` | string \| null | Ingest batch / pipeline run identifier |
| `quarantine_reason` | string \| null | Set when record is quarantined (spam/ads/bot) |
| `is_quarantined` | boolean | Default `false` |

## `source` enum (frozen)

```text
play_store
app_store
reddit
product_reviews
social_media
community_forums
quick_commerce_discussions
```

## Quality gates (ingest)

1. Drop empty / non-textual records (do not write to cleaned corpus).
2. Deduplicate near-identical content within a source window.
3. Flag spam, ads, and bot-like posts → `is_quarantined = true` with reason.
4. Retain audit trail: raw payload always preserved in raw store.

## Example record

```json
{
  "feedback_id": "play_store:abc123",
  "source": "play_store",
  "created_at": "2026-06-01T10:15:00Z",
  "text": "I always reorder the same groceries and never notice other categories.",
  "rating": 4,
  "language": "en",
  "url_or_ref": "https://example.invalid/review/abc123",
  "author_handle": null,
  "engagement": null,
  "thread_id": null,
  "parent_id": null,
  "run_id": "2026-07-16-weekly",
  "ingested_at": "2026-07-16T12:00:00Z",
  "is_quarantined": false,
  "quarantine_reason": null,
  "raw_payload": { "original": "..." }
}
```

## Change policy

- Additive optional fields may be introduced in later phases with a minor version bump.
- Renames/removals of required fields require a major version and Phase 0 re-freeze.
- Phase 1 adapters must validate against `canonical_feedback_schema.json`.
