---
status: cpu_qualified_pending_main_review
date: 2026-09-10
gpu_calls: 0
---

# Implementation report

The isolated sidecar composes the authenticated TREC partition/renderer, c32 checkpoint,
qualified token-sum SFT mechanics, native structured-output scorer, and the qualified dual-LoRA
service lifecycle. `prepare.py` materializes both 96-context training arms, a 480-coordinate
evaluation plan, all native bodies, private gold, public panels, and overlap provenance.
`train.py` creates a fresh AdamW/RNG state per arm and will only bind checkpoint-0024 after all
24 updates complete. `owner.py` trains both arms in one bounded GPU stage, then uses two owned
dual-LoRA service stages: c32/full6-SFT24 for 288 calls and full6-SFT24/ABO-SFT24 for the
remaining 192. The owner obtains the qualified runtime-an27 `service_wrapper_v2` and matching
ownership adapter through the query study dependency chain. `collect.py` preserves native
availability: authenticated malformed/empty outputs are observed zero, whereas missing/unknown
results have explicit balanced-accuracy bounds and no point estimate.

CPU preparation tokenized the exact training closure: full6 has 120,781 prompt and 23,999
target tokens; ABO has 120,493 prompt and 22,430 target tokens. Both have 1,536 unique groups,
96 contexts, and 24 planned updates. The physical target-token difference is retained and
reported; no duplicated ABO examples manufacture token equality.

No model was loaded, no service was started, and no output attempt was created during
preparation. The amended focused CPU suite covers data/optimizer closure, fixed update24,
qualified wrapper/lifecycle registration and intercepted launcher argv, durable nonzero training
exit, environment metadata, NULL bounds, finish-reason rejection, and the fake native transport.
Ruff E/F/I checks and entry-module compilation pass. Training records Python, torch,
transformers, PEFT, CUDA/device identity and peak allocated memory. No fixture made a model or
GPU call. The exact pre-review revision is retained under `pre-main-review-v1/`.
