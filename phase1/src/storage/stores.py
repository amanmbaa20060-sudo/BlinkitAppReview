"""Raw and cleaned corpus persistence."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


class RawStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, source: str, run_id: str, payloads: list[dict[str, Any]]) -> Path:
        out_dir = self.root / source / run_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "raw.jsonl"
        with out_path.open("w", encoding="utf-8") as f:
            for row in payloads:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        meta = {
            "source": source,
            "run_id": run_id,
            "record_count": len(payloads),
            "path": str(out_path.as_posix()),
        }
        (out_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return out_path


CANONICAL_CSV_FIELDS = [
    "feedback_id",
    "source",
    "created_at",
    "text",
    "rating",
    "language",
    "url_or_ref",
    "author_handle",
    "thread_id",
    "parent_id",
    "run_id",
    "ingested_at",
    "is_quarantined",
    "quarantine_reason",
]


class CleanedStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, run_id: str, records: list[dict[str, Any]]) -> dict[str, Path]:
        out_dir = self.root / run_id
        out_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = out_dir / "feedback.jsonl"
        csv_path = out_dir / "feedback.csv"

        with jsonl_path.open("w", encoding="utf-8") as f:
            for row in records:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        with csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CANONICAL_CSV_FIELDS, extrasaction="ignore")
            writer.writeheader()
            for row in records:
                flat = {k: row.get(k) for k in CANONICAL_CSV_FIELDS}
                writer.writerow(flat)

        return {"jsonl": jsonl_path, "csv": csv_path}
