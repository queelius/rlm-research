# Conditional updated AG256 readout

Existing baseline: `helper-agnews-heldout-eval-v1/READY_C32_V2.json`, SHA
`0233757687489e9adcd7c8cb0c8548abadba212ef3ba1a2528655e9884596768`.
Its unchanged native argv is `owner_v2.py run --arm c32 --outer-seconds600`.
There is no new baseline collector or automatic source-result reuse here.

New updated arm: this directory's EVAL_READY.json; `eval_owner.py run
--outer-seconds600` under MAIN's shared lock and external700-second timeout.
Output: `eval/outputs/attempt-001`. Fixed source REQUESTS SHA
`28c4b9aa984b9aa2afb796b288ee338f576ae0d04c6f8de12cd3af7f70e3f549`.

Eligibility requires top RESULT UPDATED, clean complete OWNER_TERMINAL,
checkpoint-0001 state/optimizer actual step[1], finite positive gradient/delta,
all128 importance and gradient replay gates, rederived importance diagnostics,
full dataset/mask/raw source lineage, STEP_COMMIT hashes and exact child-only
EVAL_BINDING. Both the root binding and c32 source child identity remain pinned.
Partial, failed, no-update or unknown-step outputs are never evaluable.

The collector and AG-only scorer are the unchanged existing V2. Its native
evaluation runtime is intentionally matched to the baseline, not silently
equated with the batch-invariant training provider. No pooling with other
service flags/runtime panels. Raw source reuse needs separate runtime review.

Primary paired correctness uses all256 IDs; missing records remain unavailable
against that denominator. The existing V2 cost fields are observed subtotals
when usage is missing, not guaranteed total cost. New output records explicit
unknown-usage counts as well. This one-step exploratory package has no causal
isolation or general recursive-planning claim.
