# Parent-owned sparse144

Scientific preparation is CPU-only: `CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python driver.py prepare` in this directory. It publishes READY last; do not rerun prepare over a freeze.

Verify without model/service calls: `CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python owned.py --verify`.

Parent accepted/serialized launch argv:

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-sparse-anchor-v1/owned.py --directory /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-sparse-anchor-v1/owned/attempt-001
```

The parent must hold its existing shared operation lock after exact predecessor exit and empty-GPU verification, supply the actual exclusive MIG UUID in CUDA_VISIBLE_DEVICES plus qualified LD_LIBRARY_PATH and STRICT_RLM_CALIBRATION_API_KEY environment, and bind READY/SPEC/source closure in its acceptance. Do not print the credential. This preparation agent neither approves nor launches.

Outer process cap1230 s; owned1200 s includes120 s cleanup reserve; shared work1080 s, collection900 s, request120 s, four workers. The original owned clock covers imports/verification/startup/collection; no per-phase reset or retries. The wrapper starts exactly one c32de adapter under its own directory, validates authentic endpoint/alias/base, records owned process identities and releases them in finally. It never signals a predecessor or unrelated service. Parent emergency-cleanup policy is separate.

Outputs are `outputs/attempt-001/{calls,wire,coordinates,analysis.json,STATUS.json}` and owned `FINISH.json`/`SERVICE_STOPPED.json`; unsuccessful setup, unrun cells and request failures stay explicit. All144 calls are planned; completion is not promised. Never rerun an individual failed cell, change admission, or silently substitute an endpoint. New attempts need additive parent decisions.

The built-in CPU summary runs before owned service release, inherited from the qualified small component runner. Earlier cue/AG summaries were subsecond; this is not a GPU scheduling redesign. Independent detailed analysis must run after release without holding the parent lock. Known earlier dependency/lifecycle reports and all old attempts remain unchanged.
