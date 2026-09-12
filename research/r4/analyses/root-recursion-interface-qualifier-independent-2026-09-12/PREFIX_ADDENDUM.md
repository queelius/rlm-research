---
schema: research-audit-correction-v1
date: 2026-09-12
status: completed_cpu_audit
changes_scientific_outcomes: false
---

# The initial prompts were correct; the old prefix diagnostic was not

All 12 initial model-input prefixes exactly match the frozen prompts after
reconstructing the complete chain of preceding trace nodes. All 100 completed
model calls also match their recorded prompt and answer token counts. One
additional call failed without producing a sampled node; it remains a separately
recorded failure, not a missing zero-cost completion.

The original report's `initial_prefix_verified = 0` in each condition came from
comparing a single node's token fragment with an entire prompt. That diagnostic
was wrong. The original report is preserved; use this additive correction when
interpreting its prefix fields. The actual initial model inputs were not wrong.

The correction does not change any final answer, repeated-action failure, or
decision not to expand this run. In particular, the original table's zero
“Bad imports” counts refer only to one exact historical import pattern, not all
invalid imports. One correct final answer also came from an incorrect
calculation. See [the interpretation addendum](INTERPRETATION_ADDENDUM.md).

The CPU audit is [audit_prefix_addendum.py](audit_prefix_addendum.py). Its source
SHA256 is `a4a97e5f1cd026c05402f62acfa55936c966b74c194b497479cdf716f5d6ef2b`.
It uses the reviewed parent-chain extractor, authenticates the frozen source
closure, and records every episode hash in [PREFIX_ADDENDUM.json](PREFIX_ADDENDUM.json).
No model call or training update was made by this audit.
