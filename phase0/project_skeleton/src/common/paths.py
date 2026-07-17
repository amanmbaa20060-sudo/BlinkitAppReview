"""Shared constants and path helpers."""

from __future__ import annotations

from pathlib import Path

PHASE0_ROOT = Path(__file__).resolve().parents[3]
SKELETON_ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = PHASE0_ROOT / "taxonomy" / "theme_taxonomy_v0.json"
SCHEMA_PATH = PHASE0_ROOT / "schema" / "canonical_feedback_schema.json"
SETTINGS_EXAMPLE = PHASE0_ROOT / "config" / "settings.example.yaml"

PIPELINE_STEPS = (
    "collect",
    "normalize",
    "prepare",
    "represent",
    "theme",
    "enrich",
    "answer",
    "synthesize",
    "validate",
    "publish",
)
