"""LLM interface.

`RuleBasedLLM` composes answers only from the evidence it is given, so the whole
pipeline runs and can be tested without a model. When the RAFT fine-tuned model
is ready, implement `LLM.generate` with it (e.g. Hugging Face + LoRA) and pass it
to the pipeline. The prompt builder is shared so both see the same input.
"""
from __future__ import annotations

from typing import Protocol


def build_prompt(question: str, state: dict, facts: list[str], clauses: list[tuple[str, str]]) -> str:
    """Distractor-resistant prompt: states the constraints, then evidence, then the question."""
    known = ", ".join(f"{k}={v}" for k, v in state.items() if v not in (None, [], 0) and k != "turn_count")
    clause_block = "\n".join(f"[{cid}] {text}" for cid, text in clauses)
    fact_block = "\n".join(f"- {f}" for f in facts)
    return (
        "You are a child health insurance advisor. Answer ONLY from the evidence below. "
        "Some retrieved clauses may be irrelevant; ignore them. Respect the known constraints. "
        "Cite clause ids in square brackets. If the evidence is insufficient, say so.\n\n"
        f"Known constraints: {known or 'none'}\n\n"
        f"Graph facts:\n{fact_block or '- none'}\n\n"
        f"Retrieved clauses:\n{clause_block or 'none'}\n\n"
        f"Question: {question}\nAnswer:"
    )


class LLM(Protocol):
    def generate(self, prompt: str, facts: list[str], citations: list[str]) -> str: ...


class RuleBasedLLM:
    """Deterministic stand-in: stitches the graph facts into a grounded answer."""

    def generate(self, prompt: str, facts: list[str], citations: list[str]) -> str:
        if not facts:
            return (
                "I don't have enough information in the policy to answer that. "
                "Could you tell me your child's age and which benefit you are asking about?"
            )
        cites = " ".join(f"[{c}]" for c in citations)
        return " ".join(facts) + (f" {cites}" if cites else "")
