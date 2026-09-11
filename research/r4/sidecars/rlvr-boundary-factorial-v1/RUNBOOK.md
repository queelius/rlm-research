# Boundary-factorial Stage-A runbook

Status: launch-ready but deferred. Do not launch while either assigned A100 is occupied. This
sidecar launches only the 72-episode rollout screen and performs zero optimizer steps.

## Frozen execution contract

- Policy: exact Qwen3-8B base plus adaptive SFT k576 from `SOURCE.json`.
- Screen: coarse/fine ontology × 64/80/96 records × 4-turn/1-subcall or 6-turn/2-subcall.
- Replication: two task groups and three paired sampler seeds per cell; 72 episodes total.
- Sampling: temperature 0.8 with the prior authenticated sampler and action-token capture code.
- The 4/1 and 6/2 arms use independent vLLM replicas on separate 40GB A100s.
- Every full legacy-RLM process and its IPython child run inside the authenticated rootless
  container. The environment and interpreter mounts are read-only and full-tree authenticated.
- `execution_completed`, `trace_trainable`, terminal schema, correctness, and decomposition are
  recorded independently. Invalid trajectories have JSON `null` reward and are never trainable.

## CPU-only gates

Run from the sidecar root:

```bash
SIDECAR=/project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-boundary-factorial-v1
env CUDA_VISIBLE_DEVICES='' PYTHONPATH="$SIDECAR/source" \
  /project/alex_phd/envs/rlm/bin/python "$SIDECAR/source/boundary_factorial.py" \
  preflight --probe-container
env CUDA_VISIBLE_DEVICES='' PYTHONPATH="$SIDECAR/source" \
  /project/alex_phd/envs/rlm/bin/python "$SIDECAR/scripts/seal_manifest.py" --verify
```

Both commands must exit 0. The container probe opens no port, contacts no model, and executes only
fixed trusted imports. A tree, source, image, bundle, adapter, commit, or manifest mismatch is a hard
refusal with machine-readable diagnostics.

## Prepare once, then launch or resume

Choose a new absent attempt path. Preparation hashes the real tokenizer prompts and seals all Stage-A,
confirmation, and held-out identities before any outcome exists.

```bash
SIDECAR=/project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-boundary-factorial-v1
ATTEMPT=/project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-boundary-factorial-v1/outputs/stage-a-attempt-001
env CUDA_VISIBLE_DEVICES='' PYTHONPATH="$SIDECAR/source" \
  /project/alex_phd/envs/rlm/bin/python "$SIDECAR/source/boundary_factorial.py" \
  prepare --attempt "$ATTEMPT"
```

Only after two GPUs and ports 19431/19432 are explicitly assigned and free:

```bash
SIDECAR=/project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-boundary-factorial-v1
ATTEMPT=/project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-boundary-factorial-v1/outputs/stage-a-attempt-001
env PYTHONPATH="$SIDECAR/source" \
  /project/alex_phd/envs/rlm/bin/python "$SIDECAR/source/boundary_factorial.py" \
  run-stage-a --attempt "$ATTEMPT" --gpu0 0 --gpu1 1 --port0 19431 --port1 19432
```

Replace `0` and `1` only with the controller-assigned distinct devices. Re-running the identical
command resumes missing episode identities; completed bytes are not regenerated. Conflicting bytes
or changed jobs refuse. Expected duration is approximately 45–90 minutes including two model loads;
the hard per-episode subprocess timeout bounds the rollout portion to roughly 36 minutes at the
configured concurrency if every request reaches timeout, excluding server startup and teardown.

## Completion, analysis, and safe interruption

`Ctrl-C` is safe: the host `finally` block stops both process groups, container calls use `--rm`, and
no Stage-A completion marker is written until all 72 exact identities exist. Before resuming, confirm
ports are free and inspect any remaining `boundary-*` containers; do not delete attempt artifacts.

After Stage A completes:

```bash
env PYTHONPATH="$SIDECAR/source" /project/alex_phd/envs/rlm/bin/python \
  "$SIDECAR/source/boundary_factorial.py" audit --attempt "$ATTEMPT" \
  > "$ATTEMPT/stage-a-audit.json"
env PYTHONPATH="$SIDECAR/source" /project/alex_phd/envs/rlm/bin/python \
  "$SIDECAR/source/boundary_factorial.py" promote --attempt "$ATTEMPT"
```

Promotion writes only the frozen selection result. Confirmation, one-update training, and held-out
evaluation have presealed identities but no launch shortcut; update authorization remains closed until
the complete confirmation gate is implemented and satisfied. Engineering fixtures are never research
evidence.
