"""4.1 Theme coverage check."""

from __future__ import annotations

from typing import Any


def coverage_check(enriched: list[dict[str, Any]], min_pct: float) -> dict[str, Any]:
    analyzed = [r for r in enriched if r.get("analysis_status") == "analyzed"]
    with_theme = [
        r for r in analyzed
        if any(t.get("theme_id") not in (None, "theme.other") for t in (r.get("themes") or []))
    ]
    pct = (100.0 * len(with_theme) / len(analyzed)) if analyzed else 0.0
    return {
        "check": "coverage",
        "analyzable_count": len(analyzed),
        "with_non_other_theme": len(with_theme),
        "theme_coverage_pct": round(pct, 2),
        "min_theme_coverage_pct": min_pct,
        "passed": pct >= min_pct,
    }
