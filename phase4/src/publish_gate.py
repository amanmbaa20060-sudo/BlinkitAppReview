"""4.7–4.8 Confidence finalization and publish gate."""

from __future__ import annotations

from typing import Any


def finalize_and_gate(
    insights: list[dict[str, Any]],
    *,
    faithfulness_results: list[dict[str, Any]],
    cross_source_adjustments: list[dict[str, Any]],
    sampling_precision: float,
    publish_cfg: dict[str, Any],
) -> dict[str, Any]:
    faith_by_id = {r["insight_id"]: r for r in faithfulness_results}
    weight_by_id = {r["insight_id"]: r for r in cross_source_adjustments}

    published: list[dict[str, Any]] = []
    drafts: list[dict[str, Any]] = []
    decisions = []

    for insight in insights:
        iid = insight["insight_id"]
        base = float(insight.get("confidence") or 0)
        faith = faith_by_id.get(iid, {})
        weight = float(weight_by_id.get(iid, {}).get("cross_source_weight") or 1.0)
        qa_factor = min(1.0, max(0.5, sampling_precision))

        final_conf = round(base * weight * (0.7 + 0.3 * qa_factor), 4)
        if not faith.get("faithful", False):
            final_conf = min(final_conf, publish_cfg["min_confidence"] - 0.01)

        updated = {
            **insight,
            "confidence_provisional": base,
            "confidence": final_conf,
            "cross_source_weight": weight,
            "faithfulness": {
                "faithful": bool(faith.get("faithful")),
                "method": faith.get("method"),
                "reason": faith.get("reason"),
            },
            "validation_run": True,
        }

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
        if int(updated.get("source_diversity") or 0) < int(publish_cfg.get("min_source_diversity", 2)):
            ok = False
            reasons.append("below_min_source_diversity")
        if publish_cfg.get("require_faithfulness_pass", True) and not faith.get("faithful", False):
            ok = False
            reasons.append("faithfulness_failed")

        if ok:
            updated["status"] = "published"
            published.append(updated)
            decisions.append({"insight_id": iid, "question_id": updated.get("question_id"), "decision": "published", "confidence": final_conf})
        else:
            updated["status"] = "draft"
            updated["publish_blockers"] = reasons
            drafts.append(updated)
            decisions.append({
                "insight_id": iid,
                "question_id": updated.get("question_id"),
                "decision": "draft",
                "confidence": final_conf,
                "blockers": reasons,
            })

    return {
        "published": published,
        "drafts": drafts,
        "all": published + drafts,
        "decisions": decisions,
        "publish_rule_enforced": True,
    }
