# Parent acceptance and launch only

READY.json is published last after CPU source/input/request qualification. It does not authorize a GPU launch. Parent prepares acceptance and serialization behind the existing broad→uptake→role chain; this sidecar creates no scheduler or queue entry.

Read-only CPU verification:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-identity-agnews-weight-v1/owned.py --verify
```

Exact proposed accepted argv:

```sh
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-identity-agnews-weight-v1/owned.py --directory /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-identity-agnews-weight-v1/owned/attempt-001
```

Inherit actual parent exclusive CUDA_VISIBLE_DEVICES/MIG UUID, LD_LIBRARY_PATH and existing STRICT_RLM_CALIBRATION_API_KEY. No CUDA0 hardcoding or environment edits. Require unused owned/output paths. The wrapper's clock starts at entry:1080s work,1200s inclusive including120s cleanup reserve, collection≤900s and≤remaining work. Parent outer1230s handles exceptional cleanup; overruns remain reported. Existing V2 ownership recognizes PRL::Inference, captures exact process identities and releases only owned service/workers in finally. The previously qualified vanished-process observer is reused unchanged by AST extraction.

The service writes actual original and selected endpoint descriptors. Both are validated against exact frozen adapter/config/base hashes, same address, aliases and live /models. ATTEMPT retains both descriptor objects and hashes; MODELS_PREFLIGHT/VERSION_PREFLIGHT retain actual service evidence. Each wire request must equal frozen serialized bytes. Every successful response must match requested alias and expose prompt token IDs consistent with frozen typed IDs and usage length.

Results: `outputs/attempt-001/calls/*.json`, `wire/*.json`, `coordinates/*.json`, `analysis.json`, `STATUS.json`; service/log/ownership/release evidence in `owned/attempt-001`. `analysis.json` contains twelve cells, per-context/seed/prefix arm contrasts, old-minus-original interactions, per-call class-count errors, physical prompt checks and actual usage/missing-cache counts. No numeric alignment rescue. Underlying output key order is retained by the qualified scorer; structural schema validity does not certify topic labels.

A request/protocol error stops further dispatch, without retry; already complete outcomes remain and pending coordinates are unrun. Missing usage is unknown, not a measured zero, even when a convenience sum is zero. Invalid complete arrays are strict failures with semantic alignment unavailable, not infra nulls. Preserve all errors and do not relaunch automatically. Parent/independent CPU analysis follows owned release; no whole-RLM promotion from this component result.
