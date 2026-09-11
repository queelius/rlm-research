---
status: prospective_frozen_recovery
date: 2026-09-10
planned_calls: 40
supersedes_ready: root-j1-sufficient-statistics-v1/READY.json
---

# Direct-statistics v2 recovery

This preserves the v1 scientific request: all 40 sealed ceiling chunks, seeds, record order, c32
checkpoint, strict eligible-user statistics, and the task-aware prompt/statistics/LLM-summation
bundle. It fixes only prelaunch producer accounting. Required call IDs are derived from the frozen
PLAN per episode; a missing ID makes the episode NULL. The actual sealed mapping is two 32-record
chunks per size-64 episode and eight 32-record chunks per size-256 episode.

V1 READY was withdrawn before any scientific call and its bytes remain preserved. No outcome was
rerolled. All other no-gold, no-retry, no-partial-salvage, and 1,200-second constraints are unchanged.

