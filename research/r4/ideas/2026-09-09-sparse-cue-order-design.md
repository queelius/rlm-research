# Sparse cue order96 — proposal only

Status: bounded design for MAIN review, not an implementation, frozen study, acceptance, or launch. No model calls or source changes have been made. Companion plan: `2026-09-09-sparse-cue-order-plan.md`.

## Question and smallest informative comparison

Does moving a source-ID cue after its anchor label shift the matching-versus-constant benefit from that label toward the next item? Use cadence4 only, two assigned object field orders × matching-source/constant tags, the exact12 exposed sparse144 contexts, two fresh sampling seeds, and the unchanged c32de child. This is96 distinct native component calls (6,144 planned labels); no shared/filler calls. Each task has four source clusters and32 calls. A smaller two-arm comparison could measure an order effect but could not subtract generic order/format effects; retaining both constant conditions is the narrowest identifiable interaction. Adding cadences1/16 or ordinal cues would increase scope without being necessary for this question.

Motivation is explicitly adaptive and outcome-informed. Sparse144 found cadence4 matching correct at distances0–3 of120/92/59/47 TREC,121/117/95/81 SST-2,102/51/44/38 AG (each128); corresponding constant values42/51/54/43,74/68/82/77,41/64/48/39. Cue48 found dense matching benefit survived label-first decoding; its first-record accuracy was perfect, and its order interaction varied by context. A sparse gap makes next-item spillover distinguishable from dense adjacent cues. These observations choose the study; they are not reused as new controls or scored as new endpoints.

## Inputs, treatments, and native seam

Reuse the exact source records/IDs/order and task definitions in `sidecars/leaf-sparse-anchor-v1/DATA.json`/SPEC. No context, label, permutation, or vocabulary selection after viewing outcomes. Four contexts/task (TREC0–3, SST-2 4–7, AG8–11),64 records each, displayed permutation0. Exposed developmental contexts and unknown-license/public-pretraining qualifications remain unchanged. This is a fresh sampling study on reused data, not a new-data replication.

Four cells:

| Code | Cue | Anchor object wire order |
|---|---|---|
| A | Matching source ID | `tag`, `label` |
| B | Constant `p0000` | `tag`, `label` |
| C | Matching source ID | `label`, `tag` |
| D | Constant `p0000` | `label`, `tag` |

Anchors remain positions1,5,…,61. Every other slot remains a bare canonical-label JSON string. Use the existing sparse request-builder seam; replace exactly one `the keys tag then label` with order-neutral `the keys tag and label` in all four cells. This common wording follows the already-qualified cue48 intervention. Assign order only through each anchor schema's property insertion order and `required` order; preserve exact tags, labels, cardinality64, no additional properties, and the 48 nonanchor slot schemas.

Readable prompt excerpt shared by A/C:

> Return only a JSON array in displayed input order, exactly one item per input record. Anchor positions are 1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61. At anchor positions emit an object with exactly the keys tag and label. Set tag to that record's source ID shown in the input. Set label to that record's canonical label. At all other positions emit only the canonical label as a JSON string, not an object. Do not omit any input record.

B/D replace only the tag-setting sentence with the frozen sparse constant instruction requiring literal `p0000`. Task opening, allowed labels/definitions, public input block, system/tool descriptions, and sampling remain unchanged. Illustrative shape—not a supplied gold example—A emits `[{"tag":"q5236","label":"<canonical>"},"<canonical>",…]`; C emits `[{"label":"<canonical>","tag":"q5236"},"<canonical>",…]`. Placeholder examples here are explanatory only and are not runtime prompt additions.

Order pairs A/C and B/D must have identical messages/tools/sampling, and actual full prompt token vectors must match. Their serialized schema bytes intentionally differ. Matching/constant still changes instructions and forced tag values, and all order changes alter the autoregressive output prefix. Thus the primary interaction is an observable order×cue effect, not isolated attention, semantic binding, or harmless wording. No generated tools execute: reuse the qualified native first-response component collector at `/v1/chat/completions`, retaining ordinary tools in the prompt, constrained first-response action space, full input/output token IDs, and actual ordered-wire capture. No recursive runtime/image intervention is needed.

Exact source seams: sparse `make_request`, `build_design`, `score_labels`; cue48 `make_request` orders `properties` and `required`, and `score_labels` validates actual raw key order. Reuse the unchanged qualified HTTP collector/owned lifecycle. A private thin adapter may compose these sources; no general scheduler/framework or pinned-source edit. Source parser must adapt strict assigned order at anchors, not trust a tag-first-only auxiliary. Schema compilation and raw first-response order checks are both necessary because JSON Schema semantics alone do not guarantee object order.

## Prospective estimand and nulls

