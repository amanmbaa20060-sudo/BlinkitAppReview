"""No-op end-to-end pipeline for Phase 0 exit criteria."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running as `python pipeline/smoke_test.py` from phase0/
PHASE0_ROOT = Path(__file__).resolve().parents[1]
SKELETON_SRC = PHASE0_ROOT / "project_skeleton" / "src"
sys.path.insert(0, str(SKELETON_SRC))

from common.embeddings import NoOpEmbeddingClient  # noqa: E402
from common.llm import NoOpLLMClient  # noqa: E402
from common.paths import PIPELINE_STEPS, SCHEMA_PATH, TAXONOMY_PATH  # noqa: E402
from common.schema import SCHEMA_VERSION, load_json_schema, validate_record  # noqa: E402
from common.vector_index import InMemoryVectorIndex  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sample_record(run_id: str) -> dict:
    return {
        "feedback_id": "smoke:sample-001",
        "source": "play_store",
        "created_at": "2026-06-01T10:00:00Z",
        "text": "I always reorder the same groceries and rarely try new categories.",
        "rating": 4,
        "language": "en",
        "url_or_ref": None,
        "author_handle": None,
        "engagement": None,
        "thread_id": None,
        "parent_id": None,
        "run_id": run_id,
        "ingested_at": _utc_now(),
        "is_quarantined": False,
        "quarantine_reason": None,
        "raw_payload": {"note": "phase0-smoke-test"},
    }


def run_smoke_test() -> int:
    run_id = f"phase0-smoke-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    results: list[tuple[str, str]] = []

    # --- Preflight: frozen artifacts exist ---
    if not SCHEMA_PATH.exists():
        print(f"FAIL: schema missing at {SCHEMA_PATH}")
        return 1
    if not TAXONOMY_PATH.exists():
        print(f"FAIL: taxonomy missing at {TAXONOMY_PATH}")
        return 1

    schema = load_json_schema()
    taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    print(f"Schema version (docs): {SCHEMA_VERSION}; JSON title: {schema.get('title')}")
    print(f"Taxonomy version: {taxonomy.get('taxonomy_version')}; families: {len(taxonomy.get('families', []))}")

    embeddings = NoOpEmbeddingClient()
    llm = NoOpLLMClient()
    index = InMemoryVectorIndex()
    record = _sample_record(run_id)

    # --- Pipeline steps (no-op but wired) ---
    for step in PIPELINE_STEPS:
        if step == "collect":
            collected = [record]
            results.append((step, f"ok ({len(collected)} raw)"))
        elif step == "normalize":
            errors = validate_record(record)
            if errors:
                results.append((step, f"FAIL: {errors}"))
                _print_results(results)
                return 1
            results.append((step, "ok (canonical valid)"))
        elif step == "prepare":
            cleaned_text = " ".join(record["text"].split())
            record = {**record, "text": cleaned_text}
            results.append((step, "ok"))
        elif step == "represent":
            vectors = embeddings.embed([record["text"]])
            index.upsert([record["feedback_id"]], vectors, [{"source": record["source"]}])
            results.append((step, f"ok (dim={len(vectors[0])})"))
        elif step == "theme":
            # Seed assignment placeholder — real themeing in Phase 2
            themes = ["habit.autopilot_reorder"]
            results.append((step, f"ok (noop themes={themes})"))
        elif step == "enrich":
            sentiment = "neutral"
            segment = "habitual_reorderer"
            results.append((step, f"ok (sentiment={sentiment}, segment={segment})"))
        elif step == "answer":
            questions = [f"Q{i}" for i in range(1, 9)]
            results.append((step, f"ok (noop modules={len(questions)})"))
        elif step == "synthesize":
            draft = llm.complete("Synthesize insight from evidence (noop).")
            results.append((step, f"ok ({draft[:40]}...)"))
        elif step == "validate":
            published = False  # publish gate not passed in smoke - draft only
            results.append((step, f"ok (draft_only={not published})"))
        elif step == "publish":
            results.append((step, "ok (noop - nothing published)"))
        else:
            results.append((step, "FAIL: unknown step"))
            _print_results(results)
            return 1

    _print_results(results)
    failed = [s for s, msg in results if msg.startswith("FAIL")]
    if failed:
        print("\nPhase 0 smoke test FAILED")
        return 1

    print("\nPhase 0 smoke test PASSED")
    print("Exit criteria: empty pipeline ran end-to-end as a no-op.")
    return 0


def _print_results(results: list[tuple[str, str]]) -> None:
    print("\nPipeline steps:")
    for step, msg in results:
        print(f"  [{step:10}] {msg}")


if __name__ == "__main__":
    raise SystemExit(run_smoke_test())
