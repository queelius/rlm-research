# Main-only automatic receipt72 handoff

The tiny handoff.py loader preserves the hash-pinned7d329 coordinator's exact-owner
wait, acceptance checks, empty-GPU checks, shared lock, bounded owned-child cleanup,
no-retry behavior and raw operation records. It never signals identity96 or its
upstream seed continuation. Deadline arithmetic is in DESIGN.md and PLAN.json.

Main supplies exactly the inherited MIG UUID and LD_LIBRARY_PATH declared in PLAN,
plus the existing endpoint credential. Do not copy credential values into artifacts.
No preparation command calls a GPU, starts a service, signals a process or accepts
a launch. The receipt scientific sidecar remains immutable; main's operation-local
receipt_driver.py implements only the separately documented lifecycle observation
amendment. Do not run the original driver directly through this operation.

After reviewing all exact sources, main can publish an approved copy of the false
ACCEPTANCE.template.json as ACCEPTANCE.json. Then, using the qualified native Python:

```
python handoff.py run
```

The operation waits on exact identity96 PID/start and launches one receipt72 job.
Retain START/events, COMMAND/OWNER/EXIT and RESULT/STOP, including nonzero outcomes
and missing completion markers. A failed receipt job is not retried or replaced.
No automatic CPU analysis is included while GPU authority is held. Main can run
the frozen sidecar's driver.py analyze separately after the successor operation exits.

READINESS is published only after main confirms lifecycle wrapper sources. The
template has approved=false and never grants launch authority by itself.
