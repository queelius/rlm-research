# Symmetric yes/no did not rescue binary helper targeting

All 56 calls completed with valid raw outputs, no missing tasks, qualified batch-invariant runtime and clean release. Independent actual-token decoding reproduced the collector's metrics. On all eight TREC blocks, the fresh full-category control is substantially better than targeted yes/no:

| Primary metric | Fresh full map | Yes/no target maps |
|---|---:|---:|
| Exact counts / 48 related tasks | 31 | 20 |
| Sum absolute count error | 18 | 182 |
| Sum signed count error | 0 | +166 |
| Macro target-balanced accuracy | 93.64% | 79.06% |
| Physical calls | 8 | 48 |
| Input + output tokens | 12,260 | 75,811 |

Yes/no wins 3 paired exact-count tasks and loses 14; 17 are both exact and 14 both inexact. The fresh full map also labels 117/128 records correctly. Binary decisions are not forced into six-class predictions, so that classification score is not compared with a negative-dominated yes/no accuracy.

For one uniformly requested target, yes/no costs 1.0306× the full map (+3.06%); asking all six targets costs 6.1836× one reusable full map. The full map is never charged six times. All usage and cache counts were present. The 1.25× prospective token screen passes its budget component, but the overall screen fails on exact counts, absolute error and balanced accuracy. Owner time was 563.33 seconds, including about 66.00 seconds startup; this is one shared-service experiment, not independent cold-policy latency.

## Errors remained target dependent

| Target | Yes/no TP / FP / FN / TN | Predicted positive / true positive count | Exact counts: full → yes/no |
|---|---|---|---|
| Abbreviation | 7 / 6 / 0 / 115 | 13 / 7 | 6 → 6 |
| Description | 23 / 30 / 1 / 74 | 53 / 24 | 5 → 1 |
| Entity | 19 / 91 / 5 / 13 | 110 / 24 | 2 → 0 |
| Human | 24 / 36 / 1 / 67 | 60 / 25 | 6 → 3 |
| Location | 13 / 16 / 11 / 88 | 29 / 24 | 5 → 4 |
| Numeric | 24 / 5 / 0 / 99 | 29 / 24 | 7 → 6 |

Entity remains severely over-positive: five of eight entity maps answer yes for every record. Entity recall is 79.17%, specificity 12.50%, and balanced accuracy 45.83%; removing the literal category from the output did not restore discrimination. Description recall is high (95.83%), but 30 false positives drive 29 units of count overestimate. Human has one all-yes map; abbreviation has one all-no map. The exact per-category inventories and confusion counts are retained in REPORT.json.

## Secondary verbalizer comparison: seven old completed blocks only

This is explicitly cross-service/cache-history, not a clean within-service causal comparison. On the same 42 tasks, literal-target/other versus yes/no gives 20 versus 19 exact counts, 152 versus 141 summed absolute error, and 84.64% versus 80.75% macro balanced accuracy. There is no overall rescue, despite improvement in some large positive biases.

Entity positives decrease from 112/112 (21 TP, 91 FP) to 94/112 (16 TP, 78 FP); this trades some false positives for five false negatives and still yields no exact entity counts. Description positives decrease from 69 to 44 (old 21 TP/48 FP; new 20 TP/24 FP), with absolute error 48 → 23. These category-specific changes are compatible with wording/schema sensitivity, but do not prove the proposed output-vocabulary calibration mechanism.

The fresh full control shows zero exact-count drift (27/42 both), zero absolute-error drift (16 both), and the same target-balanced accuracy on these seven blocks. An additional direct comparison of the pinned raw CALL predictions found zero changed full-label predictions across all 112 shared records, with identical full request-body hashes. Different services/cache histories remain a limitation despite this stable control.

Decision: retain full-category outputs for this c32 helper and deprioritize simple binary target-output rewrites as deployable gains. Both literal/other and yes/no fail their matched controls. This does not establish that task targeting is intrinsically ineffective; a trained binary helper, changed instruction or other task family would be a different experiment.

## Audit evidence and scope

[REPORT.json](../../../../ARTIFACTS.md) SHA `09144b71897046bb535ab8bb42e04c92cd0aa419e1556f4d39228309286309e0` verifies 243 sealed pins, 280 raw artifacts, all 56 distinct native IDs, ordered keys/allowed labels/stop conditions, actual token counts, explicit yes→target/no→complement mapping, c32 binding, pre-exec flag receipt and actual EngineCore marker. Source RESULT SHA `b10ceb544b322d6fc7fd0c34790ba80953dfeba83f022f1e8b514a47cccf341f`.

One actual first-human-map fixture passed in 5.18 seconds, with two retained upstream SWIG warnings; focused Ruff checks passed. The auditor imports only SHA/JSON helpers and count arithmetic from the previous independent audit, not production collectors or metric code. [audit.py](../../../../ARTIFACTS.md) SHA `0f2e17e11f6cf0444558d6ee0fa385ad71b07249fe82ebf672d1a834da2a7931` and [test_raw_fixture.py](../../../../ARTIFACTS.md) are preserved.

These are 48 related binary/count tasks over 128 evaluation-exposed records, absent from verified local c32 SFT/new32 helper updates but with unknown base-pretraining exposure. They are not 48 independent contexts, evidence of RL improvement, a novel ensemble method, or a general recursion result. Earlier immutable reports and delivered-deck cutoffs remain unchanged.
