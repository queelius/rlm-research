---
status: complete_native_audit
date: 2026-09-10
planned_calls: 40
authenticated_calls: 40
valid_episodes: 8
strict_exact: 0
promotion_gate: false
---

# Direct sufficient statistics did not repair J1 aggregation

The native audit authenticated all 40 planned calls and reconstructed all eight episodes without a
NULL or observed-invalid result. The direct-statistics bundle nevertheless scored 0/8 exact, the
same exact count as the historical full-label control, and had lower absolute error in 0/8 paired
episodes. It fails the frozen promotion gate and meets the frozen retirement condition.

This is a semantic failure, not an availability or JSON-contract failure. The model returned every
required user with the required Boolean and nonnegative integer fields. Its `has_target_a` values
were correct for 28/32 episode-user pairs. The dominant problem was `target_b_weight_sum`: summed
per-user absolute error was 1,706. Episode-answer absolute error totaled 1,805, versus 117 for the
shared full-label control. At size 64, mean absolute error was 86.0 versus 7.25; at size 256 it was
365.25 versus 22.0. Thus the direct interface made the existing non-exact answers substantially
worse as inputs grew.

The result retires this exact intervention bundle: task-aware prompt, direct statistics format, and
LLM summation. It does not show that sufficient statistics are intrinsically unhelpful, nor isolate
output compression, because the prompt, action space, and requested computation changed together.
It also does not diagnose a human-reviewed semantic cause. The observed pattern is compatible with
the child failing to reliably classify and add the target-B weights inside each 32-record chunk.

## Availability and cost

- 40/40 HTTP 200, native-authenticated, schema-valid calls; 8/8 valid merged episodes.
- 0 observed-invalid calls or episodes; 0 NULL calls or episodes; no partial salvage.
- New direct-statistics cost: 83,546 input tokens, 3,382 output tokens, and 40,256 reported cached
  input tokens. No usage fields were missing.
- The historical control contributes 40 shared calls counted once: 71,426 input, 24,629 output, and
  37,520 cached tokens. The comparison therefore references 80 physical calls in the union, not 80
  independent observations.
- Owner elapsed time was 59.72 seconds; the parent exited 0 after 60.25 seconds, with the service
  released and no GPU process retained.

## Interpretation

The full-label control was already 0/8 exact, but it stayed much closer numerically. Asking the same
child for the final per-user evidence did not bypass its main error source; it concentrated more
semantic classification and arithmetic into one unverified answer. The next harness experiment
should change the information source or verification boundary, rather than request another sample
of the same calculation. A trained or independent verifier, or reference-derived TRAIN-only support
for learning a root plan, remains more discriminating than further same-child rechecks.

## Provenance and limitations

The prospective reader fixed the actual mapping before outcomes: four 64-record episodes use two
32-record chunks each and four 256-record episodes use eight chunks each, totaling 40. Gold entered
only after native parsing and public-user merge. The audit did not execute sampled code and did not
perform fresh manual semantic annotation. These are eight correlated episodes from four nested
clusters using one trained checkpoint; they are not independent replications or a general estimate
across tasks, models, or prompts.

Source pins: OWNER `e34fcc7a...`; parent EXIT `b816c823...`; prospective METHOD `09fbf7a4...`;
reader `ff5fbcbe...`; reader tests `719cd93e...`; frozen reader receipt `fa9d960a...`; native audit
JSON `a9a4bf55...`.
