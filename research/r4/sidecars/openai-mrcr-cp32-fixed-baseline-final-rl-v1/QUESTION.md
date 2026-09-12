---
schema: cp32-fixed-baseline-final-reinforce-question-v1
status: approved CPU implementation, optimizer launch not admitted
starting_checkpoint: openai-mrcr-procedural-sft-continue32-v1/outputs/attempt-001/checkpoint-0032
source_rollouts: openai-mrcr-procedural-sft32-onpolicy-screen-v1/outputs/attempt-004
baseline: fixed external constant0.5, not fitted within group
advantage: raw_exact minus0.5
loss_denominator: 32
sampling_temperature: 0.5
token_importance_cap: 2
importance_objective: prospectively biased detached per-token correction, not exact sequence IS
learning_rate: 0.00001
optimizer_steps: 1 maximum, fresh AdamW
caps_seconds: {science: 900, owner: 1100, external: 1200}
---

# Can one fixed-baseline terminal policy-gradient update change a collapsed copying policy?

The completed cp32/T.5 batch has28 exact and4 incorrect answers, all32 available, correct teacher-equivalent retrieval programs and clean target stdout. Each group repeats one answer four times. RLOO is exactly zero; fixed `r-.5` instead gives28 coefficients+.5 and4 coefficients-.5. This is a different, explicitly adaptive research objective, not a relaxed RLOO gate or newly observed variation. Nonzero coefficients do not guarantee a useful or even numerically nonzero parameter gradient.

For the fixed post-tool histories h_i, the ideal score-function estimator is `(1/32) sum_i (r_i-.5) grad log pi(y_i|h_i)`. A constant action-independent baseline has zero expected score-function contribution under exact sampling. The implemented capped token-TIS correction is biased; it is not exact native/HF on-policy equivalence or unbiased sequence importance sampling. The old failed sequence gate remains failed. Fresh HF scoring, finite/support checks and exact HF gradient replay are required, and complete conditional-final sequence ratios/ESS remain diagnostics. No silent objective fallback is used.

Only the actual bare terminal response action tokens and EOS carry direct loss. The prior root program and all input/tool/child tokens have zero direct loss. This optimizes final decisions conditional on recorded successful tool histories, not the whole RLM trajectory objective or a learned decomposition policy. LoRA weights are shared: excluding program-token loss does not freeze program behavior. Held and long rollout checks are essential.

Empirically, final action-token counts are9,988 positive and432 negative (10,420 total), with repeated trajectories providing eight distinct context units. Sequence-sum weighting is retained; it is not length-normalized or rebalanced to emphasize the wrong context. The wrong final has411 correct characters plus two extra LF characters. Token18611 encodes the gold's two trailing spaces together with the erroneous two LF characters, spanning offsets409..413. The preceding106 selected native token logps round to0; almost all observed negative-answer surprisal is on that mixed whitespace token and EOS. This motivates recording actual HF selected logps and parameter-gradient contributions by negative-group body/whitespace/EOS. It does not prove the update will isolate the error or preserve the preceding characters. No tail-only or gold-localized loss is substituted.

Recommendation: this is a small, lower-confidence mechanism probe, not evidence that a collapsed batch contains diverse exploration. It can answer whether fixed-baseline REINFORCE changes final copying/termination while retaining the learned procedure. It should not become repeated blind dose. A fixed one-step endpoint is compared with cp32 on both frozen short-held and long panels; accuracy, paired losses, unavailable outcomes and actual program/stdout/copy behavior are outcomes. Training likelihood movement alone is not a gain. A null, harmful or negligible update ends this candidate; no best checkpoint or repeated attempt until improvement.

