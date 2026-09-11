# Leaf batch shape: format repair does not repair long-output classification

2026-09-08. Exploratory, CPU-only, additive audit of completed fixed-operator runs. No requests were rerun and no frozen input/output was changed.

## Finding

Exact-cardinality enum grammar repairs a clear singleton output-contract failure. It does not rescue 64-item classification: both models produce valid arrays but zero correct count coordinates, with strong late-position label repetition. Five-item SFT improves small-batch semantics markedly, yet leaves this large-batch weakness. The original adapter also fails at 64, so these data do not establish that five-item SFT caused the fragility.

The strongest next question is whether varied-granularity training improves late-position semantic correspondence while retaining small-batch reliability. This is an established kind of distribution-shift/contract test, not a generic novelty claim about recursive reasoning.

## What is actually paired

All six conditions reuse the same 48 coordinates: six source-order documents of 64 distinct questions, two target counts (human being/numeric value), two seeds, and original versus validation-selected child weights. There are 384 unique question groups, not 1,536 independent examples per arm; each question is classified four times per condition/weight. The 24 count coordinates per arm are clustered within six documents. These are predeclared compositions of already component-tested TREC test questions, not an untouched new question source.

The audit verifies all 7,056 actual call artifacts (6,240 new extreme/schema calls plus 816 batch-5/16 references). Every coordinate, question, group ID, source order, host-only gold, body hash, sampling seed, and actual model alias matches its frozen specification. Epoch-2 selection and both served adapter roots reconcile with the binding. Disk adapters are original 857a7ce6… and selected c32de129…; actual serving was vLLM 0.28.0 with auto/BF16 casting, not FP32 inference.

Schema/free comparisons at sizes 1 and 64 have identical request bodies after removing the structured_outputs field, and identical provider-reported prompt token IDs in all 3,120 pairs. The sole requested treatment is an exact-length array of six canonical-label enum strings. The native leaf system, definitions, tools specification, temperature 0.5, seeds and other sampling settings remain unchanged. No tool calls occurred, and there were no retries or answer/parse fallbacks.

Batch 1/64 have a 1,024-output-token cap; batch 5/16 have 256. Thus cross-size comparisons are operational trade-offs, not a single-variable cap-controlled ablation.

## Endpoint decomposition

Each cell below is original / selected SFT. Correct assignments are exact canonical matches among structurally aligned outputs. Unaligned outputs remain unavailable, not semantically wrong by assumption. Whole-coordinate availability additionally requires every batch to satisfy the canonical enum contract.

| Condition | Exact count /24 | Available /24 | Canonical correct / aligned assignments |
|---|---:|---:|---:|
| Batch 1, free | 2 / 5 | 4 / 5 | 1,236/1,516 ; 1,460/1,507 |
| Batch 1, schema | 10 / 16 | 24 / 24 | 1,253/1,536 ; 1,488/1,536 |
| Batch 5, free | 1 / 15 | 8 / 24 | 1,192/1,536 ; 1,485/1,536 |
| Batch 16, free | 4 / 15 | 7 / 23 | 1,068/1,376 ; 1,466/1,520 |
| Batch 64, free | 0 / 0 | 0 / 0 | unavailable / unavailable |
| Batch 64, schema | 0 / 0 | 24 / 24 | 645/1,536 ; 698/1,536 |

A correct count need not imply correct classifications: target false positives and false negatives may cancel, as the separate [joint process audit](../leaf-role-composition-fixed-2026-09-08/REPORT.md) demonstrates. Conversely, one invalid batch makes the fixed aggregate unavailable even if other classifications are correct. Do not collapse these endpoints.

## Singleton mechanism: extra answers, not changed first labels

Selected SFT has 29 wrong-length singleton outputs: 23 arrays of length two and six of length three, involving 12 unique questions. With schema, all 1,536 first labels are unchanged across matched calls. The 1,507 previously aligned predictions are identical; 28 of the 29 newly admissible singletons are correct. Exact count improves 5 to 16, with availability 5 to 24. This is particularly clean evidence for contract repair, not improved semantic classification of the first label.

