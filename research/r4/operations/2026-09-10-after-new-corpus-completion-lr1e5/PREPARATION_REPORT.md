---
date: 2026-09-10
status: prepared_unaccepted_not_launched
gpu_calls: 0
plan_sha256: 17f8284856438ea5009ed84442275910621b31f3048cd5964fa3ba72292b4eb3
handoff_sha256: e004260adba8083d920c635d82cf410a069e3004342b32f01469d265fdc4808d
lr_ready_identity: 166fbbfa7f790adf7a74bc252ca6757f32021f5d1a3040e6a1b0e0908c9ec953
lr_ready_sha256: ae69614d93cd879d54841294715a71cef7f3fbc181f6dd470a879599b7db5614
---

# Serialized LR1e-5 operation preparation

This operation is prepared behind the entire already-running new-corpus-completion coordinator. It
has not been accepted or launched. `ACCEPTANCE.json` and `attempt-001` are absent; the supplied
`PROPOSED_ACCEPTANCE.json` has `approved: false` and cannot authorize the coordinator.

The exact predecessor was resolved from `/proc` as PID 65691, start ticks 927017339, PGID 65690,
session 65690, and UID 1523821556. This is the whole coordinator, not its current stable-anchor child
or a later new-corpus owner. Its authenticated `START.json` SHA-256 is
`42c1b87d1c25d50e55eb429c4624e685740cc7d9f5ee91580c02a4dc2a7d66a1`.

The predecessor deadline is conservatively fixed at `1789086666.4420846`: its upstream
stable-anchor wait bound `1789083306.4420846`, plus 60 seconds for acceptance, 120 seconds for GPU
clearance, the complete 3,000-second new-corpus recovery cap, and 180 seconds for owned-stop/query
margin. Thus current queue waiting and the complete recovery are inside the predecessor bound. The
LR job's independent 15,000-second coordinator cap and internal owner budget begin only at actual LR
launch; they are not consumed while this operation waits.

The sole command uses the sealed native owner and exact unused output:

`/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-question-sensitive-terminal-rlvr-lr1e5-v1/lr_owner.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-question-sensitive-terminal-rlvr-lr1e5-v1/outputs/attempt-001`

CPU verification loaded the qualified coordinator, authenticated every acceptance source path,
confirmed `parent_acceptance_exists: false`, and reported zero GPU calls. The LR attempt and this
operation's attempt directory were absent at preparation time. MAIN must independently review the
exact plan and hashes, publish `ACCEPTANCE.json` with `approved: true`, and separately start the
handoff if it chooses to launch.

