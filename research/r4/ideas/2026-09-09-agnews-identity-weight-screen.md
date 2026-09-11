# AG News: source-matching output across two fixed weights

September 9, 2026. CPU acquisition and design feasibility only. Main must accept
this new-task comparison before any experiment implementation or launch. No GPU
call, model call, environment install, runner, acceptance or queue change occurred.
The brainstorming spike remains at the design boundary.

## Why this replacement is necessary

The proposed four fresh SST2 contexts cannot be assembled from the named cache:
872 normalized groups minus three disjoint leaf-study pools of256 and96 frozen
root-curriculum reservations leaves8. The old SST proposal and the negative
membership report remain unchanged. See
2026-09-09-identity-new-context-weight-feasibility.json,
SHA51a08d4ad56f04c7998def3c239d58e2fab7a7b8c55e578588d7104324bc17e5.
No reserved groups are consumed and no overlapping recompositions are called new.

AG News makes this a **new topic-classification task**, not a same-SST replication,
label rename, independent SFT seed or whole-RLM improvement. The question is
whether the disjoint source-matching versus ordinal output contrast survives new
news texts, and whether its size differs between original and historical TREC-SFT
weights. Item correspondence need not improve a permutation-invariant global
count; the separate query-sensitive-planning note explains that distinction.

## Acquired source and selection