Several malformed responses concern questions mentioning multiple things (types of twins, two territories, or legislative houses); repeated labels can act like labels for answer entities instead of one label per input record. This interpretation is a hypothesis from outputs, not proof of internal reasoning. It should not become test-error-specific training selection.

Original singleton outputs contain 20 wrong-length arrays and 23 noncanonical strings, all “abstract concept”. Schema additionally changes 25 first labels: on the 1,516 previously aligned assignments, six improve and one worsens; 12 of 20 newly aligned labels are correct. No aliases are silently accepted in the primary endpoint.

## Batch 64: full inputs, valid outputs, poor correspondence

The actual provider prompt tokens decode to the complete frozen user message and all 64 distinct questions in source order in every one of the 96 free/schema calls. The input is only 1,321–1,361 tokens; input plus the 1,024-token allowance is safely below the recorded 8,192-token service limit. This rules out truncated or wrong question payloads in these runs, not every possible model/decoder issue.

Unconstrained outputs mostly do not stop at 64 labels: original has 23 length-truncated invalid JSON outputs and one stopped array of length 62; selected has 21 length-truncated outputs and stopped arrays of lengths 84, 86 and 111. Complete leading JSON-string counts range 62–331 original and 84–333 selected. Median longest repeated-label runs are 118.5 and 281. These malformed outputs have no primary position alignment. A separately flagged first-64-prefix diagnostic gives 641/1,534 and 706/1,536 matches; it assumes order and never repairs the primary score.

Grammar enforces 64 labels in all 48 calls, all with normal stop. Yet semantic accuracy falls sharply with record position:

| Positions in 64-item request | Original correct /384 | Selected correct /384 |
|---|---:|---:|
| 1–16 | 308 | 374 |
| 17–32 | 140 | 157 |
| 33–48 | 119 | 86 |
| 49–64 | 78 | 81 |

Selected reaches 97.4% in the first quarter but only 21.1% in the last; 366/384 last-quarter predictions are entity, versus 80/384 gold entity. Original instead emits description/abstract concept in 303/384 last-quarter slots, versus 92/384 gold. Median longest same-label runs remain 22.5 original and 28.5 selected, compared with maximum gold runs of only three or four within the six documents.

