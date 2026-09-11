# Parent-only root96 waiter

The frozen root96 study has been main-reviewed. This operation's loader/plan still require main
review. `ACCEPTANCE.template.json` is deliberately false and grants no authority. Main may inspect
its exact commands/source hashes, set approved=true in a separately published ACCEPTANCE.json,
then launch the waiter using the qualified Prime interpreter:

```bash
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-after-indexed-followups/handoff.py verify
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-after-indexed-followups/handoff.py run
```

Inherit the exact CUDA_VISIBLE_DEVICES and LD_LIBRARY_PATH strings in PLAN, plus the existing
API-key environment variable without recording its value. The loader changes only ROOT in the
frozen coordinator; `sidecars/root-rlvr-campaign-v1/COORDINATOR.lock` is unchanged.

The waiter watches PID1988752/start_ticks1072428288, never signals it, requires parent acceptance,
waits for empty GPU, acquires the shared lock, checks empty GPU again, and launches root96 once.
The child receives3720s outer process envelope, while root96 retains its3600s internal budget.
The root driver owns and releases its own services. Emergency outer cleanup signals only the
owned root job's authenticated process group. An occupied GPU is not permission for broad cleanup.

`attempt-001/START.json`, event log, `root96/COMMAND.json`, `OWNER.json`, `EXIT.json`, and final
RESULT/STOP preserve actual identity and outcome. No retry or automatic rerun exists. Completion
markers pin terminal/analysis and both owned-service release records. A second grammar160 job
is intentionally absent; it will need a separate exact-predecessor operation and authentic weights.

`verify` is only a read-only path-readable check inherited from the original coordinator.
Launch authorization comes from the exact-hash ACCEPTANCE, not from verify or READY alone.
