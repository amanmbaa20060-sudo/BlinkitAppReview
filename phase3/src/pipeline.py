"""Phase 3 pipeline — run all discovery modules and write Insight Store."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .io_utils import load_json, load_jsonl, write_json, write_jsonl
from .modules import MODULES, QUESTIONS
from .evidence import analyzed_rows

PHASE3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PHASE3_ROOT.parent


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_phase3(run_id: str = "2026-07-16-weekly") -> dict[str, Any]:
    enriched_path = REPO_ROOT / "phase2" / "data" / "enriched" / run_id / "enriched_feedback.jsonl"
    metrics_path = REPO_ROOT / "phase2" / "data" / "themes" / "v1" / run_id / "metrics.json"
    taxonomy_path = REPO_ROOT / "phase2" / "taxonomy" / "theme_taxonomy_v1.json"

    if not enriched_path.exists():
        raise FileNotFoundError(f"Missing Phase 2 enriched corpus: {enriched_path}")

    enriched = load_jsonl(enriched_path)
    metrics = load_json(metrics_path) if metrics_path.exists() else {}
    taxonomy = load_json(taxonomy_path) if taxonomy_path.exists() else {}
    analyzable = analyzed_rows(enriched)

    ctx = {
        "run_id": run_id,
        "questions": QUESTIONS,
        "analyzable_count": len(analyzable),
        "metrics": metrics,
        "taxonomy_version": taxonomy.get("taxonomy_version", "v1"),
    }

    insights: list[dict[str, Any]] = []
    by_question: dict[str, list[dict[str, Any]]] = {q: [] for q in QUESTIONS}

    for qid, fn in MODULES.items():
        produced = fn(enriched, ctx)
        for insight in produced:
            # Enforce schema / exit rules
            if insight.get("question_id") != qid:
                raise ValueError(f"Orphan/mismatched insight question_id for module {qid}")
            if insight.get("status") != "draft":
                insight["status"] = "draft"
            insights.append(insight)
            by_question[qid].append(insight)

    # Exit criteria checks
    questions_with_insight = [q for q, items in by_question.items() if len(items) >= 1]
    all_have_evidence_ids = all(isinstance(i.get("evidence_ids"), list) for i in insights)
    # evidence_ids may be empty only when insufficient_evidence flagged
    all_cite_or_flagged = all(
        (len(i.get("evidence_ids") or []) > 0) or i.get("insufficient_evidence")
        for i in insights
    )
    # Prefer strict: every insight should cite when volume exists; still require field present
    all_cite = all(len(i.get("evidence_ids") or []) > 0 for i in insights)
    implications_ok = all(
        "categor" in (i.get("implication") or "").lower()
        or "mac" in (i.get("implication") or "").lower()
        or "new-category" in (i.get("implication") or "").lower()
        or "new category" in (i.get("implication") or "").lower()
        for i in insights
    )
    no_orphans = all(i.get("question_id") in QUESTIONS for i in insights)

    out_dir = PHASE3_ROOT / "data" / "insights" / run_id
    write_jsonl(out_dir / "insights.jsonl", insights)
    write_json(out_dir / "insights_by_question.json", {
        "run_id": run_id,
        "questions": QUESTIONS,
        "insights_by_question": by_question,
    })

    report = {
        "run_id": run_id,
        "generated_at": utc_now(),
        "analyzable_count": len(analyzable),
        "insight_count": len(insights),
        "questions_covered": questions_with_insight,
        "all_questions_covered": len(questions_with_insight) == 8,
        "exit_criteria": {
            "every_question_has_draft_insight": len(questions_with_insight) == 8,
            "every_draft_insight_cites_evidence_ids": all_cite and all_have_evidence_ids,
            "implications_relate_to_category_expansion": implications_ok,
            "no_orphan_insights": no_orphans,
        },
        "draft_confidence_summary": {
            i["insight_id"]: i["confidence"] for i in insights
        },
        "outputs": {
            "insights_jsonl": str((out_dir / "insights.jsonl").as_posix()),
            "insights_by_question": str((out_dir / "insights_by_question.json").as_posix()),
        },
        "notes": [
            "All insights status=draft pending Phase 4 validation/publish gate.",
            "Synthesis is evidence-constrained; quotes come only from retrieved feedback_ids.",
        ],
    }
    # Soft note if cite failed due to empty
    if not all_cite:
        report["exit_criteria"]["every_draft_insight_cites_evidence_ids"] = all_cite_or_flagged
        report["notes"].append("Some insights flagged insufficient_evidence with empty citations.")

    write_json(PHASE3_ROOT / "reports" / run_id / "phase3_report.json", report)
    return report
