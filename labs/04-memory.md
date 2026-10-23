# Lab 04 - Memory

**Goal:** make the agent remember across turns and across restarts.

Code: `src/agent/memory.py`, `save_note` / `list_notes` in `tools.py`

## Concepts
- **Short-term memory** = the `messages` list. It is resent every call and trimmed to `max_messages` so cost stays bounded.
- Trimming must never leave a `tool_result` as the first message, or the API rejects the request.
- **Long-term memory** = facts the agent chose to write down (`save_note`). The model decides what matters.
- Sessions: `python -m agent work` and `python -m agent personal` keep separate histories under `memory/`.

## Exercise
Add a `/summary` command that asks the model to compress old history into one paragraph, then replace the trimmed messages with it.

## Databricks mapping
Lakebase plus LangGraph checkpointers give the same short-term/long-term split, with MLflow tracing on top.
