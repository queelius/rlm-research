# T1/T2 four-step signal audit

This read-only audit uses completed, authenticated training and fixed256 evaluation artifacts. It
does not execute saved model code, launch a model, or infer unsaved probabilities.

## Signal was sparse even though every update was real

Both arms repeatedly sampled the same familiar 32 TREC questions for four updates (128 group
occurrences, 512 actions). T1 produced 106 all-correct, 16 mixed, and 6 all-wrong groups. Thus only
16/128 group occurrences—64/512 action sequences—had nonzero within-question RLOO advantage. At
the question level, 22/32 were all-correct in every step, only 9/32 were ever mixed, and 2/32 were
ever all-wrong. `q1e1507ae2a62` was all-wrong in all four T1 steps; RLOO assigned its 16 failures
zero advantage. `q5294a29f02e0` alternated all-wrong/mixed and contributed only when mixed.

T2 increased exploration: 84 all-correct, 40 mixed, and 4 all-wrong group occurrences. Twenty of
32 questions were ever mixed, so 160/512 action sequences had nonzero RLOO advantage. This is a
substantial signal-density change, yet T2 and T1 produced exactly the same 256 fixed-panel labels.

The applied updates were not no-ops. T1 pre-clip gradient norms were
1.451/1.808/1.129/0.784; per-step adapter deltas were .0405/.0330/.0296/.0254 and cumulative L2
distance from c32 reached .1170. T2 norms were 1.474/3.237/1.380/1.370; deltas
.0405/.0339/.0243/.0253 and cumulative distance reached .1119. All recorded immediate replay
token, sequence, and audited-support errors were exactly zero. This authenticates each sampled
policy/replay boundary; it does not show that the resulting direction improves heldout behavior.

There is saved evidence that likelihoods moved on the repeated *training* prompts. Across
consecutive policies, byte-identical completion sequences could be paired one-to-one 262 times for
T1 and 259 times for T2; every paired sequence log-prob sum differed by more than 1e-6. Median
absolute changes were .248 and .213 (max 1.506 and .802). Pairing repeated identical rows is
descriptive and confined to familiar prompts, but it demonstrates why unchanged argmax labels need
not imply an unchanged policy.

## What fixed256 establishes—and does not

C32 scored 119/128 TREC and 112/128 AG News. Both T1 and T2 scored 120/128 and 112/128. The sole
change from c32 was TREC item `tee8c28875d38a31` (“What is the Moulin Rouge ?”), from `entity` to
the correct `description and abstract concept`. T1 and T2 were identical on all 256 predictions and
all 64 completion-token arrays.

The fixed256 call records contain completion token IDs but no per-token log probabilities. They
therefore cannot establish unchanged likelihoods or margins on those 256 examples. They establish
only identical T1/T2 temperature-zero outputs under this draw. Conversely, the training-prompt
log-prob movements cannot be projected onto heldout items.

## Decisions

1. **Use LR10x as the update-scale discriminator.** If LR10x yields a clear paired fixed-panel gain
   across more than one context/label without substantial losses, update magnitude was limiting and
   deserves a matched replication. If it mainly increases adapter distance while leaving the same
   256 argmax outputs (or trades wins for losses), stop treating step size as the primary bottleneck.
2. **Use the already queued paired RLOO versus other31 baseline as the reward-sparsity discriminator.**
   The same shared actions make this the smallest test of whether learning from all-wrong groups
   helps. Require a paired evaluation improvement rather than a larger training loss or delta. If
   neither branch improves, do not add further baseline variants.
3. **Then change data/task/component.** If LR10x, fast48, and the paired baseline do not produce a
   consistent heldout gain beyond isolated flips, the combination of nonzero parameter movement,
   increased T2 mixing, and unchanged T1/T2 predictions is enough to deprioritize mechanics tuning.
   Prefer the prospectively frozen broader AG News arm for helper-domain supervision, or the
   higher-priority root-recursion/freshadaptive experiments for decomposition/component learning.

The 32 training questions are not the 256 evaluation records. Success or failure on the familiar32
must not be reported as evaluation accuracy or generalization.
