"""Pure-Python stand-in for minsearch.Index.

Why this exists: on this Windows 11 machine Smart App Control blocks unsigned
compiled extensions (.pyd). The real minsearch imports scikit-learn, which
imports scipy, and scipy's _ckdtree DLL gets blocked. This module uses only the
standard library, so nothing gets blocked.

Same API as minsearch.Index:
    index = Index(text_fields=[...], keyword_fields=[...])
    index.fit(documents)
    index.search(query, filter_dict={...}, boost_dict={...}, num_results=5)

Scoring mirrors minsearch: per text field, TF-IDF vectors (raw term counts,
smooth idf, L2 normalised, no stop word removal, same token pattern as
scikit-learn) and cosine similarity with the query.
Field scores are multiplied by their boost and summed. Keyword fields are exact
match filters applied before ranking.
"""

import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"(?u)\b\w\w+\b")  # scikit-learn's default token pattern


def tokenize(text):
    return TOKEN_RE.findall(str(text or "").lower())


class _FieldIndex:
    """TF-IDF index for one text field."""

    def fit(self, texts):
        n = len(texts)
        token_counts = [Counter(tokenize(t)) for t in texts]
        df = Counter()
        for counts in token_counts:
            df.update(counts.keys())
        self.idf = {term: math.log((1 + n) / (1 + d)) + 1 for term, d in df.items()}
        self.vectors = [self._weigh(counts) for counts in token_counts]
        return self

    def _weigh(self, counts):
        vec = {t: c * self.idf[t] for t, c in counts.items() if t in self.idf}
        norm = math.sqrt(sum(v * v for v in vec.values()))
        return {t: v / norm for t, v in vec.items()} if norm else {}

    def scores(self, query):
        q = self._weigh(Counter(tokenize(query)))
        out = []
        for doc in self.vectors:
            if len(q) < len(doc):
                s = sum(w * doc.get(t, 0.0) for t, w in q.items())
            else:
                s = sum(w * q.get(t, 0.0) for t, w in doc.items())
            out.append(s)
        return out


class Index:
    def __init__(self, text_fields, keyword_fields=()):
        self.text_fields = list(text_fields)
        self.keyword_fields = list(keyword_fields)
        self.docs = []
        self.fields = {}

    def fit(self, docs):
        self.docs = list(docs)
        self.fields = {
            f: _FieldIndex().fit([d.get(f, "") for d in self.docs])
            for f in self.text_fields
        }
        return self

    def search(self, query, filter_dict=None, boost_dict=None, num_results=10):
        filter_dict = filter_dict or {}
        boost_dict = boost_dict or {}

        total = [0.0] * len(self.docs)
        for field, fidx in self.fields.items():
            boost = boost_dict.get(field, 1.0)
            for i, s in enumerate(fidx.scores(query)):
                total[i] += s * boost

        ranked = []
        for i, doc in enumerate(self.docs):
            if any(doc.get(k) != v for k, v in filter_dict.items()):
                continue
            if total[i] > 0:
                ranked.append((total[i], i))
        ranked.sort(key=lambda x: (-x[0], x[1]))
        return [self.docs[i] for _, i in ranked[:num_results]]
