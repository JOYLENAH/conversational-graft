"""Hybrid retrieval: graph facts + vector search over exact clause text.

The vector side uses TF-IDF for now behind a small interface. Swap in FAISS or
sentence embeddings later by implementing the same `search` method.
"""
from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .graph import PolicyGraph


@dataclass
class Clause:
    clause_id: str
    text: str
    score: float = 0.0


class ClauseIndex:
    def __init__(self, clauses: list[Clause]) -> None:
        self.clauses = clauses
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.matrix = self.vectorizer.fit_transform([c.text for c in clauses])

    @classmethod
    def from_graph(cls, graph: PolicyGraph) -> "ClauseIndex":
        seen, clauses = set(), []
        for _, d in graph.g.nodes(data=True):
            cid, text = d.get("clause_id"), d.get("text")
            if cid and text and cid not in seen:
                seen.add(cid)
                clauses.append(Clause(cid, text))
        return cls(clauses)

    def search(self, query: str, k: int = 3, min_score: float = 0.05) -> list[Clause]:
        q = self.vectorizer.transform([query])
        sims = cosine_similarity(q, self.matrix)[0]
        ranked = sorted(zip(self.clauses, sims), key=lambda x: x[1], reverse=True)
        return [Clause(c.clause_id, c.text, float(s)) for c, s in ranked[:k] if s >= min_score]
