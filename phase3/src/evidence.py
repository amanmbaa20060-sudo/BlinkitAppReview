"""Evidence retrieval constrained to Theme Store membership + enriched text."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def analyzed_rows(enriched: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in enriched if r.get("analysis_status") == "analyzed"]


def theme_score(row: dict[str, Any], theme_id: str) -> float:
    for t in row.get("themes") or []:
        if t.get("theme_id") == theme_id:
            return float(t.get("score") or 0.0)
    return 0.0


def has_family(row: dict[str, Any], family_id: str, min_score: float = 0.55) -> bool:
    return any(
        t.get("family_id") == family_id and float(t.get("score") or 0) >= min_score
        for t in row.get("themes") or []
    )


def has_theme(row: dict[str, Any], theme_id: str, min_score: float = 0.55) -> bool:
    return theme_score(row, theme_id) >= min_score


def family_theme_counts(
    rows: list[dict[str, Any]],
    family_id: str,
    min_score: float = 0.55,
) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    severity: dict[str, float] = defaultdict(float)
    for row in rows:
        for t in row.get("themes") or []:
            if t.get("family_id") != family_id:
                continue
            if float(t.get("score") or 0) < min_score:
                continue
            tid = t["theme_id"]
            counts[tid] += 1
            severity[tid] += float(row.get("frustration_intensity") or 0) + float(t.get("score") or 0)
    ranked = []
    for tid, cnt in counts.most_common():
        ranked.append({
            "theme_id": tid,
            "count": cnt,
            "severity_score": round(severity[tid] / max(cnt, 1), 4),
        })
    return ranked


def retrieve_evidence(
    rows: list[dict[str, Any]],
    *,
    family_ids: list[str] | None = None,
    theme_ids: list[str] | None = None,
    segment: str | None = None,
    min_score: float = 0.55,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Return top evidence quotes with feedback_id, source, date, text — evidence only."""
    candidates: list[tuple[float, dict[str, Any]]] = []
    for row in rows:
        themes = row.get("themes") or []
        matched = []
        for t in themes:
            score = float(t.get("score") or 0)
            if score < min_score:
                continue
            if family_ids and t.get("family_id") not in family_ids:
                continue
            if theme_ids and t.get("theme_id") not in theme_ids:
                continue
            matched.append((score, t.get("theme_id")))
        if family_ids or theme_ids:
            if not matched:
                continue
        if segment and segment not in (row.get("segments") or []):
            continue
        best = max((m[0] for m in matched), default=0.0)
        rank = best + 0.15 * float(row.get("frustration_intensity") or 0)
        # diversify later by source
        candidates.append((rank, {
            "feedback_id": row["feedback_id"],
            "source": row.get("source"),
            "created_at": row.get("created_at"),
            "text": row.get("prepared_text") or row.get("text") or "",
            "matched_themes": [m[1] for m in matched],
            "sentiment_label": row.get("sentiment_label"),
            "segments": row.get("segments") or [],
            "rating": row.get("rating"),
        }))

    candidates.sort(key=lambda x: x[0], reverse=True)

    # Prefer multi-source diversity
    selected: list[dict[str, Any]] = []
    seen_sources: set[str] = set()
    remainder: list[dict[str, Any]] = []
    for _, item in candidates:
        src = item.get("source") or "unknown"
        if src not in seen_sources and len(selected) < limit:
            selected.append(item)
            seen_sources.add(src)
        else:
            remainder.append(item)
    for item in remainder:
        if len(selected) >= limit:
            break
        if item["feedback_id"] in {s["feedback_id"] for s in selected}:
            continue
        selected.append(item)
    return selected


def source_diversity(evidence: list[dict[str, Any]]) -> int:
    return len({e.get("source") for e in evidence if e.get("source")})


def month_trend(
    rows: list[dict[str, Any]],
    family_id: str,
    min_score: float = 0.55,
) -> dict[str, int]:
    trend: Counter[str] = Counter()
    for row in rows:
        if not has_family(row, family_id, min_score):
            continue
        ts = row.get("created_at") or ""
        month = ts[:7] if len(ts) >= 7 else "unknown"
        trend[month] += 1
    return dict(sorted(trend.items()))


def segment_experiment_crosstab(rows: list[dict[str, Any]], min_score: float = 0.55) -> list[dict[str, Any]]:
    """Segment × exploration/experiment theme presence."""
    seg_total: Counter[str] = Counter()
    seg_experiment: Counter[str] = Counter()
    for row in rows:
        segs = row.get("segments") or ["unspecified"]
        has_exp = has_family(row, "experiment", min_score)
        for s in segs:
            seg_total[s] += 1
            if has_exp:
                seg_experiment[s] += 1
    out = []
    for seg, total in seg_total.most_common():
        exp = seg_experiment.get(seg, 0)
        out.append({
            "segment": seg,
            "total": total,
            "with_experiment_theme": exp,
            "experiment_rate": round(exp / total, 4) if total else 0.0,
        })
    out.sort(key=lambda x: x["experiment_rate"], reverse=True)
    return out


def cross_source_consensus(
    rows: list[dict[str, Any]],
    family_id: str,
    min_score: float = 0.55,
) -> list[dict[str, Any]]:
    theme_sources: dict[str, set[str]] = defaultdict(set)
    theme_counts: Counter[str] = Counter()
    for row in rows:
        for t in row.get("themes") or []:
            if t.get("family_id") != family_id:
                continue
            if float(t.get("score") or 0) < min_score:
                continue
            tid = t["theme_id"]
            theme_counts[tid] += 1
            theme_sources[tid].add(row.get("source") or "unknown")
    ranked = []
    for tid, cnt in theme_counts.most_common():
        sources = sorted(theme_sources[tid])
        ranked.append({
            "theme_id": tid,
            "count": cnt,
            "source_count": len(sources),
            "sources": sources,
            "consensus_score": round(cnt * (1 + 0.25 * (len(sources) - 1)), 4),
        })
    ranked.sort(key=lambda x: x["consensus_score"], reverse=True)
    return ranked
