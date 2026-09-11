---
title: Composed-RL window 03 training failure and minimal recovery
date: 2026-09-10
status: diagnostic_complete_recovery_not_implemented
scope: cpu_source_and_retained_artifact_review_only
---

# Composed-RL window 03: failure and minimal recovery

## Bottom line

Window 03 did not apply update 2. Its frozen group is much larger than the group that
produced checkpoint 1, and the qualified trainer unnecessarily projects every causal
position through the 151,936-way language-model head even though the loss consumes only
the contiguous current-action positions. The log records a failed 1,939,865,600-byte CUDA
allocation and then the trainer's 240-second alarm interrupting `backward()`. This is an
infrastructure failure, not a zero-reward/no-update scientific result.

Using Qwen3's tensor-valued `logits_to_keep` for exactly the credited predecessor positions
is the smallest credible memory fix. It preserves the defined TIS/PPO objective and gradient
support mathematically, but it does **not** remove the transformer work over the full causal
history. A longer, explicitly bounded training allowance is therefore also required.

## Retained evidence

- Window 02 committed exactly one Adam update: 8 episodes, 24 root turns, 36,187 causal
  tokens, 2,145 action tokens, maximum sequence 1,964, and sum of squared sequence lengths
  55,923,025. Optimization took 15.330 seconds; peak allocated/reserved memory was
  9.802/16.123 GB. Checkpoint 1 is sealed by state
  `93300fe9cd8cb342f8a9aec8fbee833fd7da0a2caa97529ec44a177b73264c66`, adapter
  `358d2cefa3fe49f0f5201b0ddf7b4d55e63db9249be4e10b0dec17faa8c24244`, optimizer
  `f37d02fd4137ed59706f9d7b017604dd7c608d905ecc6b6e222293e13980f27b`, and RNG
  `855616cdeabe51ae463c56026606115a6a8082032870c55d611f4ca6b2442f7f`.
- Window 03's immutable group has 11 episodes, 154 root turns, 647,114 causal tokens,
  18,517 action tokens, maximum sequence 8,192, maximum action 219, and sum of squared
  sequence lengths 3,446,984,120. That is 17.88 times the causal-token load and 61.64 times
  the squared-length proxy of window 02. Only 2.86% of its causal tokens are credited action
  tokens.
- The trainer began at epoch 1789070515.3067334 with deadline 1789070755.3066828, exactly
  the recipe's 240-second inner cap. The process ended 242.078 seconds later. There is no
  `STEP_STARTED.json`, checkpoint 2, or optimizer mutation receipt in window 03.
- The log's CUDA warning occurred before the terminal timeout traceback. The traceback is
  `TimeoutError` raised by the alarm inside `backward()`, not a caught Python
  `OutOfMemoryError`; both memory pressure and insufficient wall time are evidenced.

## Why sparse logits preserve the objective

The installed Qwen3 forward accepts `logits_to_keep` as a tensor and applies `lm_head` only
to `hidden_states[:, indices, :]`. The qualified loss subsequently slices the full logits at
positions `prompt_length - 1` through `prompt_length - 1 + action_count` and ignores every
other logit. For each turn, pass precisely those predecessor indices and give the TIS loss
the resulting already-selected logits.

The language-model head is position-wise. Unselected logits have zero dependency in the
existing scalar loss, so deleting their projection preserves the loss and analytical
gradients, including gradients through each selected hidden state into its causal prefix.
It does not change rewards, advantages, TIS weights, PPO clipping, action masks, episode or
turn weighting, group membership, or optimizer-step count. It may not be bitwise identical:
the smaller BF16 matrix multiplication can use a different numerical kernel, so equivalence
must be checked to a frozen tolerance before calling this an infrastructure-only recovery.

At the maximum length, a BF16 full-vocabulary logits tensor is approximately
2,489,319,424 bytes, versus 66,547,968 bytes for 219 selected positions. The observed failed
allocation is almost exactly the projection size for roughly 6,384 positions. Sparse logits
therefore directly target the observed peak allocation.

## What remains expensive

