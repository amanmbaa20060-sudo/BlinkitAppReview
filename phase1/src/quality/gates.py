"""Ingest quality gates: empty drop, dedupe, spam/bot quarantine."""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


DEFAULT_SPAM_KEYWORDS = (
    "buy followers",
    "click here now",
    "crypto giveaway",
    "telegram @",
    "whatsapp me for",
)

DEFAULT_BOT_PATTERNS = (
    r"^as an ai",
    r"^this is an automated",
)


@dataclass
class GateStats:
    input_count: int = 0
    dropped_empty: int = 0
    dropped_duplicate: int = 0
    quarantined: int = 0
    kept: int = 0
    by_source: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {
        "input": 0,
        "dropped_empty": 0,
        "dropped_duplicate": 0,
        "quarantined": 0,
        "kept": 0,
    }))


def _normalize_for_dedupe(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _text_fingerprint(text: str) -> str:
    return hashlib.sha256(_normalize_for_dedupe(text).encode("utf-8")).hexdigest()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class QualityGates:
    def __init__(
        self,
        spam_keywords: list[str] | None = None,
        bot_patterns: list[str] | None = None,
        dedupe_window_days: int = 30,
    ) -> None:
        self.spam_keywords = [k.lower() for k in (spam_keywords or list(DEFAULT_SPAM_KEYWORDS))]
        self.bot_patterns = [re.compile(p, re.IGNORECASE) for p in (bot_patterns or list(DEFAULT_BOT_PATTERNS))]
        self.dedupe_window_days = dedupe_window_days
        self.stats = GateStats()
        self._seen: dict[str, list[datetime]] = defaultdict(list)

    def _is_spam_or_bot(self, text: str) -> str | None:
        lowered = text.lower()
        for kw in self.spam_keywords:
            if kw in lowered:
                return f"spam_keyword:{kw}"
        for pat in self.bot_patterns:
            if pat.search(text):
                return f"bot_pattern:{pat.pattern}"
        return None

    def _is_duplicate(self, text: str, created_at: str | None, source: str) -> bool:
        fp = f"{source}:{_text_fingerprint(text)}"
        created = _parse_dt(created_at) or datetime.now()
        window = timedelta(days=self.dedupe_window_days)
        prior = self._seen[fp]
        for prev in prior:
            if abs((created - prev).total_seconds()) <= window.total_seconds():
                return True
        prior.append(created)
        return False

    def apply(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """Return cleaned record, quarantined record, or None if dropped."""
        source = record.get("source", "unknown")
        self.stats.input_count += 1
        self.stats.by_source[source]["input"] += 1

        text = (record.get("text") or "").strip()
        if not text:
            self.stats.dropped_empty += 1
            self.stats.by_source[source]["dropped_empty"] += 1
            return None

        record = {**record, "text": " ".join(text.split())}

        if self._is_duplicate(record["text"], record.get("created_at"), source):
            self.stats.dropped_duplicate += 1
            self.stats.by_source[source]["dropped_duplicate"] += 1
            return None

        reason = self._is_spam_or_bot(record["text"])
        if reason:
            record = {
                **record,
                "is_quarantined": True,
                "quarantine_reason": reason,
            }
            self.stats.quarantined += 1
            self.stats.by_source[source]["quarantined"] += 1
            self.stats.kept += 1  # quarantined still written for audit
            self.stats.by_source[source]["kept"] += 1
            return record

        record = {**record, "is_quarantined": False, "quarantine_reason": None}
        self.stats.kept += 1
        self.stats.by_source[source]["kept"] += 1
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "input_count": self.stats.input_count,
            "dropped_empty": self.stats.dropped_empty,
            "dropped_duplicate": self.stats.dropped_duplicate,
            "quarantined": self.stats.quarantined,
            "kept": self.stats.kept,
            "by_source": {k: dict(v) for k, v in self.stats.by_source.items()},
        }
