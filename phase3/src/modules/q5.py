"""Q5 — What information do users need before trying a new category?"""

from __future__ import annotations

from typing import Any

from src.evidence import analyzed_rows, family_theme_counts, retrieve_evidence
from src.synthesis import build_insight, theme_list_phrase


def run(enriched: list[dict[str, Any]], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = analyzed_rows(enriched)
    ranked = family_theme_counts(rows, "info")
    themes = [r["theme_id"] for r in ranked]
    volume = sum(r["count"] for r in ranked)
    evidence = retrieve_evidence(rows, family_ids=["info"], limit=5)
    gaps = [{"gap": r["theme_id"], "count": r["count"]} for r in ranked]
    top = theme_list_phrase(themes)
    headline = (
        f"Before trying a new category, users most often ask for {top} "
        f"(information gaps ranked from feedback)."
        if themes else "Insufficient information-need signal in corpus."
    )
    implication = (
        "Equip unfamiliar categories with PDP essentials — ingredients/use-cases, freshness/sizing, "
        "returns clarity, and deeper reviews — to lower the trial threshold for MACs."
    )
    return [build_insight(
        insight_id="insight-Q5-information-needs",
        question_id="Q5",
        headline=headline,
        supporting_themes=themes[:5],
        evidence=evidence,
        implication=implication,
        analysis={"family": "info", "gap_list": gaps, "question": ctx["questions"]["Q5"]},
        analyzable_count=ctx["analyzable_count"],
        theme_volume=volume,
    )]
