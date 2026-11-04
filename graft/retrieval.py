"""Hybrid retrieval: graph facts + vector search over exact clause text + structured policy lookups.

The vector side uses TF-IDF behind a small interface. Swap in FAISS or
sentence embeddings later by implementing the same `search` method.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .graph import PolicyGraph


@dataclass
class Clause:
    clause_id: str
    text: str
    score: float = 0.0


@dataclass
class RetrievalResult:
    query: str
    graph_facts: list[dict[str, Any]] = field(default_factory=list)
    clauses: list[Clause] = field(default_factory=list)
    structured_data: dict[str, Any] = field(default_factory=dict)

    def to_context_str(self) -> str:
        """Converts retrieved context into a coherent prompt-ready block for the LLM."""
        sections = []

        if self.structured_data:
            sections.append("### Structured Policy Benefits & Rules:")
            sections.append(json.dumps(self.structured_data, indent=2))

        if self.graph_facts:
            sections.append("### Graph Relations & Entities:")
            for fact in self.graph_facts:
                sections.append(f"- {fact}")

        if self.clauses:
            sections.append("### Relevant Policy Clauses:")
            for c in self.clauses:
                sections.append(f"[{c.clause_id}] (relevance: {c.score:.2f}):\n{c.text}\n")

        return "\n\n".join(sections)


class ClauseIndex:
    def __init__(self, clauses: list[Clause]) -> None:
        self.clauses = clauses
        if clauses:
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            self.matrix = self.vectorizer.fit_transform([c.text for c in clauses])
        else:
            self.vectorizer = None
            self.matrix = None

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
        if not self.clauses or self.matrix is None:
            return []
        q = self.vectorizer.transform([query])
        sims = cosine_similarity(q, self.matrix)[0]
        ranked = sorted(zip(self.clauses, sims), key=lambda x: x[1], reverse=True)
        return [Clause(c.clause_id, c.text, float(s)) for c, s in ranked[:k] if s >= min_score]


class StructuredPolicyStore:
    """Deterministic lookup engine for tables, waiting periods, and provider lists."""

    def __init__(self, processed_data_dir: Path | str | None = None) -> None:
        if processed_data_dir is None:
            processed_data_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
        self.data_dir = Path(processed_data_dir)
        self.schedules: dict[str, Any] = self._load_json("benefit_schedules.json")
        self.rules: dict[str, Any] = self._load_json("policy_rules.json")
        self.providers: list[dict[str, Any]] = self._load_json("providers.json") or []
        self.exclusions: list[dict[str, Any]] = self._load_json("exclusions.json") or []

    def _load_json(self, filename: str) -> Any:
        path = self.data_dir / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_tier_benefits(self, tier: str) -> dict[str, Any]:
        tiers = self.schedules.get("tiers", {})
        return tiers.get(tier.upper(), {})

    def find_limit(self, tier: str, benefit_name: str) -> dict[str, Any]:
        """Resolves specific limits like 'bed limit', 'maternity', 'dental', etc."""
        tier_data = self.get_tier_benefits(tier)
        if not tier_data:
            return {}

        results = {}
        benefit_clean = benefit_name.lower()

        # Search across inpatient, outpatient, and maternity sections
        for section in ["inpatient", "outpatient", "maternity"]:
            section_data = tier_data.get(section, {})
            if isinstance(section_data, dict):
                for k, v in section_data.items():
                    if any(token in k.lower() for token in benefit_clean.split()):
                        results[f"{section}.{k}"] = v

        if not results and benefit_clean in tier_data:
            results[benefit_clean] = tier_data[benefit_clean]

        return results

    def check_waiting_period(self, condition_or_service: str) -> dict[str, Any]:
        wps = self.rules.get("waiting_periods_months", {})
        query = condition_or_service.lower()
        matched = {}
        for k, v in wps.items():
            if k in query or any(term in k for term in query.split()):
                matched[k] = f"{v} months"
        return matched or {"general_waiting_periods": wps}

    def check_pre_authorization(self, service_text: str) -> bool:
        required = self.rules.get("pre_authorization_required", [])
        srv = service_text.lower()
        return any(item.lower() in srv or srv in item.lower() for item in required)

    def search_providers(self, location_or_name: str, tier: str | None = None) -> list[dict[str, Any]]:
        query = location_or_name.lower()
        matches = []
        for p in self.providers:
            name = p.get("name", "").lower()
            loc = p.get("location", "").lower()
            region = p.get("region", "").lower()
            if query in name or query in loc or query in region:
                if tier:
                    tier_list = p.get("network_tier", [])
                    if tier.capitalize() not in tier_list and "Standard" not in tier_list:
                        continue
                matches.append(p)
        return matches[:5]


class HybridRetriever:
    """Orchestrates ClauseIndex (semantic/TF-IDF), PolicyGraph, and StructuredPolicyStore."""

    TIERS = ["PLATINUM", "GOLD", "SILVER", "BRONZE", "COPPER", "MARBLE", "SENIOR_CITIZEN"]

    def __init__(
        self,
        graph: PolicyGraph,
        clause_index: ClauseIndex | None = None,
        store: StructuredPolicyStore | None = None,
    ) -> None:
        self.graph = graph
        self.clause_index = clause_index or ClauseIndex.from_graph(graph)
        self.store = store or StructuredPolicyStore()

    def _detect_tier(self, query: str) -> str | None:
        query_upper = query.upper()
        for t in self.TIERS:
            if re.search(rf"\b{t}\b", query_upper):
                return t
        return None

    def retrieve(self, query: str, tier: str | None = None, k: int = 3) -> RetrievalResult:
        detected_tier = tier or self._detect_tier(query)
        structured_matches: dict[str, Any] = {}

        # 1. Deterministic Rule & Limit Checks
        if detected_tier:
            structured_matches["tier"] = detected_tier
            matched_limits = self.store.find_limit(detected_tier, query)
            if matched_limits:
                structured_matches["limits"] = matched_limits
            else:
                structured_matches["tier_summary"] = self.store.get_tier_benefits(detected_tier)

        if any(w in query.lower() for w in ["wait", "period", "moratorium", "how long"]):
            structured_matches["waiting_periods"] = self.store.check_waiting_period(query)

        if any(w in query.lower() for w in ["preauth", "pre-auth", "authorization", "approval"]):
            structured_matches["requires_preauthorization"] = self.store.check_pre_authorization(query)

        if any(w in query.lower() for w in ["hospital", "clinic", "provider", "doctor", "where can i go"]):
            providers = self.store.search_providers(query, detected_tier)
            if providers:
                structured_matches["matching_providers"] = providers

        # 2. Vector Clause Retrieval
        clauses = self.clause_index.search(query, k=k)

        # 3. Graph Fact Retrieval
        graph_facts = []
        if hasattr(self.graph, "find_related_facts"):
            graph_facts = self.graph.find_related_facts(query)
        elif hasattr(self.graph, "get_node_data"):
            for c in clauses:
                node_data = self.graph.get_node_data(c.clause_id)
                if node_data:
                    graph_facts.append(node_data)

        return RetrievalResult(
            query=query,
            graph_facts=graph_facts,
            clauses=clauses,
            structured_data=structured_matches,
        )