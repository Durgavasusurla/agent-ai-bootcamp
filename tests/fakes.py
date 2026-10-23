"""A scripted stand-in for the Claude API so tests run offline and free."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any


def text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text, model_dump=lambda exclude_none=True: {"type": "text", "text": text})


def tool_use_block(tool_id: str, name: str, input: dict[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(
        type="tool_use",
        id=tool_id,
        name=name,
        input=input,
        model_dump=lambda exclude_none=True: {"type": "tool_use", "id": tool_id, "name": name, "input": input},
    )


def message(stop_reason: str, *blocks: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks))


class ScriptedCompleter:
    """Returns pre-written responses in order and records every request it saw."""

    def __init__(self, responses: list[SimpleNamespace]):
        self._responses = list(responses)
        self.requests: list[dict[str, Any]] = []

    def complete(self, *, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> SimpleNamespace:
        self.requests.append({"system": system, "messages": [dict(m) for m in messages], "tools": tools})
        if not self._responses:
            raise AssertionError("ScriptedCompleter ran out of responses")
        return self._responses.pop(0)
