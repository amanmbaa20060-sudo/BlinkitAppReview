# Model Documentation Outline

**Status:** Skeleton (Phase 0)  
**To be filled:** Phases 1–5 as noted below  
**Final home:** Also surfaced in dashboard Methodology view (Phase 5)

This outline satisfies the problem-statement requirement that model documentation explain:

1. How the workflow gathers and analyzes data  
2. How themes are identified  
3. How insights are generated  
4. How insight quality was validated  

---

## 1. System purpose

**Fill in Phase 0 (done)**

- Strategic goal: increase % of MACs who purchase from ≥1 new category each month.
- System: AI-powered multi-source feedback discovery engine.
- References: `docs/problemstatement.md`, `docs/architecture.md`.

---

## 2. How the workflow gathers and analyzes data

**Fill in Phase 1 (gather) + Phase 2 (analyze foundation)**

### 2.1 Gathering (Phase 1)

**Filled:** see [`phase1/docs/gather_workflow.md`](../../phase1/docs/gather_workflow.md)

- [x] Source adapters and access method per source
- [x] Schedule / batch cadence (see Phase 0 decision: weekly)
- [x] Raw store layout and `run_id` versioning
- [x] Mapping rules into canonical schema `v1.0.0`
- [x] Quality gates: empty drop, dedupe, quarantine
- [x] Language detection and v1 English analysis filter

### 2.2 Analysis pipeline stages (Phases 2–4)

Document the architecture workflow:

1. Collect  
2. Normalize  
3. Prepare  
4. Represent  
5. Theme  
6. Enrich  
7. Answer  
8. Synthesize  
9. Validate  
10. Publish  

- [ ] Actual code entrypoints and configs used
- [ ] Model / embedding versions per run

---

## 3. How themes are identified

**Filled:** see [`phase2/docs/theme_identification.md`](../../phase2/docs/theme_identification.md)

- [x] Seed taxonomy used (`theme_taxonomy_v0` → consolidated `v1`)
- [x] Embedding model and clustering / labeling method
- [x] Inclusion/exclusion definitions for each active theme
- [x] Multi-label assignment rules and thresholds
- [x] Metrics: prevalence, trend, source mix, co-occurrence
- [x] Taxonomy versioning scheme in Theme Store

**Seed reference:** `phase0/taxonomy/theme_taxonomy_v0.md`  
**v1 reference:** `phase2/taxonomy/theme_taxonomy_v1.md`

---

## 4. How insights are generated

**Filled:** see [`phase3/docs/insight_generation.md`](../../phase3/docs/insight_generation.md)

- [x] Mapping of eight discovery questions → modules
- [x] Evidence retrieval approach (vector + theme membership)
- [x] Synthesis prompt constraints (evidence-only)
- [x] Insight schema: headline, themes, evidence IDs, implication, confidence, status
- [x] How implications tie to category-expansion strategy

---

## 5. How insight quality was validated

**Filled:** see [`phase4/docs/validation.md`](../../phase4/docs/validation.md)

- [x] Coverage check results
- [x] Sampling QA method and precision on theme assignments
- [x] Faithfulness checks (insight vs cited quotes)
- [x] Cross-source consistency weighting
- [x] Stability / holdout results
- [x] Publish thresholds and gate outcomes
- [x] Stakeholder spot-check notes

**QA approach (Phase 0 decision):** LLM-as-judge on samples + human spot-check of published insights.

---

## 6. Limitations & deferred scope

**Maintain continuously**

- English-primary analysis in v1
- Text-inferred segments only (no CRM join unless later approved)
- Deferred: multi-language, daily cadence, managed warehouse, React dashboard

---

## 7. Run card template (per pipeline run)

Copy per published run:

| Field | Value |
|-------|-------|
| `run_id` | |
| Taxonomy version | |
| Embedding model | |
| LLM model | |
| Sources included | |
| Record counts (raw / cleaned / quarantined) | |
| Theme coverage % | |
| Published insights (Q1–Q8) | |
| Validation summary link | |

---

## Change log

| Date | Phase | Change |
|------|-------|--------|
| 2026-07-16 | 0 | Outline created; purpose and deferred scope seeded |
| 2026-07-16 | 1 | Gather workflow filled (`phase1/docs/gather_workflow.md`) |
| 2026-07-16 | 2 | Theme identification filled (`phase2/docs/theme_identification.md`) |
| 2026-07-16 | 3 | Insight generation filled (`phase3/docs/insight_generation.md`) |
| 2026-07-16 | 4 | Validation filled (`phase4/docs/validation.md`) |
