# Paired step-1 evaluation handoff

This training owner creates two child-only checkpoints from one shared fresh 32-by-4 action
collection. It does not evaluate or select either checkpoint. The comparison is eligible only when
the top-level `outputs/attempt-001/RESULT.json` has status `COMPLETED_PAIRED_ONE_STEP`, both branch
results have status `UPDATED`, and each reports exactly one optimizer step. A stopped run or a
`COMPLETED_WITH_NO_UPDATE_BRANCH` result is not eligible for the paired evaluation.

For each branch (`rloo`, `other31`):

1. Verify this sidecar's complete READY closure and identity. Authenticate the top-level result,
   shared `COLLECTION.json`, all 32 shared group commits, and their pinned `ROLLOUT.json`,
   `MASKS.npz`, and RNG files. Both branches must name the same shared-collection SHA and each
   branch replay must pin the matching shared rollout and mask hashes.
2. Require all 128 fresh actions, all failures included, no importance weighting, sequence-sum loss
   with denominator 128, and all 32 exact on-policy probability gates passing before either update.
   The RLOO branch uses within-question leave-one-action-out advantages. The other31 branch uses a
   detached baseline equal to the mean reward of the other 31 questions' 124 actions; all four
   actions of the current question are excluded.
3. Require state schema `helper-hf-onpolicy-other31-paired-state-v1`, the exact branch name and
   baseline string, step 1, optimizer state steps `[1]`, original c32 start SHA, and the shared
   collection SHA. Verify checkpoint adapter/config/optimizer/RNG/state hashes and
   `STEP_COMMIT.json`. The two optimizers are separately fresh; state is not carried across arms.
4. Run `eligibility.validate_handoff(checkpoint, state, binding)`. Use only that branch's
   `checkpoint-0001/EVAL_BINDING.json`; it must replace only the fixed child adapter, retain the
   frozen root binding, and state `root_unchanged:true`.

An independent evaluator may reuse the exact fixed 256-record schedule, native request construction,
scorer, and 600-second inner / 700-second external caps from
`helper-hf-fourstep-unseen-eval-v1`. It must create distinct additive outputs for the two branches,
use paired evaluation seeds, and count missing/invalid outcomes separately. Do not select a branch
using this panel. The training contexts were previously used and the fixed evaluation panel has
already been examined, so this is an exploratory paired mechanism comparison, not pristine
generalization or an independent training replication.
