# MLflow tracing for agents

MLflow Tracing captures each step an agent takes as a span: the prompt sent to the
model, every tool call with its inputs and outputs, retrieval results, and timings.
Traces are stored in an MLflow experiment and can be viewed in the Databricks UI.

## Why tracing matters

Agents are non-deterministic. When an answer is wrong, the trace shows whether the
model chose the wrong tool, the tool returned bad data, or the retriever found the
wrong passage. Without a trace you are guessing.

## Enabling it

In a Databricks notebook, calling `mlflow.langchain.autolog()` or
`mlflow.openai.autolog()` turns on tracing for the matching framework. Custom code
can create spans manually with the `@mlflow.trace` decorator.

## Production

When an agent is deployed with Agent Framework, traces are logged automatically to
an inference table, which is a Delta table. Those traces become the raw material
for evaluation datasets and for monitoring quality over time.
