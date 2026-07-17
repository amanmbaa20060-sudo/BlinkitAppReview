from __future__ import annotations

from typing import Any

from .base import SourceAdapter, normalize_text, stable_id


class PlayStoreAdapter(SourceAdapter):
    source = "play_store"

    def to_canonical(self, raw: dict[str, Any]) -> dict[str, Any]:
        text = normalize_text(raw.get("content"))
        created_at = raw.get("at") or self.ingested_at
        native_id = str(raw.get("review_id") or "")
        return {
            "feedback_id": stable_id(self.source, native_id or None, text, created_at),
            "source": self.source,
            "created_at": created_at,
            "text": text,
            "rating": raw.get("score"),
            "language": None,
            "url_or_ref": None,
            "author_handle": raw.get("userName"),
            "engagement": None,
            "thread_id": None,
            "parent_id": None,
            "run_id": self.run_id,
            "ingested_at": self.ingested_at,
            "is_quarantined": False,
            "quarantine_reason": None,
            "raw_payload": raw,
        }
