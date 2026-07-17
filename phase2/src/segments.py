"""Lightweight text-inferred segment tags."""

from __future__ import annotations

import re
from typing import Any


def tag_segments(text: str, themes: list[dict[str, Any]]) -> dict[str, Any]:
    lowered = text.lower()
    theme_ids = {t["theme_id"] for t in themes}
    segments: list[str] = []
    confidence = 0.4

    if theme_ids & {"habit.same_basket", "habit.autopilot_reorder", "habit.low_browse_intent"}:
        segments.append("habitual_reorderer")
        confidence = max(confidence, 0.7)
    if theme_ids & {"experiment.deal_driven", "experiment.life_event", "experiment.gift_occasion", "experiment.niche_interest"}:
        segments.append("occasional_explorer")
        confidence = max(confidence, 0.7)
    if "deal" in lowered or "discount" in lowered:
        segments.append("deal_sensitive")
        confidence = max(confidence, 0.65)
    if re.search(r"\b(puppy|pet|dog|baby|parent|diaper)\b", lowered):
        segments.append("life_stage_pet_or_parent")
        confidence = max(confidence, 0.75)
    if re.search(r"\b(new user|just installed|first time)\b", lowered):
        segments.append("new_tenure_tone")
        confidence = max(confidence, 0.6)
    if re.search(r"\b(months|every week|always|for years)\b", lowered):
        segments.append("long_tenure_tone")
        confidence = max(confidence, 0.55)

    if not segments:
        segments = ["unspecified"]
        confidence = 0.3

    return {
        "segments": segments,
        "segment_confidence": round(confidence, 3),
    }
