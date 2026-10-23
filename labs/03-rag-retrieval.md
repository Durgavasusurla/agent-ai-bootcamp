# Lab 03 - Retrieval augmented generation

**Goal:** ground answers in your own documents instead of the model's memory.

Code: `src/agent/rag.py`, `data/docs/`

## Concepts
- **Chunking**: documents are split into passages of ~120 words so a hit is specific.
- **Scoring**: BM25 ranks chunks by keyword overlap, weighted by how rare each word is (IDF) and how long the chunk is.
- **Citation**: the tool returns `[source: file]` with every passage, and the system prompt tells the model to mention it.
- Retrieval is just another tool. The model decides *when* to search.

## Exercise
1. Drop your own `.md` notes into `data/docs/` and ask the agent about them.
2. Replace `Retriever` with an embedding-based version (cosine similarity over vectors) and compare results.

## Databricks mapping
Mosaic AI Vector Search does the chunk index and nearest-neighbour search over a Delta table.
