"""4.2 Sampling QA — LLM-as-judge on theme assignments."""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _heuristic_judge(text: str, theme_ids: list[str]) -> dict[str, Any]:
    """Fallback if Groq unavailable: keyword overlap heuristic."""
    lowered = text.lower()
    cues = {
        "habit": ["reorder", "same basket", "saved list", "browse", "routine"],
        "barrier": ["trust", "fee", "irrelevant", "uncertainty", "fear"],
        "discovery": ["search", "banner", "recommend", "word of mouth", "social proof"],
        "info": ["review", "ingredient", "freshness", "return", "sizing"],
        "frustration": ["late", "stockout", "substitute", "support", "opaque"],
        "experiment": ["discount", "deal", "puppy", "festival", "niche"],
        "unmet": ["starter kit", "assortment", "guidance", "cross-category", "nudge"],
    }
    ok = 0
    for tid in theme_ids:
        family = tid.split(".")[0]
        words = cues.get(family, [])
        if any(w in lowered for w in words) or any(part in lowered for part in tid.split(".")[1:]):
            ok += 1
    precision = ok / len(theme_ids) if theme_ids else 0.0
    return {"supported": precision >= 0.5, "precision_item": precision, "method": "heuristic"}


def _llm_judge(text: str, theme_ids: list[str]) -> dict[str, Any]:
    from shared.groq_client import GroqLLMClient

    client = GroqLLMClient()
    prompt = f"""Judge whether the assigned themes are reasonably supported by the feedback text.
Return JSON: {{"supported": true/false, "correct_theme_ids": ["..."], "notes": "short"}}

Text: {text}
Assigned themes: {theme_ids}
"""
    data = client.complete_json(
        prompt,
        system="You are a careful qualitative coding QA judge. Be strict but fair.",
        temperature=0.0,
        max_tokens=400,
    )
    correct = data.get("correct_theme_ids") or []
    if isinstance(correct, list) and theme_ids:
        precision = len([t for t in theme_ids if t in correct]) / len(theme_ids)
    else:
        precision = 1.0 if data.get("supported") else 0.0
    return {
        "supported": bool(data.get("supported")),
        "precision_item": precision,
        "notes": data.get("notes"),
        "method": "groq_llm",
        "model": client.model,
    }


def sampling_qa(
    enriched: list[dict[str, Any]],
    *,
    sample_size: int,
    min_precision: float,
    use_llm_judge: bool,
    seed: int = 42,
) -> dict[str, Any]:
    analyzed = [
        r for r in enriched
        if r.get("analysis_status") == "analyzed" and r.get("themes")
    ]
    rng = random.Random(seed)
    sample = analyzed[:]
    rng.shuffle(sample)
    sample = sample[: min(sample_size, len(sample))]

    judged = []
    supported = 0
    precision_scores = []
    methods_used: set[str] = set()
    for row in sample:
        theme_ids = [t["theme_id"] for t in row.get("themes") or [] if t.get("theme_id") != "theme.other"][:3]
        text = row.get("prepared_text") or row.get("text") or ""
        try:
            result = _llm_judge(text, theme_ids) if use_llm_judge else _heuristic_judge(text, theme_ids)
        except Exception as exc:  # noqa: BLE001
            result = {**_heuristic_judge(text, theme_ids), "llm_error": str(exc)}
        methods_used.add(str(result.get("method") or "unknown"))
        if result.get("supported"):
            supported += 1
        precision_scores.append(float(result.get("precision_item") or 0))
        judged.append({
            "feedback_id": row["feedback_id"],
            "theme_ids": theme_ids,
            **result,
        })

    precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0.0
    if "groq_llm" in methods_used and len(methods_used) == 1:
        judge_method = "groq_llm"
    elif "groq_llm" in methods_used:
        judge_method = "groq_llm_with_heuristic_fallback"
    else:
        judge_method = next(iter(methods_used), "none")
    return {
        "check": "sampling_qa",
        "sample_size": len(sample),
        "supported_count": supported,
        "support_rate": round(supported / len(sample), 4) if sample else 0.0,
        "precision": round(precision, 4),
        "min_precision": min_precision,
        "passed": precision >= min_precision,
        "judge_method": judge_method,
        "samples": judged[:15],  # keep report readable
    }
