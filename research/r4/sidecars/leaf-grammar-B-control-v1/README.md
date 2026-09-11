# Mixed-size B baseline on the fixed grammar-transfer requests

CPU preparation only. No model call or launch is authorized by these files.
READY.json will be the final publication marker; absent READY means not ready.

Read [DESIGN.md](DESIGN.md) for the question and limitations and [PLAN.md](PLAN.md)
for the bounded preparation steps. SPEC.json references the unchanged parent DATA,
contains every exact request and the crosswalk to both parent weight coordinates.
PROMPT_IDS.json retains full native token arrays; CPU_QUALIFICATION.json binds their
hashes to the parent study. WEIGHTS.json authenticates fixed-final B204, not a
validation-selected checkpoint. CPU_TESTS.json records focused test evidence.

Parent launch proposal (requires a matching parent PLAN/ACCEPTANCE; inherit actual
CUDA_VISIBLE_DEVICES MIG UUID and LD environment, never substitute CUDA=0):

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-grammar-B-control-v1/owned.py --operation-root /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-B-grammar-control --directory /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-B-grammar-control/attempt-001/B-service
```

The unchanged qualified lifecycle starts one truthful B alias, checks native
version/model binding, runs `driver.py bind --endpoint-descriptor ACTUAL.json
--spec-path NEW_BOUND.json`, then `driver.py run --spec-path NEW_BOUND.json
--output-dir outputs/attempt-001 --overall-start-epoch START`, and releases only
owned processes in finally. No existing endpoint-selected.json is required.

Collection900s, four workers/120s calls/3072 outputs; owned1800s including startup
and120s cleanup reserve. HTTP workers have GPUs hidden. The launch service inherits
the accepted GPU environment. Reuse frozen PID/start-ticks/UID ownership checks,
including PRL::Inference process-title handling; no generic cleanup or retry.

Retain every call and wire body, STATUS/analysis/error/usage output and owner
completion marker. Compare B to parent old/indexed coordinates within format and
grammar; invalid arrays have unavailable semantic alignment, while infrastructure
and unrun outcomes remain null. This is a later-stage component control, not a
new RLM experiment or an interleaved three-weight replication.
