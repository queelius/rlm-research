# Grammar160 after the exact root96 coordinator

Parent-authorized CPU preparation only. Reuse the exact frozen queued-successors coordinator
with only ROOT rebound. The shared campaign lock and all process/GPU/acceptance behavior remain
unchanged. Never signal the predecessor or launch a service during preparation.

Exact predecessor: PID2120762/start_ticks1072822471, recorded PGID2120755 (not assumed to equal
the PID). This is the root96 waiter, not its eventual inference child. Its START epoch is
1788924412.1280565 and it can still spend time waiting for upstream indexed SFT.

Conservative deadline derives from the immutable predecessor PLAN:
upstream deadline +120s predecessor cleanup grace +300s acceptance wait +120s GPU-clear wait
+3720s root96 process envelope +120s owned-child signal cleanup +180s operational margin.
The last allowance covers poll overshoot, up-to20s GPU-query calls and post-child metadata I/O;
it is not generation budget. The grammar waiter allows a further120s predecessor-exit grace.
Do not use waiter-start+3720, which could expire before a legitimately delayed root job finishes.

One job: leaf-indexed-grammar-transfer-v1/owned.py, explicit operation root=this directory and
owned directory=grammar160-owned beneath it. HTTP160 calls retain1800s collection,2580s work,
2700s inclusive wrapper budget, and2730s outer coordinator envelope. The earlier path in immutable
OWNED_PREPARED was an example command; the exact new path is an explicit operational relocation,
not a changed model/treatment/request. The wrapper independently checks this operation's exact
PLAN/ACCEPTANCE argv and cannot inherit old anchor approval.

Final launch acceptance must bind actual READY.json, WEIGHTS.json and OWNED_READY.json, whose
weight closure proves fixed indexed epoch2/step204 and old c32de. Missing final RESULT/readiness
is a pending dependency, never a placeholder weight or approval. This operation may be source-frozen
and the parent may start its unapproved waiter while that dependency finishes; acceptance is only
published after the real weight artifacts can be authenticated. Preparation never sets approved=true.

The coordinator requires exact predecessor exit, main acceptance, empty GPU, shared lock, and a
second empty-GPU check under lock. One attempt only, no retries, no predecessor kill or unrelated
process cleanup. The owned wrapper releases only its authenticated service/descendants. Completion
markers preserve STATUS, ANALYSIS, FINISH and SERVICE_STOPPED; errors/caps remain observable.

Verification is bounded: loader ROOT/LOCK test, deadline arithmetic regression, and final template
requires authentic weights. All sources/commands/ownership evidence are immutable; main reviews,
publishes approval and launches. No GPU, model calls, installations, or live-source edits here.
