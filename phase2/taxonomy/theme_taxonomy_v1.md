# Theme Taxonomy v1 (Consolidated)

**Version:** `v1`  
**Status:** Consolidated from Phase 0 seed `v0`  
**Assignment method:** Keyword hits + definition hashing-embedding similarity (multi-label)  
**Machine-readable:** [`theme_taxonomy_v1.json`](./theme_taxonomy_v1.json)

## Consolidation notes

1. All seven theme families from `v0` are retained with inclusion/exclusion definitions.
2. Residual unmatched clusters (if any) are recorded as `discovered_candidates` and **not** auto-merged into core themes (min-support / analyst-review rule).
3. `theme.other` is used only when no core theme clears thresholds; it is excluded from coverage numerator.
4. Taxonomy is versioned in the Theme Store under `data/themes/v1/{run_id}/`.

## Active families

| Family | Theme IDs |
|--------|-----------|
| Habit & repetition | `habit.same_basket`, `habit.autopilot_reorder`, `habit.low_browse_intent` |
| Exploration barriers | `barrier.unknown_value`, `barrier.trust_risk`, `barrier.price_uncertainty`, `barrier.relevance_doubt` |
| Discovery mechanisms | `discovery.search_led`, `discovery.homepage_banners`, `discovery.recommendations`, `discovery.social_proof`, `discovery.word_of_mouth` |
| Information needs | `info.ingredients_use_cases`, `info.sizing_freshness`, `info.return_policy`, `info.reviews_depth` |
| Frustration patterns | `frustration.stockouts`, `frustration.late_delivery`, `frustration.poor_substitutes`, `frustration.opaque_fees`, `frustration.weak_support` |
| Experiment propensity | `experiment.deal_driven`, `experiment.life_event`, `experiment.gift_occasion`, `experiment.niche_interest` |
| Unmet needs | `unmet.missing_assortment`, `unmet.weak_guidance`, `unmet.no_starter_kits`, `unmet.weak_cross_category_cues` |

Full inclusion/exclusion text is in `theme_taxonomy_v1.json` (copied from v0 families) and `data/themes/v1/{run_id}/theme_definitions.json`.

## Discovery question map

Unchanged from v0 — see JSON `discovery_question_map`.
