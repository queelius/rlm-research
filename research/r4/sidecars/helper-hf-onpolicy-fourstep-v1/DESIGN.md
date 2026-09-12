# Uniform four-update HF helper pilot — conditional preparation

Status: concrete design for MAIN review; not an accepted GPU launch. Current one-step native readouts remain the prerequisite for the experimental decision. This sidecar does not continue the v2 checkpoint or its unavailable original sampling-generator state.

## Question and fixed design

Does extending the same exact-policy helper objective to four updates change local category accuracy compared with unchanged c32, when training remains restricted to the original32 development records? Start once from original c32, create one fresh AdamW optimizer, and carry its moments through exactly four update opportunities. Load the base/adapter once, install the already CPU-verified non-reentrant decoder checkpoint wrappers once, and keep model/layers eval with dropout off throughout.

Every update visits all32 development groups in a separately seeded permutation and samples four fresh HF actions per group from that update's frozen current adapter. All128 actions are collected before replay/backprop. Never carry actions across an optimizer update. Use unchanged temperature1, B4, eager attention, full prefixes, noKV, ordered XGrammar masks, max64new tokens, sequence-sum RLOO/all128 denominator, LR1e-5, weight-decay0 and global gradient clipping1. The same original token1e-5, sequence1e-4 and first-four full-support1e-5 gates remain mandatory. The first-four audit positions refer to the saved permutation, not fixed source IDs.

Explicit new seeds: global/model RNG202609120700; CUDA categorical sampler202609120701; permutation seed202609120800 plus the one-based update number. A dedicated Python `Random` instance generates each permutation, so changing permutation order does not consume the categorical sampler stream. The sampler is initialized once and carried across updates. Save its state together with global Python/NumPy/Torch/CUDA states after every completed group.

One fresh AdamW instance is created before step1; only gradients are zeroed between updates. All32 replay groups must qualify before the one step for that update. A failed gate, nonfinite gradient, zero mixed batch or zero net gradient stops the run without applying the current step, preserving earlier completed checkpoints. There is no denominator change, selective retention of mixed groups, momentum-only extra step, automatic temperature escalation or automatic restart.

## Existing seams; minimal new orchestration

Reuse sealed `helper-hf-onpolicy-v1/train.py` functions `rollout_group`, `replay_group`, `local_reward`, `changed_binding` and their `policy.py` primitives. Reuse only `install_eval_checkpoints` from sealed HF-v2 `runner.py`, loaded through a unique import name. Do not call either prior whole-run driver, replace their files, or mutate global source roots. New orchestration owns model/optimizer loading, four update boundaries, RNG commits and checkpoint metadata. The native grammar worker remains the pinned v1 worker under its existing environment. No installs or model reload between updates.

Training inputs contain only copied original32 `GROUPS.json` and `TRAIN_GOLD.json`, plus their source checksums. No `EVAL_PUBLIC`, protected128, TREC-test, AGNews records, predictions or labels are passed to the training driver or group selector. Provenance includes original c32 adapter/config, model revision assets, relevant core source files, environment/package source pins and the fixed source binding. Any later holdout audit is separate from the training input loader.

## Artifact matrix

| Scope | Artifacts and meaning |
|---|---|
| Sidecar | `READY.json`, `CPU_TESTS.json`, `inputs/GROUPS.json`, `inputs/TRAIN_GOLD.json`, `inputs/SOURCES.json`; immutable code/source/environment/input closure and launch command. |
| Attempt | `START.json`, `ACTIVATION_STORAGE.json`, atomic `PROGRESS.json`, final `RESULT.json`/`FAILURE.json`; overall3300second owner cap and3400second outer timeout. |
| Each update | `updates/update-000N/START.json` with parent checkpoint/state and exact32-group permutation; `START_RNG.pt`; aggregate `COLLECTION.json`; `QUALIFICATION.json` before any step. |
| Each group | Existing `ROLLOUT.json`, `MASKS.npz`; `AFTER_GROUP_RNG.pt`; then immutable `GROUP_COMMIT.json` pinning all three, group position, frozen parent adapter identity and sampler seed namespace. Existing `REPLAY.json` remains bounded token-backward evidence. |
| Each successful update | `checkpoint-000N/adapter_model.safetensors`, config, optimizer state, full RNG state and `state.json`; `EVAL_BINDING.json`; final `STEP_COMMIT.json` authenticating checkpoint/state/qualification/binding and cumulative optimizer stepN. |

Checkpoint state records both step and cumulative optimizer count honestly asN, parent-state hash, starting original c32 identity, input/READY identity, per-step and total adapter delta, current collection/source hashes, per-update gradient norm, cumulative time/peak memory, all32 qualification result hashes and all504 LoRA optimizer parameter names. A step4 checkpoint is never relabeled step1 for an older evaluator. The current one-step evaluator is not modified; any four-step native successor must explicitly authenticate the stepN lineage and carried optimizer state.

Group commit ordering is rollout+mask complete, reward/advantage derivation complete, after-group RNG saved, hashes computed, then commit marker. An interrupted group without its commit marker is not a resumable completed group. Likewise a checkpoint without a valid final step commit is not promoted. All historical output directories are preserved.

## Bounded resume contract

This initial owner runs only into an unused attempt directory and does not implement an automatic retry/resume framework. Saved receipts make a later additive, separately reviewed resume possible: load the last committed checkpoint and optimizer (or original c32/fresh optimizer for step1); verify the next update's committed group prefix against its frozen parent and all input/core hashes; restore the last complete after-group sampler/global RNG; sample only the missing groups; then replay all128 from clean gradients and pass the original gates before one step. Partial backward gradients are never resumed. Replayed actions from a prior adapter are never accepted for a later adapter. No use of HF-v2's restart RNG snapshot as original sampling continuation is permitted.

## Readout and selection boundary

Step4 is the predeclared primary final checkpoint. Save every step for recovery and provenance. An optional fixed learning curve at steps1/2/4 may be declared before reading its outcomes, but is descriptive and cannot select a best checkpoint. A stop before step4 means the primary run is incomplete, even if an earlier checkpoint exists. Do not substitute the last successful checkpoint without reporting the stop.

The newly frozen256 TREC-test/AGNews panel remains excluded from all training, prompt difficulty, stopping and checkpoint selection. Reusing that panel after the current one-step experiment is explicitly adaptive evaluation reuse, not untouched confirmation. The familiar128-record readout remains separately labeled prior-SFT-exposed. No root-performance or base-pretraining-unseen claim is made.

## CPU qualification before READY

Thin actual tiny-HF/PEFT tests should run a miniature multi-update loop and prove four successive optimizer steps with carried moments; each new collection must be taken before that step, and replay must match the current—not original—policy. Reuse actual grammar IPC/EOS checks already passed in sealed core tests; add only a short actual-grammar mixed-advantage replay through the four-step orchestration seam if needed. Test group RNG save/restore reproduces the next categorical samples exactly on CPU, and that changed input/parent/commit hashes prevent reuse. Gate failure or uniform rewards must leave the current parameter/optimizer step unchanged. READY records all tests, strict constants, environment versions, input inventory, artifact schema and the unchanged3300/3400 caps. MAIN reviews READY before deciding whether to launch.
