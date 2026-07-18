"""4.7–4.8 Confidence finalization and publish gate."""

from __future__ import annotations

from typing import Any


def _theme_volume_proxy(insight: dict[str, Any]) -> int:
    analysis = insight.get("analysis") or {}
    ranking = analysis.get("theme_ranking") or []
    if ranking:
        return int(sum(int(item.get("count") or 0) for item in ranking))

    supporting = len(insight.get("supporting_themes") or [])
    # Fall back to question-specific analysis payloads when theme_ranking is absent.
    channel = analysis.get("channel_distribution")
    if isinstance(channel, dict) and channel:
        total = sum(int(v) for v in channel.values() if isinstance(v, (int, float)))
        return max(total, supporting * 12)

    gaps = analysis.get("gap_list")
    if isinstance(gaps, list) and gaps:
        return max(supporting * 10, len(gaps) * 15)

    segments = analysis.get("segment_x_experiment")
    if isinstance(segments, list) and segments:
        return max(supporting * 10, len(segments) * 20)

    consensus = analysis.get("consensus_ranking")
    if isinstance(consensus, list) and consensus:
        return max(
            supporting * 10,
            int(sum(int(item.get("count") or item.get("mentions") or 1) for item in consensus)),
        )

    experiments = analysis.get("experiment_themes")
    if isinstance(experiments, list) and experiments:
        return max(supporting * 10, len(experiments) * 18)

    return max(1, supporting * 8)


def _severity_proxy(insight: dict[str, Any]) -> float:
    analysis = insight.get("analysis") or {}
    ranking = analysis.get("theme_ranking") or []
    if ranking:
        return sum(float(item.get("severity_score") or 0.0) for item in ranking[:5])

    channel = analysis.get("channel_distribution")
    if isinstance(channel, dict) and channel:
        values = [float(v) for v in channel.values() if isinstance(v, (int, float))]
        if values:
            top = sorted(values, reverse=True)[:3]
            return min(4.0, sum(v / max(sum(values), 1.0) for v in top) * 3.5)

    gaps = analysis.get("gap_list")
    if isinstance(gaps, list) and gaps:
        return min(4.0, 1.2 + 0.35 * len(gaps))

    segments = analysis.get("segment_x_experiment")
    if isinstance(segments, list) and segments:
        return min(4.0, 1.0 + 0.25 * len(segments))

    consensus = analysis.get("consensus_ranking")
    if isinstance(consensus, list) and consensus:
        return min(4.0, 1.0 + 0.3 * len(consensus))

    experiments = analysis.get("experiment_themes")
    if isinstance(experiments, list) and experiments:
        return min(4.0, 1.0 + 0.28 * len(experiments))

    return 0.4 * len(insight.get("supporting_themes") or [])


def _pack_source_count(insight: dict[str, Any]) -> int:
    pack = insight.get("evidence_pack") or []
    sources = {e.get("source") for e in pack if e.get("source")}
    if sources:
        return len(sources)
    return int(insight.get("source_diversity") or 0)


def recompute_provisional_confidence(insight: dict[str, Any], *, analyzable_count: int) -> float:
    """Derive a per-insight provisional score from the finalized evidence pack."""
    import math

    pack = insight.get("evidence_pack") or []
    evidence_count = len(insight.get("evidence_ids") or pack)
    source_count = _pack_source_count(insight)
    theme_volume = _theme_volume_proxy(insight)
    severity = _severity_proxy(insight)
    theme_breadth = len(insight.get("supporting_themes") or [])

    if evidence_count == 0 or theme_volume == 0 or insight.get("insufficient_evidence"):
        return 0.2

    corpus = max(analyzable_count, 1)
    # Log scale keeps large theme volumes from all saturating at 1.0.
    vol = min(1.0, math.log1p(theme_volume) / math.log1p(max(corpus * 0.35, 20.0)))
    evid = min(1.0, evidence_count / 6.0)
    src = min(1.0, source_count / 6.0)
    depth = min(1.0, (evidence_count * max(source_count, 1)) / 18.0)
    sev = min(1.0, severity / 4.0)
    breadth = min(1.0, theme_breadth / 5.0)

    score = (
        0.22 * vol
        + 0.30 * evid
        + 0.20 * src
        + 0.10 * depth
        + 0.12 * sev
        + 0.06 * breadth
    )
    return round(max(0.34, min(0.95, score)), 3)


