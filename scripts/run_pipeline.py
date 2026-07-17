"""Run Phases 1-4 and refresh the dashboard data bundle."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = os.environ.get("RUN_ID", "2026-07-16-weekly")


def run_step(label: str, command: list[str]) -> None:
    print(f"\n==> {label}")
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    python = sys.executable
    steps = [
        ("Phase 1 ingest", [python, "phase1/scripts/run_ingest.py", "--run-id", RUN_ID]),
        ("Phase 2 themeing", [python, "phase2/scripts/run_phase2.py", "--run-id", RUN_ID]),
        ("Phase 3 insights", [python, "phase3/scripts/run_phase3.py", "--run-id", RUN_ID]),
        ("Phase 4 validation", [python, "phase4/scripts/run_phase4.py", "--run-id", RUN_ID]),
        ("Phase 5 dashboard data", [python, "phase5/scripts/build_dashboard_data.py"]),
    ]
    for label, command in steps:
        run_step(label, command)
    print(f"\nPipeline complete for run_id={RUN_ID}")


if __name__ == "__main__":
    main()
