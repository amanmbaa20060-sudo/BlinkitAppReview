"""Load repo-root .env into process environment."""

from __future__ import annotations

import os
from pathlib import Path


def load_repo_env() -> Path:
    """Load `.env` from repository root if present. Returns the path used."""
    # shared/ -> repo root
    root = Path(__file__).resolve().parents[1]
    env_path = root / ".env"
    if not env_path.exists():
        return env_path
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path, override=False)
    except ImportError:
        # Minimal parser fallback
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
    return env_path
