---
title: Sparse-head exact update2 under post-diagnostic engineering policy
date: 2026-09-10
status: prospective_before_recovery_v2_gpu
gpu_authorized: false
---

The original qualification remains failed: its 1% relative-gradient and 0.99995 cosine gates were
not met. A subsequent no-optimizer diagnostic found that two identical dense backward passes also
failed those thresholds (1.378%, 0.9999057), while dense versus sparse was 1.816%, 0.9998368; all
three losses and all 116 selected-action log probabilities were identical. Thus the observed excess
cannot be uniquely assigned to an objective change. It is compatible with nondeterministic
low-precision/CUDA backward reductions, but the evidence does not isolate BF16, SDPA, checkpointing,
or kernel scheduling.

This new exploratory execution policy does not revise that result. It accepts the already persisted
diagnostic only if dense-repeat and dense-sparse each have relative L2 <=3% and cosine >=0.9995,
and dense-sparse absolute difference is <=2 times dense-repeat difference. Original loss and
log-probability tolerances remain unchanged, and the prior finite 8,192-token sparse backward is
reused by exact hash. These post-diagnostic thresholds are pragmatic engineering choices, not
confirmatory equivalence or bitwise identity claims.

If the frozen CPU requalification passes, run the exact original sparse trainer once on the exact
failed group/generation from checkpoint1 with its Adam moments and RNG. The 11 episodes, 154 turns,
18,517 credited tokens, order, advantages, TIS/PPO math, weights, and selected-head implementation
are unchanged. Commit exactly checkpoint2 or preserve checkpoint1. No recollection, reselection,
qualification loop, evaluation, truncation, or threshold relaxation is allowed. One A100; 1,800
seconds work, 2,070 owned and 2,100 inclusive outer. A separate fixed readout remains required.
