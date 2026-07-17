"""Q8 — What unmet needs emerge consistently across discussions?"""

from __future__ import annotations

from typing import Any

from src.evidence import analyzed_rows, cross_source_consensus, retrieve_evidence
from src.synthesis import build_insight, theme_list_phrase


def run(enriched: list[dict[str, Any]], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = analyzed_rows(enriched)
    consensus = cross_source_consensus(rows, "unmet")
    themes = [r["theme_id"] for r in consensus]
    volume = sum(r["count"] for r in consensus)
    evidence = retrieve_evidence(rows, family_ids=["unmet"], limit=5)
    # Prefer themes with multi-source presence
    multi = [c for c in consensus if c["source_count"] >= 2]
    focus = multi[:3] if multi else consensus[:3]
    top = theme_list_phrase([c["theme_id"] for c in focus])
    headline = (
        f"Unmet needs with strongest cross-source consensus: {top}."
        if focus else "Insufficient unmet-need signal in corpus."
    )
    implication = (
        "Close structural gaps that block category entry — starter kits, assortment depth, "
        "in-app guidance, and cross-category cues — so MACs can try new categories with lower effort."
    )
    return [build_insight(
        insight_id="insight-Q8-unmet-needs",
        question_id="Q8",
        headline=headline,
        supporting_themes=themes[:5],
        evidence=evidence,
        implication=implication,
        analysis={
            "family": "unmet",
            "consensus_ranking": consensus[:10],
            "question": ctx["questions"]["Q8"],
        },
        analyzable_count=ctx["analyzable_count"],
        theme_volume=volume,
    )]
