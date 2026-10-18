"""Conversational GRAFT pipeline.

Query -> session memory -> knowledge graph facts + vector clauses -> LLM -> grounded
answer with citations and scores.
"""
from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Optional

from .graph import Fact, PolicyGraph
from .llm import LLM, RuleBasedLLM, build_prompt
from .memory import MemoryTracker
from .metrics import constraint_retention, faithfulness
from .retrieval import ClauseIndex

ELIGIBILITY_WORDS = re.compile(r"\b(eligible|eligibility|cover|covered|join|enrol|enroll|add|qualify|old)\b", re.I)
FOLLOW_UP = re.compile(r"\b(waiting|wait|exclu|excluded|limit)\w*", re.I)
DEFAULT_POLICY = Path(__file__).resolve().parent.parent / "data" / "sample_policy.json"


class GraftPipeline:
    def __init__(self, graph: PolicyGraph, index: Optional[ClauseIndex] = None, llm: Optional[LLM] = None) -> None:
        self.graph = graph
        self.index = index or ClauseIndex.from_graph(graph)
        self.llm = llm or RuleBasedLLM()

    @classmethod
    def from_policy_file(cls, path: str | Path = DEFAULT_POLICY, llm: Optional[LLM] = None) -> "GraftPipeline":
        return cls(PolicyGraph.from_json(path), llm=llm)

    def chat(self, memory: MemoryTracker, message: str) -> dict:
        start = time.perf_counter()
        state = memory.update(message)

        # Graph facts: constraints from memory first, then benefit-specific rules.
        facts: list[Fact] = []
        benefits = self.graph.match_benefits(message)
        if not benefits and FOLLOW_UP.search(message) and state.benefits_discussed:
            last = state.benefits_discussed[-1]
            benefits = [b for b in self.graph.match_benefits(last)]

        if state.age is not None and (benefits or ELIGIBILITY_WORDS.search(message) or state.age is not None):
            elig = self.graph.eligibility(state.age, state.is_student)
            if elig:
                facts.append(elig)
        # A pointed question ("what is the waiting period?") gets only the matching rule kinds.
        wants = set()
        if re.search(r"\bwait", message, re.I):
            wants.add("waiting_period")
        if re.search(r"\bexclu|not covered", message, re.I):
            wants.add("exclusion")
        for b in benefits:
            bf = self.graph.benefit_facts(b)
            if wants:
                bf = [f for f in bf if f.kind in wants] or bf
            facts.extend(bf)
            memory.record_benefit(b["name"])

        # Vector retrieval over exact clause text (kept for evidence and as a fallback).
        clauses = self.index.search(message, k=3)
        fact_clause_ids = {f.clause_id for f in facts if f.clause_id}
        citations = sorted(fact_clause_ids)
        if not facts:
            citations = [c.clause_id for c in clauses[:2]]
            facts = [Fact("clause", c.text, c.clause_id, c.text) for c in clauses[:2]] if state.age is not None else []

        summaries = [f.summary for f in facts]
        prompt = build_prompt(message, state.to_dict(), summaries, [(c.clause_id, c.text) for c in clauses])
        answer = self.llm.generate(prompt, summaries, citations)
        memory.record_answer(answer)

        # Numbers the user supplied (e.g. the child's age) are grounded in the conversation.
        conversation = " ".join(t["text"] for t in state.turns if t["role"] == "user")
        evidence = [f.text for f in facts] + [c.text for c in clauses] + [conversation]
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "answer": answer,
            "citations": citations,
            "memory_state": state.to_dict(),
            "scores": {
                "faithfulness": round(faithfulness(answer, evidence), 3),
                "constraint_retention": round(constraint_retention(answer, state.to_dict()), 3),
                "latency_ms": round(latency_ms, 2),
            },
        }
