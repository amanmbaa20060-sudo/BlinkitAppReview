"""Q6 — What frustrations emerge repeatedly?"""

from __future__ import annotations

from typing import Any

from src.evidence import analyzed_rows, family_theme_counts, month_trend, retrieve_evidence
from src.synthesis import build_insight, theme_list_phrase


def run(enriched: list[dict[str, Any]], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = analyzed_rows(enriched)
    ranked = family_theme_counts(rows, "frustration")
    ranked_sev = sorted(ranked, key=lambda x: (x["severity_score"], x["count"]), reverse=True)
    themes = [r["theme_id"] for r in ranked_sev]
    volume = sum(r["count"] for r in ranked)
    evidence = retrieve_evidence(rows, family_ids=["frustration"], limit=5)
    trend = month_trend(rows, "frustration")
    top = theme_list_phrase(themes)
    headline = (
        f"Recurring frustrations center on {top}; "
        f"these complaints appear across the collection window and suppress willingness to experiment."
        if themes else "Insufficient frustration-theme signal in corpus."
    )
    implication = (
        "Fix high-severity service failures (fees, support, substitutes, stockouts, lateness) first — "
        "MACs will not expand categories while core reliability trust is low."
    )
    return [build_insight(
        insight_id="insight-Q6-recurring-frustrations",
        question_id="Q6",
        headline=headline,
        supporting_themes=themes[:5],
        evidence=evidence,
        implication=implication,
        analysis={
            "family": "frustration",
            "top_complaints": ranked_sev[:8],
            "month_trend": trend,
            "question": ctx["questions"]["Q6"],
        },
        analyzable_count=ctx["analyzable_count"],
        theme_volume=volume,
    )]
