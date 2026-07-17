"""4.5 Stability check via holdout split of enriched corpus."""

from __future__ import annotations

import random
from collections import Counter
from typing import Any


def _top_themes(rows: list[dict[str, Any]], top_k: int) -> list[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        for t in row.get("themes") or []:
            tid = t.get("theme_id")
            if not tid or tid == "theme.other":
                continue
            if float(t.get("score") or 0) < 0.55:
                continue
            counts[tid] += 1
    return [tid for tid, _ in counts.most_common(top_k)]


def stability_check(
    enriched: list[dict[str, Any]],
    *,
    holdout_fraction: float,
    min_top_theme_overlap: float,
    top_k: int,
    seed: int = 42,
) -> dict[str, Any]:
    analyzed = [r for r in enriched if r.get("analysis_status") == "analyzed"]
    rng = random.Random(seed)
    shuffled = analyzed[:]
    rng.shuffle(shuffled)
    cut = int(len(shuffled) * (1 - holdout_fraction))
    train, holdout = shuffled[:cut], shuffled[cut:]
    top_train = _top_themes(train, top_k)
    top_hold = _top_themes(holdout, top_k)
    overlap = len(set(top_train) & set(top_hold)) / max(len(set(top_train) | set(top_hold)), 1)
    return {
        "check": "stability",
        "train_size": len(train),
        "holdout_size": len(holdout),
        "top_themes_train": top_train,
        "top_themes_holdout": top_hold,
        "jaccard_overlap": round(overlap, 4),
        "min_top_theme_overlap": min_top_theme_overlap,
        "passed": overlap >= min_top_theme_overlap,
    }
