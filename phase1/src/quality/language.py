"""Language detection for canonical records."""

from __future__ import annotations

from typing import Any


def detect_language(text: str) -> str | None:
    """Detect language code; fall back to simple heuristic if langdetect unavailable."""
    cleaned = (text or "").strip()
    if not cleaned:
        return None
    try:
        from langdetect import DetectorFactory, detect

        DetectorFactory.seed = 0
        return detect(cleaned)
    except Exception:
        # Heuristic: Devanagari → hi; else assume English for Latin script
        if any("\u0900" <= ch <= "\u097F" for ch in cleaned):
            return "hi"
        return "en"


def attach_language(record: dict[str, Any]) -> dict[str, Any]:
    lang = detect_language(record.get("text") or "")
    return {**record, "language": lang}
