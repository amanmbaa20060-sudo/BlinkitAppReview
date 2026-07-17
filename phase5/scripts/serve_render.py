"""Serve the Phase 5 dashboard for Render (binds 0.0.0.0, uses $PORT)."""

from __future__ import annotations

import functools
import http.server
import os
import socketserver
import sys
from pathlib import Path


PHASE5 = Path(__file__).resolve().parents[1]


class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class DashboardHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in {"/health", "/healthz"}:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        super().do_GET()

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def log_message(self, format: str, *args) -> None:
        print(f"[dashboard] {self.address_string()} - {format % args}", flush=True)


def resolve_port() -> int:
    raw = os.environ.get("PORT", "10000")
    try:
        return int(raw)
    except ValueError as exc:
        raise SystemExit(f"Invalid PORT value: {raw!r}") from exc


def main() -> None:
    index = PHASE5 / "index.html"
    data_file = PHASE5 / "dashboard-data.js"
    if not index.exists():
        raise SystemExit(f"Missing dashboard entrypoint: {index}")
    if not data_file.exists():
        raise SystemExit(f"Missing dashboard data bundle: {data_file}")

    host = "0.0.0.0"
    port = resolve_port()
    handler = functools.partial(DashboardHTTPRequestHandler, directory=str(PHASE5))

    print(f"Starting dashboard server on {host}:{port}", flush=True)
    print(f"Serving files from {PHASE5}", flush=True)

    with ThreadingHTTPServer((host, port), handler) as httpd:
        print("Dashboard is ready to accept traffic.", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
        sys.exit(0)
