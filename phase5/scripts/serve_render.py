"""Serve the Phase 5 dashboard for Render (binds 0.0.0.0, uses $PORT)."""

from __future__ import annotations

import functools
import http.server
import os
import socketserver
from pathlib import Path


PHASE5 = Path(__file__).resolve().parents[1]
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "10000"))


class DashboardHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()


def main() -> None:
    index = PHASE5 / "index.html"
    data_file = PHASE5 / "dashboard-data.js"
    if not index.exists():
        raise SystemExit(f"Missing dashboard entrypoint: {index}")
    if not data_file.exists():
        raise SystemExit(f"Missing dashboard data bundle: {data_file}")

    handler = functools.partial(DashboardHTTPRequestHandler, directory=str(PHASE5))
    with socketserver.ThreadingTCPServer((HOST, PORT), handler) as httpd:
        print(f"Serving Category Expansion Insights on {HOST}:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
