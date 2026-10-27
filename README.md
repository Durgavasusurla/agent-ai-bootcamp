# agent-ai-bootcamp

My hands-on work for [LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp)
(DataTalks.Club), on Windows 11 with Groq, plus a small agent written from first
principles. Goal: AI Forward Deployed Engineer.

**Notes:** open [docs/bootcamp-notes.html](docs/bootcamp-notes.html) in a browser.
It has a course map, a one-minute summary per module, every step with commands
and real outputs, troubleshooting, and the roadmap.

## Course modules (same folder names as the course repo)

| Folder | Module | What it does | Run with | Status |
|---|---|---|---|---|
| [01-agentic-rag](01-agentic-rag/) | Agentic RAG | FAQ RAG, sqlitesearch ingestion, function calling, agent loop, ToyAIKit | root `.venv` (Python 3.15) | Done |
| [02-vector-search](02-vector-search/) | Vector Search | ONNX embeddings, numpy / minsearch / sqlitesearch vector search, vector RAG | own `.venv` (Python 3.14) | Done (PGVector needs Docker) |
| [03-orchestration](03-orchestration/) | Orchestration | Kestra flows (RAG, agents, multi-agent), Windows start script | Docker | Waiting for Docker + Gemini/Tavily keys |
| [04-evaluation](04-evaluation/) | Evaluation | Ground truth, Hit Rate / MRR, boost tuning, LLM judge, agent eval | root `.venv` | Done (free-tier samples) |
| [05-monitoring](05-monitoring/) | Monitoring | Streamlit chat + dashboard, metrics, feedback, judge, SQLite/Postgres | root `.venv` | Done (Grafana needs Docker) |
| [06-best-practices](06-best-practices/) | Best Practices | Keyword vs vector vs hybrid (RRF), evaluated | `02-vector-search` `.venv` | Done |
| [07-project-example](07-project-example/) | Project Example | Map of the reference project onto this repo | - | Notes |

Key results: hybrid search hit rate 0.959 (keyword 0.908, vector 0.943) on 315
questions; boost tuning raised keyword hit rate from 0.778 to 0.908.

### Windows notes

- Smart App Control blocks unsigned `.exe` launchers: use `py -m pip`,
  `uv run python -m streamlit`, `uv run python -m jupyter`.
- PyTorch does not run here, so Module 2 uses the course's ONNX embedder.
- API keys live only in `.env` (see `.env.example`). LLM provider: Groq
  (`openai/gpt-oss-120b`) through the OpenAI client.

## My own agent (`src/`)

A small Claude agent written from first principles before the course. No
framework hides the loop: model call, tool calling, RAG, memory, evaluation are
each one readable file.

| Lab | Topic | Code |
|-----|-------|------|
| [01](labs/01-llm-basics.md) | One LLM call, content blocks, stop reasons | `src/agent/llm.py` |
| [02](labs/02-tools-and-the-agent-loop.md) | Tools and the hand-written agent loop | `src/agent/tools.py`, `src/agent/agent.py` |
| [03](labs/03-rag-retrieval.md) | BM25 retrieval over local docs | `src/agent/rag.py`, `data/docs/` |
| [04](labs/04-memory.md) | Persistent conversation memory and notes | `src/agent/memory.py` |
| [05](labs/05-evaluation.md) | Eval harness with tool-usage checks | `src/agent/evaluate.py`, `data/evals.json` |

```bash
uv sync
copy .env.example .env          # add ANTHROPIC_API_KEY
uv run python -m agent          # chat
uv run python -m agent.evaluate # eval suite
uv run pytest                   # offline tests
```

## License

MIT
