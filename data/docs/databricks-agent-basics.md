# AI agents on Databricks: the basics

An AI agent is an application where a large language model (LLM) decides which
actions to take. Instead of answering in one shot, the model can call tools,
look at the results, and keep going until it has what it needs. On Databricks this
pattern is implemented with the Mosaic AI Agent Framework.

## The three building blocks

1. A model: a foundation model served through Model Serving (for example a Claude
   or Llama endpoint) that produces text and tool calls.
2. Tools: functions the model can invoke. On Databricks these are registered as
   Unity Catalog functions so that governance, permissions and lineage apply to
   tools exactly as they apply to tables.
3. An agent loop: code that sends the conversation to the model, executes the tools
   it asks for, feeds results back and repeats.

## Retrieval augmented generation (RAG)

RAG means giving the model relevant documents at answer time instead of hoping it
memorised them. On Databricks the retriever is usually Mosaic AI Vector Search, which
indexes chunks of documents from a Delta table and returns the nearest chunks to a
query embedding. The agent then cites those chunks in its answer.

## Evaluation

Mosaic AI Agent Evaluation runs an agent over a set of questions and grades the
answers with LLM judges and deterministic checks. Common metrics are groundedness
(is the answer supported by the retrieved context), relevance, and tool-call
correctness. MLflow tracing records every step of each run so failures can be
inspected.
