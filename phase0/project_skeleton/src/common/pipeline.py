"""No-op pipeline runner placeholder for later phases."""

from __future__ import annotations

from common.paths import PIPELINE_STEPS


def list_steps() -> tuple[str, ...]:
    return PIPELINE_STEPS