Sparse logits do not shorten or truncate inputs. Qwen3 still performs the full transformer
forward and gradient-checkpointed backward for every causal token, including attention over
histories up to 8,192 tokens. The trainer also executes 154 separate forward/backward pairs
before one optimizer step. Even a favorable linear extrapolation from window 02 is about
276 seconds, already beyond 240 seconds; the much larger squared-length proxy makes that a
lower-bound heuristic rather than a runtime prediction. Gradient checkpointing reduces
activation storage but adds recomputation. A sparse-head-only retry under 240 seconds is not
a valid test of the frozen scientific group.

## Minimal recovery design

1. **Qualify the numerical seam without changing science.** Add a CPU algebra regression
   comparing full and selected-position head loss/gradients on a tiny deterministic tensor.
   Then run one bounded GPU qualification from exact checkpoint 1: on a short frozen
   window-03 turn compare full versus sparse current log-probabilities, scalar loss, and LoRA
   gradients to declared tolerances; on the longest frozen turn require one sparse
   forward/backward to finish and record peak memory/time. Do not call `optimizer.step`, and
   restore checkpoint-1 model, Adam, and RNG afterward. Suggested qualification cap: 900
   seconds including load and cleanup.
2. **Resume, do not regenerate.** If and only if the infrastructure checks pass, create an
   additive attempt namespace that consumes the exact window-03 `GROUP.json` and
   `GENERATION.json`, starts from the exact checkpoint-1 adapter/Adam/RNG above, retains the
   original turn order and weighting, and applies exactly one update. No recollection,
   reselection, refill, truncation, micro-group update, or seed change is allowed. Retain the
   failed attempt unchanged.
3. **Give the unchanged group a realistic hard cap.** Use a 1,800-second load/optimization
   cap, nested within a separately bounded owner/cleanup envelope. Record per-turn lengths
   and times, peak allocated/reserved bytes, sparse projected-position counts, distribution
   guards, `STEP_STARTED`, and the ordinary atomic checkpoint-2 lineage. The cap change is
   infrastructure capacity, not a new training recipe.
4. **Fail closed.** If the longest-turn qualification still exceeds memory, if the numerical
   comparison exceeds tolerance, or if the exact group cannot finish inside the enlarged
   cap, preserve checkpoint 1 and call window 03 infeasible under this trainer. Shrinking or
   splitting the selected group would alter weighting/update timing and must be proposed as
   a new scientific campaign rather than recovery.

This recovery can establish equivalence to the existing credited-token objective, not
bitwise trajectory identity. Later checkpoints remain exploratory because the implementation
and cap changed after observing this infrastructure failure.

## Source and artifact pins

- Qualified trainer: `sidecars/root-rlvr-campaign-v1/campaign_train.py`, SHA-256
  `38fe3087b8deb94ee8e0fa2e0330ca34a822f84192031c389ff32acf00d79d1f`.
- Qualified TIS loss: `sidecars/single-gpu-rlvr-v2/source/single_gpu_rlvr_tis_v3.py`, SHA-256
  `eff526cf496d3896e220d5aa0694bed3b703114e4a19d6f7c9e4f73de6240bd9`.
- Installed Qwen3 implementation: `modeling_qwen3.py`, SHA-256
  `cbb7f2dc274c2f5592746c0dc6985ca50353efa07376f92cc922b77680a74f69`.
- Frozen window-03 group / manifest / generation:
  `7420d808187115f14ed6ca6521b77cdd1ba4ca330dd17aca92e09db430b8948f`,
  `bf4793681e18b12e15784194edb3a7d9966d06101fd9e5bc4db0d1f51ed96c17`, and
  `bff4dc8e048496f35f2a7aaa14bf29c4c51f8362dca5f0d5f39040669be41cee`.
- Retained training log: SHA-256
  `2ca9b7560723ab9ce76c85d9384794e0fe7db06c629bfbb4ee6193815673e670`.

This review was written after the failure, from retained files and source, without importing
Torch/Transformers, initializing CUDA, or reading later campaign outcomes.
