# Stop the failed recording boundary, not a model experiment

Decision: MAIN, September 12, 2026, approximately14:11UTC.
Exact owned owner PID207689, parent timeout207688, collector208128; command
paths resolved read-only immediately before SIGTERM. Signal only the owner,
allow its registered release handler to stop owned children and service.

Observed eight saved wrappers so far contain no causal nodes or generated
action tokens. Interceptor attempts fail before forwarding the native request:
`Object of type PendingTurn is not JSON serializable` in the original
`collect.py` recording client's start receipt. Partial `*-start.json` files
exist without native response files. The derived18/19 root-call counts are
interceptor entries/retries, not completed physical model calls.

There is no reason to consume the remaining600-second scientific cap on the
same serialization failure. Preserve all partial files, timeout outcomes and
owner terminal. No update or scored model outcome is eligible. The preceding
CPU run_slot smoke did not cover this real recording-client boundary.

A later additive repair must exercise actual collector/recording client with
the real PendingTurn type and fake native transport through its complete
production path before another GPU launch. Do not relax the serialization
contract with repr or change these failed scores to zero. The independent
evidence-selection experiment is already accepted under the coordinator lock.
