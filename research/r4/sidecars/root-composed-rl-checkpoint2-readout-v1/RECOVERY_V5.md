---
title: Qualified source-namespace checkpoint-2 readout recovery
date: 2026-09-10
status: additive_prelaunch_recovery
---

Attempt 002 reached the native dependency stack but failed before service or requests because the
readout alias changed the qualified collector's root namespace. That made its original-start,
campaign, recipe, and deepest planned-phase contracts point at files or semantics absent from this
sidecar. Attempt 003 instead keeps the qualified terminal collector, native renderer, common state,
campaign, recipe, and `readout-rl_last` phase in their original source namespace. Only the service
root policy is the separately authenticated checkpoint 2; the external inventory names that arm
`checkpoint2`. The local START receipt is byte-identical to the source receipt and is pinned for
audit, but is not mislabeled as checkpoint 2 or substituted for the source collector's start.

No source coordinates, seeds, prompts, model policies, scores, caps, or comparators change. Attempts
001 and 002 remain zero-request infrastructure failures. The actual source `binding_for` and
`prepare_spec` path plus all 72 native task identities and nonempty first prefixes are exercised
under the native environment before READY.
