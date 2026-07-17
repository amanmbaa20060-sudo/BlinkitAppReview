# Phase-Wise Implementation Plan

## 1. Purpose

This plan turns the [problem statement](./problemstatement.md) and [architecture](./architecture.md) into an executable build sequence.

**Strategic goal supported**

> Increase the percentage of Monthly Active Customers who purchase products from at least one new category every month.

**End state**

An AI-powered discovery engine that:

- Ingests feedback from all seven analysis sources
- Identifies themes around habit, barriers, discovery, and unmet needs
- Answers the eight discovery questions with evidence-backed insights
- Validates insight quality
- Publishes findings on a dashboard with model documentation

---

## 2. Guiding Rules

| Rule | Meaning |
|------|---------|
| Batch-first | Prefer scheduled batch pipelines; streaming is optional later |
| Traceability | Every insight must link to feedback evidence IDs |
| Question-driven | Analysis work is complete only when all eight discovery questions have publishable answers |
| Docs as you build | Model documentation is written alongside each phase, not after the fact |
| No scope drift | Analysis intent stays as defined in the problem statement |

---

## 3. Phase Overview

| Phase | Name | Primary outcome | Depends on |
|-------|------|-----------------|------------|
| 0 | Foundations & decisions | Repo layout, schema, tech choices | — |
| 1 | Ingestion & corpus | Cleaned multi-source corpus | Phase 0 |
| 2 | Representation & themeing | Theme Store + sentiment/segments | Phase 1 |
| 3 | Discovery insights | Draft insights for all 8 questions | Phase 2 |
| 4 | Validation & governance | Publishable insight set | Phase 3 |
| 5 | Dashboard & model docs | Stakeholder-ready deliverable | Phase 4 |

```text
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
              │            │            │
              └─ sources   └─ themes    └─ Q&A insights
```

---

## 4. Phase 0 — Foundations & Decisions

### Objective

Lock implementation choices and project structure so later phases do not rework core contracts.

### Scope

- Confirm open decisions from architecture (providers, cadence, languages, QA depth, dashboard platform)
- Define canonical feedback schema in code/docs
- Set up repository structure, environments, and secrets handling
- Draft initial model-doc outline (sections to fill each phase)

### Work breakdown

| ID | Task | Details |
|----|------|---------|
| 0.1 | Decide embedding / LLM stack | Choose providers/models for embeddings, classification, synthesis |
| 0.2 | Decide storage stack | Raw store, cleaned DB/warehouse, vector index approach |
| 0.3 | Decide dashboard platform | Internal web app vs BI tool |
| 0.4 | Decide v1 languages | e.g., English primary; list any additional languages |
| 0.5 | Decide batch cadence | Weekly recommended for v1 unless volume requires daily |
| 0.6 | Finalize canonical schema | Implement fields from architecture §4.2 |
| 0.7 | Define source priority order | Suggested: Play Store → App Store → Reddit → Product reviews → Social → Forums → Q-commerce discussions |
| 0.8 | Create project skeleton | `data/`, `src/ingest/`, `src/analysis/`, `src/validation/`, `dashboard/`, `docs/` |
| 0.9 | Seed theme taxonomy draft | Habit, barriers, discovery, information needs, frustrations, experiment propensity, unmet needs |
| 0.10 | Start model documentation skeleton | Sections: gather/analyze, themes, insights, validation |

### Deliverables

- Decision log (providers, cadence, languages, dashboard, QA depth)
- Canonical schema specification
- Repo skeleton + environment templates (no secrets committed)
- Draft theme taxonomy v0
- Model documentation outline

### Exit criteria

- [ ] All architecture open decisions resolved or explicitly deferred with owner/date
- [ ] Canonical schema reviewed and frozen for Phase 1
- [ ] Empty pipeline can run end-to-end as a no-op smoke test

### Risks

