---
status: prospective_frozen_before_attempt_002_outcomes
date: 2026-09-10
study: root-question-sensitive-terminal-rlvr-lr1e5-v1
run: outputs/attempt-002
planned_training_attempts: 192
planned_new_readout_endpoints: 72
reused_start_endpoints: 72
---

# Prospective LR1e-5 terminal-RLVR audit

Do not read scientific outcomes until the exact attempt-002 `OWNER_TERMINAL.json` and parent
`EXIT.json` exist. Require the EXIT completion-marker hash to equal the owner-terminal hash,
no timeout, released ownership, and no remaining GPU process. Exit zero or a complete readout does
not imply that eight windows or any optimizer update completed. Report the actual fixed cursor,
completed windows, noops, failed/partial windows, and committed optimizer step.

The sealed attempt-002 campaign identity is
`0f59a5f3706de9ce5d95ab4696ac4772b311e91cbc703997627ca5de9341e4de`; campaign SHA-256 is
`1ac39df03ffffeaabca2cdf5e17e08d56e14f2b98a72ea2c28ad61319e8a66c9`; READY identity is
`03cd8b1d61a4c1456de353edfe7e9effaabd7eb8a6a3a975cd508c3b1bc1e41e`; READY SHA-256 is
`6b4921c90b337396ca4ee8a6b0819a6446801cbbe101ff5c9d5f8559e523b210`.

Audit all 192 planned training rows in eight fixed windows, retaining every planned coordinate and
reason for missing, capture failure, format rejection, non-admission, homogeneous-group noop, or
update. Recount physical requests/results from native `role-audit` files rather than trusting the
known-incomplete convenience cost ledger. Authenticate all exports and recompute terminal 0/1
rewards. Authenticated empty or malformed returned finals are observed zero; missing, unreturned,
or unauthenticated results are NULL. Never refill or select a subset based on outcomes.

For every committed update, require complete mixed-reward groups of four within the exact task,
recompute population-centered advantages, and verify root-current-action-only masks, no child
credit, PPO clip 0.2, TIS cap 2, norm clip 1, and the objective-matched sparse credited-position
implementation. Authenticate the checkpoint adapter/config/state, fresh-Adam-at-zero lineage,
optimizer/RNG hashes, parameter names, moments, full parameter groups, and exactly `lr=1e-5` after
each restore. Record that sparse-head numerics are not bitwise identical to the high-LR campaign's
first dense update.

Audit all 72 new fixed-last endpoints against the already authenticated 72-row QS6 start export.
Require exact coordinate, seed, public prompt/task, host-gold, fixed-c32-child, and request-content
matching except policy/call identity. Primary reporting is paired fixed-last minus QS6 start:
known-pair wins/losses/ties, availability, missing-outcome worst/best bounds, all eight contexts,
48 composed-task rows, and 24 primitive retention rows. NULL pairs never enter a known denominator
without disclosure. Separately report raw/native answer accuracy and agent-reviewed faithful+strict
execution from actual programs, child/tool observations, complete retained maps, and final-state
use; gold-zero coincidence is not faithful execution.

Report physical calls, returned responses, known/unknown token usage, input/output tokens, capture
time, optimizer time, service time, readout time, total wall time, and peak training memory. Billing
is not inferred. Comparison with high-LR fixed-last is secondary and must use its separately sealed
audit without selecting a favorable checkpoint.

Attempt 001 is an integration failure, not a scientific zero: it made no collection or optimizer
progress because local `START.json` was absent, and its readout failed through the same binding.
Its retained owner-terminal SHA-256 is
`4052d9a3ed386c5910672b0e02a0ebdf9e2e7a5738f0bcab5b6c20a9d344194f`; parent EXIT SHA-256 is
`db040cb03167ac10d6f466855e4a9633caa1851c6c7ebac0f55cb36aaf5eb48d` (exit 1, no timeout,
3.341997876763344 seconds, released, no remaining GPU process). The repair and immutable paths are
documented by `ATTEMPT002_RECOVERY.md` SHA-256
`7dec56b0cb357499261c8780509b8057fa0721ccc3879a47a39a3ee0c998501e`.
