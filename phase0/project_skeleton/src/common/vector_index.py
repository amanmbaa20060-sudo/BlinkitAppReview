"""Thin vector index interface — default v1 target is Chroma."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence


class VectorIndex(ABC):
    @abstractmethod
    def upsert(self, ids: Sequence[str], vectors: Sequence[Sequence[float]], metadatas: Sequence[dict[str, Any]] | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def query(self, vector: Sequence[float], top_k: int = 5) -> list[dict[str, Any]]:
        raise NotImplementedError


class InMemoryVectorIndex(VectorIndex):
    """Phase 0 smoke-test stub."""

    def __init__(self) -> None:
        self._rows: list[dict[str, Any]] = []

    def upsert(self, ids: Sequence[str], vectors: Sequence[Sequence[float]], metadatas: Sequence[dict[str, Any]] | None = None) -> None:
        metadatas = metadatas or [{} for _ in ids]
        for i, vec, meta in zip(ids, vectors, metadatas):
            self._rows.append({"id": i, "vector": list(vec), "metadata": meta})

    def query(self, vector: Sequence[float], top_k: int = 5) -> list[dict[str, Any]]:
        return self._rows[:top_k]
