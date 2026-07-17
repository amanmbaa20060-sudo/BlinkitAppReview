#!/usr/bin/env python3
"""Run Phase 3 discovery modules and write draft Insight Store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PHASE3_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PHASE3_ROOT))

from src.pipeline import run_phase3  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 3 — Q1–Q8 draft insights")
    parser.add_argument("--run-id", default="2026-07-16-weekly")
    args = parser.parse_args()
    report = run_phase3(run_id=args.run_id)
    print(json.dumps({
        "run_id": report["run_id"],
        "insight_count": report["insight_count"],
        "questions_covered": report["questions_covered"],
        "exit_criteria": report["exit_criteria"],
        "draft_confidence_summary": report["draft_confidence_summary"],
        "report_path": f"reports/{args.run_id}/phase3_report.json",
    }, indent=2))
    return 0 if all(report["exit_criteria"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
