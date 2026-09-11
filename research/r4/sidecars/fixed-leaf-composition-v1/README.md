# Fixed leaf-composition control: CPU-ready

624 direct leaf requests,48 matched aggregate coordinates,6 contexts,384 unique source
questions. Ten focused CPU tests and frozen-input/request-hash preflight pass.
No model calls were made during preparation.

The [design](DESIGN.md) and [spec](../../../../ARTIFACTS.md#unpublished-files "Not published: SPEC.json") preserve the parent's preselected composition
DATA and exact task seeds/order. The operator supplies batches of5, strict JSON/enum checks
and counting; there is no root model, tool execution, fallback or decoder grammar.
Selected leaf weights come only from frozen validation SELECTION epoch2. The original
converted-key adapter and selected SFT adapter are served with the parent's common BF16
inference cast; hashes identify FP32 files, not FP32 runtime arithmetic.

Parent-owned launch against the still-live service1472413:

```bash
timeout 16m env CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/fixed-leaf-composition-v1/driver.py run --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/fixed-leaf-composition-v1/SPEC.json --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/fixed-leaf-composition-v1/outputs/attempt-001
```

The API key must already be present in STRICT_RLM_CALIBRATION_API_KEY. No key is included
in this command or spec. Runtime verifies frozen server evidence, live vLLM version and
both model-card alias/path/base identities before rollout. If the service changes, create
an additive new binding/spec/attempt; do not mutate this spec or reuse an output directory.

Cap900seconds,30seconds/request,4 concurrent HTTP calls. Each call is atomic; completed
coordinates also checkpoint. A malformed/noncanonical batch is an observable aggregate
failure, while infrastructure/unrun cases remain null. Final analysis retains all48
coordinates and dynamic item/confusion/cost denominators. These are624 requests but not624
independent experimental units.

[READY.json](../../../../ARTIFACTS.md#unpublished-files "Not published: READY.json") records hashes, source/selection/service identity and launch conditions.
Spec SHA256: `7fd1c7ae11a5f9d5185328bcdb095f5ae4a070318e6e97fde5e5c5c40eb86f81`. No GPU launches by this agent.
