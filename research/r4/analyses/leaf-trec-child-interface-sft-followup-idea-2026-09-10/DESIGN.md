---
id: leaf-trec-child-interface-sft-followup-idea-2026-09-10
status: prospective_design_only
date: 2026-09-10
gpu_launched: false
implementation_ready: false
---

# Matched child-interface continuation SFT

## Decision question

Does supervised continuation on the requested A/B/other contract teach c32 to bind a
runtime category pair, or does it merely learn a shorter output format? Compare exactly two
continuations from the immutable c32 adapter: a `full6` map target and an `abo` map target.
Everything except the target interface is matched. This is exploratory child-only evidence,
not a root-task or pristine-test claim.

The sealed query study motivates training: base scored 672/768 after host projection versus
605/768 direct A/B/other, while c32 scored 726/768 versus the same 605/768. Thus prior full-six
SFT transferred strongly to the full-six contract (+54) but not to the direct contract (+0).

## Recommended two-arm curriculum

Both arms start the exact c32 weights
`c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`.
Start a fresh AdamW optimizer and fresh, shared RNG schedule in each arm; do not restore c32's
full-six optimizer moments, which would favor the full-six arm. Retain rank 8, the same LoRA
target modules, FP32 trainable adapter/BF16 base, gradient clipping 1.0, zero weight decay,
and the qualified native chat template. Use LR 5e-5, microbatch 1, accumulation 4, one fixed
96-context pass, 24 updates, and checkpoints after updates 6, 12, 18, and 24. The scientific
endpoint is fixed update 24; there is no outcome-based checkpoint or arm selection.

Select 1,536 unique normalized groups only from the authenticated 5,065-group source-TRAIN
partition by ascending SHA256 of
`["trec-child-interface-sft-followup-v1","continuation-train",group_id]`. Divide the selected
order into 96 contexts of 16 questions. Assign the six already studied cyclic ordered pairs
to contexts modulo six, giving 16 contexts and 256 unique question exposures per pair. Every
question occurs exactly once in each arm. Stable record IDs are
`q + SHA256("source-train-group:" + group_id)[:12]`.

Each prompt gives the requested pair, all six definitions, and the same 16 ID/text records.
The full6 arm targets one complete ID-to-canonical-six-label JSON map; the ABO arm targets the
corresponding complete ID-to-A/B/other map. Gold labels never enter prompts. Mask the entire
prompt and supervise the complete assistant map plus end-of-turn. Preserve malformed outputs
as failures at readout; do not repair or project ABO. Full6 projection is a fixed scoring
operation only.

The arms match 1,536 unique text groups, 96 contexts, 1,536 question-pair exposures, pair order,
batch order, 24 optimizer updates, and RNG seeds. Exact prospective tokenization gives 144,780
versus 142,923 causal tokens (1.28% difference) and 23,999 versus 22,430 supervised target
tokens (6.54% difference). Keep the qualified token-mean loss. Do not duplicate ABO examples
to equalize target tokens: that would confound the study with extra semantic and pair exposure.
Record physical tokens and per-update denominators for both arms.

## Frozen readouts

The primary readout uses 128 clean official-test groups selected from the 364 groups that are
both outside the existing query128 panel and disjoint from c32 optimizer training. Selection is
ascending SHA256 of
`["trec-child-interface-sft-followup-v1","primary-new-contract",record_id]`, divided into eight
contexts of 16. Evaluate unchanged c32, full6-SFT24, and ABO-SFT24 through both interfaces on
six new balanced ordered pairs:

1. human being / entity
2. entity / numeric value
3. numeric value / location
4. location / description and abstract concept
5. description and abstract concept / abbreviation
6. abbreviation / human being

These pairs do not occur in continuation training; every category appears once as A and once
as B. The primary readout is 8 contexts x 6 pairs x 3 policies x 2 interfaces = 288 calls.
It tests transfer to new pair parameters and continuation-untouched source groups.

There is no genuinely outcome-untouched eligible TREC semantic holdout in the authenticated
cache. C32 trained on all 5,065 source-TRAIN groups twice, validation was used for selection,
and all 489 clean official-test groups were previously evaluated. The 11 excluded test groups
are contaminated by overlap/conflict rules. Therefore the primary panel is optimizer-disjoint
and query-contract-unexposed, but not outcome-pristine.

Use the existing 128-row, eight-context query panel only as a secondary
development/research-exposed readout on the six trained pairs. Reuse its sealed c32 responses
and scores; generate only the two new policies through both interfaces (192 new calls). Do not
rerun base, unchanged c32, or the already completed host projection.

## Interpretation and metrics

Score strict per-ID A/B/other correctness, exact 16-ID maps, validity/availability, A/B/other
confusions, and prompt/completion tokens. Report paired effects by context and pair, not 768
independent Bernoulli trials.

The central generalization contrast is
`(ABO-SFT24 - full6-SFT24)` on the ABO interface of the primary new-pair panel. Report the
contract interaction by subtracting the same policy contrast on the full6 interface. A positive
ABO contrast on the exposed-pair development panel alone is output-contract adaptation. A
positive contrast on the primary new-pair panel, without a material full6 or clean-group loss,
is evidence for learned query-sensitive pair binding. Improvement on both interfaces is broader
semantic continuation; improvement only in format validity is contract compliance. Always show
both arms relative to unchanged c32 to expose forgetting or generic extra-SFT effects.

Promote to a root-level paired interface test only if ABO-SFT24 improves primary ABO accuracy by
at least 5 percentage points over both unchanged c32 and full6-SFT24, with no more than a
2-point full6-interface loss and no availability loss. Otherwise retire or redesign this
curriculum; the exposed development panel cannot satisfy the promotion rule by itself.

## Compute and provenance boundary

The original 128-update run processed 1.70M causal train tokens in 705.63 seconds. Both proposed
arms total 287,703 causal tokens, so token-linear training is about 120 seconds; model loading,
checkpointing, and two independent jobs should still remain well below 30 minutes. The 480 new
readout calls scale from 192 calls in about 204 seconds, but allow substantial service-switch and
harvest margin. Reserve one A100-40GB for at most three hours: 45 minutes training/setup,
105 minutes readout, and 30 minutes cleanup/recovery. A two-hour completion is expected; four
hours is unnecessary unless infrastructure recovery is separately authorized.

Before implementation, materialize immutable TRAIN/public/gold/pair/seed manifests, authenticate
the c32 adapter and all source hashes in `DATA_FEASIBILITY.json`, prove arm equality for IDs,
contexts, pairs, order, updates, and seeds, and prove primary/development/continuation group
disjointness as claimed. This document creates no READY, producer output, service, or GPU work.

## Alternatives not recommended

A mixed or alternating third curriculum would obscure whether direct-contract supervision caused
the effect and adds a model/readout arm. A token-equalized ABO arm made by repetition changes
semantic exposure. A larger two-epoch continuation risks overwriting the already strong c32
semantics before this minimal contract-binding hypothesis is tested.
