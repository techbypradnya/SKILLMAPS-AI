"""
Lightweight local vector store (spec sections 23, 24).

Production guidance (README): swap this for pgvector or a hosted embedding
API by implementing the same `similarity(query, corpus)` interface — the
recommendation engine only depends on that function, not on TF-IDF
specifically.

For a zero-dependency, offline-friendly demo (spec section 44, "Demo
Intelligence Mode"), we use scikit-learn's TF-IDF vectorizer + cosine
similarity as a stand-in for semantic embeddings. It is lexical rather than
truly semantic, so results are captioned honestly wherever they're surfaced.
Cached per-process to avoid recomputation on every request.
"""
from __future__ import annotations

from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@lru_cache(maxsize=1)
def _vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(stop_words="english", ngram_range=(1, 2))


def similarity_scores(query: str, documents: list[str]) -> list[float]:
    """Returns cosine similarity of `query` against each of `documents`, 0-1."""
    if not documents or not query.strip():
        return [0.0] * len(documents)
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    corpus = [query] + documents
    try:
        matrix = vec.fit_transform(corpus)
    except ValueError:
        return [0.0] * len(documents)
    sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    return [float(s) for s in sims]
