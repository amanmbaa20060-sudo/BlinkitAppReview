# Architecture

## 1. Purpose

This document defines the system architecture for an AI-powered discovery engine that analyzes user feedback at scale to explain why Monthly Active Customers (MACs) stay within familiar purchase categories — and what would help them try new ones.

It is designed to support the strategic goal:

> Increase the percentage of Monthly Active Customers who purchase products from at least one new category every month.

The architecture covers data gathering, analysis workflow, theme identification, insight generation, quality validation, and the final insight dashboard.

---

## 2. Design Principles

| Principle | Description |
|-----------|-------------|
| Source-agnostic ingestion | All feedback channels normalize into a shared schema before analysis |
| Traceable insights | Every insight links back to supporting evidence (quotes, posts, reviews) |
| Question-driven outputs | Analysis is organized around the discovery questions in the problem statement |
| Validated quality | Themes and insights are measured for reliability before dashboard publication |
| Explainable workflow | Model documentation must describe gather → analyze → theme → insight → validate |

---

## 3. High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA SOURCES                                      │
│  App Store │ Play Store │ Reddit │ Forums │ Social │ Product │ Q-Commerce  │
│  Reviews   │ Reviews    │        │        │ Media  │ Reviews │ Discussions │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     INGESTION & NORMALIZATION LAYER                         │
│  Collectors → Deduplication → Language filter → Canonical Feedback Schema   │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROCESSING & STORAGE                                 │
│  Raw Store │ Cleaned Corpus │ Embeddings Index │ Theme Store │ Insight Store│
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI ANALYSIS ENGINE                                  │
│  Cleaning → Embedding → Clustering/Themeing → Sentiment → Segment tagging   │
│  Discovery Question Answering → Insight Synthesis → Evidence Linking        │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VALIDATION & GOVERNANCE                                  │
│  Sampling QA │ Inter-rater / LLM-judge checks │ Drift & coverage metrics    │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INSIGHT DASHBOARD                                   │
│  Themes │ Barriers │ Habits │ Segments │ Unmet Needs │ Evidence Explorer    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. System Components

### 4.1 Data Sources

| Source | Typical signal | Role in analysis |
|--------|----------------|------------------|
| App Store reviews | Ratings + short free text | Friction, discovery UX, category findability |
| Play Store reviews | Ratings + free text | Same as App Store; volume and Android-specific UX |
| Reddit discussions | Long-form threads | Habits, workarounds, category reluctance |
| Community forums | Threaded Q&A | Information gaps before trying a new category |
| Social media conversations | Short posts / replies | Recurring frustrations and praise |
| Product reviews | Item-level feedback | Quality/trust barriers that block category expansion |
| Quick-commerce discussions | Platform-level discourse | Cross-category shopping patterns and unmet needs |

### 4.2 Ingestion Layer

**Responsibilities**

- Pull or import feedback from each source on a defined schedule (batch-first; streaming optional later)
- Capture metadata: source, timestamp, rating (if any), language, URL/ID, author handle (when available), engagement metrics
- Apply source-specific adapters so each feed maps to one canonical schema

**Canonical Feedback Schema (logical)**

| Field | Description |
|-------|-------------|
| `feedback_id` | Stable unique ID |
| `source` | One of the seven analysis sources |
| `created_at` | Original publish/post time |
| `text` | Normalized body text |
| `rating` | Optional star rating |
| `language` | Detected language code |
| `url_or_ref` | Permalink or external reference |
| `raw_payload` | Original payload for auditability |
| `ingested_at` | Pipeline ingest timestamp |

**Quality gates at ingest**

- Drop empty / non-textual records
- Deduplicate near-identical content within a source window
- Flag spam, ads, and bot-like posts for exclusion or quarantine
- Retain audit trail from raw → cleaned for model documentation

### 4.3 Storage Layer

| Store | Contents | Consumers |
|-------|----------|-----------|
| Raw store | Unmodified source payloads | Reprocessing, audits |
| Cleaned corpus | Canonical feedback records | Themeing, sentiment, Q&A |
| Embeddings index | Vector representations of feedback text | Clustering, semantic search, evidence retrieval |
| Theme store | Theme labels, definitions, membership, prevalence | Dashboard, reporting |
| Insight store | Synthesized insights mapped to discovery questions + evidence IDs | Dashboard, model docs |

### 4.4 AI Analysis Engine

The analysis engine is the core of the discovery system. It turns cleaned feedback into themes, segments, and question-aligned insights.

#### 4.4.1 Text Preparation

- Normalize whitespace, URLs, and repeated characters
- Optional PII redaction for public dashboard surfaces
- Language detection; primary analysis language configurable (e.g., English + major Indian languages if present)
- Chunk long threads (Reddit/forums) into post-level and thread-level units while preserving parent context

#### 4.4.2 Representation

- Generate text embeddings for semantic similarity
- Optionally enrich with structured tags: category mentions, competitor mentions, delivery/price/support keywords

#### 4.4.3 Theme Identification

Themes are the primary analytical unit.

**Workflow**

