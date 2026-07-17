"""4.3 Faithfulness — insight claims entailed by cited quotes."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _heuristic_faithfulness(insight: dict[str, Any]) -> dict[str, Any]:
    quotes = " ".join(e.get("quote") or "" for e in insight.get("evidence_pack") or []).lower()
    headline = (insight.get("headline") or "").lower()
    if not quotes.strip() or insight.get("insufficient_evidence"):
        return {"faithful": False, "method": "heuristic", "reason": "missing_evidence"}
    # Require at least one overlapping content word > 3 chars (excluding stopwords)
    stops = {"the", "and", "for", "with", "from", "that", "this", "users", "user", "due", "are", "not"}
    words = [w.strip(".,;:!?") for w in headline.split() if len(w) > 3 and w not in stops]
    hits = sum(1 for w in words if w in quotes)
    faithful = hits >= max(1, len(words) // 4) and len(insight.get("evidence_ids") or []) > 0
    return {"faithful": faithful, "method": "heuristic", "overlap_hits": hits}


def _llm_faithfulness(insight: dict[str, Any]) -> dict[str, Any]:
    from shared.groq_client import GroqLLMClient

    client = GroqLLMClient()
    quotes = "\n".join(
        f"- {e.get('feedback_id')}: {e.get('quote')}" for e in insight.get("evidence_pack") or []
    )
    prompt = f"""Decide if the insight headline and implication are faithful to the evidence quotes.
Return JSON: {{"faithful": true/false, "reason": "short"}}

Headline: {insight.get('headline')}
Implication: {insight.get('implication')}
Quotes:
{quotes}
"""
    data = client.complete_json(
        prompt,
        system="You are an evidence faithfulness auditor. Mark false if claims go beyond quotes.",
        temperature=0.0,
        max_tokens=300,
    )
    return {
        "faithful": bool(data.get("faithful")),
        "reason": data.get("reason"),
        "method": "groq_llm",
        "model": client.model,
    }


def faithfulness_check(
    insights: list[dict[str, Any]],
    *,
    use_llm_judge: bool,
    min_pass_rate: float,
) -> dict[str, Any]:
    results = []
    passed = 0
    for insight in insights:
        try:
            result = _llm_faithfulness(insight) if use_llm_judge else _heuristic_faithfulness(insight)
        except Exception as exc:  # noqa: BLE001
            result = {**_heuristic_faithfulness(insight), "llm_error": str(exc)}
        if result.get("faithful"):
            passed += 1
        results.append({"insight_id": insight.get("insight_id"), "question_id": insight.get("question_id"), **result})

    rate = passed / len(insights) if insights else 0.0
    return {
        "check": "faithfulness",
        "insight_count": len(insights),
        "passed_count": passed,
        "pass_rate": round(rate, 4),
        "min_pass_rate": min_pass_rate,
        "passed": rate >= min_pass_rate,
        "results": results,
    }
