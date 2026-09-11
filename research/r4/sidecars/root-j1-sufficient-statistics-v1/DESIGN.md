---
status: prospective_frozen
date: 2026-09-10
planned_calls: 40
---

# Direct public-J1 sufficient statistics

This study mirrors all 40 sealed ceiling chunks, record orders, seeds, and the frozen c32 child. It
changes the prompt, strict output schema, and model task: for each eligible `spec.users` user, report
a chunk-local target-A existence boolean and target-B integer weight sum. The deterministic host
bridge ORs A flags and adds B sums across every required chunk, then sums B only for eligible users
whose global A flag is true.

This is a bundle of task-aware prompting, a sufficient-statistics format, and LLM summation—not pure
output compression. Host labels and gold answers are scoring-only. Missing required chunks yield
episode NULL; authenticated malformed chunks yield observed-invalid. There is no partial salvage,
retry, reroll, or fallback. The exact 40 sealed label-map calls are shared historical controls and
are not reexecuted.

