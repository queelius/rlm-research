# Matching source IDs help on fresh research records in both released checkpoints

**Terminal independent raw audit.** Matching-ID objects strongly outperform constant-tag objects for both AG News and SST-2 in both released checkpoints, without research adapters. All32 paired context-seed comparisons and all16 two-seed context means favor matching. **All96 responses are valid and observable**, with no infrastructure NULLs, truncations, key-order violations or whole64-perfect arrays. The effect is therefore not explained by rescuing otherwise invalid outputs.

| Released checkpoint | Dataset | Plain array | Matching IDs | Constant tag | Primary matching−constant |
|---|---|---:|---:|---:|---:|
|Qwen3-4B-Instruct-2507|AG News|191/512|417/512|172/512|+245 (+47.85pp)|
|Qwen3-4B-Instruct-2507|SST-2|304/512|468/512|301/512|+167 (+32.62pp)|
|Qwen3.5-4B|AG News|199/512|425/512|211/512|+214 (+41.80pp)|
|Qwen3.5-4B|SST-2|305/512|471/512|275/512|+196 (+38.28pp)|

Each cell contains eight calls: four64-record context clusters×two seeds. The512 denominator is record presentations, not512 unique source records; each task contains256 unique groups. Models share the same source groups. No cross-task or cross-model pooled accuracy is a primary endpoint.

## What this replication supports—and does not

The source-matching output cue remains useful outside the previously exposed contexts and the research-trained c32de helper. A merely longer object-shaped output is insufficient here: constant-tag objects have the same general representation and comparable output lengths yet perform far worse. This narrows—but does not uniquely identify—the mechanism. Tags are forced by exact grammars, not freely retrieved/generated IDs. Representation instructions and schemas differ across arms. Do not call this an attention measurement, a pure equal-compute intervention, evidence of unconstrained ID retrieval, or an end-to-end RLM benefit.

Matching accuracy is81.45%/91.41% for Qwen3 AG/SST and83.01%/91.99% for Qwen3.5. The latter advantages are only8 and3 labels/512 on shared contexts; no model superiority conclusion follows. Both are released instruction/post-trained checkpoints, not untrained pretrained bases. No research LoRA was loaded.

## Context and position consistency

Primary two-seed mean improvements, in correct labels per64:

| Checkpoint/task | Four context-cluster means |
|---|---|
|Qwen3 AG|26.5,33.5,34,28.5|
|Qwen3 SST|16.5,24.5,20,22.5|
|Qwen3.5 AG|28,25,30,24|
|Qwen3.5 SST|18,27,25.5,27.5|

