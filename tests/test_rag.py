from pathlib import Path

from agent.rag import Retriever, chunk_text, tokenize

DOCS = Path(__file__).resolve().parents[1] / "data" / "docs"


def test_tokenize_drops_stopwords_and_lowercases():
    assert tokenize("The Agent is Running") == ["agent", "running"]


def test_chunk_text_respects_word_budget():
    text = "\n\n".join(["word " * 50] * 6)
    chunks = chunk_text(text, max_words=120)
    assert len(chunks) == 3
    assert all(len(c.split()) <= 120 for c in chunks)


def test_retriever_finds_relevant_doc():
    retriever = Retriever(DOCS)
    hits = retriever.search("vector search index chunks", k=1)
    assert hits and hits[0][0].source == "databricks-agent-basics.md"


def test_retriever_formats_sources():
    out = Retriever(DOCS).search_formatted("MLflow trace spans")
    assert "[source: mlflow-tracing.md" in out


def test_retriever_no_match():
    assert Retriever(DOCS).search("zzzz qqqq") == []
