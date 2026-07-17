"""4.6 Drift baseline from current theme mix."""

from __future__ import annotations

from collections import Counter
from typing import Any


def build_drift_baseline(enriched: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    analyzed = [r for r in enriched if r.get("analysis_status") == "analyzed"]
    counts: Counter[str] = Counter()
    for row in analyzed:
        for t in row.get("themes") or []:
            tid = t.get("theme_id")
            if not tid or tid == "theme.other":
                continue
            if float(t.get("score") or 0) < 0.55:
                continue
            counts[tid] += 1
    total = sum(counts.values()) or 1
    mix = {tid: round(cnt / total, 6) for tid, cnt in counts.most_common()}
    return {
        "run_id": run_id,
        "analyzable_count": len(analyzed),
        "theme_mix_share": mix,
        "theme_counts": dict(counts),
        "note": "Compare future runs against this baseline to detect theme-mix drift.",
    }
