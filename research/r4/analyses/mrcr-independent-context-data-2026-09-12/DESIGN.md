---
schema: mrcr-independent-context-data-design-v1
created_utc: 2026-09-12
status: data_frozen_no_gpu_no_model_queries
source_split: official_mrcr_v2p1_2needle_4k_8k
claim_scope: exploratory_transfer_across_two_short_synthetic_contexts
---

# Independent-context MRCR root-learning data

## Question

Can a root-only update learned from three content-disjoint 4K--8K MRCR contexts improve the
official retrieval-and-copy score on two separately frozen content-disjoint contexts? This is a
small procedure-transfer test. Five public synthetic contexts are not strong generalization
evidence, and this design says nothing about transfer to 32K or longer contexts.

## Frozen split and row selection

The source is the cached official 2-needle 4K--8K CSV (82 rows; SHA-256 recorded in
`PROVENANCE.json`). The corrected review identified five contexts whose exact paired
`User`--`Assistant` conversation blocks do not overlap. Context identity is SHA-256 of the exact
source prefix `queries[:-len(view_ops)]`, including its trailing two newlines. The live adapter
removes trailing whitespace, so the freeze also records that second, adapter-normalized hash.

The split is outcome- and answer-blind: rank the five exact context hashes by
`SHA256("mrcr-independent-context-v1:split:" + context_sha256)`. The first three are training and
the last two held. This yields training contexts of about 4.5K, 5.7K, and 6.5K tokens and held
contexts of about 6.3K and 8.2K tokens.

Within each context, freeze four official rows. For each requested ordinal (`first`, `second`),
select the lowest and highest target-position fraction; ties use
`SHA256("mrcr-independent-context-v1:row:" + full_row_sha256)`. This covers early/late targets
without using answers or model outcomes. The resulting inventory is 12 training tasks and 8 held
tasks.

## Adapter and scoring contract

- Each selected row keeps its exact full `queries` bytes in `full-queries/<sha256>.txt`; this is
  the payload written to `/context.txt` by the current MRCR root-study task setup.
- The ordinary final `view_ops` question remains visible in the root prompt. No needle, answer,
  parser hint, or pre-extracted match is exposed.
- Host truth is stored separately with mode `0600`. The public manifests contain hashes and task
  geometry, not answers.
- Scoring is the pinned official `mrcr_v2_metric`, which finds the last requested marker with
  `rfind` and compares the returned suffix. Strict prefix, exact match, marker presence, and content
  similarity remain separate diagnostics.
- No held task is queried during this freeze. Held rows are for a later paired T=0 evaluation only.

## Smallest future comparison (not launched or implemented here)

Collect four T=0.5 root trajectories for each of the 12 training tasks (48 trajectories), using
the no-adapter cached 4B root, same-base child, depth 1, and six total root-plus-child turns from
the qualified calibration adapter. Preserve full native root actions/logprobs/masks and actual
root/child inspection receipts. A root-only optimizer step remains conditional on a separately
reviewed on-policy qualification and prospectively frozen mixed-reward gate. If admitted, compare
the unchanged start and updated root on the 8 held tasks at T=0 with paired task IDs and the same
child binding.

Do not reinterpret the prior 3,900-second proposal cap as measured trajectory time: it was a
65-minute aggregate cap for collection, update, and two evaluation services. Runtime caps for this
larger study must be based on completed calibration receipts.

## Cached five versus more official data

The cached five are the fastest decision-relevant choice for short-context procedure transfer:
they are already byte-pinned, each supplies at least ten targets, and the selected paired
conversation blocks are disjoint. Their limitations are material: one official synthetic source,
only five contexts, and only 4K--8K lengths.

The cached >=32K objects are not a valid independent-context alternative: each file contributes
only one context and their conversation content is nearly subsumed across length buckets. For a
long-context or stronger generalization claim, acquire additional official-compatible contexts
with content-disjoint generation sources before freezing the study. No additional object is needed
for this short exploratory comparison, so no new download was made.

## Decision rule

This data freeze only makes the comparison possible; it does not admit training. If the preceding
calibration does not establish protocol-valid context inspection and at least two mixed groups
with mean official score below 0.90, retire or redesign before optimizer work. If a later update is
run, treat held gains across both contexts as a replication target, not as broad MRCR
generalization.
