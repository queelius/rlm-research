---
id: leaf-trec-query-conditioned-interface-v1
status: prospective_exploratory_preparation
date: 2026-09-10
planned_calls: 192
---

# Query-conditioned child label-space comparison

Ask whether reducing a TREC child's output vocabulary to the two categories a
parent needs, plus `other`, improves task-relevant classification over asking
for all six categories. This is a child-only interface study; it has no root
execution or aggregate answer.

Select the first 128 official-test records under ascending
`SHA256([namespace, record_id])`, without labels or outcomes, and divide them
into eight fixed 16-record batches. Use six cyclic ordered category pairs, so
each category appears once as A and once as B. Every prompt in both interfaces
states the same pair and the same six TREC definitions. The full-six arm emits
canonical categories and is projected to A/B/other by the frozen host mapping;
the query-conditioned arm emits A/B/other directly. Projection is analysis,
not output repair.

Cross eight batches, six pairs, base/fixed-c32 models, and two interfaces for
192 calls. One fresh seed is shared by all four cells in each batch/pair block.
Rotate four-cell dispatch order across blocks. Preserve malformed completed
outputs as observed zero, missing or unauthenticated outputs as NULL, and make
no retries or outcome-dependent substitutions.

Primary metrics are per-record A/B/other correctness and exact 16-record batch
correctness. Report TP, FP and FN separately for A, B and other, native
availability, token use, physical requests, model effects, interface effects,
and their interaction. Eight batches and 48 paired blocks are correlated
exploratory units. The full official test and 489/500 records were already
research-exposed; this deterministic 128-record panel is not pristine.

A >=5 percentage-point task-relevant gain or a clear exact-batch gain without
an availability loss promotes a paired root-level interface test. Base-only
gain motivates interface-specific adaptation; a null or negative effect
deprioritizes this representation. These are practical pilot gates, not
equivalence, confirmatory evidence, or a novelty claim.

Use the qualified Qwen3-4B base/fixed-c32 dual-model service, temperature 0.5,
top-p 1, 2,048 output tokens, 8,192 context, four workers and 90 seconds per
request. Outer/work/owned caps are 1,800/1,650/1,770 seconds, including 180
seconds startup, 30 harvest reserve, 90 release, 30 finalization and 30 outer
margin. Preserve every native request, response, completion ID and cost field.
