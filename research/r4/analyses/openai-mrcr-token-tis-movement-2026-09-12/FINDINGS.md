---
question_id: controller_training
status: completed_training_likelihood_diagnostic
date: 2026-09-12
training_episodes: 24
training_groups: 6
nonzero_advantage_groups: 2
branches: [lr1e-5, lr1e-4]
optimizer_steps_per_branch: 1
new_model_calls_in_analysis: 0
publication_readiness: mechanism_check_not_answer_improvement
---

# A larger RL update changes the rewarded trajectories more clearly

Both branches start from the same weights and random state and apply the same
saved gradient with a fresh Adam optimizer. Only the learning rate changes.
The adapter displacement is0.02968207 at1e-5 and0.29682077 at1e-4: a ratio of
10.00000073 with effectively identical direction. Training took106.45 seconds.

The smaller update increased the probability of one of two rewarded trajectories
and reduced four of six penalized trajectories. The larger update increased both
rewarded trajectories and reduced five of six penalized trajectories. At the
larger dose, mean log-probability change per token is+0.00834 for rewarded
trajectories and−0.00624 for penalized ones; the corresponding smaller-dose
values are+0.00103 and−0.00024. These are episode-weighted training-backend
measurements on saved attempts, not new responses or held-out accuracy.

The fixed-denominator advantage-weighted sequence log-probability change is
0.01720 at the smaller dose and0.44197 at the larger dose. It is not a KL
divergence or an estimator of return. The first/last-turn diagnostics in JSON
are positional, not independently authenticated semantic action categories.

Only two of six question groups supply a learning contrast;16 of24 advantages
are zero. The positive trajectories used broad conversation printing rather than
the intended retrieval procedure. Rewarded behavior is therefore not automatically
the behavior we ultimately want the RLM to learn.

## Numerical correction and its limit

The original whole-trajectory correction had effective sample size6.97/24 and
stopped before any update. The replacement uses detached per-token importance
weights capped at2, retaining all24 episodes in the denominator. Its token-level
effective sample size fraction is0.99773, and only2 of15,602 weights are capped.
That does not make it an unbiased correction for complete trajectories. The
original sequence-level diagnostics remain unchanged and visible.

The standard lower-variance approach is described in the pinned
[verl correction notes](https://github.com/verl-project/verl/blob/10db40d0da4d59150bb389960b77585f81a89b8d/docs/algo/rollout_corr_math.md).
Our measurement is not a novel estimator. It gives a controlled way to ask
whether a small update was hiding a useful learning signal.

## Decision and evidence

Evaluate the starting model and both fixed doses on the same16 separate
conversations. Do not select the larger dose because it has a more attractive
training diagnostic. A substantial probability change with no improved answers
would redirect attention toward reward relevance and exploration, not another
blind increase in learning rate.

[derive.py](derive.py) verifies all three likelihood inventory hashes, all72
episode-file hashes, exact physical prefix/action identities and branch relation,
then derives [FINDINGS.json](FINDINGS.json). It makes no model calls. It does not
independently reconstruct the gradient or establish historical hardware arithmetic.
