"""Build a normalized, review-only dataset from the pilot and generated batches."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TRAINING_DIR = Path(__file__).resolve().parent
PILOT_PATH = TRAINING_DIR / "pilot_qa.json"
REPLACEMENTS_PATH = TRAINING_DIR / "curated_replacements.json"
OUTPUT_PATH = TRAINING_DIR / "curated_draft_v1.json"
BATCH_FILES = [
    "batch_01_kido_age.json",
    "batch_02_kido_exclusions.json",
    "batch_03_kido_entities.json",
    "batch_04_jcare_junior.json",
]
POLICY_SOURCES = {
    "PRU/MED/041206/2023": "KIDO-MASTER-POLICY-231220-for-website.pdf",
    "JUBILEE-JCARE-JUNIOR-BROCHURE": "J-Care-Junior-Brochure.pdf",
}
SCOPE_REVIEW_IDS = {
    "KIDO-AGE-14",
    "KIDO-AGE-15",
    "KIDO-AGE-16",
    "KIDO-AGE-17",
    "KIDO-AGE-18",
    "KIDO-AGE-19",
    "KIDO-AGE-23",
    "JUNIOR-AGE-07",
    "JUNIOR-AGE-08",
    "JUNIOR-AGE-09",
    "KIDO-ENT-06",
    "KIDO-ENT-08",
}
NEAR_DUPLICATE_REVIEW_IDS = {
    "JUNIOR-AGE-04",
    "JUNIOR-AGE-06",
    "JUNIOR-EXCL-18",
    "JUNIOR-EXCL-19",
}


def read_array(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array in {path.name}")
    return data


def normalize(example: dict[str, Any]) -> dict[str, Any]:
    item = dict(example)
    policy_id = item["policy_id"]
    has_source_file = "source_file" in item
    item.setdefault("source_file", POLICY_SOURCES.get(policy_id, "unknown"))
    item.setdefault("answerable", item.get("category") != "not_stated")
    if not has_source_file:
        item["citation_namespace"] = "pilot_legacy_clause"
    elif policy_id == "JUBILEE-JCARE-JUNIOR-BROCHURE":
        item["citation_namespace"] = "brochure_page"
    else:
        item["citation_namespace"] = "policy_clause"

    normalized_clauses = []
    for clause in item.get("clauses", []):
        normalized_clause = dict(clause)
        normalized_clause.setdefault("role", "supporting")
        normalized_clause.setdefault("source_page", None)
        normalized_clauses.append(normalized_clause)
    item["clauses"] = normalized_clauses

    flags = list(item.get("curation_flags", []))
    if item["id"] in SCOPE_REVIEW_IDS:
        flags.append("check_relevance_to_research_scope")
    if item["id"] in NEAR_DUPLICATE_REVIEW_IDS:
        flags.append("check_for_near_duplicate")
    item["curation_flags"] = flags
    item.setdefault("review_status", "draft_needs_human_review")
    return item


def main() -> None:
    examples = read_array(PILOT_PATH)
    for filename in BATCH_FILES:
        examples.extend(read_array(TRAINING_DIR / filename))

    replacements = read_array(REPLACEMENTS_PATH)
    replacements_by_id = {item["id"]: item for item in replacements}
    replaced_ids = set(replacements_by_id)
    merged_by_id = {item["id"]: item for item in examples}
    missing_ids = replaced_ids - merged_by_id.keys()
    if missing_ids:
        raise ValueError(f"Replacement IDs not found in pilot/batches: {sorted(missing_ids)}")
    merged_by_id.update(replacements_by_id)

    merged = [normalize(item) for item in merged_by_id.values()]
    output = {
        "dataset_name": "Conversational GRAFT curated review draft v1",
        "status": "draft_needs_human_review",
        "record_count": len(merged),
        "source_batch_count": len(BATCH_FILES),
        "records": merged,
    }
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(merged)} records to {OUTPUT_PATH.name}")
    print(f"Applied {len(replaced_ids)} saved corrections: {', '.join(sorted(replaced_ids))}")
    print("All records remain unapproved drafts; no train/evaluation split was made.")


if __name__ == "__main__":
    main()
