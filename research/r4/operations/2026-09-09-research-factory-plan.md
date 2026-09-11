# Research evidence catalog: first increment

> For agentic workers: use the already active subagent-driven workflow. CPU-only
> curation runs alongside useful GPU experiments. MAIN reviews the resulting
> links and claims; this plan authorizes no new GPU study or source relocation.

**Goal:** Make completed evidence and new questions discoverable as a connected,
plain-language, machine-readable research record that supports later experiments
and honest publication decisions.

**Architecture:** Extend the existing dossier/reading-guide pattern with one
versioned post-cutoff JSON catalog and readable index. Existing raw outputs,
sealed audits, fixed-cutoff CLAIMS, DuckDB and Parquet remain unchanged. No new
database service, automatic paper writer, global metadata migration or framework.

**Tech stack:** Markdown and JSON; existing CPU Python/jq for validation. No
training environments, GPU use or speculative package installation.

**Authority:** User explicitly requests continued analysis/organization into a
research-idea/experiment/publication workflow and delegates design decisions.
The first increment is bounded to existing completed reports plus proposed
ideas; unanswered research choices stay documented, not blocking questions.

## Stable files and ownership

Agent owns only `analyses/research-factory-2026-09-09/`:
`README.md`, `CATALOG.json`, `CLAIM_CARDS.md`, `DECISIONS.md`, `VALIDATION.json`,
`SOURCE_MANIFEST.json`. No raw data copies. MAIN alone edits live queue, current
summary, global reading guide, session checkpoint and repo documentation.

## Record design

Use top-level arrays questions, experiments, claims, decisions, sources, and
publication_candidates. All entity IDs are stable namespace-qualified strings
(e.g. rq:correspondence, exp:fresh96, claim:shifted-cue-following), not array
positions. Relations refer to IDs. Include schema version, exact evidence
cutoff, source snapshot date and honest coverage boundaries. Newer unsealed
reports are pending evidence, not silently imported as confirmed results.

Questions record the falsifiable question, motivation, alternatives, status,
parent/related questions, supporting AND contrary claims, smallest follow-up,
readiness, estimated single-GPU shape/cap, and promotion/revision/retirement rule.

Experiments record question ID, planned comparison and immutable artifact paths,
actual completion/availability, source references, context/seed independence
unit and exposure, checkpoint/split provenance where available, and measured
optimizer/training/inference/outer/idle time separately. Missing measurements
are null with a reason; never infer training time from a job's wall clock.

Claims record a complete plain-language statement, fact/inference/hypothesis,
supporting experiment IDs, counterevidence, exact denominator and sampling unit,
availability sensitivity, alternative explanations, claim NOT justified, source
report hash, and evidence status. Distinguish repeated same-context checks,
new-root-source data, helper exposure, released-model checks and unknown
pretraining exposure. Do not average incomparable training doses or tests.

Decisions record the previous interpretation, new evidence, decision changed,
why, and linked follow-up question. Preserve corrections as additive revisions;
do not erase old collector scores or treat broker errors as sampled failures.

Publication candidates are organizing hypotheses, never automatic declarations
of publishability. Each needs central contribution, strongest supporting and
contrary evidence, verified primary-literature links, unverified citations
flagged, missing decisive experiments, reusable figure/report links and status
(exploratory/promising/follow-up-ready/confirmatory-ready/retired).

## Curation tasks

- [ ] Inspect the existing fixed-cutoff catalog format and use compatible source
  references where practical. Do not mutate catalog/campaign.duckdb or existing
  seals; note that this initial slice is not a complete historical catalog.
- [ ] Curate at least the following completed evidence: fresh96, shifted72,
  reminder-phase192, larger-update success-SFT48, boundedRL48, authored-planSFT48,
  query failure taxonomy, coverage48. Read the actual sealed REPORT for each
  before authoring a claim. Include older linked antecedents when needed, without
  pretending to have re-audited all original raw records.
- [ ] Add the new ideas1+5 and idea3 as the highest-ranked broader task-family
  question; idea6 as separate continuation-state line; ideas2/4/7 deferred.
  `new-ideas/ideas.md` is user-owned untracked source: hash/reference it read-only.
  MAIN's assessment distinguishes hand-designed sufficient reports from learned
  choice, partition robustness from depth generalization, and exact computation
  from a recursion benefit. The named OpenReview counterfactual citation could
  not be verified; preserve this uncertainty.
- [ ] Create three concise candidate claim cards: output-source correspondence;
  limited controller-training gains; sufficient recursive information (proposed,
  no result). Each must include contrary/negative evidence and the next decisive
  test. Scope the first two as exploratory rather than broad decomposition.
- [ ] Validate JSON parsing, unique entity IDs, all relation targets, exact
  referenced source hashes, existing local paths, and basic availability/count
  consistency. Report checks and coverage honestly, with no runtime/services.
- [ ] Return exact catalog/report hashes and a short list of query examples.

## Acceptance and maintenance

The record should support manual/jq searches for promising-but-not-confirmed
claims, questions blocked on data or implementation, effects checked on new
data, and corrections changing an interpretation. A pretty index without
source-linked facts is insufficient; a giant opaque database is unnecessary.
MAIN integrates links after review. New completed studies get additive catalog
snapshots or explicit revisions, never edits to scientific inputs or old seals.
Prepare at least two GPU successors when practical; this work must not delay an
independent ready job. No automatic submission, push, or publication action.
