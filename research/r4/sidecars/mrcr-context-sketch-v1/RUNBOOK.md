# MRCR context-sketch ablation runbook

This sidecar is ready for a later inference launch. Building and validating it used no GPU, opened
no port, and made no inference request. The experiment compares the same frozen Qwen3.5-4B model
in three conditions: one direct full-context reference, a vanilla file-backed RLM, and that same
RLM given a small task-blind map of the context. Only vanilla versus sketch is a matched causal
comparison.

## Frozen study at a glance

- Model: local `Qwen/Qwen3.5-4B` revision
  `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`.
- Sample: 48 official MRCRv2.1 rows: 16 calibration, then 32 confirmatory. Both released bands and
  all four answer-position strata are balanced.
- Direct prompt sizes under the exact chat template: 66,999 to 133,000 Qwen tokens.
- Actual sketches in the frozen sample: 2,249 bytes for every 8-needle row and 2,270 bytes for
  every 2-needle row, below the 4,096-byte ceiling.
- Matched RLM ceilings per task: eight calls, 2,048 output tokens per call, 16,384 generated tokens,
  262,144 total reported tokens, eight turns, six subcalls, depth one, and 600 seconds.
- Primary result: paired confirmatory mean of official score for sketch minus vanilla. Direct is
  reported separately because it has a different opportunity budget.

## CPU setup and verification

Run every command from this sidecar directory:

```bash
cd /project/alex_phd/runs/rlm-research-r4/sidecars/mrcr-context-sketch-v1
export UV_CACHE_DIR=/project/alex_phd/cache/uv-prime
export UV_PROJECT_ENVIRONMENT=/project/alex_phd/envs/mrcr-context-sketch-v1
export UV_NO_MODIFY_PATH=1
export UV_DISABLE_UPDATE=1
export CUDA_VISIBLE_DEVICES=''
/project/alex_phd/tools/uv-current/uv sync --frozen --group dev
/project/alex_phd/envs/mrcr-context-sketch-v1/bin/python -m pytest -q
/project/alex_phd/envs/mrcr-context-sketch-v1/bin/ruff check source tests scripts
/project/alex_phd/envs/mrcr-context-sketch-v1/bin/ruff format --check source tests scripts
/project/alex_phd/envs/mrcr-context-sketch-v1/bin/mrcr-context-sketch verify-manifest
/project/alex_phd/envs/mrcr-context-sketch-v1/bin/mrcr-context-sketch preflight
```

`preflight` hashes the complete model snapshot, both official CSVs, scorer source, sidecar, and
exact RLM source. It reads about 9 GB of weights but does not load the model or use CUDA.

The engineering-only fixture tests orchestration and resume without a socket or model:

```bash
FIXTURE=/project/alex_phd/runs/rlm-research-r4/sidecars/mrcr-context-sketch-v1/engineering-fixtures/preflight-v1
/project/alex_phd/envs/mrcr-context-sketch-v1/bin/mrcr-context-sketch fixture --output "$FIXTURE"
/project/alex_phd/envs/mrcr-context-sketch-v1/bin/mrcr-context-sketch fixture --output "$FIXTURE" --resume
```

Fixture results are explicitly ineligible as research evidence and excluded from `MANIFEST.json`.

## Prepare a new immutable attempt

Use a new explicit path. Preparation refuses any existing path and performs no network request:

```bash
ATTEMPT=/project/alex_phd/runs/rlm-research-r4/attempts/mrcr-context-sketch-v1-001
SIDE=/project/alex_phd/runs/rlm-research-r4/sidecars/mrcr-context-sketch-v1
CLI=/project/alex_phd/envs/mrcr-context-sketch-v1/bin/mrcr-context-sketch
"$CLI" prepare --attempt "$ATTEMPT"
"$CLI" make-descriptor \
  --attempt "$ATTEMPT" \
  --output "$ATTEMPT/endpoint.json" \
  --gpu-index 0 \
  --upstream-port 8951 \
  --rlm-port 8952
ENDPOINT_SHA=$(/project/alex_phd/envs/mrcr-context-sketch-v1/bin/python -c \
  'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' \
  "$ATTEMPT/endpoint.json")
```

The descriptor binds the attempt paths, exact model and RLM source, loopback ports, decoding,
opportunity caps, controller/harness fingerprints, and both launch command arrays. It also contains
a self-attestation hash over all other descriptor fields. The runner requires the external byte
hash in `ENDPOINT_SHA`, so editing the descriptor after sealing fails before any call.

