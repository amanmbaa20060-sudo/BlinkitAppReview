# Google Stitch Prompt — Insight Dashboard (UI Only)

Use this prompt in **Google Stitch** to generate the dashboard UI.  
Do **not** include data wiring, APIs, or modals yet — visual layout and interaction affordances only. Modals / implementation come later.

---

## Prompt (copy below)

```text
Design a polished internal analytics dashboard UI for a quick-commerce product insights tool named “Category Expansion Insights” (Blinkit-style context: grocery / q-commerce). UI ONLY — no backend, no real data binding, no modal dialogs yet. Use realistic placeholder content.

PRODUCT PURPOSE
Help PMs and CX leads understand why Monthly Active Customers stay in the same purchase categories and what would help them try new categories (pet, baby, personal care, etc.).

VISUAL DIRECTION
- One coherent composition, not a dense admin “widget soup.”
- Brand first: “Category Expansion Insights” should read as a hero-level product name in the top region (not tiny nav text).
- Avoid generic AI UI clichés: no purple-to-indigo gradients, no neon glow, no glassmorphism overload, no emoji, no pill-chip spam.
- Typography: distinctive, modern product UI fonts (not Inter/Roboto/Arial defaults). Clear hierarchy: product name > page title > section labels > body.
- Background: subtle atmospheric treatment (soft warm-neutral or cool-neutral wash with light texture/gradient), not flat white or pure black.
- Color system: define CSS-like tokens — deep charcoal text, soft off-white surfaces, one strong accent (Blinkit-adjacent yellow-green or fresh lime), muted secondary for charts. High contrast for readability.
- Cards: use sparingly. Prefer open sections and clear hierarchy. Cards only where they contain a clear interactive unit (e.g., one discovery question).
- Motion: imply 2–3 intentional micro-interactions (filter apply, insight hover underline, chart hover), not decorative noise.
- Desktop-first (1440px), also show a clean mobile stacked variant of the same IA.

INFORMATION ARCHITECTURE
Left or top primary navigation with these views (all screens designed):

1) Executive Overview
2) Theme Explorer
3) Discovery Q&A
4) Segment Lens
5) Frustration Monitor
6) Evidence Browser
7) Methodology

GLOBAL CHROME (every screen)
- Top bar: product name “Category Expansion Insights”, short subtitle “Why MACs stay in familiar categories — and what unlocks new ones.”
- Global filter bar: Source, Date range, Theme, Sentiment, Segment (visual controls only; inactive/placeholder state OK).
- Secondary actions: “Export summary” button (visual only), run badge “Run: 2026-07-16-weekly”, status chip “Published insights”.
- No login wall. Internal tool aesthetic.

SCREEN 1 — EXECUTIVE OVERVIEW
- One job: answer “what matters for category expansion this period?”
- Hero band with product name + one headline + one supporting sentence + CTA group (“Review Q&A”, “Export summary”).
- Below hero (not competing with it): three compact insight strips — Top barriers, Top opportunities, Habit drivers — each with a short placeholder finding and “View evidence” text link (no modal yet; link style only).
- Small trend sparkline area for “exploration willingness” (placeholder).
- Avoid stats overload in the first viewport; keep first viewport to brand, headline, sentence, CTAs, and one dominant visual (abstract store-aisle / discovery motif as full-bleed background, not an inset card image).

SCREEN 2 — THEME EXPLORER
- One job: explore theme prevalence and mix.
- Left: ranked theme list (habit, barrier, discovery, info, frustration, experiment, unmet families) with prevalence bars.
- Right: detail panel for selected theme — definition, sentiment split, source breakdown (Play Store, App Store, Reddit, etc.), monthly trend chart.
- Empty/selected states both designed.

SCREEN 3 — DISCOVERY Q&A BOARD
- One job: answer the eight discovery questions.
- Grid or stacked panels for Q1–Q8, each panel containing:
  - Question label (Q1…Q8)
  - Headline insight
  - Supporting theme tags (max 3, quiet styling)
  - Confidence meter (visual)
  - “Evidence” text button (affordance only — NO modal implementation yet; show a clear button ready for later modal hookup)
  - One-line implication for MAC new-category trial
- Clearly distinguish Published vs Draft with a subtle status label.

SCREEN 4 — SEGMENT LENS
- One job: who experiments more?
- Horizontal comparison of segments: habitual reorderer, occasional explorer, deal-sensitive, life-stage pet/parent, etc.
- Experiment-rate bars + short annotation.
- Placeholder callout: “Deal-sensitive and life-stage segments show higher experiment propensity.”

SCREEN 5 — FRUSTRATION MONITOR
- One job: recurring pain over time.
- Time-series of frustration themes (stockouts, late delivery, opaque fees, weak support, poor substitutes).
- Ranked complaint list beside the chart.
- Tone: operational, calm, serious — not alarming red everywhere; use restrained warning accent.

SCREEN 6 — EVIDENCE BROWSER
- One job: find supporting feedback quotes.
- Search field + same global filters.
- Results as a readable list (not heavy cards): quote, source, date, theme tags, sentiment.
- Row affordance “Open” (for future modal) — style as text button only.
- Show ~6–8 realistic placeholder quotes about habits, barriers, discovery, unmet needs.

SCREEN 7 — METHODOLOGY
- One job: explain trust in the analysis.
- Four sections as a clean vertical narrative:
  1. How data is gathered & analyzed
  2. How themes are identified
  3. How insights are generated
  4. How insight quality was validated
- Include a small “pipeline steps” visual: Collect → Normalize → Theme → Insight → Validate → Publish.
- Documentation tone; generous whitespace.

INTERACTION NOTES FOR STITCH (UI ONLY)
- Design the “Evidence” / “Open” controls as obvious buttons/links so engineers can attach a modal later.
- Do NOT design the modal contents in this pass.
- Include hover/selected/filter-active states for key controls.
- Ensure accessibility: readable contrast, visible focus rings.

DELIVERABLES FROM STITCH
- Full set of 7 screens (desktop).
- One mobile stacked version of Overview + Discovery Q&A.
- A simple component reference strip: filters, insight panel, theme row, evidence row, buttons, status labels.
```

---

## Later (not for Stitch yet)

When wiring the app, attach a modal to:

- Discovery Q&A → **Evidence** button  
- Evidence Browser → **Open** control  
- Executive Overview → **View evidence** links  

Modal content (future): quote list with `feedback_id`, source, date, theme tags, and close/export actions — fed from Phase 4 `insights_published.jsonl` evidence packs.
