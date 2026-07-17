"""Canonical feedback schema helpers (Phase 0)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_ENUM = (
    "play_store",
    "app_store",
    "reddit",
    "product_reviews",
    "social_media",
    "community_forums",
    "quick_commerce_discussions",
)

REQUIRED_FIELDS = (
    "feedback_id",
    "source",
    "created_at",
    "text",
    "ingested_at",
    "raw_payload",
)

SCHEMA_VERSION = "1.0.0"


def schema_path() -> Path:
    """Path to frozen JSON Schema relative to phase0/schema."""
    return Path(__file__).resolve().parents[3] / "schema" / "canonical_feedback_schema.json"


def load_json_schema() -> dict[str, Any]:
    with schema_path().open(encoding="utf-8") as f:
        return json.load(f)


def validate_record(record: dict[str, Any]) -> list[str]:
    """Lightweight structural validation (no external jsonschema dependency required).

    Returns a list of error messages; empty list means OK.
    """
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing required field: {field}")
    if "source" in record and record["source"] not in SOURCE_ENUM:
        errors.append(f"invalid source: {record['source']}")
    if "text" in record and (not isinstance(record["text"], str) or not record["text"].strip()):
        errors.append("text must be a non-empty string")
    if "raw_payload" in record and not isinstance(record["raw_payload"], dict):
        errors.append("raw_payload must be an object")
    return errors
