"""Backend protocol + Mock + Anthropic adapter."""

from __future__ import annotations

import os
from typing import Callable, Protocol


class Completion(Protocol):
    model: str

    def complete(self, prompt: str, *, system: str | None = None) -> str: ...


class MockCompletion:
    def __init__(
        self,
        responder: Callable[[str, str | None], str],
        model: str = "mock",
    ) -> None:
        self.model = model
        self.responder = responder
        self.calls: list[dict] = []

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        self.calls.append({"prompt": prompt, "system": system})
        return self.responder(prompt, system)


class AnthropicCompletion:
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 1024,
    ) -> None:
        from anthropic import Anthropic  # noqa: F401

        self.model = model or os.environ.get(
            "STEPBACK_MODEL", "claude-haiku-4-5-20251001"
        )
        self.client = __import__("anthropic").Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.max_tokens = max_tokens

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        resp = self.client.messages.create(**kwargs)
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
