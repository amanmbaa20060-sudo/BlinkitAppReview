"""Serve the Phase 5 dashboard for Render (binds 0.0.0.0, uses $PORT).

Also exposes:
  GET /api/llm-status  — pipeline LLM provenance + optional live Groq check
  GET /health          — liveness
"""

from __future__ import annotations

import functools
import json
import os
import socketserver
import sys
import urllib.parse
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler
from pathlib import Path


PHASE5 = Path(__file__).resolve().parents[1]
ROOT = PHASE5.parent
ALLOWED_ORIGINS = {
    origin.strip()
    for origin in os.environ.get(
        "CORS_ALLOW_ORIGINS",
        "http://127.0.0.1:8501,http://localhost:8501",
    ).split(",")
    if origin.strip()
}


class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json_file(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pipeline_llm_status() -> dict:
    status_path = PHASE5 / "llm-status.json"
    if status_path.exists():
        data = load_json_file(status_path)
        data["source"] = "llm-status.json"
        return data

    # Fallback: derive from committed dashboard bundle markers if present.
    sys.path.insert(0, str(PHASE5 / "scripts"))
    try:
        from build_dashboard_data import llm_status_from_existing_bundle

        derived = llm_status_from_existing_bundle()
        if derived:
            derived["source"] = "dashboard-data.js"
            return derived
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "llm_used_in_pipeline": False,
            "summary": f"Unable to load LLM status: {exc}",
            "source": "error",
        }
    return {
        "ok": False,
        "llm_used_in_pipeline": False,
        "summary": "llm-status.json missing",
        "source": "missing",
    }


def live_groq_check() -> dict:
    """Verify GROQ_API_KEY works with a tiny completion (optional, best-effort)."""
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        # Try loading repo .env when running locally / on Render with dotenv file absent.
        try:
            sys.path.insert(0, str(ROOT))
            from shared.env import load_repo_env

            load_repo_env()
            key = os.environ.get("GROQ_API_KEY", "").strip()
        except Exception:  # noqa: BLE001
            pass

    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    if not key:
        return {
            "configured": False,
            "reachable": False,
            "model": model,
            "detail": "GROQ_API_KEY is not set on this service",
        }

    try:
        sys.path.insert(0, str(ROOT))
        from shared.groq_client import GroqLLMClient

        client = GroqLLMClient()
        reply = client.complete(
            'Reply with exactly: {"pong":true}',
            system="Return only compact JSON.",
            temperature=0,
            max_tokens=20,
            retries=2,
        )
        return {
            "configured": True,
            "reachable": True,
            "model": client.model,
            "detail": "Groq chat completion succeeded",
            "sample": (reply or "")[:120],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "configured": True,
            "reachable": False,
            "model": model,
            "detail": str(exc),
        }


def build_api_llm_status(*, ping: bool) -> dict:
    status = pipeline_llm_status()
    status["checked_at"] = utc_now()
    status["live_api"] = live_groq_check() if ping else {
        "configured": bool(os.environ.get("GROQ_API_KEY", "").strip()),
        "reachable": None,
        "detail": "Pass ?ping=1 to run a live Groq completion check",
    }
    status["ok"] = True
    return status


class DashboardHTTPRequestHandler(SimpleHTTPRequestHandler):
    def _cors_origin(self) -> str | None:
        origin = self.headers.get("Origin", "").strip()
        if not origin:
            return None
        if "*" in ALLOWED_ORIGINS or origin in ALLOWED_ORIGINS:
            return origin
        # Allow any vercel.app preview/production host by default.
        if origin.endswith(".vercel.app"):
            return origin
        return None

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        origin = self._cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Vary", "Origin")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path in {"/health", "/healthz"}:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return

        if path == "/api/llm-status":
            ping = (query.get("ping") or ["0"])[0] in {"1", "true", "yes"}
            payload = build_api_llm_status(ping=ping)
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        super().do_GET()

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
    print("API: GET /api/llm-status  (add ?ping=1 for live Groq check)", flush=True)

    with ThreadingHTTPServer((host, port), handler) as httpd:
        print("Dashboard is ready to accept traffic.", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
        sys.exit(0)
