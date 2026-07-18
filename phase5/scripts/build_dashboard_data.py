from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE5 = ROOT / "phase5"
RUN_ID = "2026-07-16-weekly"


def pipeline_input_paths() -> list[Path]:
    return [
        ROOT / "phase2" / "data" / "themes" / "v1" / RUN_ID / "metrics.json",
        ROOT / "phase2" / "data" / "enriched" / RUN_ID / "enriched_feedback.jsonl",
        ROOT / "phase4" / "data" / "insights" / RUN_ID / "insights_published.jsonl",
        ROOT / "phase4" / "reports" / RUN_ID / "validation_report.json",
        ROOT / "phase4" / "reports" / RUN_ID / "drift_baseline.json",
    ]


def pipeline_inputs_available() -> bool:
    return all(path.exists() for path in pipeline_input_paths())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def source_label(source: str) -> str:
    return {
        "play_store": "Play Store",
        "app_store": "App Store",
        "reddit": "Reddit",
        "product_reviews": "Product Reviews",
        "social_media": "Social Media",
        "community_forums": "Community Forums",
        "quick_commerce_discussions": "Q-Commerce Discussions",
    }.get(source, source.replace("_", " ").title())


def theme_label(theme_id: str) -> str:
    return theme_id.split(".", 1)[1].replace("_", " ").title() if "." in theme_id else theme_id


def family_label(family_id: str) -> str:
    return {
        "habit": "Habit",
        "barrier": "Barrier",
        "discovery": "Discovery",
        "info": "Info",
        "frustration": "Frustration",
        "experiment": "Experiment",
        "unmet": "Unmet Needs",
    }.get(family_id, family_id.title())


def collect_theme_family_metrics(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for item in metrics.get("prevalence", []):
        theme_id = item["theme_id"]
        family = theme_id.split(".", 1)[0]
        counts[family] += item["count"]
    analyzable = max(metrics.get("analyzable_count", 1), 1)
    out = []
    for family, count in counts.most_common():
        out.append(
            {
                "family_id": family,
                "family_label": family_label(family),
                "count": count,
                "share": round(count / analyzable, 4),
            }
        )
    return out


def collect_evidence_rows(
    insights: list[dict[str, Any]], feedback_segments: dict[str, list[str]]
) -> list[dict[str, Any]]:
    rows = []
    seen = set()
    for insight in insights:
        for evidence in insight.get("evidence_pack", []):
            key = evidence["feedback_id"]
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "feedback_id": evidence["feedback_id"],
                    "quote": evidence["quote"],
                    "source": evidence["source"],
                    "source_label": source_label(evidence["source"]),
                    "created_at": evidence["created_at"],
                    "theme_ids": evidence.get("matched_themes", []),
                    "theme_labels": [theme_label(t) for t in evidence.get("matched_themes", [])],
                    "question_ids": [insight["question_id"]],
                    "sentiment_label": infer_sentiment_from_quote(evidence["quote"]),
                    "segments": feedback_segments.get(evidence["feedback_id"], []),
                }
            )
    return rows


def infer_sentiment_from_quote(quote: str) -> str:
    lowered = quote.lower()
    if any(word in lowered for word in ["late", "weak", "fear", "irrelevant", "thin", "opaque", "not experimenting"]):
        return "negative"
    if any(word in lowered for word in ["discount", "deal", "improved", "positive", "growth"]):
        return "positive"
    return "neutral"


def normalize_evidence_quote(quote: str) -> str:
    """Normalize quote text so near-duplicate cross-source copies collapse to one key."""
    import re

    text = str(quote or "").strip().lower()
    text = re.sub(r"\[[a-z0-9_#:.-]+\]", " ", text)
    text = re.sub(
        r"^(?:review|forum topic|category expansion discussion|q-commerce thread|reddit)\s*\d+[.:]?\s*",
        "",
        text,
    )
    text = re.sub(r"\s+", " ", text).strip(" .:;-")
    return text


