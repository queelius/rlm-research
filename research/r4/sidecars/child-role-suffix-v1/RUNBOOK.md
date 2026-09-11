# Parent-only launch

First read READY.json and authenticate its source/artifact closure. Preparation does not launch or grant device authority. Use the qualified Prime interpreter and the parent's actual exclusive MIG UUID, LD library environment and existing `STRICT_RLM_CALIBRATION_API_KEY`; do not hardcode CUDA0 or alter shared environment files.

CPU verification:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/child-role-suffix-v1/owned.py --verify
```

Exact proposed parent-accepted argv (new output directory required):

```sh
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/child-role-suffix-v1/owned.py --output /project/alex_phd/runs/rlm-research-r4/sidecars/child-role-suffix-v1/outputs/attempt-001
```

The parent supplies serialization, exclusive device checks and acceptance. This wrapper owns only its new service/collector groups, authenticates V2 process identities including `PRL::Inference`, uses the qualified vanished-process-as-absent helper, and releases in `finally`. It never cleans unrelated GPU processes or retries a stopped study. Inclusive job1800s; startup deadline180s from entry; work deadline1680s; collection≤1500s; cleanup reserve120s. Suggested parent outer timeout1830s plus120s emergency cleanup grace, recorded separately from the scientific1800s envelope. Overrun is measured, not silently redefined as compliant.

Artifacts: RUN/BINDING/CAPTURE_SPEC and service ownership/logs at output root; raw episode checkpoints in `rollout/episodes`; graph/request/response/depth/alias records in `rollout-routing/role-audit`; monotonic allowed/prevented dispatch records in `rollout-routing/dispatch-budget`; terminal/release markers retained on error. `DISPATCH_STATUS.sent` means allowed request-hook entries before transport, not known successful provider completions. Reconcile server status and sampled tokens separately. Global caps affect only incomplete/canceled/unrun coordinates, never earlier observable answers.

After release, run the bounded CPU readout once:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/child-role-suffix-v1/driver.py analyze --output /project/alex_phd/runs/rlm-research-r4/sidecars/child-role-suffix-v1/outputs/attempt-001
```

READOUT.json is the arm/coordinate comparison. The inherited rollout `analysis.json` is a checkpoint-time generic native-client summary, not the final paired suffix analysis. Conflict screening is explicitly lexical/manual-review, not a semantic adjudicator; inspect retained child user requests before concluding a suffix was ignored. Root `trace_trainable` is historical capture-mask metadata only: no RLVR admission or update is performed.
