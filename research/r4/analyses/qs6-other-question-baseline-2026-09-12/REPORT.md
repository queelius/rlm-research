# Leave-one-question-out baseline assessment

Status: CPU-only analysis; **no implementation or GPU launch approved**.

## Answer

Yes, under the current frozen-policy collection contract, the mean reward from the other 31
questions is an action-independent baseline for every sequence from the held-out question. Let

\[
b_{-g}=\frac{1}{4(32-1)}\sum_{h\ne g}\sum_{j=1}^{4}r_{hj}.
\]

The 124 actions used in `b_-g` are sampled independently of current sequence `y_gi`, conditional on
the fixed questions and pre-update policy. Therefore

\[
E[\nabla\log\pi(y_{gi}|q_g)b_{-g}]
=E[b_{-g}]E[\nabla\log\pi(y_{gi}|q_g)]=0.
\]

Consequently `(r_gi - b_-g) * sum_t grad log pi(y_git | prefix)` is unbiased for the same
sequence-sum expected-reward gradient as reward-only REINFORCE. The baseline must be detached, the
whole 32-question batch must be sampled before any update, and all four current-question actions
must be excluded. Shared model parameters do not invalidate the argument; action dependence or
within-batch policy updates would.

Within-question RLOO is also unbiased because each action's baseline uses only the other three
independent actions from the same question. The difference is finite-sample behavior. An all-wrong
group has exactly zero RLOO advantages, whereas the other-question estimator assigns approximately
`-b_-g` to every failed sequence. This is legitimate negative verifier evidence: it pushes down the
sampled failures without revealing which alternative is correct. The baseline term is zero in
unconditional expectation, so it does not create a new reward signal or identify a correct answer.

## Exact enumeration

`enumerate.py` exhausts all 64 outcomes of three independent binary-action questions with two
samples/question. All estimators use the same mean-reward scaling. In both toys, every estimator's
exact mean agrees with the analytic policy gradient to floating-point error.

| toy | estimator | variance trace |
|---|---|---:|
| three nonconstant reward functions | reward only | 0.0072333 |
|  | within-question RLOO | 0.0178000 |
|  | other questions | 0.0016042 |
| one learnable + constant-easy + constant-hard | reward only | 0.0157167 |
|  | within-question RLOO | 0.0041000 |
|  | other questions | 0.0156437 |

Thus the cross-question baseline can reduce variance, but it is not uniformly better. When question
difficulty differs sharply, it injects zero-mean gradient noise into genuinely constant easy/hard
questions; the second toy makes that visible. In the first toy, conditioning on question 0's
all-wrong event gives mean gradient `0.0216667` under the other-question baseline and zero under
reward-only/RLOO, while all three remain unbiased unconditionally.

## What the saved four-step batches imply

The completed T1/LR1e-5 run was dominated by homogeneous groups:

| update | all wrong | all correct | mixed | other-31 baseline range | RLOO-zero actions made nonzero |
|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 26 | 4 | 0.8871–0.9194 | 112/128 |
| 2 | 1 | 26 | 5 | 0.9032–0.9355 | 108/128 |
| 3 | 2 | 26 | 4 | 0.9032–0.9355 | 112/128 |
| 4 | 1 | 28 | 3 | 0.9194–0.9516 | 116/128 |

These high global baselines would give the rare all-wrong sequences large negative advantages
(roughly `-0.89` to `-0.95`) and all-correct sequences small positive advantages. That is a much
larger intervention than merely rescuing the one or two hard groups. It also changes backward cost:
the saved RLOO updates backpropagated through 54–93 autoregressive token steps, while making every
group nonzero would require 585–597 steps, a 6.35–11.0× increase in step-level backward work
(sampled action-token ratios are 6.55–11.24×). Forward collection and replay qualification remain
necessary either way.

## Relation to AVSPO

This is conceptually distinct from AVSPO. AVSPO inserts virtual rewards only into normalization
statistics for collapsed groups; its authors explicitly frame the resulting update as biased relative
to the original GRPO gradient. The other-question proposal injects no virtual outcomes and, under
the independence conditions above, is an ordinary unbiased REINFORCE control variate. It may still
have poor variance because it ignores question-specific difficulty. See the primary
[AVSPO v2 paper, Sections 4.2–4.3](https://arxiv.org/html/2605.21125v2#S4.SS2).

## Smallest fair experiment

Run one paired, single-update experiment before considering four updates:

1. Start from original c32 at T1 and collect one new immutable 32-question × 4-action batch under a
   prespecified fresh sampler seed. Save the exact actions, masks, rewards, and pre-step logprobs.
2. Branch two clean c32 model/optimizer states over that *same newly collected batch*: existing
   within-question RLOO versus `b_-g` above. Preserve LR `1e-5`, denominator 128, sequence-sum loss,
   grammar/replay tolerances, clip 1, and every other setting. This shared batch is the paired
   control; it is not historical reuse or independent replication.
3. Save both step-1 checkpoints and evaluate each on the exact fixed 256 panel with identical seeds.
   Report TREC and AGNews/context clusters, availability, cost, gradient norm, clipping, adapter
   delta, and the per-group gradient-norm contribution. Do not select checkpoints or tune from the
   panel.

Collection should remain about five minutes. The RLOO branch has reference-like cost; the
other-question branch may require roughly 6–11× more token-step backward work. A conservative first
training cap is 2400–3000 seconds for the shared collection plus both branches, followed by two
separate 600/700-second evaluations. Stop on memory, replay, or nonfinite-gradient failure rather
than changing normalization.

Promote only if the other-question branch produces a controlled finite update and improves the
fixed-panel pattern without a prohibitive cost/stability regression; then repeat with a fresh shared
batch. A null or worse endpoint, extreme clipping dominated by the one or two all-wrong questions,
or excessive compute should retire the full cross-question baseline in favor of a difficulty-aware
baseline or additional sampling. This single paired draw is exploratory, not a generalization claim.
