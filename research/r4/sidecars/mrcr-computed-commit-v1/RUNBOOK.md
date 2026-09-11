# Computed commitment versus one final restatement

Run only after the parent assigns the original 4B endpoint. This command does not
start/stop a server or acquire the GPU. `READY.json` is the final CPU-preparation
seal. The six previously used short MRCR documents are development data, not new
heldout evidence or a long-context claim.

```bash
MRCR_COMMIT_ENDPOINT=/absolute/new-service/endpoint-original.json
env CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/mrcr-computed-commit-v1/driver.py \
  run --endpoint "$MRCR_COMMIT_ENDPOINT" \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/mrcr-computed-commit-v1/outputs/attempt-001
```

The descriptor must name `strict-rlm-qwen3-4b-role-original-v1`, the exact converted
step-0 adapter `857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6`,
and the frozen original-role binding. The API key stays in the descriptor's named
environment variable, never in files/arguments. Before model calls the runner
authenticates source/input/image hashes, all 504 exact FP32 source/conversion
tensors, base manifest, endpoint identity and live `/models` alias/root/parent.
This is disk/launch/live-advertisement evidence, not live-memory tensor attestation.
An old stopped endpoint is not accepted as proof that a model is now loaded.

Six sequential owned containers; fresh seeds 981269100–981269105; T0/full support;
native Qwen3 thinking-enabled rendering; no compaction; at most five shared prefix
calls including children plus one final call; 2048 actions/call. A 35,227-byte
commitment cap was derived from full public document sizes before gold was read.
Hard dispatch/runtime budget is1200s, at most200s per episode; cancellation and
owned-container cleanup can add grace. Never automatically replay a failed case.

Every coordinate writes full `EPISODE.json`, actual native wire calls and
`SCORE.json`. Candidate UTF-8 bytes/base64/hash and the exact shared conversation
are persisted before restatement; no submission means no fabricated candidate.
Final tool requests are recorded but never executed. Raw official similarity and
byte-exact/strict-terminal results are separate. Input-budget overflow,
canonical-copy output/window exposure, length stops, tool requests, infrastructure
failures and semantic copying differences remain distinct, with raw metrics intact.

Cost accounting separates once-executed prefix cost from the single restatement
increment. Prompt counts are logical full prompts; physical uncached prefill and
cache-hit counts are unknown. Actual sampled action IDs/logprobs are retained;
they are not entropy or calibrated probabilities. No token trace is retokenized
for scoring/usage; canonical candidate encoding is explicitly a separate
feasibility diagnostic, never a replacement for native action evidence.

CPU verification (no model request):

```bash
env CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/mrcr-computed-commit-v1/driver.py verify
```

Qualifying fixtures are operator-authored, executed in unique rootless containers;
their native provider tokens/logprobs are deterministic CPU fixtures, not model
performance. Existing core, nano cache, runtime image tag and live campaigns were
not modified. The new overlay is installed and hashed only inside each owned
container. `RETRY_NOTE.md` records the inherited retry caveat and the narrow
single-attempt amendment. No resume/retry mode is provided for this six-case pilot.
