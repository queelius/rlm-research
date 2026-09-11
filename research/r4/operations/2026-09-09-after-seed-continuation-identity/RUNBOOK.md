# Parent-only successor after the already-started seed continuation

This tiny loader changes only ROOT on the hash-pinned7d329 coordinator. No scheduler
or lifecycle behavior is added. The parent reviews and writes ACCEPTANCE.json;
this preparation does not accept, launch, inspect GPUs or signal any process.

Wait on exact PID/start ticks from the active continuation START.json. Its effective
wait deadline is actual child COMMAND.started_epoch+3030+120cleanup+180margin.
Those allowances are already inside predecessor.deadline_epoch, so the additional
predecessor_cleanup_grace_seconds is0. There is no upstream-wait allowance for this
already-launched predecessor. Preserve the current predecessor regardless of
success or failure; never signal it. Require GPU process list empty and the existing
shared lock before launching the accepted identity96 command, once, without retries.

Identity96 keeps its frozen owned directory/output and600collection/1200owned caps;
parent child envelope1230s plus the coordinator's bounded authenticated cleanup.
Reuse the exact actual MIG UUID/LD environment recorded in predecessor COMMAND.
All source/input/READY hashes and the exact argv must be parent-accepted. Per-call
hash scans or adaptive experiment choices are not introduced.

Read-only CPU checks: two desired RED tests, then exact loader/plan/deadline checks;
no broad lifecycle suite or live service needed. READY.json is published last.

Parent commands, from this directory, using the qualified native Python:

```
python handoff.py acceptance-template
python handoff.py run
```

The template has approved=false and grants no authority. Parent must publish the
reviewed acceptance before a successor can run. Retain all COMMAND/OWNER/EXIT,
completion markers and RESULT/STOP, including nonzero results and elapsed wait/work.
