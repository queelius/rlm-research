---
title: Sparse-head gradient numerical diagnostic
date: 2026-09-10
status: prospective_after_failed_gate_before_diagnostic_gpu
gpu_authorized: false
---

# Question and scope

Why did the frozen sparse-head qualification report identical action log probabilities and loss but
1.722% relative LoRA-gradient difference and an impossible FP32 cosine of 1.00203? This diagnostic
distinguishes measurement/repeatability noise from an objective-gradient discrepancy. It does not
relax the original 1%/0.99995 gate and cannot construct an optimizer or authorize update 2.

Load the exact checkpoint1, failed window03 group/generation, model, recipe, shortest 1,192-token
turn, and frozen advantage. With dropout disabled exactly as in the failed qualification, compute
three backward passes in fixed order: dense A, dense B, sparse. Persist each complete FP32 LoRA
gradient vector on CPU. Recompute norms, differences, dots, and cosines with chunked CPU float64
accumulation. Also retain each loss and selected-action log-probability vector. Dense A versus dense B
measures same-path repeatability; dense A versus sparse measures the intervention. No optimizer is
constructed, no parameters are stepped, and the previous failed result remains immutable.

Interpretation is conditional. If dense/dense already exceeds the original gradient tolerances, the
old single-pair gate is numerically unstable under this execution path. If dense/dense passes but
dense/sparse fails under accurate reductions, the sparse transformation is not qualified. If both
pass, the earlier FP32 reduction was the likely gate defect, but the old failure is not rescored; a
new recovery would require explicit approval and a new qualification identity.

One A100, one direct local model process, 270 seconds work, 290 seconds owned and 300 seconds
inclusive. No service, calls, recollection, evaluation, or long-turn rerun; the already authenticated
8,192-token sparse result is only pinned provenance.
