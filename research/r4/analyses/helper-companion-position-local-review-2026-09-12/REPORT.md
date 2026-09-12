# Independent companion/order audit

All 64 raw native responses pass independent decoding, schema/ID/token checks and host-gold rescoring. All 1,024 prediction slots are valid; there are 256 unique records reused across four arms. Runtime evidence and clean release pass. No GPU was launched for this audit.

| Dataset | Original | Reversed | Neighbor A | Neighbor B |
|---|---:|---:|---:|---:|
| trec | 117/128 | 118/128 | 118/128 | 113/128 |
| ag_news | 115/128 | 111/128 | 113/128 | 109/128 |

Neighbor changes matter even when numbered record slot is held fixed. TREC changes are not consistently beneficial: neighbor A is +1 correct but neighbor B is −4. Both news neighbor arms are worse (−2 and −6). Reversal is also dataset-opposite (+1 TREC, −4 news). This establishes presentation sensitivity on these records, not an attention cause or a robust improvement strategy.

| Dataset / comparison | Wins | Losses | Label changes |
|---|---:|---:|---:|
| trec:original_vs_reverse | 5 | 4 | 9 |
| trec:original_vs_neighbor_A | 5 | 4 | 9 |
| trec:original_vs_neighbor_B | 4 | 8 | 13 |
| trec:neighbor_A_vs_neighbor_B | 4 | 9 | 14 |
| ag_news:original_vs_reverse | 5 | 9 | 16 |
| ag_news:original_vs_neighbor_A | 3 | 5 | 10 |
| ag_news:original_vs_neighbor_B | 3 | 9 | 13 |
| ag_news:neighbor_A_vs_neighbor_B | 6 | 10 | 17 |

Wins/losses use host-gold correctness; label changes also include wrong-to-different-wrong transitions. Each row has 128 paired records, with no missing outcomes. Neighbor A and B are two fixed rearrangements, not independent datasets.

## Class-level findings

- trec, entity: 21 / 20 / 21 / 22 correct out of 24 (original/reversed/A/B).
- trec, numeric value: 24 / 22 / 23 / 22 correct out of 24 (original/reversed/A/B).
- trec, human being: 23 / 25 / 25 / 23 correct out of 25 (original/reversed/A/B).
- trec, description and abstract concept: 22 / 23 / 24 / 22 correct out of 24 (original/reversed/A/B).
- trec, location: 22 / 23 / 20 / 21 correct out of 24 (original/reversed/A/B).
- trec, abbreviation: 5 / 5 / 5 / 3 correct out of 7 (original/reversed/A/B).
- ag_news, Business: 32 / 28 / 30 / 32 correct out of 32 (original/reversed/A/B).
- ag_news, Sci/Tech: 23 / 23 / 23 / 20 correct out of 32 (original/reversed/A/B).
- ag_news, World: 28 / 29 / 28 / 27 correct out of 32 (original/reversed/A/B).
- ag_news, Sports: 32 / 31 / 32 / 30 correct out of 32 (original/reversed/A/B).

These class contrasts are descriptive post-run observations; no classes were used to choose permutations. REPORT.json contains complete confusion matrices.

## Factual examples

- `t58283904433d2e3` (trec): “What is the longest suspension bridge in the U.S. ?” Gold: location. Predictions original/reversed/A/B: location / location / entity / entity.
- `t6459d0fa2e5711e` (trec): “Who invented the telephone ?” Gold: human being. Predictions original/reversed/A/B: description and abstract concept / human being / human being / human being.
- `a05885b5e67f6bd4` (ag_news): “Study: Apple, Dell lead PC customer satisfaction index The PC industry is doing a better job this year of satisfying its U.S. customers, and better technical support and easier-to-” Gold: Sci/Tech. Predictions original/reversed/A/B: Sci/Tech / Sci/Tech / Business / Business.

Examples follow fixed descriptive rules (first ID with original-correct/both-neighbors-wrong, or the converse); they are illustrations, not independent evidence.

## Cost and scope

Actual total: 98984 input + 18241 output = 117225 tokens across 64 calls; 47680 cached input tokens reported. No unknown usage. Each arm has equal input totals within dataset (TREC 9,930; news 14,816); output costs differ only slightly. Owner time 653.49s includes startup 66.58s and cleanup. Request timing reflects one shared warmed service, not cold-start latency.

Neighbor regroupings preserve slot 0–15, but change companion identity, preceding text and absolute token offsets. Reversal retains companions but changes order and positions. No attention-causality, training, root-recursion or adaptive-policy claim follows. The panel is research-exposed and absent from verified c32 SFT/new32 updates, not necessarily base pretraining.

Source READY `4d827a12f134aa0fd5afd8ce5c9fabc1f46ddcf2bfec3a1f19cc7e96713b641b`; source RESULT `3747f55b59ee93ae0b87535ff71b163ec362e1e6b29a46ebc86219adbb06621b`. Independent source, per-call hashes, runtime evidence and full paired/class metrics are in REPORT.json. CPU_TESTS.json records the one actual raw-fixture check.
