#!/usr/bin/env python3
"""Run Phase 1 multi-source ingest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PHASE1_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PHASE1_ROOT))

from src.adapters import SOURCE_PRIORITY  # noqa: E402
from src.pipeline import IngestConfig, run_ingest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 1 ingest — fixtures → raw → cleaned corpus")
    parser.add_argument("--run-id", default=None, help="Batch run id (default: YYYY-MM-DD-weekly)")
    parser.add_argument(
        "--sources",
        default=None,
        help="Comma-separated sources (default: all seven in priority order)",
    )
    args = parser.parse_args()

    sources = None
    if args.sources:
        sources = [s.strip() for s in args.sources.split(",") if s.strip()]
        unknown = set(sources) - set(SOURCE_PRIORITY)
        if unknown:
            print(f"Unknown sources: {sorted(unknown)}", file=sys.stderr)
            return 1

    config = IngestConfig.from_phase1_defaults(run_id=args.run_id, sources=sources)
    report = run_ingest(config)

    print(json.dumps({
        "run_id": report["run_id"],
        "cleaned_record_count": report["cleaned_record_count"],
        "sources_in_cleaned_corpus": report["sources_in_cleaned_corpus"],
        "quality_gates": report["quality_gates"],
        "date_range": report["date_range"],
        "report_path": report["report_path"],
        "exit_criteria": report["exit_criteria"],
    }, indent=2))

    if not report["exit_criteria"]["all_seven_sources_present"] and sources is None:
        print("WARNING: not all seven sources present in cleaned corpus", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
