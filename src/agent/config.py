"""Runtime settings. Everything is overridable through environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Settings:
    model: str = field(default_factory=lambda: os.getenv("AGENT_MODEL", "claude-opus-5-5"))
    effort: str = field(default_factory=lambda: os.getenv("AGENT_EFFORT", "medium"))
    max_tokens: int = 16000
    max_turns: int = 10  # hard cap on tool-call rounds per user message
    docs_dir: Path = field(default_factory=lambda: ROOT / "data" / "docs")
    memory_dir: Path = field(default_factory=lambda: ROOT / "memory")


SYSTEM_PROMPT = """You are a helpful, concise assistant built during an AI-agent bootcamp.

You have tools. Use them when they make the answer more accurate:
- calculator for any arithmetic, do not do math in your head
- get_current_time for anything date or time related
- search_docs to look up facts in the local knowledge base before answering questions about it
- save_note / list_notes to remember things the user asks you to remember

When you used search_docs, mention which document the answer came from.
If a tool returns an error, tell the user plainly instead of guessing.
Keep answers short unless the user asks for detail."""
