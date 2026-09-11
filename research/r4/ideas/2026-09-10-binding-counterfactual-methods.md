---
schema_version: "rlm-literature-decision-v1"
id: "idea:binding-counterfactual-controls"
status: "literature_informed_design_only"
updated_utc: "2026-09-10T03:39:00Z"
questions: ["rq:correspondence", "rq:adaptive-communication"]
primary_source: "https://arxiv.org/html/2510.06182v2"
paper_version: "v2, May 28, 2026"
acquisition: "../acquisitions/2026-09-10-mixing-mechs.json"
implementation_approved: false
gpu_launch_approved: false
---

# Test what an identifier refers to before naming an internal mechanism

## What the primary paper establishes

[Mixing Mechanisms](https://arxiv.org/html/2510.06182v2) uses counterfactual hidden-state
patching to distinguish position-based, lexical and reflexive retrieval in templated
entity-binding tasks. Its counterfactuals make the proposed mechanisms predict
different entities. A further absent-target control and later-layer intervention
distinguish a pointer from an already retrieved answer. Nine models are studied,
but not every model receives every task. The headline near0.95 metric is
Jensen–Shannon similarity of distributions, not95% task accuracy. Appendix G pads
shorter entity lists to distinguish entity count from sequence length. MAIN read
the introduction, main methods/results, and Appendices F/G, not all supplementary
experiments. These findings motivate controls; they do not identify the internal
cause of our Qwen3 classification errors.

## What this changes in our interpretation

Our strongest current result is behavioral. Under an exact output contract,
misleading IDs can shift a semantic prediction toward the other record bearing
that ID. Unrelated IDs avoid much of the deficit on the old panel. This alone
does not establish a particular attention head, residual subspace, or retrieval
algorithm. Matching, misleading and unrelated arms also change the emitted tag
strings. The source-assignment control below can remove that difference without
requiring invasive neural instrumentation.

## Next small experiment, conditional on the queued replication

Keep the per-position requested tags and the entire output grammar fixed. Change
only which opaque IDs are assigned to the visible source records: aligned,
permuted to another record, or unrelated to all requested tags. All text, order,
semantic labels and sampling coordinates remain fixed. Aligned and permuted arms
share the same ID multiset and should have equal input token counts; verify actual
rendering rather than assume it. Unrelated IDs require tokenizer-length matching.
That third arm still changes alias repetition, so it does not by itself isolate
referent semantics from repetition.

Use the sixteen already frozen new-alien contexts, after their current evaluation,
with one new paired seed per context and all48 endpoints retained. This is an
explicitly reused mechanism panel, not fresh confirmation. One existing4B service,
four workers and a20-minute outer cap should comfortably cover the comparison;
prior48-endpoint timing suggests roughly5–10minutes, not a guarantee. Metrics are
whole-contract validity, displayed-record accuracy, named-record direction on
unequal-gold positions, and paired context differences. The clean aligned-versus-
permuted contrast asks whether reassignment still changes predictions when the
output tag sequence is literally unchanged.

If the effect survives, prioritize scope tests and a useful harness mitigation.
If it vanishes, investigate differences in emitted token histories before
claiming a general source-linking effect. A later neural replay assay would need
separately frozen layer/position choices, identity-patch controls, counterfactual
inputs making hypotheses disagree, and new exposure/timing records. It must not
retroactively turn the behavioral result into an identified internal mechanism.

## Official code acquisition and execution boundary

The [official repository](https://github.com/yoavgur/mixing-mechs) was acquired at
commitc53372c606e7cadf2494d2ac7b08e466042052df:49 tracked files,43,610,304bytes,
with hashes in the receipt. Root license is MIT; the README identifies a modified
vendored CausalAbstraction copy. MAIN read the README/license/requirements fully
and only the first185 lines of tasks/dist.py and180 of grammar/schemas.py.
No code, notebook or serialized object was executed. The dependency list contains
merge-conflict markers, and the inspected prompt wrapper slices rendered text
unconditionally. It is a method reference, not a drop-in qualified runtime.
No environment was installed and no GPU work was displaced.
