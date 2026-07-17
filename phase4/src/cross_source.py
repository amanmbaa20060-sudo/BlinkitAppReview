"""4.4 Cross-source consistency weighting."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def cross_source_consistency(
    enriched: list[dict[str, Any]],
    insights: list[dict[str, Any]],
    *,
    single_source_penalty: float,
    min_sources_for_full_weight: int,
) -> dict[str, Any]:
    theme_sources: dict[str, set[str]] = defaultdict(set)
    for row in enriched:
        if row.get("analysis_status") != "analyzed":
            continue
        src = row.get("source") or "unknown"
        for t in row.get("themes") or []:
            tid = t.get("theme_id")
            if not tid or tid == "theme.other":
                continue
            if float(t.get("score") or 0) < 0.55:
                continue
            theme_sources[tid].add(src)

    theme_weights = {}
    for tid, sources in theme_sources.items():
        n = len(sources)
        if n >= min_sources_for_full_weight:
            theme_weights[tid] = 1.0
        else:
            theme_weights[tid] = max(0.0, 1.0 - single_source_penalty)

    insight_adjustments = []
    for insight in insights:
        themes = insight.get("supporting_themes") or []
        if not themes:
            weight = 0.5
        else:
            weight = sum(theme_weights.get(t, 0.7) for t in themes) / len(themes)
        insight_adjustments.append({
            "insight_id": insight.get("insight_id"),
            "cross_source_weight": round(weight, 4),
            "theme_source_counts": {t: len(theme_sources.get(t, [])) for t in themes},
        })

    return {
        "check": "cross_source_consistency",
        "theme_source_counts": {k: len(v) for k, v in sorted(theme_sources.items())},
        "theme_weights": theme_weights,
        "insight_adjustments": insight_adjustments,
        "passed": True,  # informational weighting; always applies
    }
