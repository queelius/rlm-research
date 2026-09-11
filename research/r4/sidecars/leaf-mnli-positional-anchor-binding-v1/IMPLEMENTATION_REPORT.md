---
status: cpu_qualified_no_gpu
date: 2026-09-10
study: leaf-mnli-positional-anchor-binding-v1
---

# Positional-anchor96 implementation handoff

The isolated sidecar implements the approved 8-context × 3-reference ×
2-input-row × 2-output factorial. It freezes 96 unique coordinates and request
wires with eight calls per arm, paired seeds 996217101–108, mechanically rotated
arm order, and exact whole-output grammars. The largest native prompt plus the
3,072-token output allowance is 7,409, below the 8,192 context cap.

Input-row-present adds only the integer `row` field to each otherwise identical
record object. Input-row-absent label-only messages exactly reproduce the prior
natural prompt at the new seed. Row-first grammars require field order and fixed
row constants 0–47. Scoring never repairs or reorders and retains malformed
authenticated outputs as observed zero; missing or unauthenticated endpoints
remain NULL.

The released-base service, native response authentication, tokenizer/model
configuration, and lifecycle are source-pinned. A CPU integration fixture ran
the composed service entry through binding/configuration to the intercepted
launcher. The owner binds the exact attempt namespace, four-worker collector,
and 1800/1650/1770-second envelope with a 90-second release cap. No model service
or GPU was started.

Eleven focused tests passed in 90.11 seconds. Two pre-freeze qualification
failures were corrected without changing the science: the named seed scan now
excludes only this sidecar and its already-approved proposal, and provenance
pins the actual context source resolved by the loaded ancestor protocol rather
than a nominal sibling path. No science output exists. MAIN alone owns review,
acceptance, queueing, and launch.
