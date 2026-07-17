"""Local hashing embeddings + file-backed vector index (Phase 0 interface pattern)."""

from __future__ import annotations

import hashlib
import json
import math
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Sequence

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    toks = TOKEN_RE.findall(text.lower())
    bigrams = [f"{toks[i]}_{toks[i+1]}" for i in range(len(toks) - 1)]
    return toks + bigrams


class EmbeddingClient(ABC):
    @abstractmethod
    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        raise NotImplementedError


class HashingEmbeddingClient(EmbeddingClient):
    """Deterministic feature-hashing embeddings (offline v1; swap for OpenAI later)."""

    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions
        self.model_id = f"local_hashing_dim{dimensions}"

    def embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dimensions
        for token in tokenize(text):
            h = hashlib.md5(token.encode("utf-8")).hexdigest()
            idx = int(h[:8], 16) % self.dimensions
            sign = 1.0 if int(h[8:10], 16) % 2 == 0 else -1.0
            vec[idx] += sign
        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self.embed_one(t) for t in texts]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class FileVectorIndex:
    """Simple persistent vector index (JSONL); Chroma-compatible swap later."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def upsert(self, ids: Sequence[str], vectors: Sequence[Sequence[float]], metadatas: Sequence[dict[str, Any]] | None = None) -> None:
        metadatas = metadatas or [{} for _ in ids]
        by_id = {r["id"]: i for i, r in enumerate(self.rows)}
        for i, vec, meta in zip(ids, vectors, metadatas):
            row = {"id": i, "vector": list(vec), "metadata": meta}
            if i in by_id:
                self.rows[by_id[i]] = row
            else:
                self.rows.append(row)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for row in self.rows:
                f.write(json.dumps(row) + "\n")

    def load(self, path: Path) -> None:
        self.rows = []
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    self.rows.append(json.loads(line))

    def query(self, vector: Sequence[float], top_k: int = 5) -> list[dict[str, Any]]:
        scored = [
            {"id": r["id"], "score": cosine(vector, r["vector"]), "metadata": r.get("metadata", {})}
            for r in self.rows
        ]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
