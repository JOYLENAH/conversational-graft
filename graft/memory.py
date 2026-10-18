"""Session-state memory tracker.

Keeps the constraints that must survive across turns (child age, dependent
status, benefits already discussed) so they are never lost in a multi-turn chat.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Optional

AGE_PATTERNS = [
    re.compile(r"\b(\d{1,2})\s*[- ]?\s*(?:years?|yrs?)\s*[- ]?\s*old\b", re.I),
    re.compile(r"\baged?\s+(\d{1,2})\b", re.I),
    re.compile(r"\b(?:is|turned|turns|turning)\s+(\d{1,2})\b", re.I),
]
MONTH_PATTERN = re.compile(r"\b(\d{1,2})\s*[- ]?\s*months?\s*[- ]?\s*old\b", re.I)
STUDENT_PATTERN = re.compile(r"\b(full[- ]?time student|student|university|college)\b", re.I)
NEWBORN_PATTERN = re.compile(r"\b(newborn|new born|just born|a baby)\b", re.I)
DEPENDENT_PATTERN = re.compile(
    r"\bmy\s+(son|daughter|child|kid|baby|boy|girl|toddler|teenager|niece|nephew)\b", re.I
)


@dataclass
class SessionState:
    age: Optional[int] = None
    age_in_months: Optional[int] = None
    is_dependent: Optional[bool] = None
    is_student: Optional[bool] = None
    benefits_discussed: list[str] = field(default_factory=list)
    turns: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("turns")
        d["turn_count"] = len(self.turns)
        return d


class MemoryTracker:
    """Extracts constraints from each user message and keeps them for the whole session."""

    def __init__(self) -> None:
        self.state = SessionState()

    def update(self, message: str) -> SessionState:
        s = self.state

        month_match = MONTH_PATTERN.search(message)
        if month_match:
            s.age_in_months = int(month_match.group(1))
            s.age = s.age_in_months // 12
        else:
            for pattern in AGE_PATTERNS:
                m = pattern.search(message)
                if m:
                    s.age = int(m.group(1))
                    s.age_in_months = None
                    break
            else:
                if NEWBORN_PATTERN.search(message):
                    s.age = 0

        if DEPENDENT_PATTERN.search(message) or re.search(r"\bdependent", message, re.I):
            s.is_dependent = True
        if STUDENT_PATTERN.search(message):
            s.is_student = True

        s.turns.append({"role": "user", "text": message})
        return s

    def record_benefit(self, benefit_name: str) -> None:
        if benefit_name not in self.state.benefits_discussed:
            self.state.benefits_discussed.append(benefit_name)

    def record_answer(self, answer: str) -> None:
        self.state.turns.append({"role": "assistant", "text": answer})
