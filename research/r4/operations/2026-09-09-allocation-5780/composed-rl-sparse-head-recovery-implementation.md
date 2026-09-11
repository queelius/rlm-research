---
title: Composed-RL sparse-head recovery implementation handoff
date: 2026-09-10
status: ready_cpu_qualified_not_gpu_launched
---

# Handoff

The isolated sidecar is `sidecars/root-composed-rl-sparse-head-recovery-v1`. It authenticates
the exact failed window-03 group/generation and checkpoint-1 adapter, Adam, and RNG. No prior
campaign source or output was changed, and no CUDA/model service was started.

The GPU program has two hard-gated stages. Qualification (<=900 seconds) constructs no
optimizer and performs a shortest-turn full-versus-sparse comparison plus one longest-turn
sparse backward. Training runs only after a persisted passing receipt and has <=1,800
seconds to apply exactly update 2. The owner has 2,700 seconds of work, 270 seconds of owned
cleanup reserve, and a 30-second outer margin. It performs no evaluation or later-window
continuation.

Sparse projection uses Qwen3's tensor `logits_to_keep` at exactly
`prompt_length-1 : prompt_length-1+action_count`. The adapter rebuilds the local action-only
capture's `input_ids`, masked `labels`, and `loss_mask` before invoking the unchanged
qualified TIS loss. An initial pre-seal version failed this capture-contract unit test and is
retained explicitly as `*_SUPERSEDED_PRE_CAPTURE_CONTRACT.json`; it was never accepted or
launched.

# CPU evidence

- Tiny local CPU Qwen3 full/sparse fixture: identical loss, current log-probabilities, and
  all parameter gradients (`max_gradient_absolute_difference=0.0`).
- Actual trainer preflight traversed frozen GROUP/GENERATION/checkpoint authentication,
  inherited native export replay, and model-manifest verification: 11 episodes, input
  identity `f325d8a7f56254602faaa61e40ffdebcbf4af90013e68e3a7f6800926a000718`.
- Focused final tests: 8 passed in 8.28 seconds. Python compilation passed.
- The GPU qualification tolerances are prospectively fixed at max action-logprob absolute
  difference 0.005, loss absolute difference 0.002, relative LoRA-gradient L2 difference
  0.01, and gradient cosine >=0.99995. These support numerical, not bitwise, equivalence.

# Seals

- Campaign identity: `40883af4141cf2f59f76cb6153d0f8a87bc3f2b506c865674a6ca924efc64d56`.
- `CAMPAIGN.json`: `d48c1a60cda9cf0a1b4a0933ebb5d8007364c9fe4ac8d9cd3dc994bc441b071f`.
- `READY.json`: `d3a7697381cd8ea1be2a5809990698960f0e39ea97ead6b22b1e6d597bc4028c`.
- `CPU_TEST_RECEIPT.json`: `4f12ec851259ae787b80881c8500ae200297021ef8a72057cc76173cfd4cea69`.

The 1,800-second cap is a pragmatic enlarged envelope, not a derived guarantee. Failure of
the longest-turn gate or exact update retains checkpoint 1; it does not authorize shrinking
or splitting the group.
