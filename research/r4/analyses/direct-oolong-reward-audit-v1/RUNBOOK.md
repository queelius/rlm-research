# Direct OOLONG reward audit v1 runbook

This analysis is CPU-only and reads the completed attempt without modifying it. Run it with the
pinned Prime environment:

```bash
cd /project/alex_phd/runs/rlm-research-r4/analyses/direct-oolong-reward-audit-v1
/project/alex_phd/envs/prime-rl-5990b1b/bin/python audit.py
/project/alex_phd/envs/prime-rl-5990b1b/bin/python -m pytest -q tests
/project/alex_phd/envs/prime-rl-5990b1b/bin/python -m ruff check audit.py \
  future_strict_scorer.py tests
/project/alex_phd/envs/prime-rl-5990b1b/bin/python -m ruff format --check audit.py \
  future_strict_scorer.py tests
```

`audit.py` fails closed if any authenticated run, dataset, manifest, or scorer input changes. It
rewrites only `audit.json`, `trace_scores.jsonl`, `FINDINGS.md`, and `manifest.json` in this
analysis directory.

## Future strict taskset handoff

`future_strict_scorer.py` is a tested drop-in adapter, deliberately not installed into the sealed
sidecar. A future taskset can copy it into `oolong_prime_v1`, register taskset ID
`oolong-prime-direct-strict-v1`, use `StrictTerminalResult.strict_reward` as its sole reward, and
log `audit_metrics()` as non-reward metrics. The official scalar remains visible under
`official_correctness_audit` but must not enter the advantage. The adapter requires the prompt's
explicit schema on the last nonblank output line; invalid terminals receive strict reward 0.

Before launch, add a native verifiers-v1 taskset wrapper, register the ID in the environment
package, test metric/reward routing in Prime, and reseal that *new* sidecar version. Do not retrofit
the adapter into this completed attempt or its manifest.
