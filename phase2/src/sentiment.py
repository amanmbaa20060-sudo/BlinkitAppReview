"""Lexicon sentiment and frustration intensity."""

from __future__ import annotations

import re
from typing import Any

POS = {
    "fast", "loyal", "love", "great", "good", "helpful", "clear", "works", "discount",
    "deal", "recommend", "praise", "easy",
}
NEG = {
    "opaque", "unreachable", "late", "poor", "awful", "fear", "risk", "thin", "weak",
    "missing", "broken", "frustrat", "stockout", "never", "barely", "irrelevant",
    "expensive", "doubt", "kill", "fail",
}
URGENCY = {
    "unreachable", "stockout", "late", "opaque", "awful", "kill", "never", "twice",
}


def score_sentiment(text: str, rating: float | None = None) -> dict[str, Any]:
    toks = set(re.findall(r"[a-z0-9]+", text.lower()))
    pos = len(toks & POS)
    neg = sum(1 for t in toks if any(n in t for n in NEG))
    raw = pos - neg
    if rating is not None:
        # Blend star rating when present (1-5 → -1..+1)
        raw += (rating - 3) * 0.75
    if raw > 0.5:
        label = "positive"
    elif raw < -0.5:
        label = "negative"
    else:
        label = "neutral"
    intensity = min(1.0, sum(1 for u in URGENCY if u in text.lower()) * 0.35 + max(0.0, -raw) * 0.15)
    return {
        "sentiment_label": label,
        "sentiment_score": round(float(raw), 3),
        "frustration_intensity": round(float(intensity), 3),
    }
