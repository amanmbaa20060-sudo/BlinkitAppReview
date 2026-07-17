"""Base adapter contract and shared helpers."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}") from exc


def stable_id(source: str, native_id: str | None, text: str, created_at: str) -> str:
    if native_id:
        return f"{source}:{native_id}"
    digest = hashlib.sha256(f"{source}|{created_at}|{text}".encode("utf-8")).hexdigest()[:16]
    return f"{source}:{digest}"


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


class SourceAdapter(ABC):
    source: str

    def __init__(self, fixture_path: Path, run_id: str) -> None:
        self.fixture_path = fixture_path
        self.run_id = run_id
        self.ingested_at = utc_now_iso()

    def load_raw(self) -> list[dict[str, Any]]:
        if not self.fixture_path.exists():
            raise FileNotFoundError(f"Fixture not found for {self.source}: {self.fixture_path}")
        return list(read_jsonl(self.fixture_path))

    @abstractmethod
    def to_canonical(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Map one raw payload to canonical schema (pre-quality-gates)."""

    def iter_canonical(self) -> Iterator[tuple[dict[str, Any], dict[str, Any]]]:
        """Yield (raw_payload, canonical_record)."""
        for raw in self.load_raw():
            yield raw, self.to_canonical(raw)
