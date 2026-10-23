"""Lab 01 - talking to the LLM.

A thin wrapper over the Anthropic Python SDK so the rest of the project never
touches the raw client. The agent loop calls `complete()`; tests inject a fake.
"""

from __future__ import annotations

from typing import Any, Protocol

import anthropic

from .config import Settings


class Completer(Protocol):
    """Anything that can turn (system, messages, tools) into a Message."""

    def complete(self, *, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> Any: ...


class ClaudeCompleter:
    """Real implementation backed by the Claude API.

    Notes for learners:
    - Claude Opus 5.5 always thinks; depth is controlled by `effort`, not a token budget.
    - `fallbacks="default"` lets the API re-route a safety refusal to another model
      so the agent degrades gracefully instead of returning an empty turn.
    - The API is stateless: we send the full `messages` history every call.
    """

    def __init__(self, settings: Settings | None = None, client: anthropic.Anthropic | None = None):
        self.settings = settings or Settings()
        # Credentials come from ANTHROPIC_API_KEY (or an `ant auth login` profile).
        self.client = client or anthropic.Anthropic()

    def complete(self, *, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> Any:
        return self.client.beta.messages.create(
            model=self.settings.model,
            max_tokens=self.settings.max_tokens,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=messages,
            tools=tools,
            output_config={"effort": self.settings.effort},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )


def text_of(message: Any) -> str:
    """Join all text blocks of a response. Thinking/tool blocks are skipped."""
    return "".join(block.text for block in message.content if getattr(block, "type", None) == "text").strip()