1. Embed cleaned feedback
2. Cluster semantically similar items (or use supervised/LLM-assisted labeling seeded by discovery questions)
3. Name and define each theme with inclusion/exclusion criteria
4. Assign every feedback item zero or more themes
5. Measure theme prevalence, trend over time, and source mix

**Theme taxonomy (seeded by problem context; refined from data)**

| Theme family | Example themes |
|--------------|----------------|
| Habit & repetition | Same-basket loyalty, autopilot reordering, low browse intent |
| Exploration barriers | Unknown category value, trust risk, price uncertainty, relevance doubt |
| Discovery mechanisms | Search-led, homepage banners, recommendations, social proof, word of mouth |
| Information needs | Ingredients, use-cases, sizing, freshness, return policy, reviews depth |
| Frustration patterns | Stockouts, late delivery, poor substitutes, opaque fees, weak support |
| Experiment propensity | Deal-driven trial, life-event triggers, gift/occasion buying, niche interest |
| Unmet needs | Missing assortment, weak guidance, no “starter kits”, poor cross-category cues |

Theme definitions and assignment rules must be documented for model documentation.

#### 4.4.4 Sentiment & Intensity

- Overall and theme-level sentiment
- Separate intensity/urgency signals for recurring frustrations
- Rating correlation where star ratings exist (App/Play Store)

#### 4.4.5 Segment Tagging

Infer lightweight segments from language and behavior cues in text (not from private CRM unless later integrated), for example:

- Habitual reorderers vs. occasional explorers
- Deal-sensitive experimenters
- Parents / pet owners / health-focused shoppers (when explicitly mentioned)
- New vs. long-tenure tone (when self-described)

Segments answer: *Which user segments are more likely to experiment?*

#### 4.4.6 Discovery Question Answering

Each problem-statement question maps to a dedicated insight module:

| Discovery question | Analytical approach |
|--------------------|---------------------|
| Why do users repeatedly buy from the same categories? | Habit themes + evidence of autopilot / convenience / risk avoidance |
| What prevents users from exploring new categories? | Barrier theme ranking + severity/frequency |
| How do users discover products today? | Discovery-mechanism theme distribution + channel examples |
| What role do habits play in shopping behavior? | Habit vs. deliberate-browse contrast; recurrence patterns in language |
| What information do users need before trying a new category? | Information-need theme extraction and gap list |
| What frustrations emerge repeatedly? | Frustration theme time series and top complaints |
| Which user segments are more likely to experiment? | Segment × exploration-theme cross-tabs |
| What unmet needs emerge consistently across discussions? | Cross-source unmet-need clustering and consensus scoring |

#### 4.4.7 Insight Synthesis

For each discovery question, produce:

- **Headline insight** — one clear finding
- **Supporting themes** — ranked contributors
- **Evidence pack** — representative quotes with source and date
- **Implication** — what the finding suggests for category-expansion strategy
- **Confidence** — based on volume, source diversity, and validation score

Insights are written to the Insight Store in a structured format for the dashboard.

### 4.5 Validation & Governance

Required so model documentation can explain how insight quality was validated.

| Method | What it checks |
|--------|----------------|
| Coverage check | Share of corpus assigned to at least one meaningful theme |
| Sampling QA | Human or LLM-as-judge review of random theme assignments |
| Evidence faithfulness | Insight claims must be entailed by cited feedback |
| Cross-source consistency | Themes that appear in only one noisy source are down-weighted |
| Stability check | Re-run on a holdout slice; theme rankings should remain directionally stable |
| Drift monitoring | Alert when theme mix shifts sharply after a pipeline or model change |

**Publish rule:** Insights below a configured confidence/validation threshold stay in draft and do not appear as primary dashboard findings.

### 4.6 Insight Dashboard

End deliverable for viewing all analysis and insights.

**Primary views**

1. **Executive overview** — progress narrative toward category expansion; top barriers and opportunities
2. **Theme explorer** — prevalence, trend, sentiment, source breakdown
3. **Discovery Q&A board** — one panel per discovery question with headline + evidence
4. **Segment lens** — experiment propensity by inferred segment
5. **Frustration monitor** — recurring pain themes over time
6. **Evidence browser** — search/filter feedback with theme and source filters
7. **Methodology / model docs** — workflow, themeing, insight generation, validation (embedded or linked)

**Interaction requirements**

- Filter by source, date range, theme, sentiment, segment
- Click-through from insight → supporting feedback
- Export summary for stakeholder sharing

---

## 5. End-to-End Workflow

How the system gathers and analyzes data (for model documentation):

```text
1. Collect
   Source adapters fetch reviews/discussions into the Raw Store.

2. Normalize
   Map to Canonical Feedback Schema; dedupe; language detect; quarantine junk.

3. Prepare
   Clean text; chunk long threads; optionally redact PII for display.

4. Represent
   Create embeddings; optional keyword/entity enrichment.

5. Theme
   Cluster / label themes; define taxonomy; assign themes to records.

6. Enrich
   Score sentiment; tag segments; compute prevalence and trends.

7. Answer
   Run discovery-question modules; retrieve top evidence per finding.

8. Synthesize
   Generate structured insights with confidence and implications.

9. Validate
   Coverage, sampling QA, faithfulness, stability; gate publishable insights.

10. Publish
    Load Theme Store + Insight Store into the dashboard.
```

