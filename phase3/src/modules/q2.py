"""Q2 — What prevents users from exploring new categories?"""

from __future__ import annotations

from typing import Any

from src.evidence import analyzed_rows, family_theme_counts, retrieve_evidence
from src.synthesis import build_insight, theme_list_phrase


def run(enriched: list[dict[str, Any]], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = analyzed_rows(enriched)
    ranked = family_theme_counts(rows, "barrier")
    # Rank by severity then count
    ranked_sev = sorted(ranked, key=lambda x: (x["severity_score"], x["count"]), reverse=True)
    themes = [r["theme_id"] for r in ranked_sev]
    volume = sum(r["count"] for r in ranked)
    evidence = retrieve_evidence(rows, family_ids=["barrier"], limit=5)
    top = theme_list_phrase(themes)
    headline = (
        f"Exploration is blocked most often by {top} "
        f"(trust/price/relevance barriers ranked by frequency and severity)."
        if themes else "Insufficient barrier-theme signal in corpus."
    )
    implication = (
        "Reduce perceived risk of first-time category trial: clearer fees, quality/freshness guarantees, "
        "and relevance messaging so MACs are willing to leave familiar categories."
    )
    return [build_insight(
        insight_id="insight-Q2-exploration-barriers",
        question_id="Q2",
        headline=headline,
        supporting_themes=themes[:5],
        evidence=evidence,
        implication=implication,
        analysis={"family": "barrier", "theme_ranking": ranked_sev[:8], "question": ctx["questions"]["Q2"]},
        analyzable_count=ctx["analyzable_count"],
        theme_volume=volume,
    )]
