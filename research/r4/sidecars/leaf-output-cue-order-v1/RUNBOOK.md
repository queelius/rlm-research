# Parent-only launch

Use immutable READY.json launch_argv after independent acceptance. It invokes:

```sh
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-output-cue-order-v1/owned.py --directory /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-output-cue-order-v1/owned/attempt-001
```

Cwd is this sidecar. Inherit the parent's actual exclusive MIG UUID, LD and
qualified API-key environment; do not substitute CUDA0. Parent outer cap930s.
This command owns exactly its single old-c32de service/workers; no separate
serving command or custom scheduler is needed. Parent establishes GPU exclusivity.
Unused owned/output paths required. Release is attempted in finally on errors.

Read-only CPU verification (no service/model calls):

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-output-cue-order-v1/owned.py --verify
```

Runtime artifacts: owned/attempt-001 contains service binding/descriptor,
ownership evidence, commands/logs, WRAPPER_ATTEMPT and FINISH. Collection stores
outputs/attempt-001/{calls,wire,coordinates,analysis.json,STATUS.json,ATTEMPT.json},
plus actual /version and /models preflight. Raw response model alias, complete
prompt token IDs and usage lengths are checked against frozen native templates.
Wire files retain actual bytes and order-preserving schema/body hashes; credentials
are not persisted. Request identity never uses sorted-key hashing alone.

The inherited collector stops on its first request/protocol error, without retry;
completed records persist, the affected row is null and unrun rows remain explicit.
Complete malformed/incorrectly ordered outputs remain observable strict failures
with unavailable semantic alignment. Tiny built-in summaries run before release;
subsequent independent raw audit runs after GPU release. `model_called` denotes
the collector's attempted dispatch, not proof of provider sampling. Real usage,
cache fields and missingness must accompany any cost claim. Sum of call wall
times is not overall elapsed time with four concurrent workers.

Check per-call actual key order and gold counts, not pooled histograms. Keep TREC
and SST separate and pairs nested in their two source clusters per task. The
previous-record diagnostic never repairs primary answers. No HF/vLLM pooling,
historical scores as concurrent controls, or whole-RLM benefit claim.
