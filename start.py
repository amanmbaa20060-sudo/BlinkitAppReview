"""Render web service entrypoint."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    script = Path(__file__).resolve().parent / "phase5" / "scripts" / "serve_render.py"
    runpy.run_path(str(script), run_name="__main__")