## Launch the exact endpoints

The frozen topology selects one 80 GB A100 for one vLLM server and leaves the second GPU available
for another experiment rather than paying tensor-parallel overhead for a 4B model. Capacity at the
full 262,144-token configured window remains a launch-time systems check, not a result claimed by
this CPU-only build. If it does not fit, record that outcome and create a new sidecar version rather
than silently changing this descriptor.

In terminal 1, execute the descriptor's vLLM command exactly:

```bash
/project/alex_phd/envs/mrcr-context-sketch-v1/bin/python -c \
  'import json,subprocess,sys; d=json.load(open(sys.argv[1])); subprocess.run(d["vllm"]["launch_command"],check=True)' \
  "$ATTEMPT/endpoint.json"
```

In terminal 2, execute its RLM command exactly:

```bash
/project/alex_phd/envs/mrcr-context-sketch-v1/bin/python -c \
  'import json,subprocess,sys; d=json.load(open(sys.argv[1])); subprocess.run(d["rlm_runtime"]["launch_command"],check=True)' \
  "$ATTEMPT/endpoint.json"
```

The vLLM command pins version 0.28.0, GPU index, local model path, BF16, a single sequence, prefix
caching, maximum length, and `enable_thinking=false`. The RLM command pins commit/source bytes,
same served model, temperature zero, 2,048 controller output tokens, all caps, workspace, and
canonical trace directory. Both bind only loopback. Wait for both health checks:

```bash
curl --fail http://127.0.0.1:8951/health
curl --fail http://127.0.0.1:8952/health
export MRCR_UPSTREAM_API_KEY=local
export MRCR_RLM_API_KEY=local
```

## Run, resume, and stop rules

Run calibration first:

```bash
"$CLI" run \
  --attempt "$ATTEMPT" \
  --endpoint-descriptor "$ATTEMPT/endpoint.json" \
  --endpoint-sha256 "$ENDPOINT_SHA" \
  --split calibration
"$CLI" analyze --attempt "$ATTEMPT" --split calibration
```

Re-running the same command is the resume operation. The ledger hash chain and checkpoint are
validated first; already terminal task-arm keys are skipped and no response or trace is replaced.
Failures remain zero-score terminal observations rather than being selectively retried.

Stop before confirmation if any calibration record reports `identity_mismatch`, `cap_violation`,
`usage_unreported`, or `trace_missing`; if either server exits or runs out of memory; or if four or
more of the 48 calibration arm-results are infrastructure failures (`transport_error`, `timeout`,
`http_error`, or `malformed_response`). Diagnose the frozen v1 attempt without editing it. A change
to prompts, map, caps, sample, model, server topology, or scoring requires a separately named v2.
Ordinary low task scores are a scientific result, not an infrastructure stop.

Only after those gates pass, run the sealed confirmatory split once:

```bash
"$CLI" run \
  --attempt "$ATTEMPT" \
  --endpoint-descriptor "$ATTEMPT/endpoint.json" \
  --endpoint-sha256 "$ENDPOINT_SHA" \
  --split confirmatory \
  --confirm
"$CLI" analyze --attempt "$ATTEMPT" --split confirmatory
```

Each arm can take at most ten minutes, so the absolute sequential ceiling is long; the intended
calibration is expected to finish in roughly 1–3 hours and the confirmatory split in roughly
2–6 hours. Actual wall time, calls, input/output/cached tokens, and failures are recorded, so the
final report can compare score and cost rather than accuracy alone.

## Artifacts and interpretation

The immutable attempt contains `sample-plan.json`, `task-plan.json`, one context file per selected
row, sketches, request JSON, and `seal.json`. Mutable evidence is append-only in `ledger.jsonl`,
content-addressed checkpoints, response envelopes, and canonical RLM traces. Ledger records keep
prediction and gold hashes, not copied gold text. `analysis-calibration.json` and
`analysis-confirmatory.json` are reproducible derived reports.

Interpret only sketch minus vanilla as the causal ablation. Report the direct arm as an external
reference. A positive score difference suggests that a cheap task-blind initial map helped this
fixed controller use its inspection budget; trace review must still determine whether inspection
or decomposition behavior actually changed. These trajectories are retained to design later SFT
or RLVR examples, but this inference study itself updates no weights.
