"""Build dashboard data, serve phase5/, and open the browser."""

from __future__ import annotations

import argparse
import functools
import http.server
import socket
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path


PHASE5 = Path(__file__).resolve().parents[1]
ROOT = PHASE5.parent


class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class DashboardHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        # Avoid stale cached JS/CSS while iterating on the dashboard.
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def log_message(self, format: str, *args) -> None:
        if args and isinstance(args[-1], str) and args[-1].startswith("4"):
            super().log_message(format, *args)

    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            pass


def build_data() -> None:
    sys.path.insert(0, str(PHASE5 / "scripts"))
    from build_dashboard_data import main as build_main

    build_main()


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def pick_port(preferred: int) -> int:
    for port in range(preferred, preferred + 25):
        if port_is_free(port):
            return port
    raise SystemExit(f"No free port found in range {preferred}-{preferred + 24}")


def serve(port: int) -> None:
    handler = functools.partial(DashboardHTTPRequestHandler, directory=str(PHASE5))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}/"
        print(f"Serving Category Expansion Insights at {url}")
        print(f"Also try: http://localhost:{port}/")
        print("Press Ctrl+C to stop.")
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Phase 5 insight dashboard")
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()

    index = PHASE5 / "index.html"
    data_file = PHASE5 / "dashboard-data.js"
    if not index.exists():
        raise SystemExit(f"Missing dashboard entrypoint: {index}")

    if not args.skip_build:
        try:
            build_data()
        except Exception as exc:
            print(f"Warning: dashboard data build failed ({exc}). Using existing dashboard-data.js if present.")
            if not data_file.exists():
                raise SystemExit("dashboard-data.js is missing and build failed.") from exc

    port = pick_port(args.port)
    if port != args.port:
        print(f"Port {args.port} is busy. Using {port} instead.")

    time.sleep(0.1)
    serve(port)


if __name__ == "__main__":
    main()
