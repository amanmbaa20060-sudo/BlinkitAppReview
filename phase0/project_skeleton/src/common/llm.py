"""Thin LLM client interface — classification and insight synthesis."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Provider-agnostic LLM interface."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class NoOpLLMClient(LLMClient):
    """Phase 0 smoke-test stub."""

    def complete(self, prompt: str) -> str:
        return f"[noop-llm] received {len(prompt)} chars"