| Risk | Mitigation |
|------|------------|
| Provider lock-in | Keep embedding/LLM behind thin interfaces |
| Over-scoping languages in v1 | Start with one primary language; expand in a later iteration |

---

## 5. Phase 1 — Ingestion & Cleaned Corpus

### Objective

Collect feedback from all seven sources, normalize into the canonical schema, and produce a cleaned, auditable corpus.

### Scope (analysis sources — do not drop)

1. App Store reviews  
2. Play Store reviews  
3. Reddit discussions  
4. Community forums  
5. Social media conversations  
6. Product reviews  
7. Quick-commerce discussions  

### Work breakdown

| ID | Task | Details |
|----|------|---------|
| 1.1 | Build Play Store adapter | Fetch/export reviews → raw store → canonical map |
| 1.2 | Build App Store adapter | Same contract as Play Store |
| 1.3 | Build Reddit adapter | Threads + comments; preserve parent/thread IDs |
| 1.4 | Build community forums adapter | Threaded Q&A mapping |
| 1.5 | Build social media adapter | Posts/replies with engagement metadata where available |
| 1.6 | Build product reviews adapter | Item-level reviews; keep product/category hints if present |
| 1.7 | Build quick-commerce discussions adapter | Platform-level discourse sources |
| 1.8 | Implement ingest quality gates | Drop empty text; dedupe; quarantine spam/ads/bots |
| 1.9 | Language detection | Store `language`; filter or route per Phase 0 decision |
| 1.10 | Persist raw + cleaned | Raw payloads immutable; cleaned corpus queryable |
| 1.11 | Ingest run versioning | Tag each batch with `run_id`, counts per source |
| 1.12 | Document gather workflow | Fill model-doc section: how data is gathered |

### Suggested source rollout inside Phase 1

| Sprint slice | Sources | Why |
|--------------|---------|-----|
| 1A | Play Store + App Store | High volume, ratings for later correlation |
| 1B | Reddit + product reviews | Long-form habit/barrier and trust signals |
| 1C | Social + forums + Q-commerce discussions | Completes full analysis scope |

### Deliverables

- Seven source adapters (or equivalent import pipelines)
- Raw Store populated
- Cleaned corpus in Canonical Feedback Schema
- Ingest quality report (kept / dropped / quarantined counts)
- Model-doc update: gather workflow

### Exit criteria

- [ ] All seven sources represented in the cleaned corpus (even if volumes differ)
- [ ] Deduplication and empty-text gates active
- [ ] Audit path raw → cleaned exists for sample records
- [ ] Corpus volume and date range documented

### Risks

| Risk | Mitigation |
|------|------------|
| Source ToS / access limits | Prefer official APIs/exports; keep manual/CSV fallback |
| Noisy social data | Strong quarantine rules; down-weight single-source themes later |
| Uneven volume across sources | Track coverage explicitly; do not drop low-volume sources from scope |

---

## 6. Phase 2 — Representation, Themeing & Enrichment

### Objective

Turn the cleaned corpus into embeddings, a versioned Theme Store, sentiment scores, and lightweight segment tags.

### Work breakdown

| ID | Task | Details |
|----|------|---------|
| 2.1 | Text preparation | Normalize text; chunk long Reddit/forum threads; optional PII redaction for display |
| 2.2 | Embedding generation | Embed cleaned units; store in embeddings index with `feedback_id` |
| 2.3 | Optional enrichment | Category mentions, competitor mentions, delivery/price/support keywords |
| 2.4 | Seed + discover themes | Start from taxonomy v0; cluster to discover additional themes |
| 2.5 | Consolidate taxonomy | Merge overlaps; write inclusion/exclusion definitions → taxonomy v1 |
| 2.6 | Assign themes | Similarity and/or LLM classification against definitions; multi-label allowed |
| 2.7 | Theme metrics | Prevalence, trend over time, source mix, co-occurrence |
| 2.8 | Sentiment & intensity | Overall + theme-level; urgency for frustrations; rating correlation where available |
| 2.9 | Segment tagging | Habitual vs explorer, deal-sensitive, life-stage cues when explicit, tenure tone when self-described |
| 2.10 | Theme Store persistence | Labels, definitions, membership, metrics, taxonomy version |
| 2.11 | Document themeing | Fill model-doc section: how themes are identified |

