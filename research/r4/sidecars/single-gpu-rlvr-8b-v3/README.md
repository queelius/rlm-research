# Adaptive8B one-GPU RLVR revision

This additive revision retains the original unused inventory and rootless RLM harness from
`single-gpu-rlvr-v2/outputs/attempt-001`; no original source/spec or active4B/SFT source was edited.

Three necessary changes are declared in `RECIPE.json`:

- Load the canonical k576 adapter exactly in FP32 on the unchanged BF16 base. CPU real-shape PEFT
  loading verifies504/504 exact tensors. The old setting rounded every tensor (max6.1035e-5),
  without a warning; all252 B matrices are nonzero.
- Return `processed_logprobs` from vLLM and explicitly request temperature0.8, top_p1, top_k-1,
  min_p0. The inherited command already disables HF generation defaults with `--generation-config
  vllm`. The old logprob default was raw/pre-temperature and did not match the trainer denominator.
- Reuse frozen token-TIS helpers: cap2 detached correction, exactly one full-batch optimizer step,
  real8B distribution diagnostics and declared health bounds. The4B-specific exporter/conversion
  checks are not reused or fabricated. Future updates need fresh rollout/proximal-policy handling.

The thin entrypoint binds inherited orchestration functions in its own process so training starts
the new entrypoint. No shared files are patched. It adds a read-only revision mount; generated RLM
execution still requires the original isolated container and per-episode writable scratch only.
Actual controller `model.request` settings are recorded beside each captured causal turn.
Partial traces discarded by inherited RLM exceptions remain excluded with null rewards.

## Parent launch

After the sole GPU is free, use its actual assignment (MIG identity if applicable):

```bash
env PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/rlm/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/single-gpu-rlvr-8b-v3/source/run_8b.py \
  run --attempt /project/alex_phd/runs/rlm-research-r4/sidecars/single-gpu-rlvr-8b-v3/outputs/attempt-001 \
  --gpu GPU_OR_MIG_ID --port 19472
```

One GPU is sequentially used for12 calibration episodes, up to24 fresh training rollouts plus8
heldout-pre episodes for the selected cell, one actual LoRA update, then8 paired heldout-post
episodes. Total cap90minutes; trainer cap30minutes. No reward variance means no optimizer claim.

Training artifacts: `outputs/attempt-001/training/correction-capture.json`, `training.json`, and
`checkpoint-1/{adapter_model.safetensors,adapter_config.json,optimizer.pt,rng_state.pt}`.
Final paired result: `outputs/attempt-001/result.json`. Failure artifacts preserve the observed
reason; no silent guard relaxation, reward edits, or continuation from a changed snapshot.

## Verification

Five focused revision tests passed, including split preservation, actual entrypoint routing,
read-only mounts, and rejection of host-generated execution. Both frozen TIS helper tests passed
on real CPU tensors. Original and revision fixed rootless imports passed with gold inventory
inaccessible. The actual bundled ResponsesRequest→SamplingParams CPU probe produced temperature0.8,
top_p1, top_k-1, min_p0, presence/frequency0 and repetition1. In this API min_p is the neutral
SamplingParams default; the explicit request value is additionally recorded, not assumed to
override an unsupported field. Ruff passed and the frozen source snapshot authenticated.

This is exploratory biased token-conditional correction, not exact trajectory importance
sampling or a guarantee of improvement. No8B GPU forward was run during preparation.
