"""Lab 04 - memory.

Short-term memory is just the `messages` list we resend every call. This module
persists it to disk so a conversation survives restarts, and trims it so it never
grows without bound. (Production systems use Lakebase / LangGraph checkpointers
for the same idea.)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConversationMemory:
    def __init__(self, path: Path | None = None, max_messages: int = 40):
        self.path = path
        self.max_messages = max_messages
        self.messages: list[dict[str, Any]] = []
        if path and path.exists():
            self.messages = json.loads(path.read_text(encoding="utf-8"))

    def add(self, role: str, content: Any) -> None:
        self.messages.append({"role": role, "content": _to_jsonable(content)})
        self._trim()
        self._flush()

    def _trim(self) -> None:
        if len(self.messages) <= self.max_messages:
            return
        # Drop oldest messages, but never start the history on a tool_result turn.
        self.messages = self.messages[-self.max_messages :]
        while self.messages and _is_tool_result(self.messages[0]):
            self.messages.pop(0)

    def _flush(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.messages, indent=2), encoding="utf-8")

    def clear(self) -> None:
        self.messages = []
        if self.path and self.path.exists():
            self.path.unlink()


def _is_tool_result(message: dict[str, Any]) -> bool:
    content = message.get("content")
    return isinstance(content, list) and any(b.get("type") == "tool_result" for b in content if isinstance(b, dict))


def _to_jsonable(content: Any) -> Any:
    """SDK content blocks are pydantic models; store them as plain dicts."""
    if isinstance(content, str):
        return content
    out = []
    for block in content:
        if hasattr(block, "model_dump"):
            out.append(block.model_dump(exclude_none=True))
        else:
            out.append(block)
    return out
