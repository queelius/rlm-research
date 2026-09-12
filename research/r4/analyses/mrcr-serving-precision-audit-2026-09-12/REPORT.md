---
title: MRCR one-step LoRA serving-precision audit
date: 2026-09-12
status: complete CPU storage/source audit
---

# MRCR one-step LoRA serving-precision audit

The saved evaluators did not serve the one-step adapters in FP32. All three inference configs set
base `dtype=auto` and `lora_dtype=auto`; the model config declares BF16, each actual engine log
resolves the model to `torch.bfloat16`, vLLM 0.28.0 assigns automatic LoRA dtype from the model
dtype, and its loader casts both LoRA factors to that dtype. This is strong source/config evidence
for BF16 adapter storage, but it is not a direct inspection of the live GPU tensors.

Both training checkpoints contain 504 FP32 LoRA tensors (16,515,072
parameters). Relative to the common procedural-SFT checkpoint 32:

- Fixed-baseline RL1: FP32 delta L2 0.03421448. BF16 casting leaves
  38.0% of FP32-changed parameter
  elements unchanged on the BF16 grid. The split is 70.4%
  for A factors and 10.0% for B factors.
- Fresh RLOO1: FP32 delta L2 0.04046066. BF16 casting leaves
  31.9% unchanged overall,
  62.1% for A and
  5.7% for B.

Thus BF16 serving does discard a material fraction of elementwise one-step changes, especially in
the A factors. It does **not** erase either update: 10,234,138 and
11,243,686 elements respectively move to a different BF16 value.
Quantized delta norms can exceed FP32 delta norms because crossing a coarse BF16 grid step amplifies
some movements; that is quantization error, not evidence of a stronger update. The machine-readable
result also gives exact effective B@A delta norms/cosines without materializing full base matrices.

HF training is not simply the opposite FP32 system. The training source loads a BF16 base and PEFT
upcasts LoRA factors to FP32; PEFT's installed linear forward casts the LoRA input to the factor
dtype and computes that branch in FP32, but casts the combined layer result back to the BF16 base
result dtype. The contrast is therefore FP32 LoRA factor storage/arithmetic versus BF16 vLLM factor
storage, with BF16 layer outputs in training too.

## Decision

Serving precision is a plausible attenuation/noise contributor for LR=1e-5 one-step updates, not a
complete explanation for weak RL and not evidence that either update vanished. A targeted comparison
is warranted only if it directly serves the *same fixed checkpoint* with `lora_dtype=bfloat16` versus
`lora_dtype=float32` on a small already-frozen decoding panel, after verifying vLLM supports that
configuration on one A100. This would be a serving-precision mechanism screen, not another training
arm. It should preserve all seeds/prompts and report runtime/memory compatibility; FP32 is currently
only a counterfactual and has not been run.

The audit used no GPU, model inference, or API calls. Tensor norms and B@A matrix deltas are mechanics
diagnostics, not measures of accuracy or learned decomposition.
