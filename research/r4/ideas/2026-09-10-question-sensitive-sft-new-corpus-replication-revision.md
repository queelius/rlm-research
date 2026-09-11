---
title: New-corpus replication of question-sensitive root SFT
date: 2026-09-10
status: prospective_design_revision_no_implementation
supersedes: 2026-09-10-question-sensitive-sft-independent-order-replication.md
question: Does the metadata-transfer gain reproduce after training on a disjoint set of 128 source questions?
---

# Correction to the order-seed proposal

The previously proposed shuffle-seed replication is not a genuine independent training
realization. The qualified `joint_learning.update` calls `zero_grad` once, traverses all 72
trajectories with each turn scaled by its role mass divided by 72, then clips and calls
`optimizer.step` exactly once. The loaded LoRA has dropout zero. Permuting those 72 terms therefore
changes floating-point gradient accumulation order, not minibatch sampling. It could test numerical
order robustness, but it cannot replicate the scientific training effect. The old note remains as
history and must not be implemented as an independent-seed claim.

# Recommended replication

Train a second fixed-six QS adapter from the identical fixed24 starting checkpoint and fresh Adam,
but replace all eight training contexts with **128 different TREC-train source-question groups**.
Generate the same nine task families per context, capture all **72 teacher trajectories with 72
genuine c32 child acquisitions**, run the same six full-corpus updates, and evaluate the fixed final
checkpoint once on the already frozen 72-question metadata-transfer panel. Reuse its unchanged and
original-QS6 results; rerun neither comparator.

This tests whether the large metadata result—grounded correct execution 12/72 unchanged versus
50/72 original QS6—survives a second training corpus. It is stronger than numerical reorder or a
with-replacement bootstrap because it changes the actual questions and returned child-label maps
while retaining the task generator and optimization recipe.

# Eligibility and selection

A read-only invocation of the original qualified inventory function at
`2026-09-10T21:59:59.134459+00:00` found **373 eligible groups** in the pinned 2,000-group scale
pool after subtracting every group named by 74 current selected/prepared manifest rows. The scan
also found 2,750 used seeds, 7,724 public IDs and 172 native context IDs for collision checking.
This is enough to select 128 groups without relaxation or substitution.

At implementation freeze, rerun that exact named-catalog scan and stop if fewer than 128 remain.
From the eligible set, take the first 128 by `(SHA256([new_namespace, "source", group_id]),
group_id)`. The rule is label-, length-, outcome- and prior-model-output-blind. Freeze the complete
eligible inventory, exclusions, selected sequence, source path/line, dataset revision/license,
scan start/end, and hashes before any teacher call. Never resample a context because of its labels,
gold scalar, capture outcome, or native length.

The groups must be disjoint from the original QS root train, dev and protected 320 groups and every
other named root selection at freeze. They remain TREC-train, c32-optimizer-exposed and broadly
research-catalog-exposed; “root-process-new under the named cutoff” is the strongest allowed claim.

# Frozen training and capture

- Eight new 16-record contexts, with the same `problem.specs("train", context_index)` generator:
  T1/T2, M1/M2, J1/J2, P1/P2/P3. Preserve all 72 regardless of gold, including zeros.
- Use the same public-file interface, class definitions, fixed c32 child, native coding role,
  2048/8192 caps and one independent episode-local c32 call per teacher trajectory. Preserve wrong
  child labels; no gold repair, retries, old-map reuse, or partial-corpus training.
- Freeze a new namespace, record/native IDs, layouts, capture seeds and dispatch order before GPU.
  Collision-check every value against the named catalog. Generated user/weight/layout variation is
  part of this second generator realization, so this is a corpus-package replication rather than a
  text-only ablation.
- Start from exact fixed24 adapter `94022838...`, config `9cab9150...`, state `75b31388...` and verify
  tensor equality. Instantiate fresh AdamW step 0; never load the original QS optimizer/RNG.
- Keep rank 8, 504 FP32 LoRA tensors, learning rate `1e-4`, weight decay 0, clip 1, role masses
  `.45/.50/.05`, current-root-action masks, and exactly six complete full72 updates. Save every
  checkpoint/Adam/RNG/order/corpus link; fixed checkpoint 6 only, with no dev selection.

Teacher capture is **72 real c32 calls**, not 24: the original generator assigns one independently
observed acquisition to each of nine trajectories in each of eight contexts. A missing or invalid
teacher makes the entire training treatment unavailable; it is not silently retried or replaced.

# Fixed readout and decision

Run only the new checkpoint-6 policy on the existing metadata-transfer `FREE_PLAN` SHA
`373addec...`: 72 fixed rows, eight exposed contexts, seeds `988621001..988621072`, fixed c32 child,
identical prompts/files/temperature/caps. Reuse the prior unchanged and original-QS6 arms on those
exact coordinates.

Primary is grounded faithful-and-strict execution on all 72 planned rows. Report availability and
NULL bounds, strict score, acquisition, requested operator/scope/threshold execution, final use of
observed state, faithful child-error failures, zero/nonzero, composed 48, primitive 24, six
operators and eight context clusters. Analysts must inspect actual programs/observations without
executing sampled code.

Treat the training-corpus result as replicated locally if its worst-case grounded-correct
difference from the reused unchanged arm is positive, at least 6/8 context differences are
positive, and at least 24/48 composed rows are grounded and correct. Compare it descriptively with
the original 50/72 QS6 result, but do not claim equivalence from closeness. A pass motivates a new
task-family/model replication; a failure makes corpus dependence the next target rather than
justifying seed rerolls or checkpoint selection.

# Compute envelope

One A100 40GB, sequential stages: 1,500 seconds for serial complete72 capture, 1,200 for load/gate/
six updates/checkpoints, 1,500 for one 72-row readout including service lifecycle, and 120 for
finalization. Total: **4,500 outer / 4,470 owned / 4,320 work**, with 150 cleanup and 30 margin.
Original measured training was about 776 seconds including load/gate; prior complete72 readouts were
roughly 10--13 minutes, while the original serial capture approached 16 seconds per teacher. The
caps are conservative operational envelopes, not guarantees. Record all physical calls and
known/unknown usage.

# Exact code provenance inspected

- `root-joint-state-reduction-sft-v1/joint_learning.py`: SHA-256
  `b5d063afe883d1cbaa49a6b50bfa9d0ca561815fdc2d1617e905724dcb69b4db` (qualified source pin);
  one zero-grad and one optimizer step around the full episode loop.
- `root-operator-diverse-sft-v1/od_train.py`: SHA `69174ab5...`; six full72 calls to that update.
- `root-question-sensitive-sft-v1/prepare.py`: exact source-group inventory and 8×9 generator.
- Original training adapter/config/state: `4d828753...` / `5bb10e33...` / `4c2fab63...`;
  historical comparator only.
