# Phase 0 project skeleton
# Later phases implement real adapters and analysis against these packages.

## Layout

```text
project_skeleton/
├── data/
│   ├── raw/
│   ├── cleaned/
│   ├── themes/
│   ├── insights/
│   └── vectors/
├── src/
│   ├── ingest/          # Phase 1 source adapters
│   ├── analysis/        # Phases 2–3 themeing & insights
│   ├── validation/      # Phase 4 gates
│   └── common/          # Shared schema, clients, config
├── dashboard/           # Phase 5 Streamlit app
└── docs/                # Phase-local notes (root docs/ remains source of truth)
```

Canonical schema and taxonomy live in `phase0/schema` and `phase0/taxonomy` until promoted.
