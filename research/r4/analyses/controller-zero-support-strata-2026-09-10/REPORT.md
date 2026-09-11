---
title: Controller zero-support strata audit
date: 2026-09-10
status: sealed additive analysis
metric: frozen study-specific correct-and-performed headline
---

# Result

The QS6 advantage persists after removing zero-gold items in all three independent comparisons. These are descriptive planned-denominator and complete-pair counts; NULL endpoints remain NULL. Every primitive/composed planned-denominator cell is positive, although the original nonzero-primitive complete-pair net is zero, so that narrow cell is not independent paired evidence of a gain.

| Study | Stratum | unchanged | QS6 | Gain | Complete pairs (W-L; net) | NULL pairs |
|---|---:|---:|---:|---:|---:|---:|
| original | all | 15/72 (8 NULL) | 52/72 (1 NULL) | +37 (51.4 pp) | 63 (31-0; +31) | 9 |
| original | zero | 5/26 (1 NULL) | 20/26 (1 NULL) | +15 (57.7 pp) | 24 (14-0; +14) | 2 |
| original | nonzero | 10/46 (7 NULL) | 32/46 (0 NULL) | +22 (47.8 pp) | 39 (17-0; +17) | 7 |
| fresh_seed | all | 15/72 (10 NULL) | 49/72 (2 NULL) | +34 (47.2 pp) | 60 (26-1; +25) | 12 |
| fresh_seed | zero | 6/26 (3 NULL) | 22/26 (1 NULL) | +16 (61.5 pp) | 22 (13-0; +13) | 4 |
| fresh_seed | nonzero | 9/46 (7 NULL) | 27/46 (1 NULL) | +18 (39.1 pp) | 38 (13-1; +12) | 8 |
| metadata | all | 12/72 (17 NULL) | 50/72 (0 NULL) | +38 (52.8 pp) | 55 (28-0; +28) | 17 |
| metadata | zero | 5/28 (7 NULL) | 25/28 (0 NULL) | +20 (71.4 pp) | 21 (14-0; +14) | 7 |
| metadata | nonzero | 7/44 (10 NULL) | 25/44 (0 NULL) | +18 (40.9 pp) | 34 (14-0; +14) | 10 |

## Primitive and composed strata

Overall task-kind split:

| Study | Task | unchanged | QS6 | Gain | Complete-pair net |
|---|---|---:|---:|---:|---:|
| original | primitive | 14/24 | 19/24 | +5 | +1 (19 complete) |
| original | composed | 1/48 | 33/48 | +32 | +30 (44 complete) |
| fresh_seed | primitive | 12/24 | 18/24 | +6 | +5 (23 complete) |
| fresh_seed | composed | 3/48 | 31/48 | +28 | +20 (37 complete) |
| metadata | primitive | 12/24 | 18/24 | +6 | +5 (23 complete) |
| metadata | composed | 0/48 | 32/48 | +32 | +23 (32 complete) |

### original

| Gold | Task | unchanged | QS6 | Gain | Complete-pair net |
|---|---|---:|---:|---:|---:|
| zero | primitive | 5/7 | 7/7 | +2 | +1 (6 complete) |
| zero | composed | 0/19 | 13/19 | +13 | +13 (18 complete) |
| nonzero | primitive | 9/17 | 12/17 | +3 | +0 (13 complete) |
| nonzero | composed | 1/29 | 20/29 | +19 | +17 (26 complete) |

### fresh_seed

| Gold | Task | unchanged | QS6 | Gain | Complete-pair net |
|---|---|---:|---:|---:|---:|
| zero | primitive | 5/7 | 7/7 | +2 | +2 (7 complete) |
| zero | composed | 1/19 | 15/19 | +14 | +11 (15 complete) |
| nonzero | primitive | 7/17 | 11/17 | +4 | +3 (16 complete) |
| nonzero | composed | 2/29 | 16/29 | +14 | +9 (22 complete) |

### metadata

| Gold | Task | unchanged | QS6 | Gain | Complete-pair net |
|---|---|---:|---:|---:|---:|
| zero | primitive | 5/7 | 7/7 | +2 | +2 (7 complete) |
| zero | composed | 0/21 | 18/21 | +18 | +12 (14 complete) |
| nonzero | primitive | 7/17 | 11/17 | +4 | +3 (16 complete) |
| nonzero | composed | 0/27 | 14/27 | +14 | +11 (18 complete) |

## Interpretation and limitations

Nonzero-gold gains cannot be explained by a tendency to emit zero: the planned-denominator gains are positive in every study. The primitive/composed split is also reported without pooling evidence across studies. Zero support is not randomized and is correlated with task family, so differences between zero and nonzero strata are descriptive, not causal.

A NULL is never converted to failure for the paired calculation: planned-denominator success counts show observed successes over all planned cells, while the W-L net uses only pairs whose two endpoints were available. This is why those two summaries need not have the same numerical difference.

The fresh-seed headline uses its frozen grounded rule: `faithful_and_strict` rows count except the row classified `faithful_strict_unsupported`. No semantic row was reannotated.

## Already-recorded empty-support caveats

The source annotations contain 13 zero-gold rows explicitly marked as coincidental, unsupported, or protected from an error by an empty set. They are listed verbatim in the JSON artifact and are not rubric revisions. In particular, these cautions reinforce using the nonzero stratum as the generalization check.

## Reproduction and provenance

Run `python reproduce.py --out /tmp/controller-zero-support-replay`. The script reconstructs the original 144-cell protected inventory from its native plan and host-gold file, joins its 135 frozen semantic rows, and leaves the other nine as NULL. Fresh and metadata already contain all 144 planned rows.

Source SHA-256 pins:

- `original_semantics`: `43b368dce2b22c5ad9fd19b93ef5d62cc61bfb1fbd6a2472dd8c4fe03cfb550e`
- `original_plan`: `54e8d1baddf51994d841360c1b425efb9e3d590e969ab9f00d063dab70399bc4`
- `original_gold`: `7961622d0247332be4c48c06a4dffb8b839dfa205b390ac5e9d773cac4652a9b`
- `fresh_semantics`: `0676e3f32605897d214da78b1359df8f29a3bf7b61de3e26f2507434223b560f`
- `metadata_semantics`: `7fd6dedf1895527e937a503a789fe713716c92333f9d8efad382bb4c5c3e17ab`
