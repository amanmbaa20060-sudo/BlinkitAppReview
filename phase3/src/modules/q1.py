"""Q1 — Why do users repeatedly buy from the same categories?"""

from __future__ import annotations

from typing import Any

from src.evidence import analyzed_rows, family_theme_counts, retrieve_evidence
from src.synthesis import build_insight, theme_list_phrase


def run(enriched: list[dict[str, Any]], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = analyzed_rows(enriched)
    ranked = family_theme_counts(rows, "habit")
    themes = [r["theme_id"] for r in ranked]
    volume = sum(r["count"] for r in ranked)
    evidence = retrieve_evidence(rows, family_ids=["habit"], limit=5)
    top = theme_list_phrase(themes)
    headline = (
        f"Same-category repetition is driven mainly by {top}, "
        f"with users describing autopilot reordering and low browse intent."
        if themes else "Insufficient habit-theme signal in corpus."
    )
    implication = (
        "To raise MAC new-category purchase rates, interrupt autopilot reorder flows "
        "(saved lists / same-basket) with timely adjacent-category nudges rather than relying on browse alone."
    )
    return [build_insight(
        insight_id="insight-Q1-habit-repetition",
        question_id="Q1",
        headline=headline,
        supporting_themes=themes[:5],
        evidence=evidence,
        implication=implication,
        analysis={"family": "habit", "theme_ranking": ranked[:8], "question": ctx["questions"]["Q1"]},
        analyzable_count=ctx["analyzable_count"],
        theme_volume=volume,
    )]
