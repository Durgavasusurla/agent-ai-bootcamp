# Lab 01 - Talking to an LLM

**Goal:** understand what one model call looks like before adding any agent logic.

Code: `src/agent/llm.py`

## Concepts
- The Messages API is **stateless**. Every call sends the full `messages` list; the model has no memory of previous calls.
- `system` sets the model's role and rules. We cache it with `cache_control` because it never changes between calls.
- `max_tokens` is a hard ceiling on the reply. `effort` controls how much the model thinks before answering.
- The response is a list of **content blocks** (`text`, `thinking`, `tool_use`). Always check `block.type`.
- `stop_reason` tells you *why* the model stopped: `end_turn`, `tool_use`, `max_tokens`, or `refusal`.

## Try it
```python
from agent.llm import ClaudeCompleter, text_of
resp = ClaudeCompleter().complete(system="Be brief.", messages=[{"role": "user", "content": "Hi"}], tools=[])
print(text_of(resp), resp.stop_reason)
```

## Databricks mapping
On Databricks this is a Model Serving endpoint queried through the Foundation Model API. Same shape, different URL.
