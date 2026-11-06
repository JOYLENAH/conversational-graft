# Pilot Q&A Dataset

`pilot_qa.json` is a draft supervised fine-tuning dataset for the current
knowledge-layer scope: policy-specific age eligibility and exclusions.

Each example keeps its policy ID, session memory, evidence text, question, and
grounded answer together. KIDO answers cite the policy's clause IDs. J-Care
Junior answers use brochure page references because the brochure has no clause
IDs. These page references are local source labels, not official clause numbers.

All examples are marked `draft_needs_human_review`. Review them against the
source documents before training. Do not combine examples across policies when
building a prompt or retrieval context. The JCare Johari document is omitted
because its policy data page has placeholders and the selected plan is unknown.

The examples are not yet a train/evaluation split and are not loaded by the
chatbot. More reviewed examples and held-out conversations are needed before a
meaningful fine-tuning run.

## Generated Batches

The generated draft batches are stored separately from the pilot:

- `batch_01_kido_age.json` (24 records)
- `batch_02_kido_exclusions.json` (25 records)
- `batch_03_kido_entities.json` (10 records)
- `batch_04_jcare_junior.json` (21 records)

Run `python data/training/validate_batches.py` from the repository root to
check JSON structure, unique IDs, evidence roles, and citation references. This
does not check factual accuracy. The four batches contain 80 draft records, but
some include out-of-scope topics or need policy review. See
`batch_review.md` and `curated_replacements.json`; do not train on the batches
until they have been reviewed and the pilot schema/citation IDs are normalized.

## Combined Review Draft

Run `python data/training/curate_batches.py` from the repository root to create
`curated_draft_v1.json`. It combines the 19 pilot records and four batches,
applies the three saved replacements, adds source/citation namespace metadata,
and flags known scope or duplicate-review candidates. It does not approve,
fact-check, or split the records, and it does not load them into the chatbot.
The combined draft needs human review before training or evaluation.