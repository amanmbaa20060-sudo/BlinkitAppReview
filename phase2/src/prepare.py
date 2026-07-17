"""Text preparation: normalize, chunk long threads, light PII redaction."""

from __future__ import annotations

import re
from typing import Any

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d[\d\-\s]{8,}\d)\b")
HANDLE_RE = re.compile(r"(?<!\w)@[A-Za-z0-9_]{2,}")


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def redact_pii(text: str) -> str:
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    # Keep social handles for segment cues but scrub dense handle spam
    if text.count("@") >= 3:
        text = HANDLE_RE.sub("[HANDLE]", text)
    return text


def chunk_text(text: str, source: str, max_chars: int = 1200) -> list[str]:
    """Chunk long Reddit/forum posts; short reviews stay single-unit."""
    if source not in {"reddit", "community_forums", "quick_commerce_discussions"}:
        return [text] if text else []
    if len(text) <= max_chars:
        return [text] if text else []
    chunks: list[str] = []
    paragraphs = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    buf = ""
    for p in paragraphs or [text]:
        if len(buf) + len(p) + 1 <= max_chars:
            buf = f"{buf} {p}".strip()
        else:
            if buf:
                chunks.append(buf)
            if len(p) <= max_chars:
                buf = p
            else:
                for i in range(0, len(p), max_chars):
                    chunks.append(p[i : i + max_chars])
                buf = ""
    if buf:
        chunks.append(buf)
    return chunks or ([text] if text else [])


def prepare_record(record: dict[str, Any]) -> dict[str, Any]:
    raw_text = record.get("text") or ""
    cleaned = redact_pii(normalize_text(raw_text))
    chunks = chunk_text(cleaned, record.get("source") or "")
    return {
        **record,
        "prepared_text": cleaned,
        "chunks": chunks,
        "chunk_count": len(chunks),
    }