### Theme families to cover (from architecture)

- Habit & repetition  
- Exploration barriers  
- Discovery mechanisms  
- Information needs  
- Frustration patterns  
- Experiment propensity  
- Unmet needs  

### Deliverables

- Embeddings index
- Theme taxonomy v1 (versioned)
- Theme Store with assignments and metrics
- Sentiment and segment fields on cleaned records (or linked tables)
- Model-doc update: theme identification

### Exit criteria

- [ ] Every cleaned record has been processed for embedding (or explicitly skipped with reason)
- [ ] Theme coverage measured (% with ≥1 non-other theme)
- [ ] Taxonomy definitions written for all active themes
- [ ] Sample theme assignments reviewable for Phase 4 QA

### Risks

| Risk | Mitigation |
|------|------------|
| Overly coarse themes | Split high-volume clusters using discovery-question lenses |
| Overly fine themes | Merge rare near-duplicates; require minimum support count |
| Weak segment signal | Keep segments text-inferred only; report confidence |

---

## 7. Phase 3 — Discovery Question Modules & Draft Insights

### Objective

Produce draft, evidence-linked insights for every discovery question in the problem statement.

### Discovery questions (must all be covered)

1. Why do users repeatedly buy from the same categories?  
2. What prevents users from exploring new categories?  
3. How do users discover products today?  
4. What role do habits play in shopping behavior?  
5. What information do users need before trying a new category?  
6. What frustrations emerge repeatedly?  
7. Which user segments are more likely to experiment?  
8. What unmet needs emerge consistently across discussions?  

### Work breakdown

| ID | Task | Details |
|----|------|---------|
| 3.1 | Q1 module — same-category repetition | Habit themes + autopilot / convenience / risk-avoidance evidence |
| 3.2 | Q2 module — exploration barriers | Barrier ranking by frequency and severity |
| 3.3 | Q3 module — discovery today | Discovery-mechanism distribution + channel examples |
| 3.4 | Q4 module — role of habits | Habit vs deliberate-browse contrast |
| 3.5 | Q5 module — information needs | Gap list before trying a new category |
| 3.6 | Q6 module — recurring frustrations | Top complaints + time series |
| 3.7 | Q7 module — experiment segments | Segment × exploration-theme cross-tabs |
| 3.8 | Q8 module — unmet needs | Cross-source clustering + consensus scoring |
| 3.9 | Evidence retrieval | Top representative quotes per finding (`feedback_id`, source, date) |
| 3.10 | Insight synthesis | Headline, supporting themes, evidence pack, implication, confidence |
| 3.11 | Insight Store write | Structured draft insights mapped to question IDs |
| 3.12 | Document insight generation | Fill model-doc section: how insights are generated |

### Insight record shape (minimum)

| Field | Description |
|-------|-------------|
| `insight_id` | Stable ID |
| `question_id` | One of Q1–Q8 |
| `headline` | One clear finding |
| `supporting_themes` | Ranked theme IDs |
| `evidence_ids` | Cited feedback IDs |
| `implication` | Category-expansion implication |
| `confidence` | Provisional score (finalized in Phase 4) |
| `status` | `draft` until Phase 4 gate |

### Deliverables

- Eight question modules implemented
- Draft Insight Store populated for Q1–Q8
- Evidence packs attached to each draft insight
- Model-doc update: insight generation

### Exit criteria

- [ ] Every discovery question has ≥1 draft insight
- [ ] Every draft insight cites evidence IDs
- [ ] Implications explicitly relate to new-category purchase behavior among MACs
- [ ] No orphan insights without question mapping

### Risks

