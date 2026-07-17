"""Groq-assisted theme classification for Phase 2."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.groq_client import GroqLLMClient  # noqa: E402

TAG_RE = re.compile(r"\s*\[[a-z]+#\d+\]\s*$", re.I)


def base_text(text: str) -> str:
    """Strip fixture uniqueness tags like [ps#12] for LLM dedupe."""
    return TAG_RE.sub("", (text or "").strip()).strip()


def classify_themes_with_groq(
    texts: list[str],
    theme_defs: list[dict[str, Any]],
    client: GroqLLMClient | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Classify unique base texts into multi-label themes via Groq.
    Returns map: base_text -> [{theme_id, score, rationale}]
    """
    client = client or GroqLLMClient()
    unique = []
    seen = set()
    for t in texts:
        b = base_text(t)
        if b and b not in seen:
            seen.add(b)
            unique.append(b)

    catalog = "\n".join(
        f"- {t['theme_id']}: {t['name']} | include: {t.get('inclusion', '')}"
        for t in theme_defs
    )

    results: dict[str, list[dict[str, Any]]] = {}
    # Batch a few at a time to stay within rate limits
    batch_size = 5
    for i in range(0, len(unique), batch_size):
        batch = unique[i : i + batch_size]
        numbered = "\n".join(f"{idx+1}. {txt}" for idx, txt in enumerate(batch))
        prompt = f"""Assign themes to each feedback item using ONLY the theme catalog below.
Return JSON with this shape:
{{
  "items": [
    {{
      "index": 1,
      "themes": [{{"theme_id": "habit.same_basket", "score": 0.0, "rationale": "short"}}]
    }}
  ]
}}

Rules:
- Multi-label allowed (1-4 themes max per item).
- theme_id MUST be from the catalog exactly.
- score between 0 and 1.
- Do not invent themes.
- Prefer themes clearly supported by the text.

Theme catalog:
{catalog}

Feedback items:
{numbered}
"""
        data = client.complete_json(
            prompt,
            system="You are a careful qualitative coding assistant for quick-commerce app feedback.",
            temperature=0.1,
            max_tokens=1800,
        )
        items = data.get("items") or []
        for item in items:
            try:
                idx = int(item.get("index")) - 1
            except (TypeError, ValueError):
                continue
            if idx < 0 or idx >= len(batch):
                continue
            themes = []
            for th in item.get("themes") or []:
                tid = th.get("theme_id")
                if not tid:
                    continue
                if not any(t["theme_id"] == tid for t in theme_defs):
                    continue
                themes.append({
                    "theme_id": tid,
                    "family_id": next(t["family_id"] for t in theme_defs if t["theme_id"] == tid),
                    "score": float(th.get("score") or 0.7),
                    "keyword_hits": [],
                    "similarity": 0.0,
                    "llm_rationale": th.get("rationale") or "",
                    "assignment_source": "groq_llm",
                })
            results[batch[idx]] = themes
    return results


def merge_llm_assignments(
    keyword_assignments: list[dict[str, Any]],
    llm_assignments: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Prefer LLM themes when present; keep keyword themes as fallback/enrichment."""
    if not llm_assignments:
        for a in keyword_assignments:
            a.setdefault("assignment_source", "keyword_similarity")
        return keyword_assignments

    by_id = {a["theme_id"]: dict(a) for a in keyword_assignments}
    for a in llm_assignments:
        tid = a["theme_id"]
        if tid in by_id:
            merged = {**by_id[tid], **a}
            merged["score"] = max(float(by_id[tid].get("score") or 0), float(a.get("score") or 0))
            merged["assignment_source"] = "groq_llm+keyword"
            by_id[tid] = merged
        else:
            by_id[tid] = a
    out = list(by_id.values())
    out.sort(key=lambda x: float(x.get("score") or 0), reverse=True)
    return out
