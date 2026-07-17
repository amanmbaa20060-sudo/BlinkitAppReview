"""Evidence-constrained insight synthesis (template + optional Groq LLM)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .evidence import source_diversity

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def provisional_confidence(
    *,
    evidence_count: int,
    theme_volume: int,
    source_count: int,
    analyzable_count: int,
) -> float:
    """Provisional score for Phase 4 finalization."""
    if evidence_count == 0 or theme_volume == 0:
        return 0.2
    vol = min(1.0, theme_volume / max(analyzable_count * 0.05, 1))
    evid = min(1.0, evidence_count / 5)
    src = min(1.0, source_count / 4)
    return round(0.35 * vol + 0.35 * evid + 0.30 * src, 3)


def refine_with_groq(
    *,
    question: str,
    question_id: str,
    supporting_themes: list[str],
    evidence: list[dict[str, Any]],
    draft_headline: str,
    draft_implication: str,
) -> dict[str, Any]:
    """Ask Groq to refine headline/implication strictly from evidence quotes."""
    from shared.groq_client import GroqLLMClient

    quotes = "\n".join(
        f"- ({e.get('feedback_id')}|{e.get('source')}) {e.get('text')}"
        for e in evidence
    )
    prompt = f"""You are synthesizing insights for a quick-commerce category-expansion study.
Strategic goal: increase % of Monthly Active Customers who buy from at least one NEW category each month.

Question ({question_id}): {question}
Supporting themes: {', '.join(supporting_themes) if supporting_themes else 'none'}
Draft headline: {draft_headline}
Draft implication: {draft_implication}

Evidence quotes (ONLY source of truth — do not invent facts beyond these):
{quotes}

Return JSON:
{{
  "headline": "one clear finding grounded in the evidence",
  "implication": "one action implication for MAC new-category purchase behavior",
  "used_evidence_ids": ["id1", "id2"]
}}

Rules:
- Every claim must be supportable by the quotes.
- Keep headline <= 240 characters.
- Implication must mention category expansion or new-category trial for MACs.
- used_evidence_ids must be subset of the provided feedback_ids.
"""
    client = GroqLLMClient()
    data = client.complete_json(
        prompt,
        system="You are an evidence-constrained insights analyst. Never invent quotes or unsupported claims.",
        temperature=0.2,
        max_tokens=700,
    )
    allowed = {e["feedback_id"] for e in evidence}
    used = [i for i in (data.get("used_evidence_ids") or []) if i in allowed]
    return {
        "headline": (data.get("headline") or draft_headline).strip(),
        "implication": (data.get("implication") or draft_implication).strip(),
        "used_evidence_ids": used or [e["feedback_id"] for e in evidence],
        "synthesis_source": "groq_llm",
        "llm_model": client.model,
    }


def build_insight(
    *,
    insight_id: str,
    question_id: str,
    headline: str,
    supporting_themes: list[str],
    evidence: list[dict[str, Any]],
    implication: str,
    analysis: dict[str, Any],
    analyzable_count: int,
    theme_volume: int,
    use_llm: bool = True,
    question_text: str | None = None,
) -> dict[str, Any]:
    evidence_ids = [e["feedback_id"] for e in evidence]
    src_count = source_diversity(evidence)
    confidence = provisional_confidence(
        evidence_count=len(evidence_ids),
        theme_volume=theme_volume,
        source_count=src_count,
        analyzable_count=analyzable_count,
    )
    insufficient = len(evidence_ids) == 0 or theme_volume == 0
    synthesis_meta = {"synthesis_source": "template", "llm_model": None}

    if insufficient:
        headline = f"Insufficient evidence to answer {question_id} from current corpus"
        implication = (
            "Do not prioritize category-expansion actions for this question until more "
            "multi-source feedback is available; avoid inventing drivers of new-category trial."
        )
        confidence = min(confidence, 0.25)
    elif use_llm and evidence:
        try:
            refined = refine_with_groq(
                question=question_text or (analysis or {}).get("question") or question_id,
                question_id=question_id,
                supporting_themes=supporting_themes,
                evidence=evidence,
                draft_headline=headline,
                draft_implication=implication,
            )
            headline = refined["headline"]
            implication = refined["implication"]
            # Keep original evidence pack; optionally reorder by used ids
            used = refined.get("used_evidence_ids") or evidence_ids
            evidence_ids = used
            synthesis_meta = {
                "synthesis_source": refined.get("synthesis_source"),
                "llm_model": refined.get("llm_model"),
            }
        except Exception as exc:  # noqa: BLE001
            synthesis_meta = {"synthesis_source": "template_fallback", "llm_error": str(exc)}

    # Reorder evidence pack to match evidence_ids when LLM selected a subset
    by_id = {e["feedback_id"]: e for e in evidence}
    ordered_evidence = [by_id[i] for i in evidence_ids if i in by_id]
    if not ordered_evidence:
        ordered_evidence = evidence
        evidence_ids = [e["feedback_id"] for e in evidence]

    return {
        "insight_id": insight_id,
        "question_id": question_id,
        "headline": headline,
        "supporting_themes": supporting_themes,
        "evidence_ids": evidence_ids,
        "evidence_pack": [
            {
                "feedback_id": e["feedback_id"],
                "source": e.get("source"),
                "created_at": e.get("created_at"),
                "quote": e.get("text"),
                "matched_themes": e.get("matched_themes"),
            }
            for e in ordered_evidence
        ],
        "implication": implication,
        "confidence": confidence,
        "status": "draft",
        "insufficient_evidence": insufficient,
        "analysis": analysis,
        "source_diversity": src_count,
        **synthesis_meta,
    }


def theme_list_phrase(theme_ids: list[str], limit: int = 3) -> str:
    return ", ".join(theme_ids[:limit]) if theme_ids else "none"
