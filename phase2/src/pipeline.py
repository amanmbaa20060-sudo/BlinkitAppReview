"""Phase 2 end-to-end pipeline."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .embeddings import FileVectorIndex, HashingEmbeddingClient
from .enrich import enrich_text
from .io_utils import load_jsonl, write_json, write_jsonl
from .llm_themeing import base_text, classify_themes_with_groq, merge_llm_assignments
from .metrics import compute_theme_metrics
from .prepare import prepare_record
from .segments import tag_segments
from .sentiment import score_sentiment
from .themeing import (
    assign_themes_for_text,
    consolidate_taxonomy_v1,
    discover_residual_clusters,
    flatten_themes,
    load_taxonomy,
)

PHASE2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PHASE2_ROOT.parent


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_phase2(run_id: str = "2026-07-16-weekly") -> dict[str, Any]:
    cleaned_path = REPO_ROOT / "phase1" / "data" / "cleaned" / run_id / "feedback.jsonl"
    taxonomy_v0_path = REPO_ROOT / "phase0" / "taxonomy" / "theme_taxonomy_v0.json"
    if not cleaned_path.exists():
        raise FileNotFoundError(f"Phase 1 cleaned corpus not found: {cleaned_path}")
    if not taxonomy_v0_path.exists():
        raise FileNotFoundError(f"Taxonomy v0 not found: {taxonomy_v0_path}")

    records = load_jsonl(cleaned_path)
    taxonomy_v0 = load_taxonomy(taxonomy_v0_path)
    theme_defs = flatten_themes(taxonomy_v0)
    embedder = HashingEmbeddingClient(dimensions=256)
    theme_vectors = {
        t["theme_id"]: embedder.embed_one(
            f"{t['name']}. {t.get('inclusion', '')}. {' '.join(t.get('inclusion', '').split())}"
        )
        for t in theme_defs
    }
    # Strengthen theme vectors with keyword lists
    from .themeing import THEME_KEYWORDS

    for tid, kws in THEME_KEYWORDS.items():
        if tid in theme_vectors:
            theme_vectors[tid] = embedder.embed_one(
                " ".join([next(t["name"] for t in theme_defs if t["theme_id"] == tid)] + kws)
            )

    index = FileVectorIndex()
    prepared_rows: list[dict[str, Any]] = []
    enriched_rows: list[dict[str, Any]] = []
    membership: list[dict[str, Any]] = []
    skip_counts: dict[str, int] = {"quarantined": 0, "non_english": 0, "empty_prepared": 0}
    residuals: list[dict[str, Any]] = []
    embedding_status: list[dict[str, Any]] = []

    for record in records:
        prepared = prepare_record(record)
        prepared_rows.append({
            "feedback_id": prepared["feedback_id"],
            "source": prepared["source"],
            "prepared_text": prepared["prepared_text"],
            "chunk_count": prepared["chunk_count"],
            "chunks": prepared["chunks"],
        })

        # Embedding decision
        if prepared.get("is_quarantined"):
            reason = "quarantined"
            skip_counts["quarantined"] += 1
            embedding_status.append({"feedback_id": prepared["feedback_id"], "status": "skipped", "reason": reason})
            enriched_rows.append({
                **{k: prepared.get(k) for k in (
                    "feedback_id", "source", "created_at", "text", "rating", "language",
                    "run_id", "is_quarantined", "url_or_ref", "author_handle",
                )},
                "prepared_text": prepared["prepared_text"],
                "analysis_status": "skipped",
                "skip_reason": reason,
                "themes": [],
                "embedding": None,
            })
            continue

        lang = (prepared.get("language") or "").lower()
        if lang and lang != "en" and not lang.startswith("en"):
            reason = f"non_english:{lang}"
            skip_counts["non_english"] += 1
            # Still embed for auditability but exclude from themeing per Phase 0
            vec = embedder.embed_one(prepared["prepared_text"] or "")
            index.upsert([prepared["feedback_id"]], [vec], [{"source": prepared["source"], "language": lang}])
            embedding_status.append({"feedback_id": prepared["feedback_id"], "status": "embedded_excluded_from_themes", "reason": reason})
            enriched_rows.append({
                **{k: prepared.get(k) for k in (
                    "feedback_id", "source", "created_at", "text", "rating", "language",
                    "run_id", "is_quarantined", "url_or_ref", "author_handle",
                )},
                "prepared_text": prepared["prepared_text"],
                "analysis_status": "embedded_excluded_from_themes",
                "skip_reason": reason,
                "themes": [],
                "embedding_dim": len(vec),
            })
            continue

        text = prepared.get("prepared_text") or ""
        if not text.strip():
            skip_counts["empty_prepared"] += 1
            embedding_status.append({"feedback_id": prepared["feedback_id"], "status": "skipped", "reason": "empty_prepared"})
            enriched_rows.append({
                "feedback_id": prepared["feedback_id"],
                "source": prepared["source"],
                "analysis_status": "skipped",
                "skip_reason": "empty_prepared",
                "themes": [],
            })
            continue

        # Embed primary unit (joined chunks)
        unit_text = " ".join(prepared["chunks"]) if prepared["chunks"] else text
        vec = embedder.embed_one(unit_text)
        index.upsert(
            [prepared["feedback_id"]],
            [vec],
            [{"source": prepared["source"], "created_at": prepared.get("created_at"), "language": prepared.get("language")}],
        )
        embedding_status.append({"feedback_id": prepared["feedback_id"], "status": "embedded", "reason": None})

        enrichment = enrich_text(unit_text, prepared.get("engagement") if isinstance(prepared.get("engagement"), dict) else None)
        assignments = assign_themes_for_text(unit_text, theme_defs, theme_vectors, embedder)
        for a in assignments:
            a.setdefault("assignment_source", "keyword_similarity")
        if not assignments:
            assignments = [{
                "theme_id": "theme.other",
                "family_id": "other",
                "score": 0.0,
                "keyword_hits": [],
                "similarity": 0.0,
                "assignment_source": "keyword_similarity",
            }]
            residuals.append({"feedback_id": prepared["feedback_id"], "prepared_text": unit_text})

        sent = score_sentiment(unit_text, prepared.get("rating") if isinstance(prepared.get("rating"), (int, float)) else None)
        segs = tag_segments(unit_text, [a for a in assignments if a["theme_id"] != "theme.other"])

        enriched_rows.append({
            "feedback_id": prepared["feedback_id"],
            "source": prepared["source"],
            "created_at": prepared.get("created_at"),
            "text": prepared.get("text"),
            "prepared_text": unit_text,
            "rating": prepared.get("rating"),
            "language": prepared.get("language"),
            "run_id": prepared.get("run_id"),
            "is_quarantined": prepared.get("is_quarantined", False),
            "url_or_ref": prepared.get("url_or_ref"),
            "author_handle": prepared.get("author_handle"),
            "analysis_status": "analyzed",
            "themes": assignments,
            "primary_theme_id": assignments[0]["theme_id"],
            **enrichment,
            **sent,
            **segs,
            "embedding_dim": len(vec),
            "embedding_model": embedder.model_id,
        })

    # --- Groq LLM theme refinement (unique base texts) ---
    llm_stats: dict[str, Any] = {"enabled": False, "unique_texts": 0, "error": None}
    try:
        analyzed_for_llm = [r for r in enriched_rows if r.get("analysis_status") == "analyzed"]
        texts = [r["prepared_text"] for r in analyzed_for_llm]
        llm_map = classify_themes_with_groq(texts, theme_defs)
        llm_stats = {
            "enabled": True,
            "provider": "groq",
            "unique_texts_classified": len(llm_map),
            "error": None,
        }
        for row in analyzed_for_llm:
            b = base_text(row["prepared_text"])
            llm_assign = llm_map.get(b)
            merged = merge_llm_assignments(row.get("themes") or [], llm_assign)
            if not merged:
                merged = [{
                    "theme_id": "theme.other",
                    "family_id": "other",
                    "score": 0.0,
                    "keyword_hits": [],
                    "similarity": 0.0,
                    "assignment_source": "none",
                }]
                residuals.append({"feedback_id": row["feedback_id"], "prepared_text": row["prepared_text"]})
            row["themes"] = merged
            row["primary_theme_id"] = merged[0]["theme_id"]
            row["theme_assignment_method"] = "groq_llm+keyword_similarity"
            segs = tag_segments(row["prepared_text"], [a for a in merged if a["theme_id"] != "theme.other"])
            row["segments"] = segs["segments"]
            row["segment_confidence"] = segs["segment_confidence"]
    except Exception as exc:  # noqa: BLE001
        llm_stats = {"enabled": False, "error": str(exc)}
        print(f"WARNING: Groq theme classification failed, keeping keyword themes: {exc}")

    # Rebuild membership after possible LLM merge
    membership = []
    for row in enriched_rows:
        if row.get("analysis_status") != "analyzed":
            continue
        for a in row.get("themes") or []:
            if a.get("theme_id") == "theme.other":
                continue
            membership.append({
                "feedback_id": row["feedback_id"],
                "theme_id": a["theme_id"],
                "family_id": a.get("family_id"),
                "score": a.get("score"),
                "source": row.get("source"),
                "created_at": row.get("created_at"),
                "assignment_source": a.get("assignment_source"),
            })

    discovered = discover_residual_clusters(residuals, embedder, min_support=8)
    assignment_method = (
        "groq_llm_plus_keyword_hits_plus_definition_hash_embedding_similarity"
        if llm_stats.get("enabled")
        else "keyword_hits_plus_definition_hash_embedding_similarity"
    )
    taxonomy_v1 = consolidate_taxonomy_v1(
        taxonomy_v0,
        discovered,
        assignment_method=assignment_method,
    )

    metrics = compute_theme_metrics(enriched_rows)
    analyzed = [r for r in enriched_rows if r.get("analysis_status") == "analyzed"]
    with_theme = [
        r for r in analyzed
        if any(t.get("theme_id") != "theme.other" for t in r.get("themes", []))
    ]
    coverage = (len(with_theme) / len(analyzed)) if analyzed else 0.0

    # Persist outputs
    prepared_dir = PHASE2_ROOT / "data" / "prepared" / run_id
    emb_dir = PHASE2_ROOT / "data" / "embeddings" / run_id
    enriched_dir = PHASE2_ROOT / "data" / "enriched" / run_id
    theme_dir = PHASE2_ROOT / "data" / "themes" / "v1" / run_id
    tax_dir = PHASE2_ROOT / "taxonomy"
    reports_dir = PHASE2_ROOT / "reports" / run_id
    samples_dir = PHASE2_ROOT / "samples"

    write_jsonl(prepared_dir / "prepared.jsonl", prepared_rows)
    index.save(emb_dir / "vectors.jsonl")
    write_json(emb_dir / "embedding_manifest.json", {
        "model": embedder.model_id,
        "dimensions": embedder.dimensions,
        "count": len(index.rows),
        "provider": "local_hashing",
    })
    write_jsonl(emb_dir / "embedding_status.jsonl", embedding_status)
    write_jsonl(enriched_dir / "enriched_feedback.jsonl", enriched_rows)

    write_json(tax_dir / "theme_taxonomy_v1.json", taxonomy_v1)
    write_jsonl(theme_dir / "membership.jsonl", membership)
    write_json(theme_dir / "theme_definitions.json", {
        "taxonomy_version": "v1",
        "themes": theme_defs + [{
            "theme_id": "theme.other",
            "name": "Other / unmatched",
            "family_id": "other",
            "family_name": "Other",
            "inclusion": "No core theme keyword/similarity match",
            "exclusion": "Any matched core theme",
        }],
    })

    # Sample for Phase 4 QA
    sample_pool = [r for r in analyzed if r.get("themes")]
    random.Random(42).shuffle(sample_pool)
    sample = []
    for r in sample_pool[:40]:
        sample.append({
            "feedback_id": r["feedback_id"],
            "source": r["source"],
            "created_at": r.get("created_at"),
            "text": r.get("prepared_text"),
            "themes": r.get("themes"),
            "sentiment_label": r.get("sentiment_label"),
            "segments": r.get("segments"),
        })
    write_json(samples_dir / "theme_assignments_sample.json", {
        "purpose": "Phase 4 QA sample of theme assignments",
        "sample_size": len(sample),
        "records": sample,
    })

    report = {
        "run_id": run_id,
        "generated_at": utc_now(),
        "input_cleaned_count": len(records),
        "prepared_count": len(prepared_rows),
        "embedded_count": sum(1 for e in embedding_status if e["status"] in {"embedded", "embedded_excluded_from_themes"}),
        "skipped_counts": skip_counts,
        "analyzed_count": len(analyzed),
        "theme_coverage_pct": round(coverage * 100, 2),
        "records_with_non_other_theme": len(with_theme),
        "taxonomy_version": "v1",
        "embedding_model": embedder.model_id,
        "llm_themeing": llm_stats,
        "discovered_cluster_count": len(discovered),
        "exit_criteria": {
            "all_records_embedded_or_skipped_with_reason": len(embedding_status) == len(records),
            "theme_coverage_measured": True,
            "taxonomy_definitions_written": True,
            "sample_assignments_reviewable": True,
        },
        "outputs": {
            "prepared": str((prepared_dir / "prepared.jsonl").as_posix()),
            "embeddings": str((emb_dir / "vectors.jsonl").as_posix()),
            "enriched": str((enriched_dir / "enriched_feedback.jsonl").as_posix()),
            "theme_store": str(theme_dir.as_posix()),
            "taxonomy_v1": str((tax_dir / "theme_taxonomy_v1.json").as_posix()),
            "sample": str((samples_dir / "theme_assignments_sample.json").as_posix()),
        },
    }
    write_json(reports_dir / "phase2_report.json", report)
    write_json(theme_dir / "metrics.json", metrics)
    return report