Pinned dataset: fancyzhx/ag_news revision
eb185aade064a813bc0b7f42de02595523103ca4, official test split. Only the exact-revision
card, API metadata and test Parquet were downloaded (1,246,140 bytes total).
The card provides four labels and attributes this benchmark to Zhang, Zhao and
LeCun's text-classification work. Its license field is unknown; its research-use
description is not treated as a permissive data license. [Pinned dataset card](https://huggingface.co/datasets/fancyzhx/ag_news/blob/eb185aade064a813bc0b7f42de02595523103ca4/README.md),
[paper](https://arxiv.org/abs/1509.01626).

External cache:
/project/alex_phd/research-cache/datasets/fancyzhx--ag_news--eb185aade064a813bc0b7f42de02595523103ca4.
ACQUISITION.json SHA
bba780a2e3cdc34b6f7d9ee48a86cd613a8dda9a500b8fc623bea11f58622f54
records URLs, hashes, retrieval timestamp and license uncertainty.
test.parquet SHA71de87ec66bc5737752a2502204dfa6d7fe9856ade3ea444dc6317789a4f13fb.
Only local pyarrow data reading was used; no remote loader/code or training split.

Measured:7,600 rows,7,600 groups under NFKC→casefold→whitespace collapse→UTF8
SHA256, zero duplicate rows/groups and zero conflicting-label groups. The full
test split has1,900 examples per class. This does not establish clean base-model
pretraining, absence of near-duplicate news events, or whole-history nonexposure.

Candidate selection is the first256 normalized hashes in lexical order, split
into four contiguous groups of64. No label quota, length filtering, text crop,
generated answer, or outcome-dependent selection. Retain complete original text
and zero-based source-row indices. If future verification finds a conflicting
duplicate, exclude the whole group before selecting; none exists here.
Selected-group-list SHA
1b7b1c675bac3b7e8521ff2534a681f8e6dc3274234e978610c21ac2d4f4f88c.
Class counts (World/Sports/Business/SciTech) are16/16/9/23,14/21/12/17,
22/12/14/16,19/16/17/12. These are descriptive, not selection targets.

## Exact candidate96 grid and output contract

Four contexts × two seeds × q/p source prefixes × original/old-SFT weights ×
meaningful/ordinal/constant tag rules =96 calls. One label-free randomized display
per context, shared across all conditions; no second display permutation.
Each of12 cells has8 calls/512 scheduled labels, nested within four contexts.

Proposed namespace leaf-identity-agnews-weight-v1; master981275401; sampling seeds
981275411/981275421. These candidates had zero matches in93 named top-level
SPEC/READY/RECIPE/CAMPAIGN/SEED and one-level input PLAN JSON files. They are not
globally reserved; repeat this bounded check before actual input freeze.

Let H be SHA256 of canonical compact, sorted-key JSON, matching the qualified
identity study. Stable ranks1–64 follow the selected hash order within each
context. Display order sorts H([namespace,master,"display",context_id,group_id]).
Context IDs are agnews-test-00 through03. Independently order eligible integers
1000–9999 by H([namespace,master,"disjoint-value",context_id,value]), take64, and
assign to stable ranks. Exclude last-three-digit suffixes001–064; reject an exact
affine/mod10000 mapping by source or display rank without automatic alternate IDs.
The candidate maps pass. Source numbers remain fixed when swapping q/p prefixes.

Reuse identity384's exact array-of-objects grammar:64 objects in displayed order,
keys tag then label, no extras, exact per-position tag const, canonical label enum.
Meaningful tags copy displayed source IDs; ordinal tags use the opposite prefix
plus0001…0064; constant tags use the opposite prefix plus0000. Primary labels are
always scored against the displayed record. No repair, ID-based relabeling,
permutation rescue, overlap-only numeric diagnostic or latent-rank score.

Canonical labels and common neutral definitions are exactly:

```text
World: international or national public affairs, politics, conflict, diplomacy, and major public events.
Sports: athletic competitions, teams, players, and sporting events.
Business: companies, markets, finance, trade, and economic activity.
Sci/Tech: scientific research, technology, computing, and technical innovation.
Choose the topic most central to the full news text.
```

User opening: "Classify the main topic of each news text." The three rule
instructions and source-ID input JSON retain the identity384 format. This changes
the semantic task and canonical vocabulary openly; system message/tools and
provider protocol stay identical. Labels/gold never enter model-facing records.

CPU candidate-body proof is
2026-09-09-agnews-identity-weight-feasibility.json,
SHA9453b0f2a692e4a88513151ddda6bc595a04d90b1407ef333ede2d3af1750a84.
All96 complete prompts were validated by actual vLLM ChatCompletionRequest and
rendered using tool.model_dump plus the pinned native HF tokenizer/template.
Physical input lengths4474–4707; reserving3072 output tokens gives maximum7779
of8192, leaving413. No length amendment is needed. All48 weight-paired request
bodies differ only by model alias and have identical complete prompt token IDs.
The proof contains source indices, displayed group IDs/numerals and per-body/token
hashes. It is a feasibility artifact, not a launch-ready frozen source closure.

## Service, ordering and caps

Use the same base Qwen3-4B-Instruct-2507 revision
cdbee75f17c01a7cc42f958dc650907174af0554. Fixed original adapter857a7ce6… and
historical c32de129… are already simultaneously supported by the qualified
leaf-post-sft-suite-v1/suite.py and leaf-role-routing-v1/source/serve.py.
Actual old dual-service preflight and release are retained in
operations/2026-09-09-succession/post-leaf-suite-attempt-001/original_old:
SUITE_PREFLIGHT SHA5fd8bc3544f6a87180c25b34c999aff2d3fdc0fca8442dc10087d2d7c915b872;
SERVER_READY SHAf6a99273eb489fef6b805830a67a93a246feb54c77472876d8855f239152beb9.
That stopped endpoint is evidence of capability, not authorization/current binding.

Both aliases must be authenticated at the new launch from exact adapter/config
hashes, actual descriptor, /models path/base identity, serving source/config and
the accepted owned lifecycle observer. No new environment/model is needed.
Use /project/alex_phd/envs/prime-rl-5990b1b/bin/python. This is the qualified native
HF/vLLM **Chat Completions component** path, not a TrainClient RLM episode.
Reuse existing collection/wire-capture helpers with a small private two-weight
binding/callback; no new scheduler or service framework is justified.

Proposed dispatch: for each context c and repeat r, take the six conditions
(q,M),(q,O),(q,C),(p,M),(p,O),(p,C), rotate by(2c+r) mod6 and reverse if(c+r) is odd.
For each condition with original index j, enqueue its adjacent weight pair
original→old when(c+r+j) is even and old→original otherwise. This gives each
matched condition opposite weight-first ordering across seeds, with one shared
dual service/four workers. Start order is not completion order or independent
cache exposure; retain actual timestamps and cache usage. No weight-phase change
is necessary and no perfect all-position balance is claimed for eight groups.

Preserve temperature0.5, top_p1, top_k-1, min_p0, max_tokens3072, request timeout120s,
one call per coordinate, no retry. Proposed collection900s within shared work1080s,
owned inclusive1200s with120s cleanup reserve, outer1230s for exceptional cleanup.
Collection takes the lesser of900s and the remaining work deadline. Estimate
roughly6–12minutes on one A100, not a promise; AG prompts are longer than SST.
Partial/unrun/provider failures remain null, malformed complete arrays remain
strict failures with semantic alignment unavailable. Release owned GPU authority
before independent CPU analysis.

## Endpoints and decision

Primary: meaningful−ordinal strict displayed-record accuracy, separately for each
weight/prefix, with eight task/seed pairs and four context summaries. Report the
old−original interaction of those differences, known/unknown pairing and source
context variation. Secondary: constant contrasts, schema validity, whole64 exact
accuracy, class-count error (cancellation warning), token/call/cache/wall costs.
Count four context clusters, not6,144 independent labels. Grammar constrains
allowed next tokens; this is the output-rule package, not instruction alone.

If both weights retain the contrast on news, a cross-task/cross-weight component
effect is supported; next consider a new model family or a genuinely
correspondence-sensitive RLM consumption task. If only old-SFT does, investigate
training-associated cue reliance without calling this a randomized training
effect. If weak/inconsistent, narrow the evidence. Do not pool with TREC/SST or
infer a count improvement automatically. Main selects resources and accepts any
implementation; no READY or experiment runner is produced by this design.
