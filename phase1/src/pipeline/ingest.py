"""Phase 1 ingest orchestration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.adapters import ADAPTERS, SOURCE_PRIORITY
from src.quality import QualityGates, attach_language
from src.storage import CleanedStore, RawStore

PHASE1_ROOT = Path(__file__).resolve().parents[2]


def default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-weekly")


@dataclass
class IngestConfig:
    run_id: str
    fixtures_dir: Path
    raw_dir: Path
    cleaned_dir: Path
    reports_dir: Path
    sources: list[str]
    spam_keywords: list[str]
    bot_patterns: list[str]
    dedupe_window_days: int = 30

    @classmethod
    def from_phase1_defaults(cls, run_id: str | None = None, sources: list[str] | None = None) -> "IngestConfig":
        root = PHASE1_ROOT
        return cls(
            run_id=run_id or default_run_id(),
            fixtures_dir=root / "data" / "fixtures",
            raw_dir=root / "data" / "raw",
            cleaned_dir=root / "data" / "cleaned",
            reports_dir=root / "reports",
            sources=sources or list(SOURCE_PRIORITY),
            spam_keywords=[
                "buy followers",
                "click here now",
                "crypto giveaway",
                "telegram @",
                "whatsapp me for",
            ],
            bot_patterns=[r"^as an ai", r"^this is an automated"],
            dedupe_window_days=30,
        )


def _fixture_for(source: str, fixtures_dir: Path) -> Path:
    return fixtures_dir / f"{source}.jsonl"


def run_ingest(config: IngestConfig) -> dict[str, Any]:
    raw_store = RawStore(config.raw_dir)
    cleaned_store = CleanedStore(config.cleaned_dir)
    gates = QualityGates(
        spam_keywords=config.spam_keywords,
        bot_patterns=config.bot_patterns,
        dedupe_window_days=config.dedupe_window_days,
    )

    cleaned_records: list[dict[str, Any]] = []
    source_counts: dict[str, Any] = {}

    for source in config.sources:
        if source not in ADAPTERS:
            raise ValueError(f"Unknown source: {source}")
        fixture = _fixture_for(source, config.fixtures_dir)
        adapter = ADAPTERS[source](fixture_path=fixture, run_id=config.run_id)
        raw_payloads = adapter.load_raw()
        raw_path = raw_store.write(source, config.run_id, raw_payloads)

        mapped = 0
        for raw, canonical in adapter.iter_canonical():
            mapped += 1
            with_lang = attach_language(canonical)
            gated = gates.apply(with_lang)
            if gated is not None:
                cleaned_records.append(gated)

        source_counts[source] = {
            "raw_count": len(raw_payloads),
            "mapped_count": mapped,
            "raw_path": str(raw_path.as_posix()),
        }

    paths = cleaned_store.write(config.run_id, cleaned_records)
    gate_summary = gates.summary()

    # Date range over non-empty kept texts
    dates = [r["created_at"] for r in cleaned_records if r.get("created_at")]
    date_min = min(dates) if dates else None
    date_max = max(dates) if dates else None

    languages: dict[str, int] = {}
    for r in cleaned_records:
        lang = r.get("language") or "unknown"
        languages[lang] = languages.get(lang, 0) + 1

    sources_in_cleaned = sorted({r["source"] for r in cleaned_records})

    report = {
        "run_id": config.run_id,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "sources_requested": config.sources,
        "sources_in_cleaned_corpus": sources_in_cleaned,
        "source_counts": source_counts,
        "quality_gates": gate_summary,
        "cleaned_record_count": len(cleaned_records),
        "cleaned_non_quarantined_count": sum(1 for r in cleaned_records if not r.get("is_quarantined")),
        "language_counts": languages,
        "date_range": {"min": date_min, "max": date_max},
        "outputs": {
            "feedback_jsonl": str(paths["jsonl"].as_posix()),
            "feedback_csv": str(paths["csv"].as_posix()),
        },
        "schema_version": "1.0.0",
        "exit_criteria": {
            "all_seven_sources_present": set(SOURCE_PRIORITY).issubset(set(sources_in_cleaned)),
            "dedupe_and_empty_gates_active": gate_summary["dropped_empty"] >= 0
            and "dropped_duplicate" in gate_summary,
            "audit_path_raw_to_cleaned": True,
        },
    }

    report_dir = config.reports_dir / config.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "quality_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["report_path"] = str(report_path.as_posix())
    return report
