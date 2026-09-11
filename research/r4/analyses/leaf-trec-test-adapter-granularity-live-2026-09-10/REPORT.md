---
title: Official TREC-test base versus c32 granularity audit
status: complete_independent_native_audit
date: 2026-09-10
study: leaf-trec-test-adapter-granularity-v1
planned_calls: 148
native_available: 148
---

# Official TREC-test base versus c32 audit

## Result

The fixed c32 adapter transfers strongly to the full 500-row official TREC test
source despite zero normalized-group overlap with its actual 5,065-group
optimizer corpus. All 148 calls were native-authenticated and contract-valid,
so there are no NULL bounds to resolve.

Across the two paired seeds:

| Width | Base | c32 | c32 − base |
| --- | ---: | ---: | ---: |
| W100 | 640/1,000 (64.0%) | 845/1,000 (84.5%) | +205 (+20.5 points) |
| S16 | 717/1,000 (71.7%) | 885/1,000 (88.5%) | +168 (+16.8 points) |

The gain has the same sign under both seeds: W100 gains were +100 and +105 of
500; S16 gains were +84 and +84. Joint-record transitions were respectively
115/15 and 118/13 wins/losses at W100, and 103/19 and 104/20 at S16. The adapter
effect is 3.7 points smaller at S16 than W100. Width changes batch context and
call count, so this descriptive interaction is not an equal-FLOP mechanism test.

The effect is not driven by the 11 official-test questions that also occur in
the raw training source. On the 489 previously research-evaluated groups, c32
gains +201/978 at W100 and +163/978 at S16. The 11 raw-source-overlap groups,
which were excluded from optimizer training and the earlier selected-test
evaluation, contribute only +4/22 and +5/22.

Class effects are heterogeneous. Combined c32-minus-base gains at W100/S16 are:
description-and-abstract-concept +25.4/+24.6 points, entity +26.6/+29.8,
location +32.1/+11.1, numeric-value +13.7/+8.4, human-being +1.5/+6.2, and
abbreviation 0.0/−5.6. The abbreviation stratum has only nine records per seed;
its negative S16 result is important counterevidence but imprecise.

## Provenance and native validity

The pre-outcome receipt independently traversed both prepared training passes,
recovering 5,065 unique optimizer group IDs and an empty intersection with all
500 official-test normalized groups. Every condition contains every source ID
exactly once per seed. Source lines were not deduplicated; all 500 happen to be
distinct under the frozen normalizer. The underlying cached TREC license status
remains unspecified, and no redistribution permission is inferred.

For every call the audit matched the frozen coordinate and request body,
base-versus-c32 model dispatch, raw model identity, unique provider request ID,
single choice, prompt/completion token counts, finite token log probabilities,
finish branch, renderer output, and exact 500-row reconstruction by condition.
All 148 outputs are exact complete maps. No partial map, reordering, repair, or
producer summary supplied the scores.

## Cost and scope

The physical union is 148 request, response, and result files, all HTTP 200.
Known usage totals 218,836 input tokens, 66,963 output tokens, and 165,760 cached
tokens; no usage fields are unknown. Owner time was 262.506 seconds and parent
time 263.140 seconds. Owner completion/release is clean, parent exit is zero
without timeout, and no GPU process remained. These are local physical costs,
not provider billing.

This is child-only six-class classification. It makes no claim about root
acquisition, aggregation, or end-to-end RLM performance. The 489-group majority
was already research-evaluated, two seeds share correlated source records, and
contextual batches—not individual labels—are the meaningful dependence units.
The result clears the prospective five-point transfer gate at both widths and
supports testing c32 downstream, while the class and width heterogeneity should
remain visible.
