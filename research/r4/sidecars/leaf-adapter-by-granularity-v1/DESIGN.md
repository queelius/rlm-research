---
id: leaf-adapter-by-granularity
status: exploratory_preparation
question: Does the trained child adapter improve semantic classification relative to its original base, and does batch size change that effect?
created_utc: 2026-09-10T17:07:00Z
---

# Is the child adapter helping the difficult cases?

The smaller-batch diagnostic improved some labels but left both target
answers wrong. Before changing model size, compare the current child adapter
with its unmodified4B base. Both use exactly the same native token prompts,
task definitions, label schema, sampling and batch partitions. The only
within-batch model change is selecting the adapter or base endpoint on the
same service. The base has no research adapter, not another trained checkpoint.

Use the two exposed256-record contexts from the prior batch diagnostic:
location-weight and numeric-count tasks. Keep their records and order,
without selecting on the new model comparison. Two fresh paired seeds,
986902701/702; model2 × batch-size2 × context2 × seed2,152physical calls.
Wide partitions100/100/56 versus contiguous16; both policies receive every
batch freshly. Alternate model dispatch ordering across context/seed/batch
blocks. Do not reuse prior c32 completions as the paired control.

Fixed Qwen3-4B Instruct2507 cdbee75…; c32 is actual checkpoint0128,
adapterSHA c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3.
Native prefill/parser, temperature0.5, top_p1,2048generated tokens and8192
context remain unchanged. Grammar lists IDs and six category labels, not
gold. Four client workers;90seconds per call. The qualified service may load
the unused root adapter as well; no root model calls or generated code.

Primary per-record correctness requires a native-authenticated complete
exact-ID canonical-label map and an existing matching RESULT. Authenticated
wrong-route/malformed maps are0 for the requested batch; missing/unverified
results remainNULL. No repair, partial salvage, retries or output selection.
Store all152 planned slots and every request/raw response/result, including
unused partial artifacts. Keep schema validity, semantics and host-computed
target error separate; no host diagnostic is presented as executed root success.

Report base-minus-adapter semantic differences separately for each batch
size and each of the four context/seed blocks, then context means. Report
the difference between those model effects across batch sizes. There are
only two purposively selected contexts, not2048 independent examples per
model or four independent contexts. Do not pool widths as independent data.
Cost includes input/output/cache tokens, physical wall times, release and
unknown fields. Adapter/cache service dynamics may differ even for identical
token prefixes; no equal-FLOPs or latency-causality claim.

A practical next-step signal is at least5percentage points of semantic gain
for one model, same direction in both contexts, accompanied by target-error
improvement. This prioritizes a new-group validation or targeted child SFT;
it is not a publication threshold. If both models share mistakes, prioritize
taxonomy/data ambiguity or a larger-model deployment comparison. If c32
helps strongly, preserve it and target root planning/aggregation instead.

OneA100;1800outer,1650work,1770owned;180startup within work,30harvest reserve,
90release and30finalization. Checkpoint percall, no training. MAIN authored
and reviewed locally; no independent-author claim.
