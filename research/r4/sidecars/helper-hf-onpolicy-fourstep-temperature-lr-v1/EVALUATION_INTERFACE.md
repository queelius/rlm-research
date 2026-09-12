# Fixed step-4 evaluation handoff

Each arm is eligible only when its exact `outputs/attempt-001/RESULT.json` says
`COMPLETED_FOUR_UPDATES`, records four optimizer steps, names checkpoint `checkpoint-0004`, pins the
arm runtime receipt, and its four state/qualification/collection/commit lineages verify. The step-4
state schema is `helper-hf-onpolicy-fourstep-arm-state-v1`; it must contain the READY arm's exact
`experimental_arm`, `temperature`, and `learning_rate`. The serialized optimizer must report step 4.
The `EVAL_BINDING.json` child-only update must contain the same `experimental_arm` and fixed seed
receipt, preserve the original root model, and point to the authenticated step-4 child adapter.

Use the exact already-frozen 256-record schedule and scorer from
`helper-hf-fourstep-unseen-eval-v1`, but write distinct additive outputs for `t2_lr1e5` and
`t1_lr1e4`. Cap each evaluation at 600 seconds internally / 700 externally. No step selection,
training mutation, action reuse, or claim of pristine generalization is permitted.
