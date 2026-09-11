---
title: Independent-order replication of question-sensitive root SFT
date: 2026-09-10
status: prospective_design_only
question: Does the metadata-transfer gain reproduce from the same starting weights under an independently frozen training order?
---

# Recommendation

Run one second six-update QS training realization from the exact fixed24 root adapter, with fresh
Adam state and a new prospectively frozen shuffle seed, then evaluate only that fixed checkpoint 6
on the already frozen 72-question metadata-shift panel. Reuse the panel's existing unchanged and
original-QS6 readouts; do not rerun either comparator.

This is the smallest publishability-oriented check of the strongest local result: grounded correct
execution was 12/72 for unchanged and 50/72 for the original QS6 model after the joint user-name,
weight and threshold shift. It replicates optimization-order sensitivity, not data collection,
training-corpus diversity, model-family transfer, or unseen evaluation.

# What genuinely changes

The original trainer uses `random.Random(SEED + update).shuffle(range(72))` before each full-corpus
update. Its seed was `985731003`. The proposed seed is `995731003`, absent from the named research
store scan ending `2026-09-10T21:56:07Z`. The resulting six 72-example permutations all differ
from the originals (only 0--3 positions coincide per update); their compact-JSON SHA-256 values are:

1. `a7986bb5c3d1afd08faf25c6fb80c3df56624b76afc9b3505aedfed0c115f1ed`
2. `bacb7f1827f0d751b7be244afbae8a88c1c7ac923322f0bffd661893fa00cfc9`
3. `ef77bf88b8beeb166e8801a38fd87bd570d1fc9156d9c5f0b657ca9910a40c0a`
4. `d56586c941dbe97423bac67817a4b67d336585d567432df7f66e44ab365f89f9`
5. `565a5ede1a005f5f83dbf06efd24c5c3ef91dbbf1ce4cde9eb69ac1d9471901b`
6. `aa44ce7bc11cffe7bc9858b0214d5d953a4ebe054a6cf6d459ec7a374289b79d`

This is the meaningful stochastic intervention. The loaded rank-8 adapter has `lora_dropout=0.0`,
and the trainer initializes from existing adapter tensors rather than a newly randomized LoRA.
Consequently, merely changing a nominal model seed while retaining the old six permutations would
not define a credible independent realization. GPU-kernel nondeterminism may add small variation,
but it is not the planned manipulation.

# Frozen training comparison

- Reuse the exact 72 authenticated teacher trajectories and their genuine c32 acquisitions; never
  recollect, repair, filter, or replace child mistakes.
- Start from adapter `94022838...`, config `9cab9150...`, state `75b31388...` at fixed operator-dose
  step 24. Verify tensor equality before training.
- Instantiate fresh AdamW at step 0, learning rate `1e-4`, weight decay 0, gradient clip 1. Keep
  rank 8, 504 FP32 trainable LoRA tensors, and role masses `.45/.50/.05`.
- Apply exactly six complete 72-trajectory passes (432 example exposures, 1,296 root-turn
  exposures, expected 101,424 target-token exposures), checkpointing every update. Only current
  root-action tokens receive loss; all prompts, observations, child tokens, and earlier turns stay
  masked. Missing update 6 makes the treatment unavailable; never substitute update 5.
- Record every example order, corpus hash, initial/final tensor hashes, Adam moments/ordinal,
  checkpoint ancestry, RNG, component losses, tokens, elapsed optimizer/checkpoint time, and peak
  memory. The optimizer must be newly empty; the original optimizer and RNG are provenance only.

The original realization ended at adapter `4d828753...`, state `4c2fab63...`, optimizer
`7f284a0b...`, and RNG `5231b8a6...`. Those are historical comparators, never starting inputs.

# One fixed readout

Evaluate the new fixed checkpoint 6 on exactly the 72 rows in the metadata-transfer `FREE_PLAN`
(SHA `373addec...`), with its existing paired seeds `988621001..988621072`, prompts, modified public
records, and gold unchanged. Use the fixed c32 child `c32de129...`, the same native file interface,
temperature .5, four workers, root 2048/context 8192, and no algorithm card or forced child call.
The existing unchanged and original-QS6 arms on these identical coordinates are reused once.

Primary: manually verified, actually executed requested operator/scope/threshold whose final both
uses the observed child map and is strictly correct, on the planned denominator of 72. Report
composed 48, primitive 24, nonzero/zero, six operators, and eight context clusters; strict score,
acquisition, availability, faithful-but-child-wrong, and unfaithful coincidence remain separate.
Malformed authenticated finals are observed zero; unavailable/unverified endpoints are NULL with
worst-case paired bounds. Analysts do not execute sampled programs.

Support for an independent-order replication requires all of:

- the worst-case grounded-correct difference versus the reused unchanged arm is positive;
- grounded-correct gains are positive in at least 6/8 context clusters; and
- at least 24/48 composed questions are grounded and correct.

Also report the new model against original QS6 descriptively, but do not use closeness as an
equivalence test or choose between checkpoints. Failure revises the result toward
training-order-sensitive local fit; success promotes a new-training-corpus or task-family
replication rather than another seed on the same 72 trajectories.

# Compute and limits

One A100 40GB, sequential training then readout. The original six-update training used about 776
seconds including load/gate and under 10GB peak during its measured gate; comparable 72-endpoint
readouts have taken roughly 10--13 minutes and inference approaches the 40GB allocation. Budget
`3300s outer / 3270s owned / 3120s work`: 1200 training, 1650 readout including startup/release,
270 finalization, plus 150 cleanup and 30 outer margin. These are pragmatic caps, not runtime
guarantees. Preserve all physical requests and per-field known/unknown token usage.

All 72 evaluation questions reuse eight research-exposed contexts and the prior metadata-shift
intervention. The training corpus is also identical to the first realization. Contexts, not nine
questions within each context, are the meaningful clustered units.

# Source anchors read

- Original result: `analyses/root-question-sensitive-sft-live-2026-09-10/REPORT_MAIN.md`, SHA
  `6245e955...`; semantic audit SHA `43b368dc...`; training audit SHA `6f44bbdc...`.
- Trainer composition: `root-question-sensitive-sft-v1/qs_train.py` SHA `e38c5e78...`, qualified
  shuffle trainer `root-operator-diverse-sft-v1/od_train.py` SHA `69174ab5...`, and recipe SHA
  `d53f2fd6...`.
- Metadata panel design/input: metadata-transfer READY SHA `21450d06...`, `FREE_PLAN.json` SHA
  `373addec...`, public SHA `e8915336...`, gold SHA `3b874fff...`.
