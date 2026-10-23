# Lab 02 - Tools and the agent loop

**Goal:** turn a chatbot into an agent by letting the model call functions.

Code: `src/agent/tools.py`, `src/agent/agent.py`

## Concepts
- A **tool** is a JSON schema (what the model sees) plus a function (what we run). The model never executes code itself.
- The **loop**: call model -> if `stop_reason == "tool_use"`, run tools -> append `tool_result` blocks -> call again. Repeat until plain text.
- Return **all** tool results in one user message so the model keeps making parallel calls.
- Tool failures go back as `is_error: true`, never as a Python exception, so the model can recover.
- `max_turns` is the safety net against infinite loops.
- `strict: true` makes the API validate the arguments against the schema, so the handlers can trust their inputs.

## Exercise
Add a `word_count(text)` tool. You need: a schema in `ToolRegistry.schemas`, a handler in `_handlers`, and a test.

## Databricks mapping
Tools become Unity Catalog functions; the loop is what Mosaic AI Agent Framework runs for you.
