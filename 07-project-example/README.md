# Module 7: End-to-End Project Example (notes)

Course module: [07-project-example](https://github.com/DataTalksClub/llm-zoomcamp/tree/main/07-project-example)
(recorded in 2024, optional). Reference project:
[alexeygrigorev/fitness-assistant](https://github.com/alexeygrigorev/fitness-assistant).

No code here on purpose: every piece of that project already exists in this
repo, module by module. The capstone combines them into one product on a new
dataset.

| Fitness assistant piece | Where it lives in this repo |
|---|---|
| LLM-generated dataset (structured output) | `04-evaluation/01-data-gen.ipynb` |
| minsearch + RAG flow | `01-agentic-rag/` |
| Retrieval evaluation (Hit Rate, MRR, boosts) | `04-evaluation/02-search-eval.ipynb` |
| RAG evaluation (LLM-as-a-judge) | `04-evaluation/03-rag-evals.ipynb` |
| Interface | `05-monitoring/app.py` (Streamlit; the course used Flask) |
| Monitoring, Postgres, Grafana, Docker Compose | `05-monitoring/` |
| Hybrid search + reranking (rubric best practices) | `06-best-practices/hybrid-search.ipynb` |

Full notes, rubric status and the capstone plan: `docs/bootcamp-notes.html`,
Steps 70-72.