The secondary matching-minus-plain contrast is also positive in every context. Position summaries show that the effect is not restricted to early labels. For positions49–64 (128 presentations/cell), matching versus constant is114 versus36 for Qwen3 AG,114 versus59 for Qwen3 SST,107 versus42 for Qwen3.5 AG and114 versus55 for Qwen3.5 SST. Complete quartiles, individual positions, canonical-label confusions and per-call histogram L1 remain in [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") and [POSITION_LEDGER.json](../../../../ARTIFACTS.md#unpublished-files "Not published: POSITION_LEDGER.json"). These diagnostics do not realign or repair the primary score.

No returned array is wholly correct64/64. Even matching IDs therefore do not make reliable complete batch classification automatic, particularly on AG News.

## What “fresh” means

The independent input audit reconstructed normalized NFKC+casefold+collapsed-whitespace SHA256 groups from pinned official cached parquet, then reproduced the label-independent hash ordering and earliest-index representatives. Selection excluded exact groups present in the frozen **25 named historical input/reservation catalogs**, not all upstream raw membership. The resulting512 source groups are unique and disjoint from those named exact exclusions.

| Source pool | Normalized groups | Conflicting groups removed | Historical exact groups removed | Eligible | Selected |
|---|---:|---:|---:|---:|---:|
|AG News public test|7,600|0|256|7,344|256|
|SST-2 public train text units|66,978|5|0|66,973|256|

SST uses public training text units, not the previously exhausted validation-sentence pool: **43/256 selected units have only one or two words**. They are retained, with unchanged labels and no performance-based filtering. Parent/subphrase overlap, AG event/near duplication, overlap outside the bounded catalogs, and pretraining/post-training exposure remain unknown. Thus “new to this bounded research-input crosswalk” is supported; “globally unused,” “unseen in pretraining,” or clean full-sentence task transfer is not.

Exact sources:

- SST-2 `stanfordnlp/sst2`, revision `8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb`, public train; parquet SHA `c7921283b75a42e685f50edecb96798607ea0fcbfd0739ee8975f22c12d55f09`. [Acquisition manifest](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/datasets/sst2-train-feasibility-20260909/ACQUISITION.json"), retrieved2026-09-09 14:49:17UTC.
- AG News `fancyzhx/ag_news`, revision `eb185aade064a813bc0b7f42de02595523103ca4`, public test; parquet SHA `71de87ec66bc5737752a2502204dfa6d7fe9856ade3ea444dc6317789a4f13fb`. [Acquisition manifest](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/datasets/fancyzhx--ag_news--eb185aade064a813bc0b7f42de02595523103ca4/ACQUISITION.json"), all downloads complete by2026-09-09 08:22:58UTC.

Underlying dataset licenses remain unconfirmed. The AG card's research/noncommercial language is not a permissive data license; an Apache loader/software license is not a dataset license. No downloaded code was executed for this audit.

## Actual request and checkpoint identity

All96 planned coordinates map one-to-one to raw call files, ordered wire bodies and48 HTTP200 access-log entries per model. No extra calls, missing coordinates, source/count discrepancies or disagreement with the subsequently checked implementer scores occurred. Every returned physical prompt-token sequence equals its frozen model-native reference; input and output ID lengths reconcile exactly with raw usage. Current IDs, full64 cardinality, exact label enums and duplicate-key rejection were independently checked. Primary object scoring uses the declared key set; all outputs additionally satisfy tag-before-label order.

Source texts/order are fixed within each representation comparison. Across representations, instructions/schema legitimately differ; across models, physical templates/tokenizers differ. Do not claim identical token prefixes across models or all arms. Actual prompt lengths span1,930–4,843; max input+3,072 reserve is7,915≤8,192. No input crop, tool-call output or observed reasoning text occurred. Every finish reason is`stop`.

Both actual vLLM0.28 services used BF16, eager mode,8192 context, four sequences, no LoRA, no prefix cache, and explicit nonthinking requests with temperature0.5/full-support sampling. Qwen3.5 additionally used language_model_only, GDN cache alignment and its model-specific parser; Qwen3 used its native template/parser. Weight identities are Qwen3 revision `cdbee75f17c01a7cc42f958dc650907174af0554` and Qwen3.5 revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`; both pinned model LICENSE files are Apache2.0. Prior full-shard manifests were authenticated through unchanged size/mtime/inode for five shard files, **not a new full-byte tensor rescan**. Actual endpoint/model/config/launcher bindings also match.

## Costs and the separate launcher recovery

| Checkpoint/task | Matching output tokens | Constant output tokens | Matching summed call seconds | Constant summed call seconds |
|---|---:|---:|---:|---:|
|Qwen3 AG|9,878|10,388|248.26|261.06|
|Qwen3 SST|8,728|8,767|214.95|215.25|
|Qwen3.5 AG|8,686|8,382|324.69|313.09|
|Qwen3.5 SST|8,216|7,714|307.62|289.11|

Matching is not exactly token-matched to constant. Plain arrays are much shorter (roughly2,000–2,500 output tokens per eight-call cell), so matching-versus-plain is not an equal-output-cost comparison. Matching Qwen3.5 was slower here despite fewer output tokens than Qwen3; sequential service stages, architecture/runtime/template differences and this small workload prevent a general speed conclusion.

Across96 calls:327,774 prompt and79,552 completion tokens,407,326 total. Raw cache counters are present for all calls and equal0; no missing-cache value was imputed. Summed concurrent call duration2,463.37s is not wall time.

The original attempt failed after4.307307s, before scientific client/model calls, because inherited `__file__` made SERVER_START/launcher identity disagree. Its failure and orphan/release history remain preserved. A separately authorized lifecycle-only recovery retained the original scientific requests/output locations; it is not a study reroll or erased timer. The recovered actual launcher SHA `0e116a9f950f92f796a8050a8118bc6774b56d1dd67adabf5b5e25b36f35339c` matches both SERVER_START records. Recovery took713.754054s owned/714.285384s parent, exit0/no timeout; both model services have complete owned-identity release records and parent GPU-after-exit is empty. The original and recovery job clocks sum718.592691s, excluding the separately documented cleanup/wait interval; do not call that total end-to-end elapsed time.

## Decision-relevant follow-up

This strengthens the case for a source-cue correspondence mechanism test and a separately controlled whole-RLM integration. The already prepared shifted-cue comparison can discriminate following the named source from a generic varying-output-token aid, while preserving positional scoring and acknowledging its contradictory cue. A whole-RLM test must separately verify map coverage and aggregation rather than infer planning competence from this component effect. Replication on genuinely different source domains and additional context clusters remains more informative than increasing model size without a specific uncertainty.

## Audit scope and artifacts

[METHOD.md](METHOD.md) and [AUDIT_READY.json](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT_READY.json") preceded outcome inspection. MAIN triggered terminal scoring; the independent [audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py") ran once using an authenticated earlier independent parser, not an author scorer. Nine inherited parser fixtures and five new raw/wire/null fixtures were qualified before outcomes. The auditor did not author this scientific driver or recovery, but authored earlier data-feasibility/shared Qwen work; independent raw scoring does not imply independent dataset-discovery decisions or inference implementation.

[ROW_LEDGER.json](../../../../ARTIFACTS.md#unpublished-files "Not published: ROW_LEDGER.json") preserves every raw path, validity, cost and provenance decision; [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json"), frozen input catalogs and final seal provide exact hashes. No method, scientific output, source, acceptance or model was changed. No GPU/model/network/service/process-control action occurred during this audit.
