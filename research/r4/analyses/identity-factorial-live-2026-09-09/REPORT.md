# Identity384: meaningful tags survive disjoint IDs and prefix swaps

Independent terminal audit, 2026-09-09. The primary result survives the intended control: meaningful source tags outperform ordinal position tags even when their numeric namespaces cannot overlap. Removing overlap improves the ordinal arm, but does not explain away the meaningful-tag advantage. This is a behavior-only constrained-output component result, not an attention-mechanism or whole-RLM result.

## Primary results and all cells

Every cell has **16/16 completed, observed, valid calls and 1024 aligned labels**, from four exposed contexts × two permutations × two seeds. Counts below are correct labels out of 1024, scored only against the displayed record. M = meaningful source tag; O = ordinal position tag; C = constant tag. No primary output was remapped or repaired.

| Dataset | Source prefix | Numeric namespace | M | O | C | M−O |
|---|---|---|---:|---:|---:|---:|
| TREC | q | overlap | 981 | 293 | 394 | +688 |
| TREC | q | **disjoint** | **986** | **504** | 456 | **+482** |
| TREC | p | overlap | 978 | 218 | 378 | +760 |
| TREC | p | **disjoint** | **983** | **436** | 413 | **+547** |
| SST2 | q | overlap | 964 | 509 | 600 | +455 |
| SST2 | q | **disjoint** | **963** | **603** | 605 | **+360** |
| SST2 | p | overlap | 964 | 503 | 601 | +461 |
| SST2 | p | **disjoint** | **962** | **600** | 614 | **+362** |

Primary disjoint gains are +47.07/+53.42 percentage points on TREC (q/p) and +35.16/+35.35 on SST2. Each of the 16 task-matched call differences is positive in each primary contrast. These are nested repeats, not 64 independent experiments.

| Disjoint comparison | Paired item gains/losses | Four context gains, each out of 256 |
|---|---:|---|
| TREC q | 490 / 8 | 123, 124, 117, 118 |
| TREC p | 554 / 7 | 134, 138, 145, 130 |
| SST2 q | 386 / 26 | 111, 65, 78, 106 |
| SST2 p | 390 / 28 | 106, 71, 78, 107 |

Both presentation permutations and both sampling seeds have positive aggregate differences in all four primary comparisons; their separate totals and per-call rows are retained in SUMMARY/METRICS. There are only four source-context units per dataset, so no item-level significance or broad-generalization claim is made.

## What the overlap and prefix controls change

Moving overlap→disjoint changes correct counts by:

- TREC q: M +5, O +211, C +62; the M−O gap shrinks by 206/1024 (20.12 points).
- TREC p: M +5, O +218, C +35; the gap shrinks by 213/1024 (20.80 points).
- SST2 q: M −1, O +94, C +5; the gap shrinks by 95/1024 (9.28 points).
- SST2 p: M −2, O +97, C +13; the gap shrinks by 99/1024 (9.67 points).

Every context shows that shrinkage, while every context retains a positive disjoint M−O gap. Numeric overlap is therefore a real vulnerability of this ordinal control, not a complete account of the component effect.

Prefix sensitivity remains visible. Switching source prefix q→p changes TREC ordinal accuracy by −75/1024 in overlap and −68/1024 in disjoint; the corresponding meaningful change is −3 in both. Disjoint TREC ordinal predictions disagree on 364/1024 paired items across prefixes, versus 11 for meaningful tags. SST2 prefix effects on totals are smaller: ordinal −6/−3 and meaningful 0/−1 (overlap/disjoint), though disjoint ordinal still changes 81 item predictions versus one for meaningful tags. Constant tags also vary: TREC −16/−43; SST2 +1/+9. Thus “q and p have the same standalone token length” does not imply behavioral invariance.

The prespecified **overlap-only** numeric-source diagnostic scores ordinal outputs against the source bearing each output numeral: TREC q861/p966 and SST2 q941/p947 out of 1024, versus their much lower displayed-position primary scores above. This supports source-numeral confusion, but six/two repeated semantic classes are not unique identities; it does not prove an exact internal retrieval mechanism. The diagnostic is unavailable/null for disjoint IDs, not zero or a latent-rank repair. SUMMARY contains explicit nulls; METRICS' `known_sum=0, missing=16` is only an empty accumulator, never a measured zero diagnostic score.

For scale, a random permutation of each context's own gold-label multiset has expected 220.125/1024 correct TREC labels and 519.75/1024 SST2 labels. A gold-informed per-context majority constant yields 296 and 560 respectively. These are descriptive class-frequency baselines, not extra model runs.

## Format, full-document and count endpoints

All 384 responses stop normally; none is truncated, invalid, tool-calling, unrun, censored, or an infrastructure failure. All 24,576 raw objects use lexical `tag,label` order. Independent duplicate-key/canonical-label/cardinality parsing agrees with every stored call score and every stored cell total. Reversed key order was explicitly tested and would be recorded separately without moving labels between records.

Whole-64 correctness remains demanding: TREC meaningful achieves 2,3,2,2 perfect arrays for q-overlap/q-disjoint/p-overlap/p-disjoint; all other TREC arrays and every SST2 array are imperfect. The improvement is not universal exact document classification.