Selected batch-64 recall is 54/204 human, 85/252 location, 6/28 abbreviation, 275/320 entity, 163/428 description and 115/304 numeric. Its 948 entity predictions replace a much more diverse gold distribution (320 entity). Original predicts description 835 times against 428 gold. Full confusion matrices, 64-position counts and per-document results are in [SUMMARY.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SUMMARY.json").

The same late source records are mostly classified correctly in short batches: selected batch-5 quarter counts are 378, 374, 365 and 368 out of 384. Thus difficult late questions alone cannot explain the long-request loss. Source order is fixed, however; a separately frozen validation-only order permutation would help distinguish absolute output position from composition/history effects.

## Paired question-level changes

Compare only common structurally aligned assignments; alignment gains/losses are counted separately.

| Reference → treatment | Original improved / harmed | Selected improved / harmed |
|---|---:|---:|
| Batch 5 → singleton schema | 165 / 104 | 15 / 12 |
| Batch 5 → batch 16 free | 127 / 118 | 13 / 17 |
| Batch 5 → batch 64 schema | 129 / 676 | 29 / 816 |
| Batch 16 → batch 64 schema | 94 / 583 | 29 / 798 |

Batch 5 → 16 loses alignment for 160 original and 16 selected assignments. Against batch 5, selected batch-64 schema disagrees on 852 aligned predictions spanning 247 of 384 unique questions; original disagrees on 886 spanning 275. These are repeated descriptive counts, not independent Bernoulli observations or significance tests. [Paired disagreements](../../../../ARTIFACTS.md#unpublished-files "Not published: PAIRED_QUESTION_DISAGREEMENTS.json") retain per-question change counts and [prediction matrices](../../../../ARTIFACTS.md#unpublished-files "Not published: PREDICTION_MATRICES.json") retain every coordinate/position/label so clustered follow-up analyses remain possible.

## Cost and reliability window

Logical input includes cached tokens; completion counts are actual provider output tokens. Each row includes both weight arms, while input is equal per arm.

| Condition | Calls per arm | Input per arm | Output original / selected | Combined observed wall seconds |
|---|---:|---:|---:|---:|
| Batch 1, free | 1,536 | 1,169,248 | 8,159 / 8,089 | 124.0 |
| Batch 1, schema | 1,536 | 1,169,248 | 8,119 / 7,965 | 102.9 |
| Batch 5, free | 312 | 248,804 | 7,962 / 6,721 | 54.4 |
| Batch 16, free | 96 | 86,372 | 7,351 / 6,503 | 43.7 |
| Batch 64, free | 24 | 32,228 | 23,913 / 22,473 | 200.2 |
| Batch 64, schema | 24 | 32,228 | 8,781 / 5,467 | 64.4 |

Batch 16 reduces logical input 65.3% relative to five, with selected exact count unchanged at 15/24 but one unavailable coordinate and 16 unaligned assignments. Singleton schema costs 4.70 times batch-5 input for a one-coordinate descriptive count difference. Schema64 is cheap in input but fails both semantic and exact-count endpoints. Warm caching differs across sequential runs (full logical/cached/uncached totals are retained), so wall time and token savings are not controlled latency or dollar-cost estimates. These are direct leaf calls with a fixed host aggregator, not free-root RLM costs.

## What the next experiment can add

The inspected training data builder creates only five-question examples; both epochs use 1,013 five-item batches from 5,065 training question groups. Assistant targets are complete canonical JSON arrays. The actual 4,096-token training cap raises on overlength instead of truncating. The selected checkpoint therefore has real narrow-granularity exposure, but original batch64 already fails: evidence supports a remaining/inherited shape weakness, not a causal claim that SFT introduced it.

A minimal discriminating comparison is a short, record-exposure-matched continuation from the same selected checkpoint: five-only control versus predeclared mixed sizes 1/5/16/64, using training questions only. Match optimizer updates, record exposures, learning rate and sampling as far as possible; explicitly report differences in input and format-target tokens instead of claiming compute equivalence. Freeze validation-only batch-size/position panels and fresh paired seeds before training; score natural and schema outputs separately.

A provisional one-A100-40GB budget is 32 updates per arm with checkpoints at 16/32 and a 20-minute combined cap including a small fixed validation panel, subject to the no-truncation length gate. The previous 128-update run took 705.6 training seconds, but larger examples change throughput. Promote only if late-position semantic accuracy and whole-array reliability improve without material small-batch regression. Format-only gains would revise, not confirm, the semantic hypothesis. This is a proposed comparison, not a prepared or launched job; any separately approved curriculum has its own frozen recipe.

## Reproducibility and scope

[Read-only audit](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py") reconstructs requests and scores; [bundle.py](../../../../ARTIFACTS.md#unpublished-files "Not published: bundle.py") produces the four machine-readable views. [Output diagnostics](../../../../ARTIFACTS.md#unpublished-files "Not published: OUTPUT_DIAGNOSTICS.json") include all 64-item outputs plus small-batch contract failures, raw artifact paths/hashes, response length and repeated-label diagnostics. [Verification](../../../../ARTIFACTS.md#unpublished-files "Not published: VERIFICATION.json") records fresh recomputation, binding and parser checks. [Result seal](RESULT_SEAL.json) binds these additive files, exact inputs and sorted per-run output inventories; the previous joint report/seal remain unchanged.

No GPU clients, dataset acquisition, source-test-driven training selection, new curriculum implementation, or runtime changes were performed for this audit.

