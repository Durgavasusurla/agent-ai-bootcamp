# Lab 05 - Evaluation

**Goal:** know whether a prompt or tool change made the agent better or worse.

Code: `src/agent/evaluate.py`, `data/evals.json`

## Concepts
- An **eval case** is a question plus checks: which tool must be used, what the answer must contain.
- `Agent.last_trace` records every tool call, so checks can look at *behaviour*, not just the final text.
- Deterministic checks are cheap and stable. LLM-as-judge grading (groundedness, relevance) comes next.
- Run the suite before and after every prompt change. Score going down is a regression.

```bash
python -m agent.evaluate
```

## Exercise
Add three cases that currently fail, then fix the system prompt until they pass without breaking the others.

## Databricks mapping
Mosaic AI Agent Evaluation + MLflow `evaluate()` run the same idea with built-in LLM judges and a UI.