| Risk | Mitigation |
|------|------------|
| Generic LLM summaries | Constrain synthesis to retrieved evidence only |
| Thin evidence on some questions | Surface “insufficient evidence” explicitly; do not invent |

---

## 8. Phase 4 — Validation, Governance & Publish Gate

### Objective

Validate theme and insight quality, apply confidence gating, and produce a publishable insight set for the dashboard.

### Work breakdown

| ID | Task | Details |
|----|------|---------|
| 4.1 | Coverage check | % records with ≥1 meaningful theme |
| 4.2 | Sampling QA | Human and/or LLM-as-judge on random theme assignments |
| 4.3 | Faithfulness check | Insight claims must be entailed by cited quotes |
| 4.4 | Cross-source consistency | Down-weight themes present in only one noisy source |
| 4.5 | Stability check | Holdout / re-run; top themes directionally stable |
| 4.6 | Drift baseline | Record theme-mix baseline for future pipeline changes |
| 4.7 | Confidence finalization | Combine volume, source diversity, QA scores |
| 4.8 | Publish gate | `draft` → `published` only if thresholds met; else remain draft |
| 4.9 | Validation report | Methods, samples, outcomes for model documentation |
| 4.10 | Document validation | Fill model-doc section: how insight quality was validated |

### Illustrative pass criteria (tune in Phase 0)

| Check | Illustrative bar |
|-------|------------------|
| Theme assignment precision (sample) | Meets agreed threshold |
| Corpus theme coverage | Sufficient explanatory coverage |
| Insight faithfulness | All published claims supported |
| Stability | Directionally consistent top themes |
| Stakeholder spot-check | Accepted for decision use |

### Deliverables

- Validation report with metrics and samples
- Published Insight Store subset + remaining drafts labeled
- Governance config (thresholds, publish rules)
- Model-doc update: validation

### Exit criteria

- [ ] All four model-doc pillars have content (gather/analyze, themes, insights, validation)
- [ ] Published insights exist for as many of Q1–Q8 as evidence allows; gaps explicitly documented
- [ ] Publish rule enforced in pipeline (no silent promotion of low-confidence insights)

### Risks

| Risk | Mitigation |
|------|------------|
| QA bottleneck | Prioritize top themes and all published insights for review |
| Over-filtering | Keep drafts visible in an internal “draft” dashboard view if needed |

---

## 9. Phase 5 — Insight Dashboard & Stakeholder Delivery

### Objective

Ship the dashboard so all analysis and insights are visible, filterable, and backed by methodology documentation.

### Dashboard views (from architecture)

1. Executive overview  
2. Theme explorer  
3. Discovery Q&A board (one panel per discovery question)  
4. Segment lens  
5. Frustration monitor  
6. Evidence browser  
7. Methodology / model docs  

### Work breakdown

| ID | Task | Details |
|----|------|---------|
| 5.1 | Wire Theme Store + Insight Store | Read-only API or direct BI dataset |
| 5.2 | Executive overview | Top barriers, opportunities, category-expansion narrative |
| 5.3 | Theme explorer | Prevalence, trend, sentiment, source breakdown |
| 5.4 | Discovery Q&A board | Headline + evidence for each question |
| 5.5 | Segment lens | Experiment propensity by inferred segment |
| 5.6 | Frustration monitor | Recurring pain themes over time |
| 5.7 | Evidence browser | Search/filter by source, date, theme, sentiment, segment |
| 5.8 | Insight → evidence click-through | Navigate from finding to supporting feedback |
| 5.9 | Export summary | Stakeholder-ready export (PDF/CSV/share link) |
| 5.10 | Methodology view | Embed or link full model documentation |
| 5.11 | Access & privacy polish | Minimize PII on public views; respect source terms |
| 5.12 | UAT with stakeholders | Spot-check findings; capture acceptance |

### Deliverables

- Working insight dashboard with all primary views
- Filters: source, date range, theme, sentiment, segment
- Embedded/linked model documentation
- Stakeholder UAT notes and final acceptance

