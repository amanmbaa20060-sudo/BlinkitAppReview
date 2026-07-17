"""Groq LLM client via HTTPS (no openai SDK — avoids local DLL policy issues)."""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any

from .env import load_repo_env


class GroqLLMClient:
    """Groq chat client using the OpenAI-compatible HTTP API."""

    def __init__(self) -> None:
        load_repo_env()
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is missing. Set it in the repo-root .env file.")
        base = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip().rstrip("/")
        self.url = f"{base}/chat/completions"
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        self.provider = "groq"

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1200,
        retries: int = 4,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        body = json.dumps(payload).encode("utf-8")
        last_err: Exception | None = None
        for attempt in range(retries):
            req = urllib.request.Request(
                self.url,
                data=body,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "BlinkitAppReview/1.0 (+https://github.com/local/blinkit-app-review)",
                    "Accept": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=90) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                return (data["choices"][0]["message"]["content"] or "").strip()
            except urllib.error.HTTPError as exc:
                err_body = exc.read().decode("utf-8", errors="replace")
                last_err = RuntimeError(f"HTTP {exc.code}: {err_body}")
                # Rate limit / transient
                time.sleep(2.0 * (attempt + 1))
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"Groq completion failed after {retries} retries: {last_err}")

    def complete_json(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1200,
    ) -> dict[str, Any]:
        text = self.complete(
            prompt,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return extract_json_object(text)


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    else:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)
