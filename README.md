# agent-ai-bootcamp

A small AI agent written from first principles while following the Databricks
**Agent AI / LLM bootcamp**. No framework hides the loop: every piece a bootcamp
talks about (model call, tool calling, RAG, memory, evaluation) is a readable file
you can change.

```
you > According to the docs, what does Unity Catalog do for agent tools?
agent > Unity Catalog functions become governed tools: access control, audit logs and
        lineage apply automatically (source: unity-catalog-tools.md).
```

## What's inside

| Lab | Topic | Code |
|-----|-------|------|
| [01](labs/01-llm-basics.md) | One LLM call, content blocks, stop reasons | `src/agent/llm.py` |
| [02](labs/02-tools-and-the-agent-loop.md) | Tools and the hand-written agent loop | `src/agent/tools.py`, `src/agent/agent.py` |
| [03](labs/03-rag-retrieval.md) | BM25 retrieval over local docs | `src/agent/rag.py`, `data/docs/` |
| [04](labs/04-memory.md) | Persistent conversation memory and notes | `src/agent/memory.py` |
| [05](labs/05-evaluation.md) | Eval harness with tool-usage checks | `src/agent/evaluate.py`, `data/evals.json` |

Tools the agent can call: `calculator`, `get_current_time`, `search_docs`, `save_note`, `list_notes`.

## Quick start

```bash
git clone https://github.com/Durgavasusurla/agent-ai-bootcamp.git
cd agent-ai-bootcamp
python -m venv .venv
.venv\Scripts\activate          # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # then put your ANTHROPIC_API_KEY in .env

python -m agent                 # chat
python -m agent.evaluate        # run the eval suite
pytest                          # offline unit tests, no API key needed
```

The model defaults to `claude-opus-5-5`. Override with `AGENT_MODEL` / `AGENT_EFFORT` in `.env`.

## How the agent works

```
user message
    |
    v
+-----------------+   tool_use    +----------------+
|  Claude (LLM)   | ------------> |  ToolRegistry  |
|  + system prompt| <------------ |  run handler   |
+-----------------+  tool_result  +----------------+
    |  end_turn
    v
answer  (+ Trace of every tool call, used by evals)
```

`Agent.ask()` in [src/agent/agent.py](src/agent/agent.py) is the whole loop, about 40 lines.

## Project layout

```
src/agent/      the package (one file per concept)
data/docs/      knowledge base for RAG (drop your own .md files here)
data/evals.json eval cases
labs/           notes per bootcamp module, with exercises
tests/          offline tests using a scripted fake model
memory/         created at runtime, per-session history (git-ignored)
```

## Roadmap

- [ ] Embedding-based retriever (compare with BM25)
- [ ] LLM-as-judge groundedness metric in the eval harness
- [ ] Streaming replies in the CLI
- [ ] Deploy the same agent on Databricks with Mosaic AI Agent Framework and MLflow tracing

## License

MIT
