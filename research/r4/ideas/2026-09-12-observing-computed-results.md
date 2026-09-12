---
question_id: observing_computed_results
date: 2026-09-12
status: proposal_pending_trace_and_training_audit
evidence_level: posthoc_mechanism_observation
new_model_queries: 0
priority: conditional_after_current_controller_readouts
---

# Can the root see the answer its program computed?

In the fresh live-helper comparison, both helper variants produced three correct
final answers out of sixteen. The RL helper improved the observed category labels,
but not the exact final-answer count. We should not immediately respond by making
the helper bigger or training it longer.

Four inspected count trajectories (two questions, two helper variants) assigned
`answer = len(matches)` or `result = len(matches)` without printing the result.
Every Python observation in those trajectories was empty. The root then returned
`Answer: 2`. In contrast, an inspected weighted-sum trajectory explicitly printed
its computed sum; the final answer followed that observation, including when the
helper labels made the sum wrong. These are selected trace observations, not yet
a complete prevalence estimate or proof of causal dependence.

The newly exact helper-based count is particularly cautionary: its label change
appears to introduce a misclassification that cancels another error. A correct
aggregate is not necessarily evidence of correct underlying labels. The ongoing
trusted host reduction and training-provenance audit must resolve this before a
follow-up is selected.

## Candidate comparison after that audit

If missing visibility is common, compare unchanged execution with a small automatic
preview of changed scalar variables after a Python cell. This should expose only
actual runtime state, not host gold, an answer solver, or guessed state. Names,
types and bounded scalar values could make results observable without another
special command for the model to learn. Keep the root/helper weights, records,
limits and paired seeds fixed. A prompt-only explanation control would distinguish
the new observations from merely reminding the model to inspect its work.

Alternatively, train matched examples that explicitly print the computed result
before the model answers. This tests a training remedy rather than a new runtime.
First inspect the existing QS6 training examples: whether they teach silent
assignments, what observation is available before the final answer, and how varied
the final answers are. Do not assume a particular training defect until verified.

Use the entire fixed panel, not only the failures that motivated the proposal;
then replicate any gain on fresh context groups. Primary outcomes are exact final
answers and agreement with the *actually computed* value. Separate wrong programs,
wrong helper labels, invisible results, and failures to return an answer. Measure
added observation tokens and context failures. No output is repaired after scoring.

## Prior-art and scope limits

Explicit return-from-variable mechanisms already exist in RLM implementations.
This repository already has `FINAL_TEXT` and `FINAL_RESPONSE`; adding an equivalent
API to an experimental harness is not a new algorithm. The candidate scientific
question is whether automatic bounded state visibility helps a fixed small model
transfer an executable routine, relative to a matched training or prompting change.
An explicit-return control would also be useful, but must not silently treat every
variable named `answer` as authoritative or claim the MRCR broad dumps were correct
retrieval programs.

This document authorizes no GPU job or implementation. Expected first screen would
be a single-A100 paired rollout comparison of roughly 32–48 episodes, under thirty
minutes with per-episode artifacts, using existing frozen maps only if clearly
identified as replay rather than live helper computation. Choose exact controls
and caps after the complete audit; retire the proposal if the premise is rare or
the proposed observation would not contain the needed result.

Evidence: `analyses/root-qs6-ag-live-helper-transfer-independent-2026-09-12/outcome/REPORT.json`,
SHA256 `b6c2839135a4015c20277555f18daab48cbb29f45241c6863b9fc66a4f87ecbb`.
