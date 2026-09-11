---
title: Exact sparse-head continuation over frozen windows 4--8
date: 2026-09-10
status: prospective_cpu_preparation
gpu_authorized: false
---

Resume the exact committed Adam-2 checkpoint and consume only the original unrun composed-task
windows 4 through 8, in order. Each window retains its original 24 coordinates, seeds, task groups,
root/child interface, fixed c32 child, terminal reward, root-only masks, PPO/TIS recipe, and no-refill
rule. A clean homogeneous or admission-empty window advances the fixed window cursor as a noop but
does not advance Adam. A mixed admitted group may commit exactly one update. There is no outcome
selection, reroll, replacement, or reuse of windows 1--3.

Collection, binding, native rendering, export, replay authentication, generation, and transition
remain in the original unaliased `root-question-sensitive-terminal-rlvr-recovery-v2` namespace.
Only this owner/output namespace and the already qualified generic sparse credited-position head are
new. Each optimizer subprocess has an 1,800-second cap; each collection has the original 360-second
cap. The training-only owner has 11,700 seconds work, 11,970 owned, and 12,000 inclusive. A separate
fixed72 readout is required and is not part of this owner.

The launch is gated on the exact checkpoint-2 readout completing, releasing, and retaining auditable
physical costs, but never on its score. The final policy is the last actual commit after window 8,
including checkpoint 2 if all remaining windows noop. Strict answer reward is not evidence of
operator faithfulness; later readout must retain the semantic distinctions in the approved design.
