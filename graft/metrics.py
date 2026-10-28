"""Lightweight evaluation metrics (proxies; refine for the W5 comparative evaluation).

Each metric returns None when there is nothing to check, so a reply with no
figures or no remembered constraints is not given an empty "100%".
"""
from __future__ import annotations

import re
from typing import Optional

NUM = re.compile(r"\b\d+\b")


def faithfulness(answer: str, evidence_texts: list[str]) -> Optional[float]:
    """Share of numbers in the answer that also appear in the evidence.

    Catches the most damaging hallucinations in insurance (wrong ages, days,
    limits). 1.0 means every number is supported. None means the answer states
    no figures, so there is nothing to verify.
    """
    nums = NUM.findall(answer)
    if not nums:
        return None
    evidence = " ".join(evidence_texts)
    supported = sum(1 for n in nums if re.search(rf"\b{n}\b", evidence))
    return supported / len(nums)


def constraint_retention(answer: str, state: dict) -> Optional[float]:
    """Share of remembered constraints (currently age) that the answer reflects.

    None means nothing has been remembered yet, so there is nothing to retain.
    """
    checks = []
    if state.get("age") is not None:
        checks.append(bool(re.search(rf"\b{state['age']}\b", answer)))
    return sum(checks) / len(checks) if checks else None
