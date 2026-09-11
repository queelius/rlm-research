---
schema: research-decision-v1
status: design_for_MAIN_review_not_READY
question: Does source-matching output improve relational record classification when IDs are freely generated?
recommendation: one_new_task_transfer_screen_then_prioritize_composable_harness
implementation_authorized: false
model: Qwen3-4B-Instruct-2507
revision: cdbee75f17c01a7cc42f958dc650907174af0554
adapter: null
source: nyu-mll/multi_nli
source_revision: da70db2af9d09693783c3320c4249840212ee221
split: validation_matched
context_design: 8_contexts_x_16_premises_x_3_hypotheses
representation: [matching_tag_objects, constant_tag_objects]
decoder: [free, shape_cardinality_vocabulary_only]
seeds_per_context: 2
primary_calls: 64
singleton_reference_calls: 16
total_planned_calls: 80
gpu: one_A100_40GB
outer_seconds: 2700
owned_seconds: 2610
work_seconds: 2490
startup_max_seconds: 180
cleanup_reserve_seconds: 120
collection_reserve_seconds: 60
workers: 4
request_timeout_seconds: 90
selected_or_reserved_source_records: 0
readiness_blockers: [MAIN_design_approval, freeze_membership_and_seeds, native_prompt_and_schema_qualification, exact_owner_entry_and_NULL_tests]
---

# Free correspondence on relational records: one useful extension, not another ID replication

2026-09-09, runtime_port. CPU design/source-feasibility only. No GPU/model service, lock, queue, active source or sealed artifact changed.

## Decision and difference from completed work

Run this once if MAIN wants to close the component's remaining deployment/generalization gap. Do **not** repeat matching-versus-constant on exposed TREC/AG/SST, another shifted-ID grid, or specialized ID SFT. [Fresh96](../analyses/leaf-fresh-correspondence-live-2026-09-09/REPORT.md) already found positive matching effects in all32 paired comparisons across two released checkpoints. [Shifted72](../analyses/leaf-shifted-cue-live-2026-09-09/REPORT.md) already shows named-source following under forced cues. These are not freely generated source bindings.

[Free-ID96](../analyses/leaf-free-id-live-2026-09-09/REPORT.md) had only4/48 valid free answers, with35 tool-directed outputs under an inherited coding/tool interface. [Role/tool96](../analyses/leaf-role-tool-live-2026-09-09/REPORT.md) removes that explanation in part: classifier/no-tools matching is valid3/4 free calls; its residual failure uses a forbidden label, not wrong IDs. Under exact structure it scores218/256 versus129 constant. That leaves a useful untested contrast: new relational records, clean final-only contract, and structure support that **does not supply literal IDs**. It is not yet evidence for internal attention or whole-RLM benefit. Read the current correspondence card and PROMISING_RESULTS through its22:32 priority update; conclusions below preserve their contrary bridge evidence.

## Proposed fixed-policy comparison

Use eight48-record contexts from MNLI: two contexts from each of government, slate, telephone and travel; each context contains16 distinct premises and all three available hypotheses per premise. This demands classification of a premise–hypothesis relation rather than a single-text topic/sentiment. Select exact-three groups by a frozen label-blind hash, never requiring one gold label of each type. Majority-annotation repetitions remain. No premise spans contexts. Interleave the three text-hash-ordered pairs of each premise across three independently permuted16-item blocks, without using labels or original ID suffixes. Do not claim independence between hypotheses sharing a premise.

Each visible record has only `id`, `premise`, `hypothesis`. Generate `m`+12hex IDs from normalized pair text with collision checks; keep original row/prompt/pair IDs host-side. **Original MNLI pair IDs often reveal the author's intended class through their suffix.** Gold mutation must leave public IDs, membership/order and every model-visible byte unchanged. The common instruction defines entailment, contradiction and neutral directionally from premise to hypothesis; it must not imply symmetric entailment or expose class counts.

Two outputs, both tag-before-label objects: matching copies each displayed record ID; constant emits `m000000000000`. Both classify in displayed order. Cross with free decoding and the **same** structural grammar: exactly48 objects, fixed fields/order, three canonical labels, and the universal `m[0-9a-f]{12}` tag shape. No literal-ID enumeration, fixed per-position tags, uniqueness, gold labels or source-order enforcement in the grammar. Both arms must generate their own tag values. Free/structured request pairs differ only by `structured_outputs`; no reasoning/tool inventory, examples, prefills, retries or repair.

Use the qualified role/tool classifier system verbatim, released cdbee base/noLoRA, thinking disabled, temperature0.5/full-support sampling, max3,072 output tokens,8,192 context, four sequences and prefix caching disabled. Freeze two new paired seeds per context and balanced four-cell order. Add16 prespecified singleton references: the lowest text-hash pair per context, both seeds, matching/free only. They diagnose gross NLI-task difficulty without selecting or replacing batch outcomes; they are not a separately tuned baseline. Total80 physical final-only calls, no acquisition or root/child execution.

## Source audit and honest freshness

