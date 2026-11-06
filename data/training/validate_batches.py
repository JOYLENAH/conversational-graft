"""Validate structure and cross-references in generated Q&A batches."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

TRAINING_DIR = Path(__file__).resolve().parent
BATCH_FILES = [
    "batch_01_kido_age.json",
    "batch_02_kido_exclusions.json",
    "batch_03_kido_entities.json",
    "batch_04_jcare_junior.json",
]
REQUIRED_FIELDS = {
    "id",
    "policy_id",
    "source_file",
    "category",
    "review_status",
    "answerable",
    "memory",
    "clauses",
    "question",
    "answer",
}
CITATION_PATTERN = re.compile(r"\[([^\]]+)\]")


def load_batch(filename: str) -> list[dict[str, Any]]:
    path = TRAINING_DIR / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{filename}: top-level JSON must be an array")
    return data


def cited_ids(answer: str) -> set[str]:
    found: set[str] = set()
    for citation in CITATION_PATTERN.findall(answer):
        found.update(part.strip() for part in citation.split(","))
    return found


def main() -> int:
    errors: list[str] = []
    seen_ids: set[str] = set()
    total = 0

    for filename in BATCH_FILES:
        try:
            entries = load_batch(filename)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            errors.append(f"{filename}: {error}")
            continue

        total += len(entries)
        print(f"{filename}: {len(entries)} records")
        for index, entry in enumerate(entries):
            location = f"{filename} record {index + 1}"
            missing = REQUIRED_FIELDS - entry.keys()
            if missing:
                errors.append(f"{location}: missing fields {sorted(missing)}")
                continue

            example_id = entry["id"]
            if example_id in seen_ids:
                errors.append(f"{location}: duplicate ID {example_id}")
            seen_ids.add(example_id)

            clause_ids = set()
            for clause in entry["clauses"]:
                clause_ids.add(clause["id"])
                if clause.get("role") not in {"supporting", "distractor"}:
                    errors.append(f"{location}: invalid evidence role for {clause['id']}")

            citations = cited_ids(entry["answer"])
            if entry["answerable"] and not citations:
                errors.append(f"{location}: answerable example has no citation")
            if not citations <= clause_ids:
                errors.append(
                    f"{location}: citations lack matching evidence {sorted(citations - clause_ids)}"
                )
            if not entry["answerable"] and (entry["clauses"] or citations):
                errors.append(f"{location}: not-stated example must have no evidence or citations")

    print(f"Total records: {total}")
    if errors:
        print("Validation issues:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Unique IDs: {len(seen_ids)}; structure and citation references pass.")
    print("This check does not verify answers against the source policy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
