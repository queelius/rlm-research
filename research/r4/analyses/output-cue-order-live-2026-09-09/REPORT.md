# Cue order: the identity benefit survives label-first decoding

Moving the source-ID tag after its label does not remove the meaningful-tag advantage. All 48 calls are observed, correctly bound and strictly valid in their assigned raw object order. The order-only interaction is small, with opposite signs across the two contexts in each task. This weakens the hypothesis that a same-record tag must appear immediately before the label for the benefit, without identifying the actual mechanism.

## Primary outcomes

Each entry is correct labels /256 (two exposed contexts × two fresh seeds ×64 records). Fixed historical child weights `c32de129…` are used throughout; this is not a new-weight or new-context replication.

| Task | Assigned order | Meaningful | Ordinal | Constant | Meaningful − ordinal |
|---|---|---:|---:|---:|---:|
| TREC | tag, label | 251 | 129 | 113 | +47.66 pp |
| TREC | label, tag | 240 | 122 | 111 | +46.09 pp |
| SST2 | tag, label | 241 | 162 | 165 | +30.86 pp |
| SST2 | label, tag | 241 | 157 | 149 | +32.81 pp |

The primary interaction `(M−O)tag-first − (M−O)label-first` is +1.56 pp TREC and −1.95 pp SST2. Context-level interactions are +4.69/−1.56 pp TREC and +0.78/−4.69 pp SST2, after averaging seeds within context. All four context/seed contrasts per task/order and all four interactions per task are complete and jointly valid. No task, order or seed is selected after scoring.

Tag-first minus label-first accuracy within meaningful/ordinal/constant arms is +4.30/+2.73/+0.78 pp TREC and 0/+1.95/+6.25 pp SST2. These are small, noisy exposed-cluster comparisons, not an equivalence test. All 48 first-item classifications are correct; later positions account for every error.

## Predeclared previous-record diagnostic

For meaningful label-first output, previous-gold agreement is only 70/252 TREC and 133/252 SST2, versus current-record correctness of 240/256 and 241/256. First-position previous agreement is undefined, retained as null. Much of previous agreement overlaps genuinely repeated adjacent labels: TREC has 62 repeated-gold opportunities per cell, SST2 136.

Marginal-adjusted previous-gold agreement (observed minus expected rate under fixed 63-position predicted/previous-gold multisets) is:

| Task | Arm | tag-first | label-first |
|---|---|---:|---:|
| TREC | Meaningful | +3.31 pp | +5.99 pp |
| TREC | Ordinal | +1.25 pp | +3.38 pp |
| TREC | Constant | +3.80 pp | +5.39 pp |
| SST2 | Meaningful | +0.55 pp | +1.78 pp |
| SST2 | Ordinal | −10.64 pp | −8.89 pp |
| SST2 | Constant | −6.44 pp | −10.64 pp |

This is not a simple universal one-record lag pattern. The fixed-marginal reference is descriptive, not a randomized causal null or permission to realign scores. Every call's marginals, previous/current overlap, first-item result and confusion matrices remain in the ledger; no offset search or repair was performed.

## Evidence and costs

The independent audit reconstructed all 48 coordinates, inherited source-coordinate joins, batches, seeds, dispatch order, and exact ordered request/schema bytes. It independently joined 128 TREC questions to official `TREC_10.label` lines and 128 SST2 sentences to the pinned validation Parquet (revision `8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb`), preserving all source group IDs, full texts, labels and disjoint q IDs. Selected normalized groups are unique. These are the lowest two original context indices per task from identity384, already exposed; public/pretraining exposure remains unknown and source/license qualifications remain inherited, not upgraded here.

All 24 assigned-order pairs have byte-identical messages/tools/sampling and identical full returned prompt-token arrays; only the ordered schema properties and required lists differ. All 48 actual physical prompts match frozen typed arrays and all response aliases match the authenticated c32de adapter/base binding. All starts follow the frozen dispatch plan. There are 48 captured generation POSTs and 48 provider responses; access logs additionally show one adapter-load POST and six models/version GETs. No unrun, HTTP failure, provenance quarantine, malformed array, wrong assigned order, truncation, or usage null occurs. Strict and aligned accuracies therefore coincide. Independent raw scores and previous-record expectations agree with stored projections.

Cost: 112,100 logical input tokens, 91,248 cached, 20,852 uncached, and 50,726 output tokens, reconciled to full token IDs. The overlapping call span is 150.41 s, reported collection 150.51 s, owned elapsed 198.89 s and outer operation 199.65 s (caps 600/900/930 s). Launch-to-collector is 45.84 s; final response-to-collector exit 0.45 s; owned release follows 1.03 s later. The 599.91 s sum of concurrent call durations is not GPU wall time. Terminal records show exit 0, no timeout, owned identities released and no GPU processes after exit; this auditor made no live GPU checks or lifecycle calls.

The next useful component test should probe a different dependency—for example, whether an explicit ID-indexed record selection/aggregation interface transfers this classification advantage into a root task—rather than assume that tag-before-label timing explains it. A small original-weight/new-context cue-order replication would test the scope of this result, but this screen alone does not establish whole-RLM improvement, attention dynamics, or generalization.

[METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") contains all rows, pairs, task-specific confusion/count errors and null-aware denominators. [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") records a single bounded source/raw authentication pass; historical outcome-bearing pins were excluded as predeclared. [METHOD.md](METHOD.md) is unchanged. Six independent fixtures passed before raw scoring. The raw audit used no scientific scorer imports, generated-code execution, GPU calls, source edits, queue edits or answer changes.

Schema note: `assigned_order_conformant` is the cue-specific order check. The unused `key_order_conformant` field inherited from the independent AG physical helper means literal tag-before-label, not conformance to the cue assignment; it is intentionally not used for cue validity or any reported contrast. `descriptive_raw_score` contains the independently reconstructed cue score. This annotation does not change either primary scoring rule.
