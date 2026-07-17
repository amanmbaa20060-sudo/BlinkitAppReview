from __future__ import annotations

from typing import Any

from .base import SourceAdapter, normalize_text, stable_id


class AppStoreAdapter(SourceAdapter):
    source = "app_store"

    def to_canonical(self, raw: dict[str, Any]) -> dict[str, Any]:
        title = normalize_text(raw.get("title"))
        body = normalize_text(raw.get("body"))
        text = normalize_text(f"{title}. {body}" if title and body else (body or title))
        created_at = raw.get("date") or self.ingested_at
        native_id = str(raw.get("id") or "")
        return {
            "feedback_id": stable_id(self.source, native_id or None, text, created_at),
            "source": self.source,
            "created_at": created_at,
            "text": text,
            "rating": raw.get("rating"),
            "language": None,
            "url_or_ref": raw.get("url"),
            "author_handle": raw.get("reviewerNickname"),
            "engagement": None,
            "thread_id": None,
            "parent_id": None,
            "run_id": self.run_id,
            "ingested_at": self.ingested_at,
            "is_quarantined": False,
            "quarantine_reason": None,
            "raw_payload": raw,
        }
