---
status: frozen_pending_main_review
date: 2026-09-10
study: root-question-sensitive-terminal-rlvr-recovery-v2
gpu_launch_authority: MAIN_only
---

# Question-sensitive composed-task terminal RLVR

This is additive attempt-003. Attempt-001 is retained unchanged as an integration
failure: windows 1 and 2 recorded 24 rows each but made zero physical requests due
to missing `task_hash`; window 3 was stopped by MAIN, with zero optimizer updates.
Attempt-002 repaired the native TASKS identity contract and made physical requests,
but carried the owner startup `SIGALRM` into collection. The alarm interrupted
window 1 after 146.67 seconds even though the collector had been given a 359.67-second
cap: 20/24 rows were recorded, 16 were admitted, no complete training batch was
exported, and no optimizer update occurred. Initial descriptions that blamed the
360-second collection cap were therefore incorrect. Fixed-start readout completed;
MAIN stopped attempt-002 after the fixed-last service had started, and the attempt is
retained unchanged as integration/timer evidence.

Attempt-003 changes only the owner phase boundary: immediately before each collection
stage, it replaces the consumed startup alarm with the absolute collection deadline.
The 360-second cap, all 192 coordinates, seeds, task groups, policies, objective, and
readout are unchanged. There is no reward-based subset selection, repartitioning,
reroll, or fill-in. Namespace-dependent task hashes are regenerated for this distinct
sidecar while prompts and scientific coordinates remain unchanged.

The decision question is whether terminal-reward RL on composed question-sensitive
tasks strengthens learned task-sensitive routines, unlike the earlier primitive-only
curriculum that damaged primitives and produced no faithful composed behavior.

The immutable start is the exact fixed-last QS recovery checkpoint selected by
`root-question-sensitive-sft-recovery-v1/outputs/attempt-003/training/SELECTION.json`:
checkpoint-0006, adapter SHA-256
`4d8287537a9ff3d8e33bc0314f64315dee06e71b801257b389dab8b667e27aca`.
The root starts from this QS6 4B checkpoint. The child remains the exact fixed c32
adapter `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`
used by the original and follow-up QS studies; root and child intentionally differ.
RL starts at cursor/optimizer step zero; SFT optimizer state is not loaded.
The frozen recipe uses AdamW at learning rate 5e-5, PPO clip epsilon 0.2,
token-importance-sampling cap 2.0, and root-action-only loss.

Training uses all 48 composed tasks (T1, T2, M1, M2, J1, J2) from the eight QS
TRAIN contexts. There are eight fixed windows, one context per window, six task
groups per window, and four independent samples per task: 24 physical attempts per
window and 192 planned attempts total. Seeds are fresh and fixed. There are no
rerolls, replacements, gold-zero filters, or protected examples in training.

The qualified group-relative terminal-reward kernel is reused. Exact format-valid
`Answer: N` finals receive reward 0/1 against host gold. Authenticated malformed or
empty finals are preserved in the physical inventory but remain unadmitted when the
qualified kernel cannot construct trainable root actions. Missing/unreturned results
remain NULL. No reward is manufactured. Advantages are centered within each
four-sample task group; only root action tokens are credited, current actions are
masked as in the qualified trainer, and child actions are never credited. Four
samples make advantage estimates higher variance and more format-conditioned than
the earlier eight-sample groups.

Each complete window is consumed exactly once. A window with no admitted update is
a recorded noop; cursor order still advances, and no later window fills it. At most
eight optimizer updates are possible. Every actual update commits a checkpoint in
its own window-local training namespace. The selected policy is fixed-last committed,
including the start checkpoint if there are zero updates; there is no validation or
outcome selection.

Readout is fixed before launch: all 72 protected QS tasks under the exact start and
fixed-last RL policies (144 endpoints), with the existing eight protected contexts
disjoint from the eight training contexts under the QS process. The 24 primitive
tasks are retention readout only. Readout uses actual returned finals: authenticated
empty/malformed is observed zero; missing/unreturned/unverified is NULL. All child
evidence and physical requests remain auditable.

The single-A100 envelope is 7200 seconds inclusive: training/capture through 4500,
paired readout reserve 2400, cleanup 300; owned termination is at 7170 to retain a
30-second parent margin. Capture time and optimizer time are
reported separately. The qualified GPU trainer/dispatcher and process-identity
lifecycle are reused; CPU clients receive no GPU visibility. MAIN alone may review,
seal READY, and launch.

The additive timer fix is qualified on the actual native dispatcher/run-slot path:
24 fixed window-1 slots with four workers completed 24/24 provider calls in 201.30
seconds under the production 360-second cap. The provider was a CPU-only fake and
made no model or GPU calls. This validates transport completeness and timer margin,
not model latency, rewards, or scientific outcomes.
