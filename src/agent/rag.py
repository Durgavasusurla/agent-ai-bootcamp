"""Lab 03 - retrieval (the R in RAG).

A deliberately small BM25 implementation over markdown/text files. No vector
database, no embeddings: the goal is to understand what retrieval *does* before
swapping in Databricks Vector Search or a hosted embedding model.

Pipeline:  load files -> split into chunks -> tokenize -> score query vs chunk
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "is", "are", "was", "it",
    "for", "with", "as", "by", "at", "be", "this", "that", "from", "what", "how", "do",
}


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


@dataclass(frozen=True)
class Chunk:
    source: str
    text: str


def chunk_text(text: str, max_words: int = 120) -> list[str]:
    """Split on blank lines, then merge paragraphs up to ~max_words each."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    count = 0
    for para in paragraphs:
        words = len(para.split())
        if current and count + words > max_words:
            chunks.append("\n\n".join(current))
            current, count = [], 0
        current.append(para)
        count += words
    if current:
        chunks.append("\n\n".join(current))
    return chunks


class Retriever:
    def __init__(self, docs_dir: Path, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.chunks: list[Chunk] = []
        for path in sorted(docs_dir.glob("**/*")):
            if path.suffix.lower() in {".md", ".txt"}:
                for piece in chunk_text(path.read_text(encoding="utf-8")):
                    self.chunks.append(Chunk(source=path.name, text=piece))
        self._tf = [Counter(tokenize(c.text)) for c in self.chunks]
        self._len = [sum(tf.values()) for tf in self._tf]
        self._avg_len = (sum(self._len) / len(self._len)) if self._len else 0.0
        df: Counter[str] = Counter()
        for tf in self._tf:
            df.update(tf.keys())
        n = len(self.chunks)
        self._idf = {term: math.log(1 + (n - d + 0.5) / (d + 0.5)) for term, d in df.items()}

    def _score(self, query_terms: list[str], idx: int) -> float:
        tf, length = self._tf[idx], self._len[idx]
        score = 0.0
        for term in query_terms:
            if term not in tf:
                continue
            f = tf[term]
            norm = f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / (self._avg_len or 1)))
            score += self._idf.get(term, 0.0) * norm
        return score

    def search(self, query: str, k: int = 3) -> list[tuple[Chunk, float]]:
        terms = tokenize(query)
        scored = [(self.chunks[i], self._score(terms, i)) for i in range(len(self.chunks))]
        scored = [s for s in scored if s[1] > 0]
        scored.sort(key=lambda s: s[1], reverse=True)
        return scored[:k]

    def search_formatted(self, query: str, k: int = 3) -> str:
        hits = self.search(query, k=k)
        if not hits:
            return "no matching passages found"
        return "\n\n---\n\n".join(f"[source: {c.source} | score: {s:.2f}]\n{c.text}" for c, s in hits)
