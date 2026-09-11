# AG News: source-ID tags help both fixed weights

The meaningful-tag package improves displayed-record classification by **42.6–47.3 percentage points** over ordinal tags on these four AG News contexts. The effect occurs with both original and historical leaf-SFT weights and both q/p prefixes. All 96 responses satisfy the exact schema and tag constraints; this is a semantic difference, not a formatting-success difference. Historical SFT is not necessary for the benefit and is slightly worse on the meaningful-tag arm.

## Primary paired results

Each cell below is correct labels /512: four contexts × two seeds ×64 labels. There are only four context clusters. Strict and conditional aligned scores coincide because all calls are valid and authenticated.

| Weight | Source prefix | Meaningful | Ordinal | Constant | Meaningful − ordinal |
|---|---|---:|---:|---:|---:|
| Original | q | 420 | 180 | 176 | +46.88 pp |
| Original | p | 423 | 181 | 175 | +47.27 pp |
| Historical SFT | q | 404 | 184 | 189 | +42.97 pp |
| Historical SFT | p | 405 | 187 | 188 | +42.58 pp |

The eight task/seed pairs per weight/prefix are all observed and jointly valid. Averaging the two seeds within each context gives these meaningful-minus-ordinal differences:

| Context | Original q | Original p | SFT q | SFT p |
|---|---:|---:|---:|---:|
| 00 | +40.63 pp | +43.75 pp | +38.28 pp | +40.63 pp |
| 01 | +53.91 pp | +50.00 pp | +45.31 pp | +46.09 pp |
| 02 | +44.53 pp | +46.88 pp | +38.28 pp | +37.50 pp |
| 03 | +48.44 pp | +48.44 pp | +50.00 pp | +46.09 pp |

The old-minus-original interaction is −3.91 pp for q and −4.69 pp for p. Old weights change meaningful accuracy by −3.13/−3.52 pp, ordinal by +0.78/+1.17 pp, and constant by +2.54/+2.54 pp (q/p). Prefix swaps change each cell by at most 0.59 pp. Ordinal and constant scores are similarly low; neither constitutes an anonymous-output control. All eight seed/first-weight strata retain positive meaningful-minus-ordinal differences (+40.23 to +49.22 pp), but scheduling/cache interactions remain descriptive.

## Data, correspondence, and validity

The independent scorer reconstructed the pinned official AG test Parquet, all 7,600 normalized groups, the first 256 lexical group hashes, four disjoint 64-record contexts, deterministic display orders/IDs, and every exact serialized request. There were no duplicate or conflicting normalized groups. Source group support (World/Sports/Business/Sci-Tech) is 16/16/9/23, 14/21/12/17, 22/12/14/16, and 19/16/17/12. Selection used no label quotas, text cropping, or outcomes. Revision is `eb185aade064a813bc0b7f42de02595523103ca4`; underlying license remains UNKNOWN, and base-model pretraining/historical news exposure remains unknown.

Both actual disk adapters, descriptors, dual-alias binding and returned model aliases agree with the freeze: original `857a7ce6…`, historical SFT `c32de129…`, shared Qwen3-4B base manifest. All 96 captured physical bodies and full returned prompt-token arrays match the independent request reconstruction and frozen typed arrays. All 48 weight pairs have identical physical input IDs; all 32 tag triples retain identical visible records/system/tools. All 96 starts follow frozen dispatch order; first weight starts first in 48/48 pairs but finishes first in 39/48, with four concurrent calls.

There are 96 local attempts, 96 wire records, 96 HTTP/provider responses, 96 valid arrays, and no unrun, quarantined, malformed, length-stopped, or key-order-violating calls. Primary validity checks property sets; the separately recorded tag-then-label order also conforms throughout. No repair, numeric realignment, or rescued score was used. No call gets all 64 labels correct. The independent raw scorer agrees with every stored per-call score and derived strict/valid summary.

Class-count diagnostics do not replace correspondence accuracy. Mean per-call count-vector L1 is 9.50/9.75 original meaningful versus 42.25/45.25 ordinal and 45.50/48.00 constant; old meaningful is 15.75/15.50 versus 52.25/55.50 and 52.50/52.75. The full confusion matrices and signed vectors are retained. Across the deliberately heterogeneous conditions, sum of per-call count L1 is 3,556 versus pooled-vector L1 3,206: pooling hides some error. No call has a completely correct class-count vector.

## Cost and interpretation

All 96 usage records are present: 442,744 logical input tokens, 253,600 cached, 189,144 uncached, and 114,380 output tokens, reconciled to full native token IDs. The overlapping call span is 409.66 s; reported collection including projection is 409.93 s, owned elapsed 460.56 s, and outer operation 461.17 s, well within the 1,200/1,230 s caps. Launch-to-collector time is 47.22 s; last response-to-collector exit is 0.71 s and release follows 1.02 s later. Sum of concurrent call durations (1,617.75 s) is not GPU wall time or FLOPs. The service released all recorded owned identities and the parent reports no remaining GPU processes. These are recorded lifecycle facts, not an additional live GPU check by this auditor.

The service access log separately corroborates 96 successful generation POSTs and two successful adapter-load POSTs; models/version GETs are setup/preflight, not model calls. The log reports vLLM force-killing one remaining EngineCore during shutdown before the verified owned release. Neither item changes episode outcomes. Exact route totals are in [SERVER_ACCOUNTING.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SERVER_ACCOUNTING.json").

This strengthens the case for the source-ID instruction-plus-grammar package as a useful leaf-classification component on a third task and original weights. It does not isolate attention, copying, or decoding mechanisms; establish a randomized SFT effect; or show whole-RLM count improvement. A smallest next component comparison should hold the output labels/tags and grammar fixed while varying a single input/output correspondence cue, with these weights frozen and paired context-level scoring. The queued cue-order study is more informative for that distinction than another broad weight sweep.

Evidence: [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") contains the complete 96-row independent ledger, per-context/seed contrasts, confusion/count errors, physical checks and costs; [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") authenticates inputs once per terminal pass. [METHOD.md](METHOD.md) was frozen before outcomes; [AUDITOR_HANDOFF.md](AUDITOR_HANDOFF.md) discloses that this auditor authored acquisition/design and source review, not the scientific implementation/scorer. Thirteen focused fixtures passed before raw scoring; the bounded terminal pass took 2.06 s. No source, output, admission, GPU, process, or queue mutation was performed.
