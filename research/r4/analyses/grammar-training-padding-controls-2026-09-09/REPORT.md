# Output correspondence matters more than specialized indexed-output training here

COMPLETE at2026-09-09 approximately05:03UTC: all368 calls across grammar160,
B80 and padding128 are terminal and raw-audited. No infrastructure or unrun nulls.
The pre-outcome [method](METHOD.md) was frozen before this analyst read these outcomes.

Two conclusions stand out. Specialized indexed-output training adds no demonstrated
benefit over mixed-size B on these indexed readouts. But the choice of output tokens
matters greatly: under exact grammar, meaningful IDs outperform same-shaped constant
placeholder tags at similar realized token cost. This supports a correspondence/
position-cue explanation over generic extra output length alone, not yet a uniquely
identified internal mechanism or a general RLM improvement.

## The missing training baseline changes the interpretation

Mixed-size B already performs as well as the specialized indexed-output model on
indexed readouts. Across the same requests and seeds, B is ahead by two TREC labels
and behind by one SST label in each decoding mode. These are small exploratory
differences, not evidence of equivalence, superiority or an added indexed-training
benefit. The large contrast is the output representation, not those weight differences.

All fractions below are correct/aligned items. Parentheses give valid calls when
not all calls align. TREC has12 calls/768 planned items per cell; SST has8/512.
“Unavailable” means no complete output could be aligned, not established failure
on every classification. Every recorded call remains in strict scoring.

| Task | Model | Anonymous/free | Anonymous/exact | Indexed/free | Indexed/exact |
| --- | --- | --- | --- | --- | --- |
| TREC | Old short-batch SFT | unavailable (0/12) |343/768|727/768|727/768|
| TREC | Mixed-size B |41/64 (1/12)|444/768|740/768|739/768|
| TREC | Indexed-output SFT |unavailable (0/12)|339/768|738/768|737/768|
| SST | Old short-batch SFT |unavailable (0/8)|344/512|357/384 (6/8)|479/512|
| SST | Mixed-size B |unavailable (0/8)|347/512|478/512|478/512|
| SST | Indexed-output SFT |unavailable (0/8)|351/512|479/512|479/512|

Exact grammar makes the anonymous outputs structurally valid but does not solve
their correspondence problem. For B on TREC, anonymous/exact correct items by
successive16-position blocks are189,152,60,43 of192 each. Its indexed/exact values
are188,189,179,183. All64 questions are present in the authenticated physical input;
this is not input truncation. No call in either completed stage is completely
correct on all64 items, despite high indexed per-item accuracy.

The indexed model also does substantially worse than B on anonymous/exact TREC:
339 versus444, with68 newly correct and173 newly wrong item positions. All six
context groups favor B after combining their two seeds. That is an important
negative finding for portability across output contracts. It does not prove that
every indexed curriculum would regress: one training seed/checkpoint per recipe,
different target-token exposure and a later B service stage limit causal attribution.

