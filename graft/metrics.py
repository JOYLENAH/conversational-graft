"""Lightweight evaluation metrics (proxies; refine for the W5 comparative evaluation)."""
from __future__ import annotations

import re

NUM = re.compile(r"\b\d+\b")


def faithfulness(answer: str, evidence_texts: list[str]) -> float:
    """Share of numbers in the answer that also appear in the evidence.

    Catches the most damaging hallucinations in insurance (wrong ages, days,
    limits). 1.0 means every number is supported; an answer with no numbers scores 1.0.
    """
    nums = NUM.findall(answer)
    if not nums:
        return 1.0
    evidence = " ".join(evidence_texts)
    supported = sum(1 for n in nums if re.search(rf"\b{n}\b", evidence))
    return supported / len(nums)


def constraint_retention(answer: str, state: dict) -> float:
    """Share of remembered constraints (currently age) that the answer reflects."""
    checks = []
    if state.get("age") is not None:
        checks.append(bool(re.search(rf"\b{state['age']}\b", answer)))
    return sum(checks) / len(checks) if checks else 1.0