For each task, context c, paired seed s, assigned order o, cue a, and distance d∈{0,1,2,3}, define Y as correct displayed-position assignments /16 within that call/distance. A completed malformed response contributes strict0 at all positions; infrastructure/unavailable/provenance failures remain NULL. Do not repair arrays or match by source IDs after decoding.

Define G(o,d)=Y(o,matching,d)−Y(o,constant,d). Primary interaction:

`I(c,s) = [G(label-first,1) − G(label-first,0)] − [G(tag-first,1) − G(tag-first,0)]`.

Positive I means the relative matching advantage shifts toward the next slot under label-first output. Average the two seed contrasts within each context, then report the four context values and their equal-weight mean separately per task. The primary complete-quadruple interaction is NULL if any constituent call is unavailable; report planned8, observed-complete, and jointly full-schema-valid quadruple denominators per task. An observed malformed call remains strict0, with a separate jointly-valid semantic interaction. No NULL-as-zero conversion, task pooling as new primary, context filtering, best seed, position realignment, or fallback metric.

Report full G(o,0..3) and underlying arm accuracies with planned/observable/aligned denominators. Predeclare first anchor versus later anchors as a descriptive split: position1 has no previous cue, and this boundary could matter. Retain whole64 accuracy, total aligned/strict assignments, exact schema violations/key order/tags, canonical label confusion, count-vector L1, stop reasons, and all96/null accounting. No offset search or previous-gold rescue is needed. The distance interaction compares the same records across treatments, but d0 and d1 are different source records; labels repeat and context/semantic differences remain possible effect modifiers.

Positive, context-consistent interaction accompanied by an interpretable full profile would motivate testing cue placement in a downstream count interface. A null or inconsistent interaction with preserved matching gains would weaken a simple within-block timing account; it would not prove equivalence or rule out correspondence. Improvement concentrated in format validity must be reported as such, not semantic transfer. No claim of learned root planning or whole-RLM improvement is possible.

## Weights, seeds, costs, and bounds

Fixed alias `strict-rlm-qwen3-4b-role-sft-selected-v1`, adapter `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`, config `ec773bc3b9de58af98a7c4dce9a40af795a4d05cd47284dbbfb27eac99b74174`, original base Qwen3-4B-Instruct-2507 revision `cdbee75f17c01a7cc42f958dc650907174af0554`. No weight selection from active RLVR or future studies. Sampling remains temperature0.5, top_p1, top_k−1, min_p0, max_tokens3072, timeout120s, four collectors. No API retry/replacement call in this qualified component path.

Proposed master981304001 and sampling seeds981304011/981304021. A read-only bounded scan of research sidecar Python, seed JSON, decision and design/plan documents found no matches before this proposal; this is a declared scope, not proof about external/private seed use. Recheck frozen scientific seed manifests immediately before READY, reserving these values if still unused. Seeds are shared across the four treatments as variance-reduction intent, not guaranteed identical first sampled labels or deterministic counterfactuals.

Sparse144's48 cadence4 calls consumed264.1007 summed call-seconds at concurrency4;96 analogous calls suggest roughly132s service-collection work, with130–200s a rough range rather than a promise. Native grammar compilation/order may add overhead. Proposal: cumulative collection600s, shared work780s including preflight, owned inclusive900s including120s cleanup, outer930s. These are smaller than sparse144's900/1080/1200/1230 bounds while leaving several-fold collection margin and observed≈50s launch/preflight overhead. No phase reset, timeout extension, or reroll after failure. All96 share one service.

Account all physical requests once. Parse raw usage including cached tokens; report logical prompt, cached/uncached, output, call durations and overlapped collection/owned wall separately. Include within-order cue cost and within-cue order cost, plus all-work and jointly-valid accuracy comparisons. Equal tag tokenization does not imply equal compute; no FLOPs or accuracy-preserving efficiency claim from token savings alone.

## Pins and review boundary

Sparse source study SHA `2728361c0f6b12dc887d6e171cc1f12941380428ab983ad18403e7d47ea0faa9`; SPEC `1627f461a52811e68dfab15bd5a0ec1f173ef71accee493b50bc5fcb31c173c3`; audit REPORT `316683e51faa4d19cb789f992c67fe20a2788d58ec1af3f2c68fc5d66a207ae9`. Cue source study SHA `3e2c9ede21b6d56d2f0ad04477712e4cf4c521282ccdfb82a7c0d550b2d38ccd`; independent REPORT `5759b983ee0bfa361467354b134d5f1d297760e3c074202a806b3e3aad3ca1df`. These are source-grounded proposed seams, not a new CPU qualification. MAIN must choose implementation/acceptance separately. The brainstorming skill kept this turn at design-only; no implementation approval is inferred.
