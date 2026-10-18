"""Insurance policy knowledge graph.

Nodes: Policy, Benefit, AgeRule, WaitingPeriod, Exclusion.
Every rule node carries the clause_id and text it came from, so answers can cite it.
Backed by NetworkX for now; the interface is small so Neo4j can replace it later.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import networkx as nx


@dataclass
class Fact:
    kind: str          # "eligibility" | "waiting_period" | "exclusion" | "benefit"
    summary: str
    clause_id: str
    text: str


class PolicyGraph:
    def __init__(self) -> None:
        self.g = nx.DiGraph()
        self.policy_id: Optional[str] = None
        self.policy_name: Optional[str] = None

    # ---- building -----------------------------------------------------
    @classmethod
    def from_json(cls, path: str | Path) -> "PolicyGraph":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "PolicyGraph":
        pg = cls()
        pg.policy_id = data["policy_id"]
        pg.policy_name = data.get("name", data["policy_id"])
        g = pg.g
        g.add_node(pg.policy_id, kind="policy", name=pg.policy_name)

        for r in data.get("age_rules", []):
            g.add_node(r["id"], kind="age_rule", **r)
            g.add_edge(pg.policy_id, r["id"], rel="HAS_AGE_RULE")
        for b in data.get("benefits", []):
            g.add_node(b["id"], kind="benefit", **b)
            g.add_edge(pg.policy_id, b["id"], rel="COVERS")
        for i, w in enumerate(data.get("waiting_periods", [])):
            wid = f"W{i + 1}"
            g.add_node(wid, kind="waiting_period", **w)
            g.add_edge(w["benefit_id"], wid, rel="HAS_WAITING_PERIOD")
        for e in data.get("exclusions", []):
            g.add_node(e["id"], kind="exclusion", **e)
            g.add_edge(e["benefit_id"], e["id"], rel="EXCLUDES")
        return pg

    # ---- querying -----------------------------------------------------
    def _nodes(self, kind: str):
        return [(n, d) for n, d in self.g.nodes(data=True) if d.get("kind") == kind]

    def eligibility(self, age: Optional[int], is_student: Optional[bool] = None) -> Optional[Fact]:
        """Which age rule applies to a child of this age, and are they eligible?"""
        if age is None:
            return None
        for _, r in self._nodes("age_rule"):
            if r["min_age"] <= age <= r["max_age"]:
                needs_student = "student" in r["text"].lower()
                if needs_student and not is_student:
                    summary = (
                        f"At age {age} a dependent is only eligible if a full-time student "
                        "and financially dependent."
                    )
                else:
                    summary = f"At age {age} the child falls within an eligible age band."
                return Fact("eligibility", summary, r["clause_id"], r["text"])
        return Fact(
            "eligibility",
            f"Age {age} is outside the eligible age bands in this policy.",
            "",
            "No age rule covers this age.",
        )

    def match_benefits(self, message: str) -> list[dict]:
        text = message.lower()
        found = []
        for _, b in self._nodes("benefit"):
            if any(k in text for k in b.get("keywords", [])) or b["name"].lower() in text:
                found.append(b)
        return found

    def benefit_facts(self, benefit: dict) -> list[Fact]:
        facts = [Fact("benefit", f"{benefit['name']}: {benefit['text']}", benefit["clause_id"], benefit["text"])]
        for succ in self.g.successors(benefit["id"]):
            d = self.g.nodes[succ]
            if d["kind"] == "waiting_period":
                facts.append(
                    Fact(
                        "waiting_period",
                        f"{benefit['name']} has a {d['days']}-day waiting period.",
                        d["clause_id"],
                        d["text"],
                    )
                )
            elif d["kind"] == "exclusion":
                facts.append(Fact("exclusion", f"Exclusion for {benefit['name']}: {d['text']}", d["clause_id"], d["text"]))
        return facts
