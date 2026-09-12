---
schema: research-idea-v1
created_utc: 2026-09-12T13:30:00Z
status: conditional_not_admitted
priority: below_root_learning_and_evidence_selection
question: can_fixed_budget_sampling_find_more_useful_reward_contrast
trigger: evidence_that_data_are_learnable_but_uniform_RL_sampling_is_uninformative
source: https://arxiv.org/html/2602.01601v1
source_review: sections_4_5_6_and_appendix_E
training: one_paired_update_if_later_admitted
gpu_shape: one_A100_40GB_serial_collection_and_training
compute_cap_proposal_seconds: 1200
artifact_policy: additive_sidecar_frozen_inputs_raw_actions_optimizer_and_RNG
---

# Decide where to sample before seeing the answers used for training

## Why it might help

Our two new-news pilot collections had only five and six mixed-reward groups
out of32. Many groups always got three of four labels correct: their average
accuracy was75%, but their sampled reward variance was zero. Intermediate
accuracy therefore does not necessarily mean a useful learning signal.

VIP predicts prompt-level reward variability and allocates a fixed sampling
budget before the new training outcomes arrive. Its analysis makes assumptions
about correlations between rewards and projected gradients; the paper's
token-averaged gradient also differs from our sequence-summed, importance-weighted
estimator. Appendix E treats continuous rewards. This is motivation for a
comparison, not a theorem validating our implementation or a reproduction of
VIP. [Primary paper](https://arxiv.org/html/2602.01601v1).

## Our proposed small comparison

If the broader SFT/RL comparison shows that the material is learnable but RL
still has little reward contrast, compare uniform sampling with allocation
informed by an independent small pilot. Keep the same32 training prompts,
starting weights and total generation budget per arm. For example, a256-action
allocation arm spends64 actions on a two-per-prompt pilot and192 on fresh
training actions; the uniform arm spends all256 on eight-per-prompt training.
The pilot is real charged computation, not free data. Do not reuse its actions
in the training gradient after selecting their groups.

Freeze the allocation rule, at least two fresh training actions per prompt,
maximum per-prompt allocation, and exact total budget before any pilot. Weight
each prompt equally, averaging its own group first; do not accidentally give
more objective weight to prompts that received more samples. Use genuine count
variance, not mean item accuracy as a substitute. All action/likelihood and
optimizer checks still apply. A prospective follow-up must qualify the changed
estimator; no current sealed trainer silently acquires this behavior.

Measure useful mixed groups, nonzero-gradient sequences, sampled tokens/time,
and paired endpoint accuracy. Promotion requires an endpoint benefit or a
replicable equal-budget signal improvement worth a longer test. Retire it if
the pilot cost cancels the gain, the allocation fails to predict variability,
or useful contrast still does not improve decisions. Do not build a Gaussian
process service or sweep allocation knobs before this question earns a slot.

This idea cannot repair a wrong task component, bad decomposition, a broken
verifier, or a model that never produces a better answer. Root learning and
evidence-selection experiments remain ahead of it in the queue.
