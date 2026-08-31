"""
LLM provider abstraction (spec sections 23, 39, 44).

Any service that wants natural-language generation (goal extraction,
explanations, the companion chat) goes through `LLMProvider.complete_json` or
`.complete_text`. If no API key is configured, or the call fails/times out,
callers fall back to deterministic, rule-based logic and the API responses
carry `"source": "fallback_rules"` / `intelligence_mode: "demo"` so the
frontend can honestly display "Demo Intelligence Mode" (spec section 44)
instead of silently pretending an LLM was used.

This keeps a hard separation from the app's structured data pipeline: the
LLM is only ever used for extraction/explanation *of* data the app already
computed (skill graph, gaps, scores) — never as a replacement for that
pipeline (spec section 43, "do not build a fake AI").
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from app.core.config import get_settings

settings = get_settings()


@dataclass
class LLMResult:
    ok: bool
    text: str = ""
    data: Any = None
    provider: str = "none"


class LLMProvider:
    def __init__(self):
        self.available = settings.llm_available
        self._client = None
        self._provider_name = "none"
        if self.available:
            self._init_client()

    def _init_client(self) -> None:
        try:
            if settings.ANTHROPIC_API_KEY and settings.LLM_PROVIDER in ("auto", "anthropic"):
                import anthropic

                self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                self._provider_name = "anthropic"
            elif settings.OPENAI_API_KEY and settings.LLM_PROVIDER in ("auto", "openai"):
                import openai

                self._client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                self._provider_name = "openai"
            else:
                self.available = False
        except Exception:
            # Missing dependency or bad init -> gracefully degrade to fallback mode.
            self.available = False
            self._client = None

    def complete_json(self, system: str, user: str, max_tokens: int = 800) -> LLMResult:
        """Ask the model to return ONLY a JSON object. Falls back cleanly."""
        if not self.available or self._client is None:
            return LLMResult(ok=False, provider="none")
        try:
            raw = self._raw_complete(system, user, max_tokens)
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.lower().startswith("json"):
                    cleaned = cleaned[4:]
            data = json.loads(cleaned)
            return LLMResult(ok=True, text=raw, data=data, provider=self._provider_name)
        except Exception:
            return LLMResult(ok=False, provider=self._provider_name)

    def complete_text(self, system: str, user: str, max_tokens: int = 500) -> LLMResult:
        if not self.available or self._client is None:
            return LLMResult(ok=False, provider="none")
        try:
            raw = self._raw_complete(system, user, max_tokens)
            return LLMResult(ok=True, text=raw, provider=self._provider_name)
        except Exception:
            return LLMResult(ok=False, provider=self._provider_name)

    def _raw_complete(self, system: str, user: str, max_tokens: int) -> str:
        if self._provider_name == "anthropic":
            resp = self._client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return "".join(block.text for block in resp.content if hasattr(block, "text"))
        elif self._provider_name == "openai":
            resp = self._client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                max_tokens=max_tokens,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            return resp.choices[0].message.content or ""
        raise RuntimeError("No provider configured")


_provider: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        _provider = LLMProvider()
    return _provider
