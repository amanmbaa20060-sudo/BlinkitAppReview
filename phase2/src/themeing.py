"""Theme identification: seed taxonomy + keyword/similarity assignment + residual discovery."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .embeddings import HashingEmbeddingClient, cosine

# Keyword cues aligned to taxonomy inclusion criteria + fixture language
THEME_KEYWORDS: dict[str, list[str]] = {
    "habit.same_basket": ["same basket", "same groceries", "same items", "same 8 skus", "never changes", "usual basket"],
    "habit.autopilot_reorder": ["autopilot", "reorder", "saved lists", "repeat order", "usual"],
    "habit.low_browse_intent": ["barely open", "barely look", "zero browse", "low browse", "stop exploring", "rarely browse"],
    "barrier.unknown_value": ["unsure why", "unknown value", "why to try"],
    "barrier.trust_risk": ["trust risk", "freshness and authenticity", "quality fear", "authenticity"],
    "barrier.price_uncertainty": ["opaque fees", "price uncertainty", "surge", "surprise charges", "too expensive to try"],
    "barrier.relevance_doubt": ["irrelevant", "relevance doubt", "not for me"],
    "discovery.search_led": ["through search", "via search", "search-led", "search only", "mostly use search"],
    "discovery.homepage_banners": ["homepage", "banners", "banner"],
    "discovery.recommendations": ["recommendations", "recommended", "suggested for you"],
    "discovery.social_proof": ["social proof", "deep reviews", "ratings, reviews"],
    "discovery.word_of_mouth": ["word of mouth", "friend told", "friends mention", "peer"],
    "info.ingredients_use_cases": ["ingredients", "use-case", "use case", "usage guidance"],
    "info.sizing_freshness": ["sizing", "freshness info", "freshness cues", "expiry"],
    "info.return_policy": ["return policy", "returns", "refund policy"],
    "info.reviews_depth": ["review depth", "more reviews", "better reviews", "deep reviews"],
    "frustration.stockouts": ["stockout", "stockouts", "oos", "unavailable"],
    "frustration.late_delivery": ["late delivery", "eta slips", "missed eta"],
    "frustration.poor_substitutes": ["poor substitutes", "substitute was awful", "bad replacements"],
    "frustration.opaque_fees": ["opaque fees", "opaque delivery fees", "surprise charges", "unclear"],
    "frustration.weak_support": ["support is unreachable", "support chat", "weak support", "unreachable"],
    "experiment.deal_driven": ["discount", "deal-driven", "deals drive", "big discount", "festival deal"],
    "experiment.life_event": ["puppy", "life event", "adopted", "new parent", "got a puppy"],
    "experiment.gift_occasion": ["festival", "gift hampers", "gift", "occasion"],
    "experiment.niche_interest": ["niche diet", "niche interest", "specialty"],
    "unmet.missing_assortment": ["assortment feels thin", "missing assortment", "assortment"],
    "unmet.weak_guidance": ["weak guidance", "no help choosing", "guidance is poor"],
    "unmet.no_starter_kits": ["starter kits", "starter kit", "bundles"],
    "unmet.weak_cross_category_cues": ["cross-category", "adjacent categories", "adjacent aisles", "never nudges"],
}


def load_taxonomy(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def flatten_themes(taxonomy: dict[str, Any]) -> list[dict[str, Any]]:
    themes: list[dict[str, Any]] = []
    for family in taxonomy.get("families", []):
        for theme in family.get("themes", []):
            themes.append({
                **theme,
                "family_id": family["family_id"],
                "family_name": family["name"],
            })
    return themes


def _keyword_hits(text: str, theme_id: str) -> list[str]:
    lowered = text.lower()
    hits = []
    for kw in THEME_KEYWORDS.get(theme_id, []):
        if kw.lower() in lowered:
            hits.append(kw)
    return hits


def assign_themes_for_text(
    text: str,
    theme_defs: list[dict[str, Any]],
    theme_vectors: dict[str, list[float]],
    embedder: HashingEmbeddingClient,
    min_keyword_hits: int = 1,
    min_similarity: float = 0.12,
) -> list[dict[str, Any]]:
    """Multi-label assignment via keywords and definition similarity."""
    text_vec = embedder.embed_one(text)
    assignments: list[dict[str, Any]] = []
    for theme in theme_defs:
        tid = theme["theme_id"]
        hits = _keyword_hits(text, tid)
        sim = cosine(text_vec, theme_vectors[tid])
        if len(hits) >= min_keyword_hits or sim >= min_similarity:
            score = min(1.0, 0.55 * min(len(hits), 3) / 3 + 0.45 * max(sim, 0.0))
            if hits:
                score = max(score, 0.65)
            assignments.append({
                "theme_id": tid,
                "family_id": theme["family_id"],
                "score": round(score, 4),
                "keyword_hits": hits,
                "similarity": round(sim, 4),
            })
    assignments.sort(key=lambda a: a["score"], reverse=True)
    return assignments


def discover_residual_clusters(
    residuals: list[dict[str, Any]],
    embedder: HashingEmbeddingClient,
    min_support: int = 8,
) -> list[dict[str, Any]]:
    """Greedy cosine clustering for unassigned English texts."""
    if not residuals:
        return []
    vectors = [embedder.embed_one(r["prepared_text"]) for r in residuals]
    used = [False] * len(residuals)
    clusters: list[dict[str, Any]] = []
    for i, vec in enumerate(vectors):
        if used[i]:
            continue
        members = [i]
        used[i] = True
        for j in range(i + 1, len(vectors)):
            if used[j]:
                continue
            if cosine(vec, vectors[j]) >= 0.55:
                used[j] = True
                members.append(j)
        if len(members) >= min_support:
            sample_ids = [residuals[m]["feedback_id"] for m in members[:10]]
            clusters.append({
                "discovered_id": f"discovered.cluster_{len(clusters)+1}",
                "support": len(members),
                "sample_feedback_ids": sample_ids,
                "label_hint": "residual_unmatched_feedback",
                "action": "reviewed_not_merged_into_v1_core",
            })
    return clusters


def consolidate_taxonomy_v1(
    taxonomy_v0: dict[str, Any],
    discovered: list[dict[str, Any]],
    assignment_method: str,
) -> dict[str, Any]:
    """Produce taxonomy v1: v0 definitions retained; discovered noted as candidates."""
    themes = flatten_themes(taxonomy_v0)
    return {
        "taxonomy_version": "v1",
        "status": "consolidated",
        "created_at": "2026-07-16",
        "derived_from": taxonomy_v0.get("taxonomy_version", "v0"),
        "assignment_method": assignment_method,
        "min_support_rule": "Rare near-duplicate themes not promoted; core v0 themes retained",
        "families": taxonomy_v0.get("families", []),
        "discovery_question_map": taxonomy_v0.get("discovery_question_map", {}),
        "active_theme_ids": [t["theme_id"] for t in themes],
        "discovered_candidates": discovered,
        "notes": [
            "Seed themes from Phase 0 covered all seven theme families.",
            "Residual clusters (if any) recorded as candidates; not merged into core v1 without analyst review.",
            "Multi-label assignment allowed when keyword hits or definition similarity clears thresholds.",
        ],
    }