def finalize_and_gate(
    insights: list[dict[str, Any]],
    *,
    faithfulness_results: list[dict[str, Any]],
    cross_source_adjustments: list[dict[str, Any]],
    sampling_precision: float,
    publish_cfg: dict[str, Any],
    analyzable_count: int | None = None,
) -> dict[str, Any]:
    faith_by_id = {r["insight_id"]: r for r in faithfulness_results}
    weight_by_id = {r["insight_id"]: r for r in cross_source_adjustments}

    published: list[dict[str, Any]] = []
    drafts: list[dict[str, Any]] = []
    decisions = []
    corpus_n = int(analyzable_count or 0)
    if corpus_n <= 0:
        # Fall back to theme ranking totals if pipeline did not pass analyzable_count.
        corpus_n = max((_theme_volume_proxy(i) for i in insights), default=1)
        corpus_n = max(corpus_n * 2, 100)

    for insight in insights:
        iid = insight["insight_id"]
        # Always recompute from the finalized pack so Q1–Q8 do not share one score.
        base = recompute_provisional_confidence(insight, analyzable_count=corpus_n)
        faith = faith_by_id.get(iid, {})
        weight = float(weight_by_id.get(iid, {}).get("cross_source_weight") or 1.0)
        qa_factor = min(1.0, max(0.5, sampling_precision))
        source_count = _pack_source_count(insight)
        evidence_count = len(insight.get("evidence_ids") or insight.get("evidence_pack") or [])
        pack_strength = min(
            1.0,
            0.55 * min(1.0, evidence_count / 5.0) + 0.45 * min(1.0, source_count / 5.0),
        )

        final_conf = round(
            base * weight * (0.75 + 0.25 * qa_factor) * (0.7 + 0.3 * pack_strength),
            4,
        )
        if not faith.get("faithful", False):
            final_conf = min(final_conf, publish_cfg["min_confidence"] - 0.01)
        single_source_note = False
        if source_count < int(publish_cfg.get("min_source_diversity", 2)) and evidence_count >= 1:
            final_conf = round(min(final_conf, 0.68), 4)
            single_source_note = True

        updated = {
            **insight,
            "confidence_provisional": base,
            "confidence": final_conf,
            "source_diversity": source_count,
            "cross_source_weight": weight,
            "faithfulness": {
                "faithful": bool(faith.get("faithful")),
                "method": faith.get("method"),
                "reason": faith.get("reason"),
            },
            "validation_run": True,
        }
        if single_source_note:
            updated["publish_notes"] = list(updated.get("publish_notes") or []) + [
                "single_source_confidence_cap"
            ]

        reasons = []
        ok = True
        if updated.get("insufficient_evidence") and publish_cfg.get("require_not_insufficient_evidence", True):
            ok = False
            reasons.append("insufficient_evidence")
        if final_conf < float(publish_cfg.get("min_confidence", 0.6)):
            ok = False
            reasons.append("below_min_confidence")
        if len(updated.get("evidence_ids") or []) < int(publish_cfg.get("min_evidence_count", 1)):
            ok = False
            reasons.append("below_min_evidence_count")
        if (
            source_count < int(publish_cfg.get("min_source_diversity", 2))
            and evidence_count < 1
        ):
            ok = False
            reasons.append("below_min_source_diversity")
        if publish_cfg.get("require_faithfulness_pass", True) and not faith.get("faithful", False):
            ok = False
            reasons.append("faithfulness_failed")

        if ok:
            updated["status"] = "published"
            published.append(updated)
            decisions.append(
                {
                    "insight_id": iid,
                    "question_id": updated.get("question_id"),
                    "decision": "published",
                    "confidence": final_conf,
                }
            )
        else:
            updated["status"] = "draft"
            updated["publish_blockers"] = reasons
            drafts.append(updated)
            decisions.append(
                {
                    "insight_id": iid,
                    "question_id": updated.get("question_id"),
                    "decision": "draft",
                    "confidence": final_conf,
                    "blockers": reasons,
                }
            )

    return {
        "published": published,
        "drafts": drafts,
        "all": published + drafts,
        "decisions": decisions,
        "publish_rule_enforced": True,
    }
