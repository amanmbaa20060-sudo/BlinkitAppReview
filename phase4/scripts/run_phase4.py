#!/usr/bin/env python3
"""Run Phase 4 validation, governance, and publish gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PHASE4_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PHASE4_ROOT))

from src.pipeline import run_phase4  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4 — validation & publish gate")
    parser.add_argument("--run-id", default="2026-07-16-weekly")
    args = parser.parse_args()
    report = run_phase4(run_id=args.run_id)
    print(json.dumps({
        "run_id": report["run_id"],
        "published_count": report["publish_gate"]["published_count"],
        "draft_count": report["publish_gate"]["draft_count"],
        "published_questions": report["publish_gate"]["published_questions"],
        "gaps_documented": report["publish_gate"]["gaps_documented"],
        "checks_passed": {
            "coverage": report["checks"]["coverage"]["passed"],
            "sampling_qa": report["checks"]["sampling_qa"]["passed"],
            "faithfulness": report["checks"]["faithfulness"]["passed"],
            "stability": report["checks"]["stability"]["passed"],
        },
        "exit_criteria": report["exit_criteria"],
        "report_path": f"reports/{args.run_id}/validation_report.json",
    }, indent=2))
    return 0 if all(report["exit_criteria"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
