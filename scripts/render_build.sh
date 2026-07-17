#!/usr/bin/env bash
# Render-safe build: never fail if pipeline outputs are absent.
set -euo pipefail

echo "Render build: preparing dashboard"

if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
fi

# Prefer committed dashboard-data.js; rebuild only when inputs exist.
python phase5/scripts/build_dashboard_data.py || {
  echo "Dashboard data rebuild skipped or failed; checking committed bundle..."
  test -f phase5/dashboard-data.js
}

echo "Render build OK"
