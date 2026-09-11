---
id: trec-child-interface-sft-followup-v1
status: prospective_cpu_prepared
date: 2026-09-10
planned_train_updates: 48
planned_readout_calls: 480
---

# Matched TREC child-interface continuation SFT

Test whether direct A/B/other continuation teaches c32 to bind a requested runtime pair,
versus merely learning an output contract. Two arms start the exact c32 adapter and receive
the same 1,536 authenticated source-TRAIN groups, 96 contexts of 16, six cyclic pairs, order,
seeds, 24 updates, LR5e-5, and fresh AdamW/RNG. Full6 emits a complete canonical-six map;
ABO emits a complete A/B/other map. The intervention is an honest bundle: output instruction,
guided JSON vocabulary/schema, and target strings differ. It is not a target-token-only effect.

Use microbatch1/accumulation4, token-normalized assistant-only loss, FP32 rank8 LoRA over the
frozen BF16 base, clip1, and checkpoints with adapter/config/Adam/RNG/cursor at updates
6/12/18/24. The endpoint is true completed update24 for each arm, never a best checkpoint.

Primary readout: 128 clean official-test groups outside query128, eight contexts, and six new
balanced ordered pairs. Evaluate unchanged c32 plus both continuations through both interfaces
(288 calls). Secondary development readout: the existing research-exposed query128 panel and
trained pairs, reusing sealed c32 results/host projection and generating only both continuations
through both interfaces (192 calls). Seeds are identical within every paired context/pair block.
Report strict accuracy, exact maps, availability, A/B/other supports/confusions, balanced
accuracy, paired effects, and full6-vs-ABO interaction.

Authenticated empty or malformed finals are observed failures with zero correctness. Missing,
unreturned, or unauthenticated results are NULL: report strict and balanced-accuracy bounds and
no NULL-contaminated balanced point estimate. Reject unknown native finish reasons.

Only 125/128 development rows meet the clean split. The three split-ineligible cases are:

- `q008f41f6bc63`, “What are the twin cities?”: official-train overlap with coarse conflict
  (test LOC versus train DESC).
- `q58ee62170525`, “What are amphibians?”: official-train and OOLONG validated-pool overlap.
- `q27d11599d7c8`, “What does CPR stand for?”: official-train and OOLONG validated-pool overlap.

They remain optimizer-disjoint because c32 used the filtered source-TRAIN partition, but they
are not split-eligible. Preserve them in the development panel to maintain its sealed identity.
No eligible cached TREC semantic holdout is outcome-pristine: all source-TRAIN groups trained
c32 twice, validation selected c32, all 489 clean test groups were evaluated, and 11 excluded
test groups violate overlap/conflict rules.

One MAIN-assigned A100-40GB has a 10,800-second hard cap: 2,700 seconds training/setup, 6,300
seconds readout, and 1,800 seconds cleanup/recovery. Every native request/response/result and
every six-update checkpoint is durable. No retry, reroll, output repair, outcome-based subset,
or GPU launch is authorized by CPU preparation.
