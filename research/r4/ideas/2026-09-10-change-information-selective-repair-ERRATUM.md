---
status: additive_erratum
date: 2026-09-10
superseded_card: 2026-09-10-change-information-selective-repair.yaml
replacement: 2026-09-10-change-information-selective-repair-revision-v2.yaml
---

# Full-context inventory and causal-language correction

The original card's 12-call count was wrong for the full-context comparison. Twelve calls is one
25%-selective-review arm. The sealed ceiling covers all records with 40 calls: each of four size-64
episodes uses four 16-record chunks and each of four size-256 episodes uses eight 32-record chunks.
The corrected experiment therefore makes 40 direct-statistics calls and reuses the exact 40 sealed
label-map controls without reexecuting them.

The direct interface must emit statistics only for `spec.users`. Across all required chunks, merge
`has_target_a` by OR and `target_b_weight_sum` by addition, then sum B weights only for eligible users
whose merged A flag is true. A missing required chunk makes the episode NULL. Host gold is scoring-
only and never enters the prompt, selection, or tuning.

The intervention bundles a task-aware prompt, a statistics schema, and LLM summation. It is not pure
output compression. Finally, the same-child recheck result is evidence compatible with correlated
errors; it does not prove correlated errors caused the failure. No actual human semantic review was
performed.
