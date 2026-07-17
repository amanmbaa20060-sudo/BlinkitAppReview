"""Q7 — Which user segments are more likely to experiment?"""

from __future__ import annotations

from typing import Any

from src.evidence import analyzed_rows, family_theme_counts, retrieve_evidence, segment_experiment_crosstab
from src.synthesis import build_insight


def run(enriched: list[dict[str, Any]], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = analyzed_rows(enriched)
    crosstab = segment_experiment_crosstab(rows)
    ranked = family_theme_counts(rows, "experiment")
    themes = [r["theme_id"] for r in ranked]
    volume = sum(r["count"] for r in ranked)

    leaders = [c for c in crosstab if c["segment"] != "unspecified" and c["total"] >= 10][:3]
    if leaders:
        leader_txt = "; ".join(
            f"{c['segment']} ({c['experiment_rate']:.0%} of {c['total']})" for c in leaders
        )
        headline = f"Segments most likely to experiment: {leader_txt}."
    else:
        headline = "Experiment-prone segments are weakly signaled; see crosstab for details."

    # Evidence from top experimenting segment if available
    top_seg = leaders[0]["segment"] if leaders else None
    evidence = retrieve_evidence(
        rows,
        family_ids=["experiment"],
        segment=top_seg,
        limit=5,
    )
    if len(evidence) < 3:
        evidence = retrieve_evidence(rows, family_ids=["experiment"], limit=5)

    implication = (
        "Prioritize category-expansion campaigns toward deal-sensitive and life-stage segments "
        "(pets/parents, occasion buyers) where experiment themes already appear — higher MAC conversion likelihood."
    )
    return [build_insight(
        insight_id="insight-Q7-experiment-segments",
        question_id="Q7",
        headline=headline,
        supporting_themes=themes[:5],
        evidence=evidence,
        implication=implication,
        analysis={
            "segment_x_experiment": crosstab,
            "experiment_themes": ranked[:8],
            "question": ctx["questions"]["Q7"],
        },
        analyzable_count=ctx["analyzable_count"],
        theme_volume=volume,
    )]
