# How Themes Are Identified (Phase 2)

Fills model documentation section: **How themes are identified**.  
Outline: [`phase0/model_docs/model_documentation_outline.md`](../../phase0/model_docs/model_documentation_outline.md)

---

## 1. Seed taxonomy

- Start from Phase 0 `theme_taxonomy_v0` (seven families covering habit, barriers, discovery, information needs, frustrations, experiment propensity, unmet needs).
- Each theme has inclusion/exclusion definitions used for assignment and documentation.

## 2. Workflow

```text
Cleaned corpus (Phase 1)
  → Text preparation (normalize, chunk long threads, light PII redaction)
  → Local hashing embeddings (dim=256) stored in embeddings index
  → Optional enrichment (category / competitor / delivery-price-support tags)
  → Multi-label theme assignment (keywords + definition similarity)
  → Residual clustering for discovery candidates
  → Consolidate taxonomy v1
  → Sentiment + segment enrichment
  → Theme metrics (prevalence, trend, source mix, co-occurrence)
  → Theme Store persistence
```

## 3. Embedding model

| Item | Value |
|------|-------|
| Provider (v1) | Local feature-hashing (`HashingEmbeddingClient`) |
| Model id | `local_hashing_dim256` |
| Dimensions | 256 |
| Rationale | Offline, deterministic, provider-swappable per Phase 0 interfaces |
| Future | OpenAI-compatible embeddings behind the same interface |

## 3b. Groq LLM theme classification

| Item | Value |
|------|-------|
| Provider | Groq (`GROQ_API_KEY` from repo-root `.env`) |
| Model | `GROQ_MODEL` (default `llama-3.3-70b-versatile`) |
| Role | Multi-label theme classification on unique base texts; merged with keyword/similarity assignments |
| Assignment method | `groq_llm_plus_keyword_hits_plus_definition_hash_embedding_similarity` |

Every cleaned record is either **embedded** or **skipped with an explicit reason** (`quarantined`, `non_english:*`, `empty_prepared`). Non-English rows may still be embedded for audit but are excluded from themeing (Phase 0 language policy).

## 4. Assignment rules

Multi-label allowed. A theme is assigned when either:

1. **Keyword hits** ≥ 1 against the theme’s cue list, or  
2. **Cosine similarity** between text embedding and theme-definition embedding ≥ `0.12`

Scores combine keyword strength and similarity. If nothing matches → `theme.other` (excluded from coverage %).

## 5. Discovery & consolidation → v1

1. Collect residuals (`theme.other`).
2. Greedy cosine clustering; keep clusters with support ≥ 8 as `discovered_candidates`.
3. Do **not** auto-merge candidates into core themes (avoids overly fine/noisy themes).
4. Publish `taxonomy_version = v1` with v0 definitions retained + consolidation notes.

## 6. Metrics produced

- Prevalence (count + share among analyzable records)
- Trend by month
- Source mix per theme
- Co-occurrence pairs
- Sentiment mix per theme

Stored at: `data/themes/v1/{run_id}/metrics.json` and `membership.jsonl`.

## 7. Sentiment & segments (enrichment)

- **Sentiment:** lexicon + optional star-rating blend; frustration intensity for urgency.
- **Segments:** text-inferred only — habitual reorderer, occasional explorer, deal-sensitive, life-stage pet/parent, tenure tone cues — with confidence scores.

## 8. Artifacts for Phase 4 QA

- `samples/theme_assignments_sample.json` — reviewable sample of assignments with text + themes.
