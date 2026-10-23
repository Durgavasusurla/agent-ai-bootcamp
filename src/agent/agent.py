"""The agent loop.

This is the heart of the project and the thing every agent framework hides:

    1. send the conversation + tool schemas to the model
    2. if the model asks to call tools, run them and append the results
    3. repeat until the model answers in plain text (or we hit max_turns)

We write the loop by hand instead of using the SDK's tool runner so that every
step is visible. Swap in `client.beta.messages.tool_runner` once it makes sense.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import SYSTEM_PROMPT, Settings
from .llm import ClaudeCompleter, Completer, text_of
from .memory import ConversationMemory
from .rag import Retriever
from .tools import NoteStore, ToolRegistry


@dataclass
class Trace:
    """Everything that happened while answering one user message (useful for evals)."""

    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    turns: int = 0
    stop_reason: str | None = None


class Agent:
    def __init__(
        self,
        settings: Settings | None = None,
        completer: Completer | None = None,
        memory: ConversationMemory | None = None,
        session: str = "default",
    ):
        self.settings = settings or Settings()
        self.completer = completer or ClaudeCompleter(self.settings)
        self.memory = memory or ConversationMemory(self.settings.memory_dir / f"{session}.json")
        retriever = Retriever(self.settings.docs_dir)
        notes = NoteStore(self.settings.memory_dir / f"{session}-notes.json")
        self.tools = ToolRegistry(retriever, notes)
        self.last_trace = Trace()

    def ask(self, user_message: str) -> str:
        trace = Trace()
        self.memory.add("user", user_message)

        for _ in range(self.settings.max_turns):
            trace.turns += 1
            response = self.completer.complete(
                system=SYSTEM_PROMPT,
                messages=self.memory.messages,
                tools=self.tools.schemas,
            )
            trace.stop_reason = response.stop_reason
            self.memory.add("assistant", response.content)

            if response.stop_reason == "refusal":
                self.last_trace = trace
                return "I can't help with that request."

            tool_uses = [b for b in response.content if b.type == "tool_use"]
            if response.stop_reason != "tool_use" or not tool_uses:
                self.last_trace = trace
                return text_of(response) or "(no answer)"

            # Run every requested tool and send ALL results back in one user turn.
            results = []
            for call in tool_uses:
                output, is_error = self.tools.run(call.name, dict(call.input))
                trace.tool_calls.append({"name": call.name, "input": call.input, "output": output, "error": is_error})
                results.append(
                    {"type": "tool_result", "tool_use_id": call.id, "content": output, "is_error": is_error}
                )
            self.memory.add("user", results)

        self.last_trace = trace
        return "I ran out of steps before finishing. Try asking a smaller question."

    def reset(self) -> None:
        self.memory.clear()