For the principal indexed comparison, the specialized model's TREC free-output
net−2 consists of4 gains/6 losses; exact grammar gives5 gains/7 losses. SST's+1 is
one gain/no loss, in one of four contexts. Detailed seed/context pairs, rather than
only pooled totals, are retained in [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json").

## Exact counts are harder than high item accuracy suggests

Count-vector agreement was recomputed within each complete aligned call, not from
pooled histograms. No TREC call in grammar160 or B80 gets the complete six-label
count vector right. In indexed SST, B gets2/8 count vectors exactly right per mode;
the indexed-output model gets1/8. This can differ from item-accuracy ranking because
misclassifications can cancel within a call. It is not legitimate to infer correct
counts from near-matching totals pooled across calls.

B's anonymous/exact TREC outputs nevertheless recover approximate counts better:
mean total absolute count error6.5 per call, versus42.5 for indexed-output SFT and
54.3 for old SFT. Those approximate counts coexist with many misplaced labels.
This is evidence worth distinguishing from perfect counts or correct correspondence,
not a replacement scoring rule. Per-label/per-call count errors are retained too.

## Meaningful IDs beat equal-shaped constant tags under exact grammar

Padding128 uses the old SFT checkpoint throughout, four contexts per task and two
new seeds. All exact-grammar cells have8/8 valid64-item outputs. Values are correct
items/512; the two tag formats have identical object structure, but one emits the
corresponding input ID and the other always emits the task-irrelevant `q0000`.

| Task | Anonymous/exact | Indexed/exact | Meaningful tag/exact | Placeholder tag/exact |
| --- | --- | --- | --- | --- |
| TREC |242|489|491|229|
| SST |340|480|481|328|

Meaningful minus placeholder is+262 TREC items (268 gains,6 losses) and+153 SST
items (163 gains,10 losses). All four contexts favor meaningful tags on both tasks.
The two-seed context totals are+55,+61,+75,+71 for TREC and+40,+30,+40,+43 for SST.
These are repeated observations within four groups, not16 independent datasets.

The gap is concentrated after the beginning of the batch. Meaningful TREC quartile
counts are124,125,124,118 of128; placeholder gives116,63,21,29. SST gives
123,122,117,119 versus125,74,66,63. Again, exact grammar alone guarantees structure,
not correct input/output correspondence.

Real output-token totals are close: TREC8792 meaningful versus8492 placeholder
(3.5% more); SST8216 versus8225 (slightly fewer). Thus a large generic “more output
tokens means more computation” explanation is insufficient for this observed
comparison. It is not a perfectly compute-matched causal test: instructions differ
by26 input tokens, realized labels differ, and a repeated dummy tag is not neutral.
Most importantly, current input IDs are sequential: meaningful tags also supply a
changing position counter. This experiment does not distinguish input-identity
matching from the benefit of that counter/progression signal.

Free generation supplies a sharp limit. Both tag arms are0/8 valid on both tasks:
28/32 free-tag calls stop at the length cap; two others end as tool responses.
The semantic contrast is unavailable in all sixteen matched pairs. A zero strict
score difference here is a mutual format failure, not evidence of equal semantic
ability. For reference, free anonymous is also0/8 valid on each task, while free
indexed is490/512 TREC (8/8 valid) and183/192 aligned SST (3/8 valid,5 length stops).

All2048 objects in valid exact-tag outputs actually place `tag` before `label`.
There is no complete parseable free-tag output from which to establish valid free
key order; no partial prefix was credited or repaired. All69 valid free indexed
objects across the three stages preserve input-ID key order. These observations
support an ordering description, not a claim that free generation demonstrated an
ID-before-label causal mechanism.

Even the better exact-tag outputs do not solve entire batches: zero whole64
successes. Exact per-call count vectors are right for1/8 meaningful TREC and2/8
meaningful SST calls; placeholder is0/8 on both. Per-label counts, their errors in
each call and lexical diagnostics are in [COUNTS_AND_FORMATS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: COUNTS_AND_FORMATS.json").

## Real cost and completion

| Stage | Calls | Valid outputs | Logical input tokens | Cached input tokens | Output tokens | Collection / owned wall seconds |
| --- | --- | --- | --- | --- | --- | --- |
| Grammar160 |160|118|347872|286688|149167|477.53 /551.32|
| B80 |80|61|173936|143344|36685|113.53 /192.97|
| Padding128 |128|75|291744|239520|190865|600.79 /648.87|

All stages report completion with no stop reason; all owned release markers exist.
All input/output/cache fields are present, so no missing cache value was turned
into zero. Cache overlap and service phase differ: these wall/token totals are
actual costs, not a controlled throughput benchmark. B's owned clock excludes its
initial CPU source verification; the parent has the separate1830s total envelope.
Parent-observed process durations, including those initial checks, are580.28s for
grammar160,228.18s for B80 and649.38s for padding128. All exit0 without timeout;
each parent's retained result reports no GPU process left by the exited job.
Grammar uses1800s collection/2700s owned limits; B/padding use900s collection/1800s
execution-stage limits. All finished below their limits.

## Audit scope and limits

All368 calls pass exact raw request-wire serialization, truthful alias,
qualified physical prompt-ID and usage-length checks. Both frozen scorer replay
and independent strict parsing reproduce their saved scores. The160 B-to-parent
comparisons differ only in model alias and have matching actual prompt hashes.
Grammar160 has160/160 observable calls,118 valid outputs,26 length stops and two
tool-call responses; B80 has80/80 observable calls,61 valid, no length stops or tool
responses. Tool responses here are invalid task outputs, not endpoint failures;
no generated code was executed. There are no infrastructure or unrun nulls in
these two stages. Padding adds128 observable calls,75 valid,40 length stops and
two tool responses; these are also task-output failures, not infrastructure nulls.
All184 free/exact physical-input pairs match. Every saved cell aggregate and
coordinate score matches replay of its frozen scorer and the independent parser.

The common base is pinned Qwen3-4B-Instruct-2507. Exact adapters are old `c32de129…`,
B `59ad8542…`, indexed `7a18736d…`; source inventories retain full hashes and actual
endpoint descriptors. vLLM0.28.0 uses BF16 base/automatic BF16 inference cast of
FP32 stored LoRA tensors, native tool rendering, T0.5/full-support sampling, two
declared seeds,3072 output tokens and8192 context. This is not pooled with HF-greedy
results. Shared immutable model/source hashes are cached across stage audits using
unchanged file identity; each raw call and wire file is authenticated.

Six TREC and four SST source contexts, not repeated calls, are the main grouping
units. TREC is exposed. SST was fresh at the parent input freeze but is reused
across these follow-ups; later observations are not an unseen-test replication.
Public pretraining exposure is unknown. B was added after the HF result and runs
in a later service stage, not fully interleaved with the two parent weights.
Padding uses four/four developmental contexts, retaining parent data order/IDs.
These are component results, not an end-to-end RLM orchestration result.

I authored the B companion. This is a reproducible results audit, not a fresh
independent code review. Separate parent reviews are
[B80](../../operations/2026-09-09-proceed/B_CONTROL_SOURCE_REVIEW.md) and
[padding128](../../operations/2026-09-09-proceed/PADDING_SOURCE_REVIEW.md).
The two small audit tests cover per-call versus pooled count mistakes,
lexical key order, duplicate keys and unavailable alignment; they passed after
the desired initial RED. No broad tests, experiment edits or model calls occurred.

## What this changes next

Do not promote specialized indexed-output SFT as the necessary ingredient. Preserve
B and old-weight interface baselines; the later-stage B nuisance prevents claiming
formal equivalence, but the observed tiny indexed differences do not justify more
training by themselves. The anonymous/exact regression deserves preservation as
negative evidence rather than hiding it behind the preferred output format.

The most discriminating next component control is a changing-but-irrelevant tag
sequence versus the real input IDs, with input IDs randomized out of positional
order, exact grammar and equal token-shape budgets. A small paired fresh-context
comparison can distinguish identity matching from a generic position counter;
the present constant-placeholder comparison cannot. A surviving identity advantage
would strengthen the correspondence interpretation; matching performance would
revise it toward positional bookkeeping. This is a proposal, not prepared code or
launch authority.

Separately, any practical gain needs a fixed-root end-to-end comparison of the
chosen child interface, with identical data/seeds, explicit child-call failures
and actual inference cost. A better leaf readout is not itself evidence that a
root discovers or correctly uses that interface. None of these suggestions alters
the accepted runs or the live queue.

## Reproducibility and artifact map

Run the read-only [audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py") once per terminal stage, then
[synthesize.py](../../../../ARTIFACTS.md#unpublished-files "Not published: synthesize.py") and [count_readout.py](../../../../ARTIFACTS.md#unpublished-files "Not published: count_readout.py"), in a new
analysis destination or with existing results left intact. Writes are additive and
refuse overwrite. Each stage directory retains detailed per-call metrics and a
SOURCES.json mapping every raw call, wire body and authenticated input to SHA256.
[SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") links those inventories; FINAL_MANIFEST.json seals this
report, method, analysis code, machine-readable summaries and operation markers.
The terminal parent command/wait/job/cap evidence is separately captured by
[seal.py](../../../../ARTIFACTS.md#unpublished-files "Not published: seal.py") in OPERATION_AUDIT.json; no live process was inspected or signaled.
The earlier partial snapshot is preserved unchanged.

Machine-readable paired aggregate sums over zero jointly valid pairs are empty-sum
bookkeeping, not semantic estimates; check `jointly_valid_pairs` and the per-pair
null fields. In this report those semantic results are explicitly unavailable.
