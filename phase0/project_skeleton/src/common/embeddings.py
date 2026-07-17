"""Thin embedding client interface — swap providers without schema changes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence


class EmbeddingClient(ABC):
    """Provider-agnostic embedding interface."""

    @abstractmethod
    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        raise NotImplementedError


class NoOpEmbeddingClient(EmbeddingClient):
    """Phase 0 smoke-test stub: returns fixed-size zero vectors."""

    def __init__(self, dimensions: int = 8) -> None:
        self.dimensions = dimensions

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[0.0] * self.dimensions for _ in texts]