---

## 6. How Themes Are Identified

Documented process (to be mirrored in model documentation):

1. **Seed** themes from strategic context (habits, barriers, discovery, information needs, frustrations, segments, unmet needs).
2. **Discover** additional themes from unsupervised clustering of embeddings on the cleaned corpus.
3. **Consolidate** overlapping clusters into a stable taxonomy with clear definitions.
4. **Assign** themes to each feedback item via similarity thresholds and/or LLM classification against definitions.
5. **Measure** frequency, co-occurrence, sentiment, and source diversity per theme.
6. **Review** ambiguous or low-confidence assignments in the validation loop.
7. **Version** the taxonomy so dashboard and docs can cite the theme version used.

---

## 7. How Insights Are Generated

1. Aggregate theme metrics relevant to each discovery question.
2. Retrieve the strongest evidence examples from the embeddings index / theme members.
3. Synthesize a concise insight using AI generation constrained to retrieved evidence.
4. Attach implication for category-expansion strategy.
5. Score confidence from volume, multi-source agreement, and validation results.
6. Persist to Insight Store only if publish criteria are met.

---

## 8. How Insight Quality Is Validated

| Stage | Metric / activity | Pass criteria (illustrative) |
|-------|-------------------|------------------------------|
| Theme assignment | Precision on sampled labels | Meets agreed threshold |
| Coverage | % records with ≥1 non-other theme | Sufficient explanatory coverage |
| Faithfulness | Insight vs. cited quotes | Claims supported by evidence |
| Stability | Rank correlation across re-runs / holdout | Directionally consistent top themes |
| Stakeholder review | Spot-check of dashboard findings | Accepted for decision use |

All validation methods, samples, and outcomes should be recorded for model documentation.

---

## 9. Logical Data Flow (per feedback item)

```text
Source record
  → Raw Store
  → Canonical Feedback Record
  → Cleaned Text (+ optional chunks)
  → Embedding
  → Theme Assignment(s)
  → Sentiment + Segment Tags
  → Contribution to Question-Level Aggregates
  → Eligible as Evidence for Published Insights
  → Visible in Dashboard (filters + evidence browser)
```

---

## 10. Technology Building Blocks (reference)

Implementation can vary; the architecture assumes these capability types:

| Capability | Examples of approach |
|------------|----------------------|
| Ingestion | Source APIs, scrapers/exports, batch connectors |
| Storage | Object store for raw; warehouse/DB for cleaned + insights; vector DB for embeddings |
| NLP / LLM | Embedding model, clustering, classification, insight synthesis |
| Orchestration | Scheduled pipelines (batch) with versioned runs |
| Dashboard | BI / web app with filters, charts, and evidence drill-down |
| Docs | Versioned model card describing workflow, themes, insights, validation |

---

## 11. Non-Functional Requirements

| Area | Requirement |
|------|-------------|
| Scalability | Handle multi-source volume growth without redesigning the schema |
| Traceability | Every published insight cites feedback IDs |
| Reproducibility | Pipeline runs are versioned (code, theme taxonomy, model) |
| Privacy | Respect source terms; minimize PII on public dashboard views |
| Refresh | Support periodic re-analysis as new feedback arrives |
| Explainability | Dashboard methodology view matches model documentation |

---

## 12. Deliverables Mapped to Architecture

| Problem-statement need | Architecture response |
|------------------------|------------------------|
| Analyze seven feedback source types | Source adapters + canonical schema |
| Answer eight discovery questions | Question modules + Insight Store |
| Explain gather/analyze workflow | Sections 5 and model docs view |
| Explain theme identification | Section 6 + Theme Store versioning |
| Explain insight generation | Section 7 + synthesis pipeline |
| Explain validation | Section 8 + governance gates |
| Dashboard of analysis & insights | Section 4.6 Insight Dashboard |

---

## 13. Suggested Implementation Phases

| Phase | Focus | Outcome |
|-------|-------|---------|
| 1 | Ingestion + canonical schema for priority sources | Cleaned multi-source corpus |
| 2 | Embeddings, themeing, sentiment | Theme Store populated |
| 3 | Discovery question modules + evidence packs | Draft insights |
| 4 | Validation loop + confidence gating | Publishable insight set |
| 5 | Dashboard + embedded methodology | Stakeholder-ready deliverable |

---

## 14. Open Decisions

These do not change the analysis intent, but should be decided during build:

- Exact embedding / LLM providers and hosting
- Batch cadence (daily / weekly) vs. near-real-time
- Primary languages in scope for v1
- Human-in-the-loop depth for theme QA
- Dashboard platform (internal web app vs. BI tool)

---

## 15. Summary

The system is a multi-source feedback intelligence pipeline: ingest and normalize reviews and discussions, identify themes around habit and category exploration, answer the discovery questions with evidence-backed insights, validate quality, and publish everything to a dashboard — with model documentation covering gather/analyze workflow, themeing, insight generation, and validation.
