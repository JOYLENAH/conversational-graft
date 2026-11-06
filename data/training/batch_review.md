# Generated Batch Review

Status: review required; do not train on or merge the generated batches yet.

## Counts

The pasted batches contain 80 new records, but the batch sizes differ from the planned distribution:

- Batch 1: 24 KIDO age records (`KIDO-AGE-05` through `KIDO-AGE-28`), not 25.
- Batch 2: 25 KIDO exclusion records (`KIDO-EXCL-08` through `KIDO-EXCL-32`).
- Batch 3: 10 KIDO entity/relationship records.
- Batch 4: 21 J-Care Junior records: 6 age records and 15 exclusion records, not 20.

The pilot has 19 additional records, so retaining it would result in 99 records before any curation removals or replacements.

## Required Corrections

1. `KIDO-EXCL-27` and `KIDO-EXCL-32` are marked not stated, but the KIDO source has PE3: experimental or unproven treatment is excluded unless the Company has given specific pre-authorization (PDF page 34). Change these to answerable, include PE3 as supporting evidence, and word the answer conditionally. The policy does not specifically name gene editing or stem-cell therapy.
2. `KIDO-AGE-24` cites Clause 3.21(ii)(d), whose text refers to Insured members, not Dependents. Do not use it to claim when dependent-child coverage terminates. Replace the example with one grounded in the child eligibility clause or make the precise termination date not stated.
3. Keep the project's agreed scope: age/eligibility, exclusions, and entity/relationship distinctions. Reclassify or remove benefit questions such as lodger fees, vaccinations, premium pricing, dental benefits, and post-deletion claims unless the research scope is explicitly expanded.
4. Check for near-duplicates against the pilot. In particular, J-Care Junior newborn eligibility, genetic exclusions, and accident-related cosmetic surgery substantially overlap existing pilot examples.
5. Normalize all records to one schema before merging. The pilot uses simplified IDs such as `C1`; the new KIDO batches use source IDs such as `Clause 3.5(ii)` and `PE23`. Preserve a canonical source reference and create an explicit mapping if the prototype needs its simplified IDs. Keep J-Care brochure page citations distinct from KIDO clause citations.
6. Add verified `source_file`, `answerable`, `source_page`, and evidence `role` fields consistently. The pilot currently lacks these fields.
7. Human-review each answer and evidence excerpt, especially claims from the J-Care Junior brochure, which is a summary rather than the full policy.

## Merge Gate

Merge only after the actual batch JSON files are saved in this folder, parsed successfully, checked for unique IDs and matching citations, and reviewed against the source policy. Keep a held-out evaluation set separate from training examples. The generated examples are drafts and have not been human-approved.
