from __future__ import annotations

from typing import Any

from .base import SourceAdapter, normalize_text, stable_id


class RedditAdapter(SourceAdapter):
    source = "reddit"

    def to_canonical(self, raw: dict[str, Any]) -> dict[str, Any]:
        title = normalize_text(raw.get("title"))
        body = normalize_text(raw.get("body"))
        if title and body:
            text = f"{title}\n\n{body}"
        else:
            text = body or title
        text = normalize_text(text)
        created_at = raw.get("created_utc") or self.ingested_at
        native_id = str(raw.get("id") or "")
        return {
            "feedback_id": stable_id(self.source, native_id or None, text, created_at),
            "source": self.source,
            "created_at": created_at,
            "text": text,
            "rating": None,
            "language": None,
            "url_or_ref": raw.get("permalink"),
            "author_handle": raw.get("author"),
            "engagement": {"score": raw.get("score"), "subreddit": raw.get("subreddit")},
            "thread_id": raw.get("thread_id"),
            "parent_id": raw.get("parent_id"),
            "run_id": self.run_id,
            "ingested_at": self.ingested_at,
            "is_quarantined": False,
            "quarantine_reason": None,
            "raw_payload": raw,
        }
