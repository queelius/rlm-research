---
status: conditional_prospective_design_only
date: 2026-09-10
study: root-supplied-plan-selective-recheck-v1
gpu_authorized: false
implementation_authorized: false
maximum_gpu: 1xA100
outer_cap_seconds: 1800
episodes: 8
---

# Question

Conditional on the completed supplied-plan ceiling showing that c32 child-label mistakes materially
limit deterministic J1 answers, does rechecking the lowest-confidence 25% of labels improve child
maps and J1 answers more than rechecking a label-blind hash-uniform 25% at the same call shape?

This is a selection-policy test on eight already-frozen episodes, not a confidence-calibration test.
The four clusters recur at nested sizes 64 and 256, so the eight episodes are correlated. Their
source groups are research-exposed and c32-optimizer-exposed; the result cannot establish new-source
generalization or independent replication.

# Immutable starting point and conditional admission

The starting point is the exact 40 native 32-record calls in
`root-lambda-supplied-plan-ceiling-v1`, covering all four clusters at sizes 64 and 256. The baseline
map is the frozen complete c32 map formed from those calls; it is never regenerated for this study.
The design remains inactive unless all of the following are met:

1. MAIN supplies exact parent `EXIT.json` and `OWNER_TERMINAL.json` hashes, proves service release,
   and adopts an audit of all 40 calls.
2. All 40 calls and all 1,280 planned labels are native-authenticated, complete, and uniquely
   attributable to their frozen requests. A partial ceiling cannot be silently narrowed.
3. The pinned Qwen tokenizer exactly reconstructs every completion, and every emitted label has a
   nonempty token span wholly inside its JSON value. Any ambiguous boundary stops preparation.
4. The private audit establishes at least two baseline-wrong J1 episodes, including at least one at
   each size, whose scalar discrepancy is fully explained by predicted-versus-host label
   contributions while the host-label J1 reducer reproduces the frozen gold. If this condition fails,
   do not launch or weaken it; redesign around the remaining bottleneck.
5. The frozen c32 binding and qualified native reader remain byte-pinned, all proposed second-pass
   seeds pass the named-input collision scan, and MAIN explicitly accepts a newly sealed producer.

Host labels, gold answers, error identities, record length, predicted class names, and J1
contributions are excluded from selection. They become available only to the post-terminal audit.
Gold-class-stratified selection is not deployable and is not an arm.

# Label-only confidence selection

For each ceiling call, decode native completion token IDs using the exact pinned tokenizer and align
tokens to the authenticated JSON content. For every record, retain only log probabilities of tokens
fully inside the emitted label string. Exclude IDs, quotes, colons, commas, braces, whitespace, and
terminal special tokens. Confidence is the arithmetic mean of the chosen label-token log
probabilities; sequence sums are diagnostic only and cannot affect selection.

Within each 64- or 256-record episode, rank by ascending mean log probability. Select exactly
`size/4`: 16 or 64 records. Break exact score ties by SHA-256 of the canonical JSON array
`["root-supplied-plan-selective-recheck-v1/confidence-tie", episode_id, record_id]`. This tie break
is deterministic and label-blind.

The uniform arm independently selects exactly the same count by ascending SHA-256 of
`["root-supplied-plan-selective-recheck-v1/uniform", episode_id, record_id]`. Do not force overlap
or disjointness. Freeze the natural overlap by episode before execution.

# Second-pass context choice

Use selected-only repacking. Restore selected records to their original episode order, then make one
16-record call for each size-64 episode and two consecutive 32-record calls for each size-256
episode. Each arm therefore predicts 320 selected labels in 12 calls; total new work is 24 calls.
Use the same c32 adapter, exact classification definitions/instruction, structured six-label JSON
schema, tokenizer/chat envelope, temperature 0.5, top-p 1.0, top-k -1, max-tokens 2048, and native
capture contract as the ceiling. Only the selected record list and required schema keys differ.

This choice keeps the arms equal in reviewed labels and call shape, avoids the overhead and major
distribution shift of 320 single-record calls per arm, and avoids wasting generation on every member
of an original batch. Replaying unchanged 32-record contexts would preserve first-pass context but,
because selected records are distributed across batches, could approach rerunning all 40 calls per
arm and generate many labels outside the review budget. Repacking is therefore the bounded choice,
but context composition is part of the treatment and must be disclosed.

The second-pass prompt contains records and instructions only. It never includes prior labels,
confidence values, correctness hints, or gold, so there is no prior-answer anchoring condition.
Fresh seeds are paired across the confidence and uniform arms by episode and repack index; identical
seed does not imply identical context. Use `1002048101 + 2*episode_index + repack_index`, where
episodes are ordered `(cluster, size)` and repack index is 0 or 1. There is no retry or seed reroll.

# Merge and failure semantics

The original complete map is the immutable baseline. For an authenticated, contract-valid recheck
batch, overwrite every selected ID in that batch with the new label—even if it is lower-confidence or
wrong—and leave every unselected ID unchanged. Do not choose between old and new using gold, and do
not partially salvage an invalid batch.

The primary operational policy explicitly uses baseline retention: if a recheck batch is native
unavailable or authenticated but malformed, retain the old labels for every selected ID in that
batch. Record unavailable and invalid calls separately; never describe retained labels as successful
rechecks. A per-protocol view is also mandatory: an episode with any unavailable recheck batch is
NULL, while one with any authenticated-invalid batch is an observed invalid episode. This separates
operational fallback value from recheck efficacy.

The two arms share the 40 frozen baseline calls physically. Count that union once and map it to both
logical arms. New calls are distinct unless their complete request bytes are identical; preserve
request hashes, provider IDs, and logical-to-physical mappings. Report natural selected-ID overlap,
but do not reuse a response across nonidentical repacked contexts merely because a record overlaps.

# Measures and fixed decision rule

Child measures, all reported per episode and by size, are: initial errors selected and error recall;
selected-label old-wrong/new-right corrections and old-right/new-wrong regressions; selected-label
accuracy; merged full-map accuracy and net correct-label change; qualifying-user symmetric
difference; and per-record J1 contribution error. The initial selection diagnostics use private gold
only after both selections are frozen.

Downstream measures are deterministic J1 exact correctness, absolute scalar error, baseline
wrong-to-right repairs, baseline right-to-wrong regressions, and confidence-versus-uniform paired
wins/losses/ties. The public J1 reducer consumes only public records and the merged predicted map.
The host-label reducer and gold answer remain private audit oracles, never model inputs.

Promote to a larger fresh-context study only if:

- at least 11/12 new calls and 7/8 per-protocol episodes are valid in each arm;
- confidence has a larger merged-map net correction than uniform in at least 6/8 episodes, with a
  positive aggregate advantage separately at sizes 64 and 256;
- confidence has a positive downstream paired net versus uniform, with at least two more J1 wins
  than losses, and does not cause more baseline-correct regressions than uniform; and
- actual physical calls, input/output/cache tokens, elapsed time, and unknown usage fields show no
  material arm imbalance; a token-cost ratio outside 0.8–1.25 blocks an efficiency claim.

Failure to clear the gate is informative and triggers no reroll. Passing motivates replication; it
does not prove calibration, isolate context from selection, or show generalization.

# Budget and ownership

One A100, one reused qualified c32 service, 24 planned second-pass calls, four workers at most,
1,800 seconds outer cap with a shorter owned-work deadline that leaves cleanup reserve, no root-model
calls, no training, no checkpoint, and no producer implementation under this design task. MAIN alone
may approve, queue, and launch a later immutable sidecar.
