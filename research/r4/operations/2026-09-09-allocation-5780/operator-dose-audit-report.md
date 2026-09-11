---
title: Independent audit of exact operator SFT6 to SFT24
date: 2026-09-10
status: sealed
---

# Question

Does more training on the same full operator trajectories make the learned child-acquire/reduce/stop
routine reachable in free execution, rather than only lowering teacher loss?

# Evidence

The exact checkpoint continuation passed all independent ancestry, 504-Adam-moment, RNG, mask and
exposure checks. SFT24 then scored 29/48 strict full endpoints (28 nonzero), versus SFT6's 5/48
(2 nonzero). Among jointly available pairs, SFT24 won 19 and lost one. Conservative planned bounds
remain separated: 29--39 versus 5--22.

SFT24 physically acquired a child in 48/48 planned endpoints, versus 1/48 for SFT6. All 29 SFT24
successes had a complete observed child map, independently matched the reduction of those actual
returned labels, and displayed the scalar in executed code before the final. Five wrong results were
faithful reductions of imperfect child predictions; one was a root reduction error. The evidence
supports actual single-batch acquisition and scoped reduction, but not robust multi-batch state
accumulation.

# Interpretation and next comparison

Repeated SFT on this narrow corpus crossed a real behavioral threshold for this model/interface; it
was not just better teacher NLL or more zero answers. The panel has only 12 dependent context
clusters, policy phases were serial, and source-prepared contexts are not globally unseen.

Deprioritize more identical passes. The smallest next comparisons are a fixed intermediate-checkpoint
readout to locate the threshold and a genuinely new-context SFT24 replication. Only then decide
whether to add diverse stopping/error-recovery and multi-batch-accumulation trajectories.

Authoritative analysis: `analyses/root-operator-dose-continuation-live-2026-09-10/REPORT.md`.
