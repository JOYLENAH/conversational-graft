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