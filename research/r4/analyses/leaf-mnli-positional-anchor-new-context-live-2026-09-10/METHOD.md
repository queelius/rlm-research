---
id: leaf-mnli-positional-anchor-new-context-v1-native-audit
status: prospective_pre_outcome
date: 2026-09-10
planned_endpoints: 192
---

# Fresh-context positional-anchor192 native audit method

After an exact terminal relay, audit all 192 frozen endpoints. Match the emitted
request bytes, expected prompt-token IDs, model, unique choice, completion-token
IDs/logprobs, usage, finish branch, and tokenizer-rendered message before scoring.
An authenticated malformed or wrong-route completion is an observed zero. An
absent request/response, non-200 response, or incoherent native envelope is NULL;
there is no reordering, repair, or partial label salvage.

Report all twelve relation × input-row × output-form cells, each with 16 calls
and 768 planned labels, early/late/total correctness, contract validity,
availability and NULL bounds. The primary estimand is the late-position
input-row × output-row interaction, averaged over wrong/alien/aligned references:
`(present row-first - present labels-only) - (absent row-first - absent labels-only)`.
Its frozen practical gate is at least 10 percentage points, a positive effect in
at least 12/16 paired contexts, and no row-first availability loss. Separately,
report whether present-row row-first improves late accuracy for every reference.
The original output-only contrast at input-row absent remains secondary; this
replication does not move its earlier gate.

Use sixteen contexts as the correlated units. Report simple effects by relation,
early/late/total results, native failure reasons, and the complete physical
REQUEST/RESPONSE/RESULT union with known and unknown prompt/completion/cache usage.
The panel is inventory-excluded from named earlier MNLI panels but is not claimed
globally or pretraining unseen.

This reviewer authored the producer and reader. The method is prospective with
respect to model outcomes and is reproducible, but not author-independent. No
producer output is read until terminal authorization.