### Exit criteria

- [ ] All published insights visible on the Q&A board
- [ ] Evidence click-through works for published insights
- [ ] Methodology view covers gather/analyze, themes, insights, validation
- [ ] Stakeholders can answer the eight discovery questions from the dashboard without reading the raw corpus

### Risks

| Risk | Mitigation |
|------|------------|
| Dashboard built before data is ready | Phase 5 starts only after Phase 4 publish gate |
| Overbuilt UI | Ship required views first; defer polish |

---

## 10. Cross-Phase Workstreams

These run alongside phases rather than as a separate phase:

| Workstream | Activities | Owner focus |
|------------|------------|-------------|
| Model documentation | Update after each phase exit | Always current with pipeline behavior |
| Pipeline versioning | `run_id`, taxonomy version, model version | Reproducibility |
| Data ethics / ToS | Source compliance, PII minimization | Continuous |
| Stakeholder sync | Share interim theme findings after Phase 2–3 | Avoid late surprises |

---

## 11. Dependency Map

```text
Canonical schema (0)
        │
        ▼
Source adapters + cleaned corpus (1)
        │
        ▼
Embeddings + Theme Store + sentiment/segments (2)
        │
        ▼
Q1–Q8 modules + draft Insight Store (3)
        │
        ▼
Validation + publish gate (4)
        │
        ▼
Dashboard + methodology (5)
```

**Hard blockers**

- Phase 2 cannot start without a usable cleaned corpus  
- Phase 3 cannot publish answers without theme assignments  
- Phase 5 must not present unpublished low-confidence insights as primary findings  

---

## 12. Suggested Timeline (indicative)

Exact dates depend on team size and source access. Relative effort:

| Phase | Relative effort | Notes |
|-------|-----------------|-------|
| 0 | Small | 3–5 days if decisions are prompt |
| 1 | Large | Source access is the critical path |
| 2 | Large | Theme consolidation needs analyst review time |
| 3 | Medium–Large | Eight modules; reuse shared evidence retrieval |
| 4 | Medium | QA sampling effort dominates |
| 5 | Medium–Large | Parallelize UI views after data contracts are stable |

**Fast path option:** After Phase 1A (app stores only), run a thin Phase 2–3 pilot on that subset to validate methods, then complete remaining sources — without removing any source from final scope.

---

## 13. Definition of Done (Project)

The implementation is complete when all of the following are true:

1. Feedback from all seven problem-statement sources is in the cleaned corpus.  
2. Themes covering habit, barriers, discovery, information needs, frustrations, experiment propensity, and unmet needs are identified and versioned.  
3. All eight discovery questions have dashboard answers (published insights or documented evidence gaps).  
4. Model documentation explains gather/analyze workflow, theme identification, insight generation, and validation.  
5. The dashboard shows analysis and insights with evidence drill-down.  
6. Published insights passed the validation/publish gate.

---

## 14. Traceability Matrix

| Problem / architecture requirement | Phase(s) |
|------------------------------------|----------|
| Analyze App Store reviews | 1 |
| Analyze Play Store reviews | 1 |
| Analyze Reddit discussions | 1 |
| Analyze community forums | 1 |
| Analyze social media conversations | 1 |
| Analyze product reviews | 1 |
| Analyze quick-commerce discussions | 1 |
| Answer eight discovery questions | 3, 4, 5 |
| Document gather & analyze workflow | 1, 2, 5 |
| Document theme identification | 2, 5 |
| Document insight generation | 3, 5 |
| Document insight validation | 4, 5 |
| Insight dashboard deliverable | 5 |
| Canonical schema + stores | 0, 1, 2, 3 |
| Validation & publish gate | 4 |

---

## 15. Immediate Next Step

Start **Phase 0**: resolve open technical decisions, freeze the canonical schema, scaffold the repo, and draft theme taxonomy v0 plus the model documentation outline.
