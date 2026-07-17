from __future__ import annotations

from typing import Any

from .base import SourceAdapter, normalize_text, stable_id


class ProductReviewsAdapter(SourceAdapter):
    source = "product_reviews"

    def to_canonical(self, raw: dict[str, Any]) -> dict[str, Any]:
        text = normalize_text(raw.get("text"))
        created_at = raw.get("created_at") or self.ingested_at
        native_id = str(raw.get("review_id") or "")
        category = raw.get("category")
        product_id = raw.get("product_id")
        if category or product_id:
            prefix = " | ".join(p for p in [f"category={category}" if category else "", f"product={product_id}" if product_id else ""] if p)
            # Keep product/category hints in engagement metadata; text stays review body
        else:
            prefix = ""
        return {
            "feedback_id": stable_id(self.source, native_id or None, text, created_at),
            "source": self.source,
            "created_at": created_at,
            "text": text,
            "rating": raw.get("rating"),
            "language": None,
            "url_or_ref": None,
            "author_handle": raw.get("reviewer"),
            "engagement": {
                "helpful_votes": raw.get("helpful_votes"),
                "product_id": product_id,
                "category": category,
                "category_hint": prefix or None,
            },
            "thread_id": None,
            "parent_id": None,
            "run_id": self.run_id,
            "ingested_at": self.ingested_at,
            "is_quarantined": False,
            "quarantine_reason": None,
            "raw_payload": raw,
        }
