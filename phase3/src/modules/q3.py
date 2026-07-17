"""Q3 — How do users discover products today?"""

from __future__ import annotations

from typing import Any

from src.evidence import analyzed_rows, family_theme_counts, retrieve_evidence
from src.synthesis import build_insight, theme_list_phrase


def run(enriched: list[dict[str, Any]], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = analyzed_rows(enriched)
    ranked = family_theme_counts(rows, "discovery")
    themes = [r["theme_id"] for r in ranked]
    volume = sum(r["count"] for r in ranked)
    evidence = retrieve_evidence(rows, family_ids=["discovery"], limit=5)
    top = theme_list_phrase(themes)
    channel_examples = [
        {"theme_id": r["theme_id"], "count": r["count"]} for r in ranked[:5]
    ]
    headline = (
        f"Product discovery today is dominated by {top}; "
        f"in-app banners/recommendations underperform versus search and social proof."
        if themes else "Insufficient discovery-theme signal in corpus."
    )
    implication = (
        "Shift discovery design toward search-adjacent and social-proof surfaces that introduce "
        "new categories, instead of depending on ignored homepage banners alone."
    )
    return [build_insight(
        insight_id="insight-Q3-discovery-today",
        question_id="Q3",
        headline=headline,
        supporting_themes=themes[:5],
        evidence=evidence,
        implication=implication,
        analysis={
            "family": "discovery",
            "channel_distribution": channel_examples,
            "question": ctx["questions"]["Q3"],
        },
        analyzable_count=ctx["analyzable_count"],
        theme_volume=volume,
    )]
