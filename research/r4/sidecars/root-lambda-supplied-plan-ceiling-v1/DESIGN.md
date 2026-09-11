---
id: root-lambda-supplied-plan-ceiling-v1
status: prospective_cpu_prepared
date: 2026-09-10
planned_episodes: 8
planned_child_calls: 40
---

# Supplied-plan J1 ceiling

Question: with the same fixed c32 child, does an experimenter-supplied complete
acquisition plan and deterministic public J1 reducer suffice at 64 and 256
records?

Use all four frozen scale clusters at both sizes. Split records, without
reordering, into complete 32-record batches; ask the genuine c32 model for a
complete ID-to-six-label map; and apply the fixed J1 reducer to predicted labels
and public user/weight fields. One fresh seed is fixed per episode. Host labels
and answers are analysis-only and are never rendered, repaired into a response,
or used by the reducer.

Primary: exact deterministic final versus host gold on all eight episodes,
including zero-gold episodes. Secondary: complete-map coverage, leaf label
accuracy, qualifying-user error, absolute aggregate error, and per-record
contribution error. The CPU gold-label reducer is an explicit diagnostic only.
An authenticated malformed child batch makes its episode an observed invalid
zero; an infrastructure/native-unverified batch makes the episode NULL. No
partial-map salvage, retry, reroll, or answer repair is allowed.

This is a public executable plan inspired by lambda-RLM, not an implementation
or reproduction of its learned planner. It makes no root-model or autonomous
planning claim and is not compute-matched to free-root runs.