Acquired only a4,938,568-byte development parquet and8,895-byte card into the external cache at `datasets/multinli-correspondence-feasibility-20260909-da70db2/`; no remote code or environment changes. Revision `da70db2…`; parquet SHA256 `350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186`.

The [CPU source receipt](../../../ARTIFACTS.md#unpublished-files "Not published: ../analyses/multinli-correspondence-feasibility-2026-09-09/SOURCE_FEASIBILITY.json"), SHA256 `f45b93236229f57e17fffbe1b7e05110ca3102796ce4627ece0d2d737680f079`, records9,815 unique labeled pairs,3,334 normalized premises, zero conflicting pair groups and3,151 exact-three groups. The four chosen genres supply2,513 such groups. The23:00:09–23:00:15 scan checked115 named input catalogs across the runs tree, with zero exact premise/hypothesis text hits and no oversized/skipped candidates. It excludes source-provenance branches from exposure and reads no sampled outcomes. No records have been selected or reserved yet.

This supports feasibility for catalog-new contexts, not arbitrary-history nonexposure, near-duplicate independence, or unseen pretraining/post-training. TREC's earlier all-system pool was effectively exhausted; a fresh root-only composition is not new source text. AG test and SST training still have room but would mostly repeat established tasks. MNLI source text and annotations are public, old benchmarks. The authors describe permissive OANC terms for the non-fiction sources; fiction has mixed licenses, not blanket MIT. Preserve attribution and source-specific terms; no dataset redistribution is proposed. [Original data paper, §2.2](https://cims.nyu.edu/~sbowman/multinli/paper.pdf).

## Measurement, budget and stopping decision

Primary: paired matching-minus-constant strict positional label accuracy on the full planned denominator, **separately by decoder**. Report eight context means and two-seed variation, not independent record p-values. Distinguish whole shape/vocabulary validity, literal ID/order fidelity, semantic accuracy conditional on each admission, and all48-perfect batches. No ID-based reordering or prefix salvage. Authentic malformed/wrong-route returns score0; missing/failed/unverified endpoints areNULL with lower/upper bounds and a separately named operational view. Length is a flag, not infrastructureNULL; a complete valid capped answer remains scoreable. Preserve all80 slots, native prompt/completion identities, raw body/usage, errors and calls. Costs are physical requests/observed tokens/time, not known provider billing or equal FLOPs.

2,700-second inclusive cap:2,490 work including startup≤180 and60 collection reserve, then120 cleanup,90 outer margin. Four workers and90-second calls bound20 waves at1,800 seconds, leaving staging headroom. Freeze native input+output budgets before launch; any overflow returns for design review, never silent cropping or replacement. Reuse the qualified noLoRA leaf lifecycle and strict parser.

A practical positive is matching's free semantic/ID advantage across most context means, surviving structural control without forced IDs. If only structure helps, report contract support—not freely reliable correspondence. If matching and constant are similar despite useful singleton accuracy, treat this as a transfer boundary and stop more ID grids. If all are poor, task competence remains unresolved. Even a strong positive earns only a bounded relational-classification claim. The higher-value RLM question remains whether source-bound evidence is actually consumed and sufficient for a verified cross-partition answer; the already accepted record-interface pilot and genuine-report analyses address different parts of that boundary. Do not displace them or infer downstream benefit from this screen.

## Four primary readings and prior-art overlap

- [BatchPrompt v3](https://arxiv.org/html/2309.00384v3): read §§1–4, MNLI appendixC and indexed prompt appendixD. Source-indexed input/output, positional instability, NLI batching and permutation ensembling already exist. Its input-token accounting excludes generated tokens; we cannot claim a new indexing method or inherit its efficiency numbers.
- [Let Me Speak Freely? v1](https://arxiv.org/html/2408.02442v1): read §§2–4 and selected §5 discussion. It distinguishes prompt restrictions, JSON mode and two-stage conversion, with task-dependent effects and an LLM answer extractor. We instead preserve strict uncorrected outputs and isolate structure support from literal IDs; generic format effects are prior art.
- [Multi-Problem Evaluation](https://aclanthology.org/2025.insights-1.12.pdf): read §§3–5.1 and tables2–4. Classification versus index selection and gold-label substitution controls already separate components, including paired-text tasks. Our all-record output is not its subset-selection task, and no broader competence claim follows.
- [MultiNLI](https://cims.nyu.edu/~sbowman/multinli/paper.pdf): read §2 collection/validation, split and license passages, plus the pinned dataset card. The three hypotheses originally target three relations but majority labels can differ; our exact-three criterion must not filter for balanced gold. These are selected-method reads, not four full-paper reviews or a systematic novelty search.

Remaining blockers are narrow: MAIN design approval; freeze the exact128 premises/384 pairs, public IDs, seeds and renewed exclusion receipt; CPU-native prompt/identical-grammar qualification including zero gold/pairID leakage; and actual composed owner/collector plus unavailable/wrong-route scoring checks. There is no model-performance gate, training selection or implementation yet.
