---
date: 2026-09-10
status: complete
scope: CPU-only native supplied-plan and child-transfer audit
---

# Mixed-child supplied-plan bridge result

The exact owner terminal and parent EXIT authenticate a complete, released run with exit 0, no
timeout, and no remaining GPU process. Native replay accounts for 40/40 new physical calls and the
40/40 unique reused c32 controls. Every response is available and valid, every provider request ID
is unique within its cohort, and no NULL is silently converted to zero.

The mixed child improves local label quality relative to c32. Across the eight nested episodes it
gets 1,148/1,280 true six-class labels correct versus 1,129/1,280 (+19), and 1,219/1,280 projected
A/B/other labels correct versus 1,199/1,280 (+20). These are deliberately separate metrics: the
projection does not substitute for actual six-class correctness.

The downstream J1 result is heterogeneous and does not pass the frozen promotion gate. Exact final
counts improve from 0/8 episodes to 1/8, short of the required +2. The sums of absolute error for
the four context clusters are `[49, 23, 11, 47]` for the mixed child and `[17, 29, 14, 57]` for c32,
so three of four clusters improve but total absolute error worsens from 117 to 130. Availability is
unchanged. The overall gate therefore fails.

All four mixed-training checkpoints are present at updates 6/12/18/24 with cursors 24/48/72/96 and
state hashes pinned in `AUDIT.json`. New usage is 71,426 input, 23,423 output, and 37,520 cached
tokens; reused controls account for 71,426 input, 24,629 output, and 37,520 cached tokens. No usage
cell is unknown.

This supports a narrow exploratory conclusion: mixed-interface continuation transfers to better
child labels under an unchanged supplied plan, but the resulting errors do not reliably compose
into better aggregate counts. Both cohorts are research-exposed, the eight episodes are nested in
only four context clusters, and the study makes no claim about root planning or outcome-pristine
generalization.
