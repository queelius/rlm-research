# Main-owned launch runbook

Review PLAN.json, OWNERSHIP_EVIDENCE.json, READY.json and the independently
reviewed root replication source. ACCEPTANCE.template.json is explicitly false
and grants no launch authority. Only main may publish matching ACCEPTANCE.json
and launch. No new outcomes are needed to prepare this handoff.

Read-only CPU verification:

```
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-after-controls-root-replication/handoff.py verify
```

Exact proposed automatic coordinator argv, inheriting the same reserved GPU,
LD_LIBRARY_PATH and existing STRICT_RLM_CALIBRATION_API_KEY as the predecessor:

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-after-controls-root-replication/handoff.py run
```

The single accepted child argv is:

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-independent-seed-v1/campaign.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-independent-seed-v1/outputs/attempt-001
```

The waiter may start while B80/padding remain queued/running; it observes exact
PID/start identity and never signals the predecessor. Its conservative deadline
includes all declared upstream waits and both jobs; it is not waiterstart+6000.
Once predecessor exits, acceptance wait is at most300seconds and GPU-clear wait
at most120seconds. The root job's outer cap is6030seconds plus at most120seconds
owned-child cleanup. Allocation fit remains main's responsibility.

Operation records are created exclusively in attempt-001. The independent
campaign output must not exist beforehand. Root FINAL/SELECTION and each of
eight checkpoint state files are recorded as completion markers; absent markers
remain null, and nonzero exit is preserved without retry. Root transfer and
training failures remain in their original raw artifacts.

If independent review changes the replicated source, do not edit frozen files
or autoapprove. Main coordinates an additive amendment/new plan and renewed
exact source acceptance. This prepared operation has no ACCEPTANCE.json and
has not been launched.
