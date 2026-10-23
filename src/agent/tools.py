"""Lab 02 - tools (function calling).

Each tool is a plain Python function plus a JSON-schema description. Claude only
ever sees the schema; our loop runs the function and sends the result back.

`strict: True` makes the API guarantee the arguments match the schema exactly,
so the functions can trust their inputs.
"""

from __future__ import annotations

import ast
import json
import operator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .rag import Retriever

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

_SAFE_OPS: dict[type, Callable[..., float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"unsupported expression: {ast.dump(node)}")


def calculator(expression: str) -> str:
    """Safely evaluate an arithmetic expression (no eval())."""
    tree = ast.parse(expression, mode="eval")
    result = _eval_node(tree.body)
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return str(result)


def get_current_time() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class NoteStore:
    """Tiny JSON-backed note store so the agent can 'remember' facts."""

    def __init__(self, path: Path):
        self.path = path

    def _load(self) -> list[str]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, note: str) -> str:
        notes = self._load()
        notes.append(note)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(notes, indent=2), encoding="utf-8")
        return f"saved note #{len(notes)}"

    def list(self) -> str:
        notes = self._load()
        if not notes:
            return "no notes saved yet"
        return "\n".join(f"{i + 1}. {n}" for i, n in enumerate(notes))


# ---------------------------------------------------------------------------
# Tool registry: schema (what Claude sees) + handler (what we run)
# ---------------------------------------------------------------------------


class ToolRegistry:
    def __init__(self, retriever: Retriever, notes: NoteStore):
        self._handlers: dict[str, Callable[..., str]] = {
            "calculator": calculator,
            "get_current_time": get_current_time,
            "search_docs": lambda query, k=3: retriever.search_formatted(query, k=k),
            "save_note": notes.save,
            "list_notes": notes.list,
        }

    @property
    def schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "calculator",
                "description": "Evaluate an arithmetic expression like '(12 + 7) * 3' or '2 ** 10'. Use for any math.",
                "strict": True,
                "input_schema": {
                    "type": "object",
                    "properties": {"expression": {"type": "string", "description": "Arithmetic expression"}},
                    "required": ["expression"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "get_current_time",
                "description": "Return the current date and time in UTC (ISO 8601).",
                "strict": True,
                "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
            {
                "name": "search_docs",
                "description": "Keyword search over the local knowledge base (data/docs). Returns the best matching passages with their source file.",
                "strict": True,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "What to look for"},
                        "k": {"type": "integer", "description": "How many passages to return (default 3)"},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "save_note",
                "description": "Persist a short note for later. Use when the user asks you to remember something.",
                "strict": True,
                "input_schema": {
                    "type": "object",
                    "properties": {"note": {"type": "string"}},
                    "required": ["note"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "list_notes",
                "description": "List every saved note.",
                "strict": True,
                "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        ]

    def run(self, name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
        """Execute a tool. Returns (result_text, is_error)."""
        handler = self._handlers.get(name)
        if handler is None:
            return f"unknown tool: {name}", True
        try:
            return str(handler(**arguments)), False
        except Exception as exc:  # noqa: BLE001 - surface every tool failure to the model
            return f"{type(exc).__name__}: {exc}", True