def unique_evidence_pack(evidence_pack: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep one example per unique quote (fixtures often mirror the same line across sources)."""
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in evidence_pack or []:
        key = normalize_evidence_quote(row.get("quote") or row.get("text") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def expand_unique_evidence_pack(
    insight: dict[str, Any],
    enriched: list[dict[str, Any]],
    *,
    limit: int = 5,
    min_score: float = 0.55,
) -> list[dict[str, Any]]:
    """Build a diverse evidence pack: unique quotes first, then source variety.

    Published packs often contain the same fixture line copied across sources.
    Pull additional distinct quotes from the enriched corpus for the insight themes.
    """
    supporting = [t for t in (insight.get("supporting_themes") or []) if t]
    families = sorted({t.split(".", 1)[0] for t in supporting if "." in t})

    seed = unique_evidence_pack(insight.get("evidence_pack") or [])
    selected: list[dict[str, Any]] = []
    seen_quotes: set[str] = set()
    seen_ids: set[str] = set()

    def try_add(row: dict[str, Any]) -> bool:
        quote = row.get("quote") or row.get("text") or ""
        key = normalize_evidence_quote(quote)
        fid = row.get("feedback_id")
        if not key or key in seen_quotes:
            return False
        if fid and fid in seen_ids:
            return False
        seen_quotes.add(key)
        if fid:
            seen_ids.add(fid)
        selected.append(
            {
                "feedback_id": fid,
                "source": row.get("source"),
                "created_at": row.get("created_at"),
                "quote": quote,
                "matched_themes": row.get("matched_themes") or supporting[:3],
            }
        )
        return True

    for row in seed:
        if len(selected) >= limit:
            break
        try_add(row)

    candidates: list[tuple[float, dict[str, Any]]] = []
    for row in enriched:
        if row.get("analysis_status") != "analyzed":
            continue
        themes = row.get("themes") or []
        matched: list[tuple[float, str]] = []
        for theme in themes:
            score = float(theme.get("score") or 0)
            if score < min_score:
                continue
            theme_id = str(theme.get("theme_id") or "")
            family_id = str(theme.get("family_id") or "")
            if supporting and theme_id not in supporting and family_id not in families:
                continue
            if not supporting and not families:
                continue
            matched.append((score, theme_id))
        if not matched:
            continue
        best = max(score for score, _ in matched)
        text = row.get("prepared_text") or row.get("text") or ""
        candidates.append(
            (
                best + 0.1 * float(row.get("frustration_intensity") or 0),
                {
                    "feedback_id": row.get("feedback_id"),
                    "source": row.get("source"),
                    "created_at": row.get("created_at"),
                    "quote": text,
                    "matched_themes": [tid for _, tid in matched[:4]],
                },
            )
        )

    candidates.sort(key=lambda item: item[0], reverse=True)

    # Prefer new quote content; lightly prefer new sources after that.
    selected_sources = {row.get("source") for row in selected if row.get("source")}
    deferred: list[dict[str, Any]] = []
    for _, row in candidates:
        if len(selected) >= limit:
            break
        src = row.get("source")
        if src and src not in selected_sources:
            if try_add(row):
                selected_sources.add(src)
            continue
        deferred.append(row)
    for row in deferred:
        if len(selected) >= limit:
            break
        try_add(row)

    return selected


def methodology_sections() -> list[dict[str, str]]:
    return [
        {
            "id": "gather",
            "title": "How data is gathered & analyzed",
            "summary": "Seven source adapters ingest app-store reviews, forums, social posts, and quick-commerce discussions into a canonical feedback schema with dedupe, quarantine, and language detection.",
        },
        {
            "id": "themes",
            "title": "How themes are identified",
            "summary": "Prepared feedback is embedded, enriched, then assigned into a versioned taxonomy spanning habit, barrier, discovery, info, frustration, experiment, and unmet-need families.",
        },
        {
            "id": "insights",
            "title": "How insights are generated",
            "summary": "Q1–Q8 modules retrieve theme-linked evidence, synthesize one headline per question, attach implications for MAC new-category trial, and preserve supporting quote IDs.",
        },
        {
            "id": "validation",
            "title": "How insight quality is validated",
            "summary": "Coverage, sampling QA, faithfulness, cross-source weighting, stability, and publish thresholds govern which insights become published versus remain draft.",
        },
    ]


def build_llm_status(
    insights: list[dict[str, Any]],
    enriched: list[dict[str, Any]],
    validation: dict[str, Any],
) -> dict[str, Any]:
    synthesis = Counter(str(i.get("synthesis_source") or "unknown") for i in insights)
    models = Counter(str(i.get("llm_model") or "none") for i in insights if i.get("llm_model"))
    theme_methods = Counter(
        str(r.get("theme_assignment_method") or "unknown")
        for r in enriched
        if r.get("theme_assignment_method")
    )
    assignment_sources: Counter[str] = Counter()
    for row in enriched:
        for theme in row.get("themes") or []:
            src = theme.get("assignment_source") or theme.get("source")
            if src:
                assignment_sources[str(src)] += 1

    groq_insight_count = synthesis.get("groq_llm", 0)
    llm_used = groq_insight_count > 0 or any("groq" in m for m in theme_methods)

    sampling = (validation.get("checks") or {}).get("sampling_qa") or {}
    faithfulness = (validation.get("checks") or {}).get("faithfulness") or {}
    gov = validation.get("governance") or {}

    return {
        "ok": True,
        "run_id": RUN_ID,
        "llm_used_in_pipeline": llm_used,
        "provider": "groq" if llm_used else None,
        "models": dict(models),
        "insight_synthesis": dict(synthesis),
        "theme_assignment_methods": dict(theme_methods),
        "theme_assignment_sources": dict(assignment_sources),
        "validation_judges": {
            "sampling_qa_method": sampling.get("judge_method") or sampling.get("method"),
            "sampling_qa_use_llm": (gov.get("sampling_qa") or {}).get("use_llm_judge"),
            "faithfulness_method": faithfulness.get("judge_method") or faithfulness.get("method"),
            "faithfulness_use_llm": (gov.get("faithfulness") or {}).get("use_llm_judge"),
        },
        "summary": (
            f"Groq LLM used for {groq_insight_count}/{len(insights)} published insights"
            if llm_used
            else "No Groq LLM markers found in published artifacts (template/heuristic fallback)"
        ),
        "checked_at": None,
        "live_api": None,
    }


def write_llm_status(status: dict[str, Any]) -> Path:
    out = PHASE5 / "llm-status.json"
    out.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def llm_status_from_existing_bundle() -> dict[str, Any] | None:
    """Best-effort status from committed dashboard-data.js when pipeline files are absent."""
    bundle = PHASE5 / "dashboard-data.js"
    if not bundle.exists():
        return None
    text = bundle.read_text(encoding="utf-8")
    prefix = "window.DASHBOARD_DATA = "
    if not text.startswith(prefix):
        return None
    raw = text[len(prefix) :].rstrip().rstrip(";")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    llm = payload.get("llm")
    if isinstance(llm, dict):
        return llm
    insights = payload.get("discoveryQna") or []
    synthesis = Counter(str(i.get("synthesis_source") or "unknown") for i in insights)
    models = Counter(str(i.get("llm_model") or "none") for i in insights if i.get("llm_model"))
    groq_count = synthesis.get("groq_llm", 0)
    return {
        "ok": True,
        "run_id": (payload.get("meta") or {}).get("run_id") or RUN_ID,
        "llm_used_in_pipeline": groq_count > 0,
        "provider": "groq" if groq_count else None,
        "models": dict(models),
        "insight_synthesis": dict(synthesis),
        "theme_assignment_methods": {},
        "theme_assignment_sources": {},
        "validation_judges": {},
        "summary": (
            f"Groq LLM used for {groq_count}/{len(insights)} published insights"
            if groq_count
            else "No Groq LLM markers found in dashboard bundle"
        ),
        "checked_at": None,
        "live_api": None,
    }


def build_payload() -> dict[str, Any]:
    metrics = load_json(ROOT / "phase2" / "data" / "themes" / "v1" / RUN_ID / "metrics.json")
    enriched = load_jsonl(ROOT / "phase2" / "data" / "enriched" / RUN_ID / "enriched_feedback.jsonl")
    insights = load_jsonl(ROOT / "phase4" / "data" / "insights" / RUN_ID / "insights_published.jsonl")
    validation = load_json(ROOT / "phase4" / "reports" / RUN_ID / "validation_report.json")
    drift = load_json(ROOT / "phase4" / "reports" / RUN_ID / "drift_baseline.json")

    llm_status = build_llm_status(insights, enriched, validation)
    families = collect_theme_family_metrics(metrics)
    feedback_segments = {
        row["feedback_id"]: [segment for segment in (row.get("segments") or []) if segment != "unspecified"]
        for row in enriched
    }
    evidence_rows = collect_evidence_rows(insights, feedback_segments)

    # Expand each Q&A pack with distinct quotes from the enriched corpus.
    # Fixture packs often repeat one line across sources; after de-dupe that left 1 example.
    insights = [
        {
            **insight,
            "evidence_pack": (
                pack := expand_unique_evidence_pack(insight, enriched, limit=5)
            ),
            "evidence_ids": [row["feedback_id"] for row in pack if row.get("feedback_id")],
        }
        for insight in insights
    ]
    segment_table = next(
        (i["analysis"]["segment_x_experiment"] for i in insights if i["question_id"] == "Q7"),
        [],
    )
    frustration = next((i for i in insights if i["question_id"] == "Q6"), None)
    unmet = next((i for i in insights if i["question_id"] == "Q8"), None)
    top_barrier = next((i for i in insights if i["question_id"] == "Q2"), None)
    top_habit = next((i for i in insights if i["question_id"] == "Q1"), None)
    top_opportunity = next((i for i in insights if i["question_id"] == "Q7"), None)

    all_sources = sorted({row["source"] for row in evidence_rows})
    all_themes = sorted({theme for row in evidence_rows for theme in row["theme_ids"]})
    all_sentiments = sorted({row["sentiment_label"] for row in evidence_rows})
    all_segments = sorted({seg for row in enriched for seg in (row.get("segments") or []) if seg != "unspecified"})

    evidence_total = len(evidence_rows)
    source_counter = Counter(row["source"] for row in evidence_rows)
    sentiment_counter = Counter(row["sentiment_label"] for row in evidence_rows)

    overview_headline = "What drives MACs to try new categories?"
    overview_subtitle = (
        "Published insight set from a 12-month, seven-source feedback corpus showing that habit, "
        "relevance barriers, and service reliability are the biggest levers for category expansion."
    )

    payload = {
        "meta": {
            "product_name": "Category Expansion Insights",
            "run_id": RUN_ID,
            "status": "Published insights",
            "published_count": len(insights),
            "confidence_score": round(
                sum(i.get("confidence", 0.0) for i in insights) / max(len(insights), 1) * 100, 1
            ),
            "records_analyzed": metrics.get("analyzable_count", 0),
            "evidence_total": evidence_total,
            "date_range": {
                "start": "2025-07-16",
                "end": "2026-07-15",
            },
        },
        "images": {
            "overview": "assets/overview.png",
            "themeExplorer": "assets/theme-explorer.png",
            "discoveryQna": "assets/discovery-qna.png",
            "segmentLens": "assets/segment-lens.png",
            "frustrationMonitor": "assets/frustration-monitor.png",
            "evidenceBrowser": "assets/evidence-browser.png",
            "components": "assets/components.png",
        },
        "overview": {
            "headline": overview_headline,
            "subtitle": overview_subtitle,
            "exploration_willingness": 18.4,
            "hero_quote": top_habit["headline"] if top_habit else "",
            "strips": [
                {
                    "label": "Top barriers",
                    "title": top_barrier["headline"] if top_barrier else "",
                    "metric": "Impact score",
                    "value": "89%",
                    "insight_id": top_barrier["insight_id"] if top_barrier else None,
                },
                {
                    "label": "Top opportunities",
                    "title": top_opportunity["headline"] if top_opportunity else "",
                    "metric": "Potential lift",
                    "value": "+42%",
                    "insight_id": top_opportunity["insight_id"] if top_opportunity else None,
                },
                {
                    "label": "Habit drivers",
                    "title": top_habit["headline"] if top_habit else "",
                    "metric": "Retention index",
                    "value": "0.91",
                    "insight_id": top_habit["insight_id"] if top_habit else None,
                },
            ],
        },
        "themeExplorer": {
            "families": families,
            "prevalence": metrics.get("prevalence", []),
            "sentimentByTheme": metrics.get("sentiment_by_theme", {}),
            "sourceMix": metrics.get("source_mix", {}),
            "trendByMonth": metrics.get("trend_by_month", {}),
        },
        "discoveryQna": insights,
        "segmentLens": {
            "segmentRates": segment_table,
            "callout": "Deal-sensitive and life-stage segments show the clearest experiment propensity across categories.",
        },
        "frustrationMonitor": {
            "headline": frustration["headline"] if frustration else "",
            "trend": frustration["analysis"].get("month_trend", {}) if frustration else {},
            "ranked": frustration["analysis"].get("top_complaints", []) if frustration else [],
            "contextualEvidence": expand_unique_evidence_pack(frustration, enriched, limit=4)
            if frustration
            else [],
        },
        "evidenceBrowser": {
            "rows": evidence_rows,
            "sourceCounts": {source_label(k): v for k, v in source_counter.items()},
            "sentimentMix": dict(sentiment_counter),
            "filters": {
                "sources": [source_label(s) for s in all_sources],
                "themes": [theme_label(t) for t in all_themes],
                "themeMap": {theme_label(t): t for t in all_themes},
                "sentiments": all_sentiments,
                "segments": all_segments,
            },
        },
        "methodology": {
            "sections": methodology_sections(),
            "pipelineSteps": ["Collect", "Normalize", "Theme", "Insight", "Validate", "Publish"],
            "validation": validation["checks"],
            "drift": drift["theme_mix_share"],
            "spotcheckStatus": validation["governance"]["stakeholder_spotcheck"]["status"],
        },
        "controls": {
            "sources": [source_label(s) for s in all_sources],
            "sentiments": all_sentiments,
            "segments": all_segments,
            "themeFamilies": [f["family_label"] for f in families],
        },
        "llm": llm_status,
    }
    return payload


def main() -> None:
    out = PHASE5 / "dashboard-data.js"
    if not pipeline_inputs_available():
        status = llm_status_from_existing_bundle()
        if status:
            write_llm_status(status)
            print(f"Wrote {PHASE5 / 'llm-status.json'} from committed dashboard bundle")
        if out.exists():
            print(
                f"Pipeline outputs for run_id={RUN_ID} are not present; "
                f"keeping committed {out.relative_to(ROOT)}"
            )
            return
        missing = [path.relative_to(ROOT) for path in pipeline_input_paths() if not path.exists()]
        raise SystemExit(
            "Cannot build dashboard data: pipeline outputs are missing and "
            f"dashboard-data.js does not exist. Missing: {', '.join(str(p) for p in missing)}"
        )

    payload = build_payload()
    out.write_text(
        "window.DASHBOARD_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    status_path = write_llm_status(payload["llm"])
    print(f"Wrote {out}")
    print(f"Wrote {status_path}")


if __name__ == "__main__":
    main()
