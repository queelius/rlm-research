# Leaf indexed grammar transfer160

CPU-prepared only; parent owns the unchanged native vLLM dual-alias service. See DESIGN.md for the frozen160-call factorial and exposure/cost qualifications. PREPARED.json means source/data/request freeze, not permission to launch or a successfully completed indexed checkpoint. READY.json is published only after authenticated fixed final epoch2/step204, never from a favorable intermediate result.

Use the existing native environment, with no CUDA visible to the HTTP client:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-indexed-grammar-transfer-v1/driver.py prepare
```

After indexed RESULT.json, SELECTION.json and checkpoint-0204/state.json are immutable:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-indexed-grammar-transfer-v1/driver.py accept-weights
```

Parent binds two actual descriptors on one qualified service. Replace the two descriptor paths with the truthful c32de and indexed-final aliases; do not reuse a stale descriptor merely because its alias looks right. The binding command makes no service requests:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-indexed-grammar-transfer-v1/driver.py bind --old-endpoint /absolute/actual/endpoint-old.json --indexed-endpoint /absolute/actual/endpoint-indexed.json --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-indexed-grammar-transfer-v1/BOUND-attempt-001.json
```

Run only after parent review/service handoff. Pass the parent's real launch epoch, captured before service startup, to include that time in the2700s overall envelope. Collection is additionally limited to1800s and four concurrent calls. If omitted, the recorded overall envelope starts at client entry and does not include previous startup; do not claim otherwise.

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-indexed-grammar-transfer-v1/driver.py run --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-indexed-grammar-transfer-v1/BOUND-attempt-001.json --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-indexed-grammar-transfer-v1/outputs/attempt-001 --overall-start-epoch ACTUAL_PARENT_LAUNCH_UNIX_SECONDS
```

No retry or resume changes the plan. Existing destinations are never overwritten. Per-call files retain complete provider response/token IDs and reported cached-token details. Completed malformed free responses receive strict0 with unavailable alignment; infrastructure/unrun remain null. Final STATUS lists every unrun coordinate and any identity/cap failure. analysis.json separates dataset, weight, output format and grammar; do not pool TREC/SST or treat repeated cells as independent contexts.
