# Prespecified implementation amendments

This pilot implements the approved `DESIGN_V2` comparison, with three corrections fixed before any
outcomes exist.

1. The 48 task/repeat pairs are nested within 24 tasks and eight context documents. Paired
   win/loss/tie counts are descriptive. The report gives eight context-cluster deltas and does not
   emit a naive 48-pair sign-test p-value.
2. No already-qualified shared per-request admission limiter exists in this collector stack. The
   value 600 is therefore an admission-stop trigger checked before each 24-episode ABBA block, not
   a hard physical-request cap. The result records physical requests before/after every block and
   any measured overshoot. The owner and external wall caps remain hard at 1800 and 1900 seconds.
3. The leave-one-context-out family router is diagnostic only. It uses the benchmark-supplied
   family field, trains its six binary preferences only on the other seven context groups, carries
   unavailable pairs separately, and never consults held-context outcomes while selecting a mode.
   It is not a deployable learned planner and supplies no evidence about features inferred from raw
   task text.

Both conditions retain the identical raw context, records and query, Python ABI, task prompt,
temperature 0.5, 2048-token root cap, QS6 root and c32 child binding. The nano-RLM system prompt
truthfully advertises `rlm` only when `max_depth=1`; at `max_depth=0` the callable guidance is absent.
There is no confidence field, judge, update, retry, or gold answer in the model input. Protected
contexts are research-exposed and were seen by c32 SFT, so this is a mechanism/headroom study, not a
generalization estimate.
