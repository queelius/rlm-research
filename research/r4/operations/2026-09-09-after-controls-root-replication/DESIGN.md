# Automatic independent-root replication after B80 and padding128

This operation waits for the exact existing after-grammar-followups coordinator:
session39984, PID2260395, start ticks1073262797, PGID2260394. It never signals
that predecessor. A PID with changed start ticks is a replacement, not the
predecessor. Process evidence and its frozen PLAN/ACCEPTANCE/START bind this
identity. Outcome files are not consulted for the proposed successor choice.

The only runtime code is a tiny private import of the unchanged qualified
coordinator.py with ROOT rebound to this operation. Source SHA256:
7d3294241939297741f26ca657782f757e43b520a717a17a6edac378f32873c1.
Its shared campaign lease, empty-GPU checks, explicit main acceptance, exact
argv/source authentication, bounded owned-child cleanup and no-retry behavior
remain unchanged. This is not a new scheduler.

The conservative predecessor deadline starts at the predecessor PLAN's own
upstream deadline1788935662.2401078, which already includes the complete earlier
root-contract→grammar waiting chain. Add120seconds predecessor cleanup,
300seconds acceptance wait, two per-job GPU-clear allowances120seconds each,
both1830-second B80/padding jobs, two120-second owned-child cleanup allowances,
and180seconds operational margin:4740seconds total. The result is
1788940402.2401078. The new coordinator additionally retains its normal120-second
predecessor grace. Neither deadline is derived from this waiter's launch time.

After exact predecessor exit, main must publish acceptance. The coordinator then
requires the shared GPU to be empty, acquires the unchanged shared lease, checks
the GPU again, and launches exactly one independent-root command. Its outer
process cap is6030seconds around the6000-second replication wrapper, with the
coordinator's normal90/20/10-second owned cleanup escalation. No retries or
additional experiments are implied. Runtime/failure/checkpoint evidence stays
in the independent sidecar; operation logs remain in this new namespace.

The accepted source set covers the qualified coordinator, wrapper/tests/docs,
process evidence, predecessor plan/acceptance/start, and complete frozen
independent campaign, QUALIFIED_READY, recipe, initial weights/base, source/input
and both lifecycle/admission manifests. Frozen replication files remain unchanged.
An independent review that requires a source amendment must return to main for
explicit coordination; this operation's acceptance must then be regenerated.

Preparation creates only false ACCEPTANCE.template.json. It neither publishes
ACCEPTANCE.json nor launches this handoff or any GPU/model/service operation.
