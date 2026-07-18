"""Recompute per-insight confidence from finalized evidence packs (no LLM calls)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "phase4" / "src"))

from publish_gate import (  # noqa: E402
    _pack_source_count,
    recompute_provisional_confidence,
)


RUN_ID = "2026-07-16-weekly"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def finalize_score(insight: dict, *, analyzable_count: int, sampling_precision: float = 0.84) -> dict:
    base = recompute_provisional_confidence(insight, analyzable_count=analyzable_count)
    weight = float(insight.get("cross_source_weight") or 1.0)
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
    if source_count < 2 and evidence_count >= 1:
        final_conf = round(min(final_conf, 0.68), 4)

    updated = {
        **insight,
        "confidence_provisional": base,
        "confidence": final_conf,
        "source_diversity": source_count,
    }
    return updated


def main() -> None:
    enriched_path = REPO_ROOT / "phase2" / "data" / "enriched" / RUN_ID / "enriched_feedback.jsonl"
    published_path = REPO_ROOT / "phase4" / "data" / "insights" / RUN_ID / "insights_published.jsonl"
    draft_path = REPO_ROOT / "phase3" / "data" / "insights" / RUN_ID / "insights.jsonl"
    all_path = REPO_ROOT / "phase4" / "data" / "insights" / RUN_ID / "insights_all.jsonl"

    analyzable_count = 1070
    if enriched_path.exists():
        enriched = load_jsonl(enriched_path)
        analyzable_count = sum(1 for r in enriched if r.get("analysis_status") == "analyzed") or analyzable_count

    sampling_precision = 0.84
    report_path = REPO_ROOT / "phase4" / "reports" / RUN_ID / "validation_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        precision = ((report.get("checks") or {}).get("sampling_qa") or {}).get("precision")
        if precision is not None:
            sampling_precision = float(precision)

    for path in (published_path, draft_path, all_path):
        if not path.exists():
            print(f"skip missing {path}")
            continue
        rows = load_jsonl(path)
        updated = [
            finalize_score(row, analyzable_count=analyzable_count, sampling_precision=sampling_precision)
            for row in rows
        ]
        write_jsonl(path, updated)
        print(f"updated {path.name}:")
        for row in updated:
            print(
                f"  {row.get('question_id')}: "
                f"{round(float(row['confidence']) * 100)}% "
                f"(evid={len(row.get('evidence_pack') or [])}, "
                f"sources={row.get('source_diversity')})"
            )


if __name__ == "__main__":
    main()
