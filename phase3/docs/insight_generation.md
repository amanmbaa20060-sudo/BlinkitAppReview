# How Insights Are Generated (Phase 3)

Fills model documentation section: **How insights are generated**.  
Outline: [`phase0/model_docs/model_documentation_outline.md`](../../phase0/model_docs/model_documentation_outline.md)

---

## 1. Mapping: discovery questions → modules

| ID | Question | Module | Primary family |
|----|----------|--------|----------------|
| Q1 | Why repeatedly buy same categories? | `modules/q1.py` | habit |
| Q2 | What prevents exploring new categories? | `modules/q2.py` | barrier |
| Q3 | How do users discover products today? | `modules/q3.py` | discovery |
| Q4 | What role do habits play? | `modules/q4.py` | habit (+ contrast) |
| Q5 | What information before trying a new category? | `modules/q5.py` | info |
| Q6 | What frustrations emerge repeatedly? | `modules/q6.py` | frustration |
| Q7 | Which segments experiment more? | `modules/q7.py` | experiment × segments |
| Q8 | What unmet needs emerge consistently? | `modules/q8.py` | unmet |

Entry point: `scripts/run_phase3.py` → `src/pipeline.py`.

---

## 2. Evidence retrieval

For each module:

1. Filter Phase 2 **analyzed** enriched rows.
2. Select rows matching family/theme (min theme score 0.55) and optional segment.
3. Rank by theme score + frustration intensity.
4. Diversify across sources when possible.
5. Keep top N quotes (`feedback_id`, source, date, text, matched themes).

No quotes are invented. If volume is zero, the insight is marked `insufficient_evidence`.

---

## 3. Synthesis constraints (evidence-only)

- Headlines summarize **retrieved** theme rankings / crosstabs / consensus scores.
- Implications must relate to **MAC new-category purchase** behavior.
- Evidence packs embed the actual quotes tied to `evidence_ids`.
- Status is always `draft` until Phase 4 publish gate.
- Confidence is **provisional** (volume + evidence count + source diversity).

**LLM mode (Groq):** After template draft, Groq refines `headline` + `implication` strictly from the evidence pack (`synthesis_source=groq_llm`). Falls back to template if the API call fails.

Mode: `evidence_constrained_template` + optional `groq_llm` refinement.

---

## 4. Insight schema

| Field | Description |
|-------|-------------|
| `insight_id` | Stable ID |
| `question_id` | Q1–Q8 |
| `headline` | One clear finding |
| `supporting_themes` | Ranked theme IDs |
| `evidence_ids` | Cited feedback IDs |
| `evidence_pack` | Quotes with source/date |
| `implication` | Category-expansion implication |
| `confidence` | Provisional 0–1 |
| `status` | `draft` |
| `analysis` | Module-specific metrics |

---

## 5. Link to strategic goal

Every implication ties back to increasing the % of Monthly Active Customers who purchase from ≥1 new category per month — by removing barriers, reshaping discovery, closing info gaps, fixing frustrations, targeting experiment-prone segments, or fulfilling unmet needs.
