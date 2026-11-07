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
from .memory import MemoryTracker, mentions_facts
from .metrics import constraint_retention, faithfulness
from .retrieval import ClauseIndex

# "Can she be covered?", "Is my son eligible?" -> a question about the child, not about a benefit.
ELIGIBILITY_QUESTION = re.compile(
    r"\b(eligible|eligibility|qualify|qualifies|join|enrol|enroll|add|added|dependent)\b"
    r"|\b(he|she|they|him|her|them|child|son|daughter|kid)\b[^?.!]*\b(covered|insured|cover)\b",
    re.I,
)
# Words that appear in almost every insurance question. They are removed before the fallback
# clause search, otherwise "Is acupuncture covered?" would match any clause containing "covered".
GENERIC_WORDS = re.compile(
    r"\b(cover|covers|covered|coverage|policy|insurance|include|included|includes|insured)\b", re.I
)
# When no benefit or age rule matched, a clause is used as the answer only if it is at least
# this similar to the topic words in the question. Otherwise the system says it could not find it.
FALLBACK_MIN_SCORE = 0.1
FOLLOW_UP = re.compile(r"\b(waiting|wait|exclu|excluded|limit)\w*", re.I)
DEFAULT_POLICY = Path(__file__).resolve().parent.parent / "data" / "sample_policy.json"


class GraftPipeline:
    def __init__(self, graph: PolicyGraph, index: Optional[ClauseIndex] = None, llm: Optional[LLM] = None) -> None:
        self.graph = graph
        self.index = index or ClauseIndex.from_graph(graph)
        self.llm = llm or RuleBasedLLM()
        self.clause_text = {c.clause_id: c.text for c in self.index.clauses}

    @classmethod
    def from_policy_file(cls, path: str | Path = DEFAULT_POLICY, llm: Optional[LLM] = None) -> "GraftPipeline":
        return cls(PolicyGraph.from_json(path), llm=llm)

    def chat(self, memory: MemoryTracker, message: str) -> dict:
        start = time.perf_counter()
        state = memory.update(message)

        # Pointed questions should not be answered with unrelated benefit facts.
        wants = set()
        if re.search(r"\bwait", message, re.I):
            wants.add("waiting_period")
        if re.search(r"\bexclu|not covered", message, re.I):
            wants.add("exclusion")

        # Graph facts: constraints from memory first, then benefit-specific rules.
        facts: list[Fact] = []
        benefits = self.graph.match_benefits(message)
        if not benefits and FOLLOW_UP.search(message) and state.benefits_discussed:
            last = state.benefits_discussed[-1]
            benefits = [b for b in self.graph.match_benefits(last)]

        # The age rule is relevant when the user is asking about the child, has just told us
        # about the child, or is asking about a benefit (then a short reminder is added).
        # It is not added to unrelated questions such as "Is acupuncture covered?".
        asks_eligibility = bool(ELIGIBILITY_QUESTION.search(message))
        if state.age is not None and not wants and (benefits or asks_eligibility or mentions_facts(message)):
            elig = self.graph.eligibility(state.age, state.is_student, detail=not benefits)
            if elig:
                facts.append(elig)
        for b in benefits:
            bf = self.graph.benefit_facts(b)
            if wants:
                bf = [f for f in bf if f.kind in wants]
            facts.extend(bf)
            memory.record_benefit(b["name"])

        # Vector retrieval over exact clause text (kept for evidence and as a fallback).
        clauses = self.index.search(message, k=3)
        fact_clause_ids = {f.clause_id for f in facts if f.clause_id}
        citations = sorted(fact_clause_ids)
        if not facts and not wants:
            topic = GENERIC_WORDS.sub(" ", message)
            strong = self.index.search(topic, k=2, min_score=FALLBACK_MIN_SCORE)
            citations = [c.clause_id for c in strong]
            facts = [Fact("clause", c.text, c.clause_id, c.text) for c in strong]

        summaries = [f.summary for f in facts]
        prompt = build_prompt(message, state.to_dict(), summaries, [(c.clause_id, c.text) for c in clauses])
        answer = self.llm.generate(prompt, summaries, citations)
        memory.record_answer(answer)

        # Numbers the user supplied (e.g. the child's age) are grounded in the conversation.
        conversation = " ".join(t["text"] for t in state.turns if t["role"] == "user")
        evidence = [f.text for f in facts] + [c.text for c in clauses] + [conversation]
        latency_ms = (time.perf_counter() - start) * 1000

        # Evidence for the UI: clauses the answer cites, then clauses retrieval
        # returned that the answer did not use (the "distractors" the model must ignore).
        faith = faithfulness(answer, evidence)
        # Retention is only scored when the remembered age was supposed to shape this answer.
        # A waiting-period or "not found" reply has nothing to retain, so it shows "Not applicable".
        age_matters = any(f.kind == "eligibility" for f in facts)
        retention = constraint_retention(answer, state.to_dict()) if age_matters else None
        evidence_items = [
            {"clause_id": cid, "text": self.clause_text.get(cid, ""), "used": True} for cid in citations
        ]
        evidence_items += [
            {"clause_id": c.clause_id, "text": c.text, "used": False}
            for c in clauses
            if c.clause_id not in citations
        ]
        return {
            "answer": answer,
            "citations": citations,
            "evidence": evidence_items,
            "memory_state": state.to_dict(),
            "scores": {
                "faithfulness": None if faith is None else round(faith, 3),
                "constraint_retention": None if retention is None else round(retention, 3),
                "latency_ms": round(latency_ms, 2),
            },
        }
