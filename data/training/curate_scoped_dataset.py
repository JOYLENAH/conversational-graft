"""Create a scope-focused candidate and an audit of omitted draft records."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

TRAINING_DIR = Path(__file__).resolve().parent
SOURCE_PATH = TRAINING_DIR / "curated_draft_v1.json"
OUTPUT_PATH = TRAINING_DIR / "curated_training_candidate_v1.json"
AUDIT_PATH = TRAINING_DIR / "curation_exclusions.json"
EXCLUSIONS = {
    "KIDO-AGE-08": "Near-duplicate of the pilot's over-18 full-time student eligibility example.",
    "KIDO-AGE-10": "Near-duplicate of the pilot's premature-birth eligibility boundary example.",
    "KIDO-AGE-14": "Lodger-fee benefit question, outside the age/eligibility, exclusion, and entity scope.",
    "KIDO-AGE-15": "Lodger-fee benefit question, outside the age/eligibility, exclusion, and entity scope.",
    "KIDO-AGE-16": "Lodger-fee benefit question, outside the age/eligibility, exclusion, and entity scope.",
    "KIDO-AGE-17": "Senior Citizens dental-benefit question, outside the child age/eligibility, exclusion, and entity scope.",
    "KIDO-AGE-18": "Senior Citizens dental-benefit question, outside the child age/eligibility, exclusion, and entity scope.",
    "KIDO-AGE-19": "Vaccination benefit question, outside the age/eligibility, exclusion, and entity scope.",
    "KIDO-AGE-23": "Ongoing benefit after policy deletion, outside the agreed knowledge-layer scope.",
    "KIDO-ENT-06": "Master-policy enforcement rights are outside the child/dependent entity distinctions in scope.",
    "KIDO-ENT-08": "Fraud liability is outside the child/dependent entity distinctions in scope.",
    "JUNIOR-AGE-04": "Near-duplicate of the pilot's J-Care Junior newborn-at-38-weeks example.",
    "JUNIOR-AGE-06": "Near-duplicate of the pilot's J-Care Junior 0-17 age-range example.",
    "JUNIOR-AGE-07": "Premium-pricing question, outside the age/eligibility, exclusion, and entity scope.",
    "JUNIOR-AGE-08": "Lodger-fee benefit question, outside the age/eligibility, exclusion, and entity scope.",
    "JUNIOR-AGE-09": "Lodger-fee benefit question, outside the age/eligibility, exclusion, and entity scope.",
    "JUNIOR-EXCL-18": "Near-duplicate of the pilot's J-Care Junior genetic-exclusion example.",
    "JUNIOR-EXCL-19": "Near-duplicate of the pilot's J-Care Junior accident-related cosmetic surgery example.",
    "JUNIOR-EXCL-17": "Co-payment question is outside the agreed scope and lacks the provider details needed to determine whether the stated co-payment applies.",
}
ANSWERABILITY_CORRECTIONS = {
    "KIDO-AGE-27": {
        "category": "age_eligibility",
        "answerable": True,
        "clauses": [
            {
                "id": "Clause 3.5(ii)",
                "text": "Children aged over eighteen (18) years shall only be eligible if they are full-time students at a school, college or university and are not aged above twenty-five (25) years of age.",
                "role": "supporting",
                "source_page": None,
            }
        ],
        "answer": "The policy's stated rule requires children over 18 to be full-time students and not aged above 25. It does not state a disability exception, so please check with the insurer about this situation [Clause 3.5(ii)].",
    },
    "KIDO-AGE-28": {
        "category": "age_eligibility",
        "answerable": True,
        "clauses": [
            {
                "id": "Clause 3.5(ii)",
                "text": "Children aged over eighteen (18) years shall only be eligible if they are full-time students at a school, college or university and are not aged above twenty-five (25) years of age.",
                "role": "supporting",
                "source_page": None,
            }
        ],
        "answer": "The policy says children over 18 must be full-time students and not aged above 25; it does not state that part-time study qualifies [Clause 3.5(ii)].",
    },
}


def main() -> None:
    source: dict[str, Any] = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    records = source["records"]
    ids = {record["id"] for record in records}
    missing = EXCLUSIONS.keys() - ids
    if missing:
        raise ValueError(f"Exclusion IDs not present in the source draft: {sorted(missing)}")

    included = [record for record in records if record["id"] not in EXCLUSIONS]
    for record in included:
        if record["id"] in ANSWERABILITY_CORRECTIONS:
            record.update(ANSWERABILITY_CORRECTIONS[record["id"]])
        record["review_status"] = "draft_needs_human_review"

    output = {
        "dataset_name": "Conversational GRAFT scope-focused training candidate v1",
        "status": "draft_needs_human_review",
        "record_count": len(included),
        "source_record_count": len(records),
        "excluded_record_count": len(records) - len(included),
        "records": included,
    }
    audit = {
        "status": "draft_curation_decisions_for_human_review",
        "excluded_record_count": len(EXCLUSIONS),
        "excluded_records": [
            {"id": record_id, "reason": reason}
            for record_id, reason in EXCLUSIONS.items()
        ],
    }
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    AUDIT_PATH.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    categories = Counter(record["category"] for record in included)
    print(f"Candidate records: {len(included)} of {len(records)}")
    print(f"Excluded for review: {len(EXCLUSIONS)}; see {AUDIT_PATH.name}")
    print(f"Categories: {dict(categories)}")
    print("No records were approved, fact-verified, or split for training/evaluation.")


if __name__ == "__main__":
    main()
