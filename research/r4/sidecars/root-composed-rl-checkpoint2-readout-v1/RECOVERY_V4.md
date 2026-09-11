---
title: Native-entry recovery for checkpoint-2 fixed readout
date: 2026-09-10
status: additive_prelaunch_recovery
---

Attempt 001 exited before service startup or any request because MAIN invoked the owner with the
control interpreter, whose transitive dependency stack lacks `verifiers`. Its operation and planned
NULL inventory remain untouched. This recovery changes only the exact output namespace to
`outputs/attempt-002` and the required owner interpreter to the already qualified native Python.
The fixed 72 coordinates, seeds, checkpoint-2 weights, collector, budgets, scoring, and comparisons
are unchanged. Native dependency preflight is exercised before sealing. A request without matching
cost evidence remains unknown rather than zero cost.
