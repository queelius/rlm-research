---
id: child-batch-granularity76
status: completed_exploratory
question: Do smaller child batches reduce the label errors behind two failed large-context answers?
evidence: AUDIT_MAIN.json
contexts: 2
seeds_per_context: 2
planned_calls: 76
claim_level: exposed_context_diagnostic
---

# Smaller batches helped modestly, but did not solve the task

Fresh16-record batches classified894/1024 labels correctly (87.30%), compared
with869/1024 (84.86%) for batches of100/100/56. The2.44-point improvement was
mostly in one of the two contexts: gains were1/512 and24/512 labels. This
does not support a broad claim that smaller batches reliably solve the
semantic problem.

| Context and seed | Wide: correct/256 | Small: correct/256 | Absolute aggregate error: wide → small |
| --- | ---: | ---: | ---: |
| Location-weight task, seed1 | 224 | 224 | 8 → 2 |
| Location-weight task, seed2 | 223 | 224 | 14 → 9 |
| Numeric-count task, seed1 | 208 | 222 | 7 → 2 |
| Numeric-count task, seed2 | 214 | 224 | 7 → 2 |

All four aggregate errors became smaller, but none became zero. Those
aggregates were calculated by our analysis code from returned labels; the
root model was not rerun. Smaller batches changed individual predictions in
both directions, including22 improvements and22 regressions in the first
block. Total label accuracy alone can conceal changes relevant to a requested
count or weighted total.

## Design and limits

Both conditions used fresh calls, the same512 records and order, category
definitions, IDs and fixed c32 child adapter (actual checkpoint0128). Two
paired seeds were used. The contexts were selected because earlier root
executions successfully accumulated256 labels but got their final answers
wrong due to child classification errors. They are exposed, purposively
chosen diagnostic cases—not a random or held-out benchmark.

The comparison changes input/output length, call count, cache behavior and
overhead together. It is a batch-size strategy comparison, not an isolated
attention mechanism or equal-compute experiment. Twelve wide calls versus64
small calls all produced native-authenticated complete maps. There were no
NULL labels, scorer disagreements or unplanned dispatches. Known usage was
119,316 input and32,252 output tokens, with88,720 cached input tokens and no
unknown usage fields. Owner time149.993seconds; parent time150.650seconds.

## Evidence and next decision

The author-assisted reader independently enumerated labels and host arithmetic
using the qualified native parser. MAIN read the full reader, ran five focused
tests, executed it on the actual outputs, and rechecked341 output pins without
change. The c32 adapter/config hashes matched the fixed binding. The actual
descriptor refers to the unused root adapter; child identity must instead be
checked using the role binding and each physical child request. Service-stop
receipts confirm all captured owned processes exited and ports were free.
Author overlap is disclosed; this is not an independent-author replication.

The next useful question is whether changing the child model or its semantic
training helps more than further batch fragmentation. The root accumulation
mechanism worked in the source cases; these results keep child semantics,
not just bookkeeping, on the critical path. Preserve the possibility that
some source labels or category boundaries are ambiguous.
