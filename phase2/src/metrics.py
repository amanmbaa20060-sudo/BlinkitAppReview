"""Theme prevalence, trends, source mix, co-occurrence."""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from typing import Any


def _month(ts: str | None) -> str:
    if not ts or len(ts) < 7:
        return "unknown"
    return ts[:7]


def compute_theme_metrics(enriched: list[dict[str, Any]]) -> dict[str, Any]:
    prevalence: Counter[str] = Counter()
    by_source: dict[str, Counter[str]] = defaultdict(Counter)
    by_month: dict[str, Counter[str]] = defaultdict(Counter)
    co_occur: Counter[tuple[str, str]] = Counter()
    sentiment_by_theme: dict[str, Counter[str]] = defaultdict(Counter)

    analyzable = [r for r in enriched if r.get("analysis_status") == "analyzed"]
    for row in analyzable:
        themes = [t["theme_id"] for t in row.get("themes", []) if t["theme_id"] != "theme.other"]
        source = row.get("source") or "unknown"
        month = _month(row.get("created_at"))
        sent = row.get("sentiment_label") or "neutral"
        for tid in themes:
            prevalence[tid] += 1
            by_source[tid][source] += 1
            by_month[tid][month] += 1
            sentiment_by_theme[tid][sent] += 1
        for a, b in combinations(sorted(set(themes)), 2):
            co_occur[(a, b)] += 1

    n = max(len(analyzable), 1)
    return {
        "analyzable_count": len(analyzable),
        "prevalence": [
            {"theme_id": tid, "count": cnt, "share": round(cnt / n, 4)}
            for tid, cnt in prevalence.most_common()
        ],
        "source_mix": {tid: dict(counter) for tid, counter in by_source.items()},
        "trend_by_month": {tid: dict(sorted(counter.items())) for tid, counter in by_month.items()},
        "co_occurrence_top": [
            {"themes": [a, b], "count": c}
            for (a, b), c in co_occur.most_common(40)
        ],
        "sentiment_by_theme": {tid: dict(counter) for tid, counter in sentiment_by_theme.items()},
    }
