from __future__ import annotations

from typing import Any

from .base import SourceAdapter, normalize_text, stable_id


class SocialMediaAdapter(SourceAdapter):
    source = "social_media"

    def to_canonical(self, raw: dict[str, Any]) -> dict[str, Any]:
        text = normalize_text(raw.get("text"))
        created_at = raw.get("created_at") or self.ingested_at
        native_id = str(raw.get("post_id") or "")
        return {
            "feedback_id": stable_id(self.source, native_id or None, text, created_at),
            "source": self.source,
            "created_at": created_at,
            "text": text,
            "rating": None,
            "language": None,
            "url_or_ref": raw.get("url"),
            "author_handle": raw.get("author"),
            "engagement": {
                "platform": raw.get("platform"),
                "likes": raw.get("likes"),
                "replies": raw.get("replies"),
            },
            "thread_id": raw.get("reply_to"),
            "parent_id": raw.get("reply_to"),
            "run_id": self.run_id,
            "ingested_at": self.ingested_at,
            "is_quarantined": False,
            "quarantine_reason": None,
            "raw_payload": raw,
        }
