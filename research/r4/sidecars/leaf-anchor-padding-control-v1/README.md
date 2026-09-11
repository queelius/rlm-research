# CPU-prepared padding control128

Read DESIGN.md for the frozen exploratory comparison. DATA.json preserves the
eight selected grammar160 contexts. REQUESTS.json and SPEC.json freeze all128
requests before outcomes. CPU_QUALIFICATION.json records exact schema compilation,
paired physical prompt hashes, prompt lengths and tag/synthetic-output token
audits. CPU_TESTS.json records the focused test-first checks. READY.json states
what was qualified; it does not claim a service was launched or outputs observed.

The source remains in this external isolated namespace. Qualified anchor/grammar
and service lifecycle sources are imported privately and pinned by SHA256. Their
files and the active GPU chain are unchanged. Raw model outputs remain absent
during preparation; test fixtures are synthetic and written only in pytest tmp.

CPU verification (native environment, no installs):

```
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-anchor-padding-control-v1/owned.py --verify
```

Proposed owned launch argv, after main assigns the reserved GPU and retains the
qualified STRICT_RLM_CALIBRATION_API_KEY environment:

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-anchor-padding-control-v1/owned.py --directory /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-anchor-padding-control-v1/owned/attempt-001
```

The command starts the authenticated one-adapter service, verifies the actual
endpoint against the already frozen model alias, collects at most128 calls,
and releases its owned service through the unchanged lifecycle. Main owns
automatic handoff integration; this sidecar writes no parent acceptance.
One attempt only; never retry implicitly or overwrite frozen inputs/artifacts.
Owned startup/cleanup records land in owned/attempt-001; per-call output and
analysis land in outputs/attempt-001. Cap is1800 seconds including startup,
collection (at most900 seconds) and reserved cleanup. The actual endpoint/HTTP
transport has not been exercised during preparation.
