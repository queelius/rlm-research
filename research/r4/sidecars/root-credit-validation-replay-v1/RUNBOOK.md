# Exact root-credit validation replay

Original-weight replay is ready. The coordinator launches only when the bound dual service is assigned:

```bash
env CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/replay.py run-original \
  --endpoint /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-role-routing-v1/service-attempt-001/endpoint-original.json \
  --binding /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-role-routing-v1/BOUND_WEIGHTS.json \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/outputs/original-replay-attempt-001
```

Inherit the assigned API-key environment variable; do not print it. This does not start a server or directly use a local GPU. Both explicit input files must match the frozen Phase1 endpoint/binding, both adapters/configs are rehashed, the source/processed-logprob log prefix is verified, and live advertised alias/root/parent checks occur before model calls. Changed weights/aliases are rejected rather than silently substituted.

The replay is exactly the eight `split=validation` coordinates from Phase1, preserving their original IDs, order, seeds, task hashes, full prompts/definitions, two64-record contexts and four questions. No source trajectory outcomes were read for selection. Native renderer, T=.5/full support,2048-token cap, depth1/no compaction, four workers,1800-second batch cap, role routing and native wire/physical-graph capture are inherited unchanged. Gold stays host-side. Root-only credit semantics remain unchanged; no optimizer or training-group export is included. Per-episode schema retains the inherited Phase1 name; `SPEC_ORIGINAL.json` explicitly identifies the replay condition and source identity.

This unchanged original-root + selected-child replay estimates whole-trajectory variability. It is not a learning effect. Identical requests/seeds did not ensure identical earlier root trajectories, so before/after improvement needs this baseline variability and per-episode process review.

Three focused red→green tests passed. Fresh verification checked all source/binding hashes and reconstructed each validation prompt/hash. The parent Phase1 source/spec remain unchanged. No GPU, model endpoint, or new rootless-container calls occurred during this preparation; the unchanged collector retains its sealed real rootless/native three-call qualification.

Post-update replay is intentionally `WAITING_CHECKPOINT_IDENTITY`: same eight coordinates/prompts/seeds and selected child, but it requires a separate immutable post-update spec plus an explicitly authenticated actual root-checkpoint endpoint/binding before any call. See `POST_UPDATE_WAITING.json`. The original launcher cannot accept a trained root.

Original replay spec SHA256: `c7a3c8d0bb4af8d22b6ab10c6f8a3131c6ecd4ab9a78468522c5d1dcab22d4b7`.

Validation coordinate-plan SHA256: `15bf5bb728b8e467d4d0903b631beb3696edb90021dc9dc9d1e8d8c9c71b551b`.
