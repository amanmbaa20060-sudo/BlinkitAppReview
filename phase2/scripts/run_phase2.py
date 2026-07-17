#!/usr/bin/env python3
"""Run Phase 2 representation, themeing, and enrichment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PHASE2_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PHASE2_ROOT))

from src.pipeline import run_phase2  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 2 — embeddings, themes, sentiment, segments")
    parser.add_argument("--run-id", default="2026-07-16-weekly")
    args = parser.parse_args()
    report = run_phase2(run_id=args.run_id)
    print(json.dumps({
        "run_id": report["run_id"],
        "input_cleaned_count": report["input_cleaned_count"],
        "embedded_count": report["embedded_count"],
        "analyzed_count": report["analyzed_count"],
        "theme_coverage_pct": report["theme_coverage_pct"],
        "taxonomy_version": report["taxonomy_version"],
        "exit_criteria": report["exit_criteria"],
        "report_path": f"reports/{args.run_id}/phase2_report.json",
    }, indent=2))
    ok = all(report["exit_criteria"].values()) and report["theme_coverage_pct"] > 0
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
