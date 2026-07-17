"""Q4 — What role do habits play in shopping behavior?"""

from __future__ import annotations

from typing import Any

from src.evidence import analyzed_rows, family_theme_counts, has_family, retrieve_evidence
from src.synthesis import build_insight


def run(enriched: list[dict[str, Any]], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = analyzed_rows(enriched)
    ranked = family_theme_counts(rows, "habit")
    themes = [r["theme_id"] for r in ranked]
    volume = sum(r["count"] for r in ranked)

    habit_only = 0
    habit_and_experiment = 0
    deliberate = 0
    for row in rows:
        h = has_family(row, "habit")
        e = has_family(row, "experiment")
        d = has_family(row, "discovery")
        if h and e:
            habit_and_experiment += 1
        elif h:
            habit_only += 1
        if d and not h:
            deliberate += 1

    evidence = retrieve_evidence(rows, family_ids=["habit"], limit=5)
    headline = (
        f"Habits dominate shopping language ({habit_only} habit-only vs "
        f"{habit_and_experiment} habit+experiment co-mentions); deliberate browse without habit cues appears in {deliberate} records."
    )
    implication = (
        "Treat habit as the default MAC state: category expansion must ride existing reorder journeys "
        "(add-on suggestions, list upgrades) rather than assuming open-ended browsing intent."
    )
    return [build_insight(
        insight_id="insight-Q4-role-of-habits",
        question_id="Q4",
        headline=headline,
        supporting_themes=themes[:5],
        evidence=evidence,
        implication=implication,
        analysis={
            "habit_only": habit_only,
            "habit_and_experiment": habit_and_experiment,
            "deliberate_discovery_without_habit": deliberate,
            "theme_ranking": ranked[:8],
            "question": ctx["questions"]["Q4"],
        },
        analyzable_count=ctx["analyzable_count"],
        theme_volume=volume,
    )]
