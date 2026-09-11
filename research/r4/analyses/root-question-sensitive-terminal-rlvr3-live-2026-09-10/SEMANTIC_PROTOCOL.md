---
status: prospective_manual_protocol
date: 2026-09-10
scope: protected_composed_start_vs_fixed_last
planned_rows: 96
---

# Executed-composition manual review protocol

Review every observed composed endpoint in `MANUAL_PACK.json`; leave availability
NULL rows unjudged. Read the actual root programs, their tool observations, child
responses, and final in sequence. Do not infer behavior from variable names or
answer correctness alone, and do not execute sampled code.

For each observed row record:

- `acquisition_faithful`: requested records/labels were actually acquired for the
  requested scope; a deliberate sufficient subset must be justified from execution.
- `retained_complete_map`: acquired labels needed downstream were retained without
  silent drops, overwrites, invented labels, or ID mismatch.
- `requested_operator_scope_threshold_faithful`: executed aggregation implements
  the exact requested operator, users/scope, target categories, and strict threshold.
- `final_uses_observed_state`: the final is derived from the executed state/tool
  observation rather than a stale, hard-coded, or contradictory value.
- `strict`: terminal reward equals one. This is copied from authenticated scoring,
  not manually revised.
- `faithful_and_strict`: operator/scope/threshold faithfulness AND strict.
- `grounded_faithful_and_strict`: acquisition AND retained map AND operator fidelity
  AND final-use AND strict.
- `classification` and `note`: concise failure mode and concrete executed evidence.

When a faithful computation is wrong, compare actual child labels with the trusted
QS oracle in `root-question-sensitive-sft-v1/qs_problem.py` and name the label IDs
responsible. Do not expose host gold or protected labels to prompts, producers, or
training. Aggregate paired start/fixed-last changes overall and by eight protected
contexts only after all observed rows have judgments. Availability changes remain
separate from semantic changes.

