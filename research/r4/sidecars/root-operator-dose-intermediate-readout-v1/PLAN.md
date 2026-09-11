---
id: root-operator-dose-intermediate-readout-v1
status: cpu-prepared-not-launched
date: 2026-09-10
---

# Fixed intermediate-dose behavioral readout

Question: across the already-trained exact checkpoints 6, 12, 18, and 24, when does freely
executed acquisition, faithful reduction, and stopping change on a mechanically fixed panel?

The primary comparison is 16 paired coordinates per checkpoint (64 endpoints), using one new seed
per coordinate shared across checkpoints. Twelve capped teacher-first probes per checkpoint (48
endpoints) are a cheap syntactic-intent diagnostic and do not replace free behavior. The 16
coordinates comprise two coordinates from each of four dose-new contexts and one from each of eight
exposed contexts; planned-16, equal-12-context descriptive, and source-stratum summaries stay
separate. Checkpoint order is rotated (18, 24, 12, 6), fixed before outcomes, and is not a
best-checkpoint search.

All 112 slots remain in the denominator. A genuine native final, an attempted response without a
native final, an attempted failure without `RESULT.json`, and an unstarted slot are distinct. No
sampled code is re-executed or repaired. One paired seed can suggest an exploratory dose pattern; it
cannot establish equivalence or an abrupt phase transition.

The shared-clock cap is 3,300 seconds outer, 3,270 owned, and 3,150 work: four fixed 750-second
phases plus 150 seconds for harvest. Each phase budgets at most 180 seconds startup, 60 probe, 480
free collection, and reserves 30 for cleanup. Ordinary predecessor-stage failure does not suppress
later fixed stages when time remains.
