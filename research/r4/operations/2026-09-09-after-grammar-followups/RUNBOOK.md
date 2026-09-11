# Automatic B80 and padding128 controls after grammar160

This operation reuses the frozen coordinator through handoff.py; only ROOT is
rebound. The existing shared GPU lock, empty-process checks and exact same-user
owned lifecycle remain. No accepted predecessor or sidecar source is changed.

Order: grammar160's exact coordinator PID2129741/start1072915615 exits; B80 starts;
then padding128 starts. Each new job needs empty GPU and shared lock. A failed job
is preserved without retry; an occupied GPU blocks its successor, never triggers
unrelated cleanup. The conservative predecessor bound is06:34:22 UTC, not a
planned start time. A normal exit permits immediate handoff.

B80 uses the frozen earlier mixed-size-trained adapter59ad854 and exact parent
grammar160 coordinates with alias-only request changes. Padding128 uses oldc32de
and compares meaningful versus placeholder tags, with anonymous and ID-map bridges.
See ../2026-09-09-proceed/B_CONTROL_BRIEF.md and PADDING_CONTROL_BRIEF.md.
These are exposed/developmental component studies, not whole-RLM gains or a fully
interleaved three-weight confirmation. Their results do not depend on the outcome
of the preceding coordinator-instruction study.

Main read all new sidecar source/test/design files and both independent bounded
source reviews. Fresh checks: B six tests PASS; padding eight PASS; both owned
--verify commands PASS. The three handoff tests first failed with missing loader,
then all passed with the minimal ROOT-rebinding implementation. No broad suite.
Independent reviews found no material blocker; real single-alias service binding
remains an explicitly accepted exploratory integration risk, checked live by each
run's version/model-card/prompt-identity checks.

Clock boundaries: B1800 seconds begins inside execute after source verification;
parent1830 covers that verification allowance. Padding1800 begins at main entry.
Both collectors have900-second caps, and owned cleanup reserves120 seconds.
The unchanged parent's own signal grace is additionally bounded90+20+10 seconds.
Partial/unrun/invalid/error outcomes are separate, and no failing raw output is
repaired, executed or hidden. Exact commands and completion markers are in PLAN.

B's owned directory is this operation's B80-owned, required by its accepted
operation-root interface. Padding's directory is its sidecar/owned/attempt-001,
required by its own wrapper. Each collector writes its frozen outputs/attempt-001.
No output directory may preexist; do not relaunch manually.

After main publishes and validates ACCEPTANCE.json, the command is:

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-after-grammar-followups/handoff.py run
```

Inherit only the explicit CUDA/driver paths from PLAN and the existing owned
service API-key environment without printing credentials. Confirm the actual
waiter's PID/start in attempt-001/START.json; a template with approved=false is
not acceptance. Live launch details belong in the session/queue, outside the
immutable accepted source closure.

Analysis cautions from independent review: free object key order may put label
before tag; do not claim a before-label mechanism without checking raw order.
Pooled class histograms are not per-context count accuracy. The later additive
analysis should compute per-call count agreement from retained aligned records.
Placeholder instructions add26 prompt tokens; synthetic matched output lengths
are not matched realized compute. B's later service phase is a time/order nuisance.