Aggregate counts can conceal correspondence errors. TREC ordinal's mean class-count-vector L1 is 10.00/4.75 in overlap (q/p), versus 40.875/45.125 in disjoint, despite better disjoint position accuracy. SST2 ordinal similarly changes from 5.125/4.375 to 28.375/29.00. Two p-overlap SST2 ordinal arrays have an exactly correct class-count vector despite incorrect item labels; q-disjoint has one. Across SST2 meaningful cells, 18 arrays have exact class counts despite at least one wrong label. These are separate count diagnostics, not repaired semantic scores or evidence of invalid success on a task that asks only a count.

## Source and physical-request audit

The frozen design is 8 contexts × 2 permutations × 2 seeds × 2 source prefixes × 2 numeric namespaces × 3 tag rules = 384. The exact 256 TREC questions and 256 SST2 sentences were checked against cached official source text/labels, their dataset-specific normalized group IDs, original source ranks, presentation permutations and frozen disjoint assignments. Across this selected set each dataset has 256 unique question groups; repeated coordinates do not add source examples. TREC uses NFKC/casefold/word-token grouping; SST2 uses NFKC/casefold/whitespace grouping.

The current eight contexts were already developmentally exposed through the earlier grammar/padding/identity studies. Upstream provenance's “fresh SST” wording refers to its earlier acquisition relative to two older SST batches, not to this experiment. SST2 is public `stanfordnlp/sst2` validation revision `8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb`; the underlying dataset license remains unknown in the cached card. TREC `TREC_10.label` is an unversioned external file pinned by SHA `033f22c028c2bbba9ca682f68ffe204dc1aa6e1cf35dd6207f2d4ca67f0d0e8e`, not assigned an invented revision. Inherited six-context/384-group provenance describes the parent pool; this audit uses four/256. No new-source or base-pretraining-independence claim follows.

All 118 accepted/scientific closure paths authenticated, along with terminal service/operation records. Independently checked all 384 frozen request digests, exact serialized wire bodies, fixed c32de alias and `/models` adapter/base mapping, sampling seeds 1127389105/1656446467, T0.5/full support, max3072, exact tag/enum/cardinality grammar, model-visible ID→question maps, and equal input/system/tools within each three-arm group. Host gold is absent from those record payloads. All actual full prompt-token arrays equal frozen typed-vLLM/HF prompt IDs; all output IDs decode to recorded content and agree with completion usage. This is standalone Chat Completions with the qualified native HF template and typed tool serialization, not a new TrainClient/RLM rollout. Tools are present but none was invoked or executed; logprobs were not requested, so no probability claims are made. Service binding is authenticated; GPU tensor contents were not independently introspected by this CPU audit.

## Actual cost and release

Recorded usage has no missing values: **883,552 logical input tokens**, **582,048 cached**, **301,504 uncached**, and **405,141 completion tokens**. All-call summed seconds are 4921.04, overlapping across four workers; this is not elapsed GPU occupancy. Per-call durations are 12.21–13.68 seconds. Per-cell usage is preserved in METRICS; tag-length equality was not substituted for measured compute.

The owned wrapper ran 1284.20 seconds (21m24s), below its 2400-second cap; actual first→last call interval was 1231.98 seconds. Launch→server-start took 4.59 seconds, service startup 42.13 seconds, ready→first call 2.90 seconds. Last call→collector exit was 1.57 seconds, then release took 1.02 seconds. All seven observed owned parent/descendant identities exited and ports were free; parent recorded empty GPU processes, child exit0 and no timeout. The service released at 07:44:54.555 UTC. There was no substantial post-rollout CPU tail under this ownership. This independent audit acquired no GPU lifecycle lock and did not delay the automatic BROAD continuation.

## Decision, limits and reproducibility

Retain the meaningful-ID component effect; retire the claim that shared ordinal numerals explain its entirety. Preserve prefix sensitivity and poorer whole-array success. The smallest useful next decision is whether a fixed root actually consumes such keyed child evidence correctly in an uptake-aware RLM comparison, or whether this component advantage survives a small fresh-source/fixed-weight replication. Another automatic SFT or mechanism sweep is not licensed by these results. No new experiment, source change or queue mutation was performed here.

METHOD SHA `d3df1afeb85f54fda551fbfee91214eb4376cf6c9e98c44841370eb42fb02737` was frozen before analyst outcome inspection, but after inference had begun; the scientific inputs preceded inference. The successful single-scoring pass completed 93,844 checks in 3.79 CPU seconds, with zero stored-score disagreements. One earlier preflight stopped before scoring on the first TREC group because the analyst initially used SST-style normalization; the inspected TREC rule and a red/green fixture corrected that audit assumption. Closures were consequently read in that aborted preflight and again in the successful pass, never inside per-episode loops. Five focused parsing/missingness/grouping tests pass; no broad tests or model reruns were performed.

Artifacts: `METRICS.json` SHA `c4d146246c2891c108d1ed2831df03316288f9f07b85487a59f36f3a92b1b217`; `SUMMARY.json` SHA `b015b0630781f56de01ff582447cf17bbfdb9ec9eb2944862dc577e1e3cf7d43`; `SOURCES.json` SHA `02fdf3aac5e3fa390f2a2e600c6307bbbe4eac64c20b7e50fe697003af0d635f` contains 911 source/input/output hashes. The executed analysis source and snapshot-only derivation are included. Scientific READY SHA `ff741613acaa31108dd3873879c24a581006495faafda91216096a35fdf711d5`; SPEC SHA `150e2510a804042dc499fc1b9d8a195473d9f697c784a2bb929a803e96417792`; parent acceptance SHA `04dd7158c115aaf55fc2bd281d2ee4d5da877520eb655906a66ccd2cdafbb5a9`.
