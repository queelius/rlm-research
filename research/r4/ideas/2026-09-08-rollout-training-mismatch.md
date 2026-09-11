# Native4B rollout–training discrepancy: bounded next treatment

The first fresh RLVR attempt made **zero optimizer steps**. Its 6,454 sampled actions had
mean absolute HF/vLLM logprob discrepancy 0.007472, but eight exceeded the old 0.5 maximum
threshold. That maximum alone does not describe importance-weight risk: the actual BF16
ratio range was **0.3641–1.8591**, with mean 1.000500 and sampled k3 statistic 0.000975.
Only 71/6,454 ratios were outside the PPO interval [0.8,1.2]. An FP32-head probe did not
eliminate the discrepancy; changing the head is not part of the chosen retry.

Kernel/batch/execution differences are a plausible remaining cause, not a proven uniquely
identified cause. Published vLLM/SkyRL work describes differing reduction orders across
training, prefill and decode as a source of probability mismatch, and addresses exactness
through shared execution contracts and kernels. Rebuilding this stack is a separate systems
study, not a prerequisite for this one-step exploratory update.
[IsoExec, 2026-08-21](https://vllm-project.github.io/2026/08/21/isoexec.html)

An independent real loading problem was also found: Prime adapter key names are not HF PEFT
key names. The additive converted artifact preserves all 504 FP32 tensors exactly. Both
self-SFT and TIS use the converted adapter with `autocast_adapter_dtype=True`; TIS verifies
exact loaded GPU values and dtypes before any forward. This is not a new random adapter or
a license to ignore loading errors.

## Estimator choice, not an arbitrary relaxed maximum

The old loss already used the actual rollout policy as its PPO denominator, which is the
documented bypass-PPO formulation. Multiplying that same loss by another HF/rollout ratio
would double-count correction. VeRL distinguishes this from decoupled PPO, with separate
behavior and proximal policies.
[VeRL mathematical formulation](https://verl.readthedocs.io/en/latest/algo/rollout_corr_math.html)

The separately declared v3 treatment uses:

```
mu       = preserved vLLM rollout action probability
p0       = frozen HF starting-policy probability from the same forward
w        = stop_gradient(min(p0 / mu, 2))
r(theta) = p_theta / p0
loss     = -mean(w * min(r(theta)*A, clip(r(theta), .8, 1.2)*A))
```

There is exactly one optimizer step after the full batch accumulates. Thus `p0=current.detach()`
is valid for every forward with dropout off, `r=1`, and the PPO clipping term is inactive for
this initial gradient. Repeated optimizer steps would require a separately frozen proximal
policy; recomputing the anchor after updates would change the method. The upper cap of 2,
detached weights, and no weight normalization match the documented token-TIS implementation.
[VeRL correction implementation](https://raw.githubusercontent.com/verl-project/verl/main/verl/trainer/ppo/rollout_corr_helper.py)

This remains a biased token-level surrogate: it corrects conditional action weights, not
history visitation; truncation adds bias if active. It does not establish exact trajectory
IS or a monotonic-improvement guarantee. Sequence-level divergence can remain important
even when individual token corrections appear modest.
[Trust Region Masking, arXiv:2512.23075](https://arxiv.org/abs/2512.23075)

## Frozen scope and health checks

Keep the original 16-episode mixed group, advantages, all captured actions, temperature0.5,
BF16 base/head output, equal episode/turn weighting, seed950260400, AdamW5e-6, and one update.
The completed probe predicts zero cap2 clipping; the actual retry records its own statistics.

Run-health limits, approved before the retry and without heldout selection: mean absolute
logratio ≤0.1; sampled k3 ≤0.02; raw token ESS/N ≥0.90; at most1% of token ratios outside
[0.5,2]; at most1% of positive IS mass removed by truncation. These are declared exploratory
health bounds, **not theory-derived tolerances**. Finite aligned captures remain mandatory.
VeRL provides ESS, weight-tail and off-policy diagnostics, but does not justify these
specific experiment-level limits for this model.
[VeRL rollout correction guide](https://verl.readthedocs.io/en/latest/algo/rollout_corr.html)

The new trainer saves every rollout/HF-old logprob and correction, ratio quantiles,
sign-specific bypass clipping, loss-weighted coefficient changes, and per-episode summed
logratios before the update. Success requires a finite nonzero gradient, changed adapter,
and optimizer state proving one step. Then compare the fixed primary14 heldout coordinates
(excluding revealing12000052) against step0 and six-step self-SFT; all16 remain secondary.
An update is systems/optimization evidence, not evidence of benefit until that comparison.

## Seals and executable treatment

Paths below are relative to `/project/alex_phd/runs/rlm-research-r4/`.

- `operations/2026-09-08-resume/lm-head-tail-probe.jsonl`:
  `6b595f6a2af65ca18066cdd1a98aeca559213251a9026c0feefea50a5e1cf5a3`.
- `sidecars/single-gpu-rlvr-v2/outputs/4b-native-update-attempt-001/drift-failure.json`:
  `9e4d5fb9fb66386427c0efc9ada1c2c06370f22ce173a12d433eb5538c8494a1`.
- `sidecars/single-gpu-rlvr-v2/source/single_gpu_rlvr_tis_v3.py`:
  `eff526cf496d3896e220d5aa0694bed3b703114e4a19d6f7c9e4f73de6240bd9`.
- `sidecars/single-gpu-rlvr-v2/TIS_V3_SPEC.json`:
  `d5ea0c327e5871f16a6646560a883c7f91da3b54f3891611cc1fb68d5291e76a`.
- Original unchanged `training-group.json`:
  `66735af70be5e972f90df5109d8dde1c278ffa59b0ec60060287056c49627bc3`.
- VeRL reference source SHA-256, retrieved2026-09-08:
  `763158342551bc4077805a8a009d959a7a2043c4d43b772fe6045f4a40932f3e`.

CLI: `single_gpu_rlvr_tis_v3.py --group PATH --output NEW_DIRECTORY --model FROZEN4B_PATH
--adapter EXACT_CONVERTED_STEP0_PATH`. Parent owns GPU assignment/launch. Two focused CPU
tests passed (hand-derived capped/detached weights with exact masked gradients, and the
bulk-health guard), as did targeted Ruff and the launch interpreter's CLI check. Original
v2 source, collection outputs, rewards and historical failed attempt were not edited.
