# Additive V2 runtime correction

V1 was CPU-sealed but never accepted or launched. V2 retains the exact V1 campaign,
192 training coordinates,96 readout coordinates, seeds, SFT24 start, c32 child,
terminal reward, optimizer numerics and10,800-second outer cap. It writes only the
new exact namespace `outputs/attempt-002`; this is a pre-science correction, not a
reroll or response replacement.

Independent read-only reproduction found four composition defects before any V1
science call: inherited trainer replay named absent `qsr_native.py`; exporter and
nested metrics lazily imported aliases after the original temporary alias scope;
the180-second startup alarm remained armed across600/2,340-second collection; and
frozen warm TASKS intentionally stored exact first-prefix IDs but not the ancestor
`task_hash` key that the composed collector still required.

V2 adds a real `warm_native_v2.py verify-export` entry and changes only the one
qualified trainer replay path to that file. Export/replay calls bind both qualified
collector and native modules for the full lazy call. Collection re-arms its
stage/shared deadline before command and again before export, including after a
fired command timer. The collector replaces the impossible missing-task-hash check
with equality to the frozen exact first native prefix. Context, records, question,
setup, coordinate and raw episode identities remain bound by frozen inputs/spec,
collector records and authenticated replay; no task-data authentication is dropped.

Focused qualification includes the original three reproductions, exact attempt-002
guard, timer-after-timeout regression, real authored mixed24 native collection,
complete export, native replay, root token/logprob evidence and trainer `--preflight`.
The provider fixture is synthetic and never training/scientific input; model and
gradient execution are disabled. MAIN retains acceptance and GPU launch authority.
