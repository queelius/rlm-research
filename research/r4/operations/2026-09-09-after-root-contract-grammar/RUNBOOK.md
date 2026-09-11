# Parent-only grammar160 successor

Preparation freezes loader/PLAN/ownership now. `finalize.py` returns WAITING without writes if
the authentic fixed-final weight closure is unavailable. After current_literature publishes
grammar READY/WEIGHTS/OWNED_READY, run CPU-only:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-after-root-contract-grammar/finalize.py
```

This independently calls the frozen fixed-final weight authenticator and writes READY plus
ACCEPTANCE.template.json with approved=false. It never grants launch authority or changes any
training/HTTP/owned-wrapper source. Main inspects the exact operation/template, separately
publishes ACCEPTANCE.json with approved=true, and alone launches:

```bash
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-after-root-contract-grammar/handoff.py run
```

The parent may start the unapproved waiter earlier; it cannot launch a job until acceptance
exists and all exact hashes validate. Inherit PLAN CUDA_VISIBLE_DEVICES/LD_LIBRARY_PATH and the
existing API-key environment without printing its value. The shared campaign lock is unchanged.

Waiter predecessor is PID2120762/start_ticks1072822471; PGID2120755 is recorded but never signaled.
Deadline is upstream indexed deadline+4560s, with an additional120s exit grace. This includes
all upstream waits,3720s root envelope, signal cleanup and180s polling/query/metadata allowance.
No premature waiter-start+3720 deadline is used.

One exact2730s child command starts owned.py with this operation root and grammar160-owned beneath
it. The wrapper owns/releases its two-adapter service; semantic aliases authenticate old c32de
and fixed indexed epoch2/step204. The collector retains its160calls/1800s sampling cap and2700s
overall wrapper clock. No retries, generic cleanup, source changes or direct host code execution.

`attempt-001` stores START/events/grammar160 COMMAND/OWNER/EXIT and RESULT or STOP. Service release
is proven by grammar160-owned/SERVICE_STOPPED, not merely a closed port. Occupied GPU always
prevents the next launch. The root predecessor may finish nonzero; that is retained, not retried,
and the independent grammar job still requires its own approval and an empty GPU.
