"""agent-ai-bootcamp: a small, readable AI agent built from first principles.

Modules (each maps to a bootcamp lab, see labs/):
    config    - settings loaded from environment / .env
    llm       - thin wrapper over the Anthropic client (Lab 01)
    tools     - tool definitions the agent can call (Lab 02)
    rag       - tiny BM25 retriever over local docs (Lab 03)
    memory    - persistent conversation memory (Lab 04)
    agent     - the agentic loop that ties it together (Lab 02-04)
    evaluate  - a minimal eval harness (Lab 05)
"""

from .agent import Agent

__all__ = ["Agent"]
