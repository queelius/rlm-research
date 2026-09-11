---
title: Continue fixed composed-task RL from sparse checkpoint 2
date: 2026-09-10
status: design_only_pending_checkpoint2_readout
gpu_authorized: false
start_policy: exact_sparse_checkpoint2
planned_training_calls: 120
maximum_new_adam_updates: 5
---

# Decision question

Do additional fixed composed-task terminal-reward updates produce faithful acquisition, requested
computation, and stopping beyond checkpoint 2, or do they mainly increase exact-answer coincidences?
Two updates are too little evidence to retire RL, especially because update 2 was the first large
154-turn group successfully optimized with the sparse head.

# Smallest useful continuation

Resume the exact checkpoint-2 adapter, Adam state, RNG, and generation cursor. Consume the already
frozen, previously unrun windows 4 through 8 in their original order: six supported operator/scope
groups, four samples each, 24 attempts per window, 120 planned attempts total. Do not recollect or
retrain windows 1--3, refill malformed/missing samples, select by reward, or change the task renderer,
root/child roles, c32 child, temperature, PPO/TIS weights, masks, learning rate, or terminal reward.
Every fixed window advances once; homogeneous/admission-empty groups remain recorded noops.

Use the qualified sparse-head trainer and authenticate continuity at each commit. Give each optimizer
subprocess up to 1,800 seconds. That cap is pragmatic, not a runtime guarantee: update 2 used
241.797 optimizer seconds for 154 turns, 647,114 causal tokens and 18,517 credited actions, with
12.294 GB allocated, 17.421 GB reserved, and parameter delta L2 0.14389. Keep collection, optimizer,
checkpoint, and cleanup clocks separate. A conservative owner envelope is 12,000 seconds for all
five windows including five 360-second capture caps, five 1,800-second optimizer caps, and bounded
release/checkpoint margin; actual physical calls and elapsed time remain primary cost evidence.

# Readout and decision

Fix the comparison checkpoint prospectively as the last committed state after window 8 (or the last
genuine commit if later windows are fixed noops), never the best observed checkpoint. Run one paired
protected72 readout only after training. Compare it to immutable checkpoint 2, checkpoint 1 and start;
do not rerun those controls. Report NULL bounds and, separately, strict score, child acquisition,
complete retention, requested operator/scope/threshold execution, observed-state use, and stopping.

Promote further training only if the final continuation improves grounded faithful composed success
over checkpoint 2 on at least four of eight context clusters without a material primitive-retention
or availability loss. A strict-score gain driven by zero answers or wrong-operator coincidences does
not pass. If fewer than two additional real updates occur, diagnose the instantiation/admission path;
that is not evidence against the learning hypothesis. If at least two updates occur with no faithful
gain, deprioritize repeating this exact terminal-only recipe and compare a task/interface or
execution-grounded warm start instead.

# Interpretation

This remains an exposed-panel dose extension with changing fixed training contexts, not an estimate
of a smooth learning curve or new-context generalization. Sparse-head qualification supports a
mathematically aligned engineering path under measured numerical repeatability; it is not bitwise
equivalence to dense training.
