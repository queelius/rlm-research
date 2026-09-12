# Next controller comparison: make execution results observable

The smallest decision-relevant follow-up should hold the root, child maps, questions, seeds, and
execution budget fixed while changing only the result-delivery behavior.

## Arm A: print-only procedural SFT

Train a small, fixed root SFT dose from train-only demonstrations whose every executable reducer ends
in exactly one `print(integer)`. Mask prompts, tool observations, and child actions; train root actions
and terminal response as separate reported token classes. Reject a demonstration before training if a
real-container/fake-provider replay does not produce a nonempty integer observation followed by the
matching terminal answer. Do not filter by evaluation outcome.

Compare the fixed checkpoint with unchanged QS6 on prospectively frozen contexts. Primary mechanism
metrics are: silent reducers, observed-scalar→matching-final consistency, exact intended-scope
reducers, and endpoint correctness. Promote only if silent reducers fall without increasing invalid
actions and the endpoint gain appears in at least two context clusters; retire if observation improves
but endpoints do not, because aggregation or helper quality is then the binding constraint.

## Arm B: explicit return-channel control

As a non-learning control, route a supported scalar result directly through the engine's existing
`FINAL_TEXT`/`FINAL_RESPONSE` mechanism after authenticated execution. Require an exact supported AST
and otherwise preserve failure/unknown status—no answer fallback. This isolates “computed correctly
but lost between Python and final LM” from “computed the wrong quantity.” It is **not a novel API**:
the core RLM already provides these return channels. The research contribution would be the controlled
measurement and, if useful, training a policy to use the channel reliably.

Use fresh contexts or a preregistered held subset; the eight contexts audited here are diagnostic data.
Report the explicit-return arm's saved root-model calls separately because bypassing a final model turn
changes cost. Neither arm repairs helper misclassification, and exact aggregates created by label-error
cancellation must remain separately labeled.
