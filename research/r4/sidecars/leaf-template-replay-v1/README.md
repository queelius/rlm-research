# B-only template replay: CPU-prepared, parent launch only

12 fresh HF calls, six paired microbatches, one exact B-final checkpoint load. Training and probe conditions use the two saved physical token sequences for the same six frozen transfer64 contexts. They differ only in tool JSON key serialization; no gold/task/decoder change. Historical B outputs are not reused as a control.

Use the trained environment, not the vLLM/Prime interpreter:

```bash
REPLAY_DIR=/project/alex_phd/runs/rlm-research-r4/sidecars/leaf-template-replay-v1
REPLAY_PY=/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python
# Parent first assigns one exclusively released CUDA_VISIBLE_DEVICES.
PYTHONDONTWRITEBYTECODE=1 "$REPLAY_PY" "$REPLAY_DIR/driver.py" run --spec-path "$REPLAY_DIR/SPEC.json" --output-dir "$REPLAY_DIR/outputs/attempt-001"
```

CPU-only verification adds CUDA_VISIBLE_DEVICES='' and uses command verify. Parent must not run inference alongside an owned live service/training job. No resume or retries; existing output directories are rejected. Internal global alarm900seconds covers verification/load/generation; parent should apply an owned-process external watchdog for stalled native/device calls. No claim that an uninterruptible kernel is forcibly stopped at exactly900seconds.

Checkpoint0204 SHA59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200 is authenticated against B's fixed-final RESULT/SELECTION/epoch2 state/member/source closure. Exact trained environment is checked. Base BF16/SDPA and autocast_adapter_dtype=true yield audited FP32 LoRA values; inference-only, no gradients/optimizer restore/merge. One model load for both conditions.

Each two-row microbatch holds both templates for one context, alternating row order across contexts. This is a fresh within-backend comparison, not an exact repetition of historical cross-context microbatch placement. All12 calls are greedy1024 with the same padding/EOS helpers. Exact actual input IDs and masks at the HF generate boundary are checked against the outer spec. New row IDs and manifest identity bind the template IDs, condition, data, checkpoint, environment and decode settings.

Frozen mixed evaluate_long checkpoints each completed row; batch manifests, input capture, shared generation time and COST.json are additive. Partial batch errors preserve completed rows. analysis.json reports contract validity/strict full-array success, aligned-only semantic/positional/confusion metrics, raw lengths and paired differences. Malformed arrays are unaligned, not64 semantically wrong labels; absent completions are null. Batch time is shared and must not be double-counted per row. Prompt/completion IDs and costs are retained without repair.

Inputs reuse six test compositions/384 unique question groups already examined in the research campaign. This is an exploratory exact-template sensitivity check at fixed B weights, not untouched test data or proof that serialization explains batching failure. Similar outcomes weaken this specific explanation; a consistent fresh paired difference supports sensitivity to this exact serialization, not a generic attention/planning claim.

DESIGN.md states the frozen comparison. CPU_CHECK.json and READY.json record final reconstruction/generate-boundary tests and source hashes. Preparation performs no GPU model load or generation.

