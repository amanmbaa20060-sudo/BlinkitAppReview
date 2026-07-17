# Theme Taxonomy v0 (Draft Seed)

**Version:** `v0`  
**Status:** Draft seed for Phase 2 consolidation → `v1`  
**Aligned to:** Problem statement discovery questions + architecture theme families

This taxonomy seeds clustering and labeling. Phase 2 will discover additional themes from embeddings and consolidate into a stable `v1`.

---

## Theme families

### 1. Habit & repetition

| Theme ID | Name | Inclusion | Exclusion |
|----------|------|-----------|-----------|
| `habit.same_basket` | Same-basket loyalty | Mentions always buying the same items/categories | One-off purchase complaints unrelated to repetition |
| `habit.autopilot_reorder` | Autopilot reordering | Reorder, repeat order, “usual”, saved lists as default behavior | Deliberate browsing / exploration |
| `habit.low_browse_intent` | Low browse intent | Rarely opens categories beyond search/reorder | Active category exploration |

### 2. Exploration barriers

| Theme ID | Name | Inclusion | Exclusion |
|----------|------|-----------|-----------|
| `barrier.unknown_value` | Unknown category value | Unsure why to try a new category | Price-only objections without value uncertainty |
| `barrier.trust_risk` | Trust / quality risk | Fear of bad quality, freshness, authenticity in unfamiliar categories | General delivery delay complaints |
| `barrier.price_uncertainty` | Price uncertainty | Unclear fees, surge, “too expensive to try” | Praise of deals |
| `barrier.relevance_doubt` | Relevance doubt | “Not for me”, category feels irrelevant | Explicit niche interest in that category |

### 3. Discovery mechanisms

| Theme ID | Name | Inclusion | Exclusion |
|----------|------|-----------|-----------|
| `discovery.search_led` | Search-led discovery | Finds products mainly via search | Recommendation/banner led |
| `discovery.homepage_banners` | Homepage / banners | Discovers via home, banners, campaigns | Search-only journeys |
| `discovery.recommendations` | Recommendations | Personalized / “suggested for you” | Pure social word-of-mouth |
| `discovery.social_proof` | Social proof | Ratings, reviews, influencer/friend mentions drive trial | Internal app search alone |
| `discovery.word_of_mouth` | Word of mouth | Offline/online peer recommendation | Paid ads as sole mention |

### 4. Information needs

| Theme ID | Name | Inclusion | Exclusion |
|----------|------|-----------|-----------|
| `info.ingredients_use_cases` | Ingredients / use-cases | Needs usage guidance before trying | Post-purchase taste preference only |
| `info.sizing_freshness` | Sizing / freshness | Needs size, weight, expiry, freshness cues | Packaging aesthetics only |
| `info.return_policy` | Return / refund policy | Needs clarity on returns before trying new category | Completed refund logistics after order |
| `info.reviews_depth` | Review depth | Wants more/better reviews before trial | Star rating UI bugs |

### 5. Frustration patterns

| Theme ID | Name | Inclusion | Exclusion |
|----------|------|-----------|-----------|
| `frustration.stockouts` | Stockouts | Items unavailable / frequently OOS | Successful fulfillments |
| `frustration.late_delivery` | Late delivery | Missed ETA / slow delivery | Praise of speed |
| `frustration.poor_substitutes` | Poor substitutes | Bad replacements | Acceptable substitutes |
| `frustration.opaque_fees` | Opaque fees | Surprise charges, unclear delivery/surge fees | Clear fee explanations |
| `frustration.weak_support` | Weak support | Hard to reach support / unresolved issues | Positive support experiences |

### 6. Experiment propensity

| Theme ID | Name | Inclusion | Exclusion |
|----------|------|-----------|-----------|
| `experiment.deal_driven` | Deal-driven trial | Tries new categories because of discounts/offers | Habitual same-basket without deals |
| `experiment.life_event` | Life-event triggers | Pet, baby, move, health change drives new category | No life-context mentioned |
| `experiment.gift_occasion` | Gift / occasion buying | Festival/gift prompts exploration | Routine weekly shop |
| `experiment.niche_interest` | Niche interest | Specialty diet, hobby, brand fandom | Generic convenience shopping |

### 7. Unmet needs

| Theme ID | Name | Inclusion | Exclusion |
|----------|------|-----------|-----------|
| `unmet.missing_assortment` | Missing assortment | Category/product gaps | Temporary single SKU stockout |
| `unmet.weak_guidance` | Weak guidance | No help choosing in unfamiliar categories | Expert users who don’t need guidance |
| `unmet.no_starter_kits` | No starter kits | Wants bundles/starter packs for new categories | Prefers à-la-carte only |
| `unmet.weak_cross_category_cues` | Weak cross-category cues | App doesn’t suggest adjacent categories | Users who reject recommendations |

---

## Mapping to discovery questions

| Question | Primary theme families |
|----------|------------------------|
| Why repeatedly buy same categories? | Habit & repetition |
| What prevents exploring new categories? | Exploration barriers |
| How do users discover products today? | Discovery mechanisms |
| What role do habits play? | Habit & repetition |
| What information before trying a new category? | Information needs |
| What frustrations emerge repeatedly? | Frustration patterns |
| Which segments experiment more? | Experiment propensity (+ segment tags) |
| What unmet needs emerge consistently? | Unmet needs |

---

## Versioning

- **v0** — seed definitions (this document)
- **v1** — consolidated after Phase 2 clustering + review (versioned in Theme Store)
