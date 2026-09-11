---
status: approved_additive_amendment_before_implementation
date: 2026-09-10
supersedes: DESIGN.md merge-and-failure primary policy only
---

# No-answer-fallback correction

The primary result is per-protocol. If any planned recheck batch is native unavailable, its episode
is NULL. If any planned recheck batch is authenticated but invalid, its episode is an observed
invalid result. Neither case produces a merged map or downstream answer, and neither retains the
baseline labels as runtime fallback. No partial batch is salvaged.

For a valid complete recheck batch, every selected ID is overwritten unconditionally with the new
label and every unselected ID remains from the immutable baseline map. The unchanged baseline is a
separate read-only comparator, not a fallback arm.

All other frozen choices remain: exact label-token mean confidence; label-blind tie and uniform
hashes; selected-only 16/32 repacks; paired fresh seeds; 24 new calls; all eight correlated episodes;
child and J1 measures; promotion requirements; one A100 and 1,800-second cap; no retry or reroll.
