# Approved four-update sidecar implementation plan

Goal: prepare a runnable, CPU-qualified four-update helper-only HF pilot for MAIN review. Fresh original c32 and one fresh AdamW carried across four updates; each update collects32×4 fresh actions from its frozen current policy before any step. Step4 is primary. No GPU launch is authorized here.

Exact files: `config.py` fixes paths/constants/seeds; `core.py` loads sealed HF-v1 rollout/replay/reward/binding functions and HF-v2 decoder activation wrappers; `rng_receipts.py` saves/restores complete RNG snapshots and authenticates group/step commits; `train_four.py` owns the single model/optimizer lifecycle, four update boundaries and checkpoints; `test_four.py` exercises focused CPU behavior; `seal.py` creates training-only inputs, source manifest, CPU_TESTS and immutable READY. Existing `DESIGN.md` remains the detailed approved contract. Generated source/input receipts are `SOURCE_MANIFEST.json`, `inputs/GROUPS.json`, `inputs/TRAIN_GOLD.json`, `inputs/SOURCES.json`; no evaluation inventory is copied.

Global constraints: preserve every sealed source; use only the approved external sidecar; no installs, production branch workflow, automatic resume framework, training-data expansion or evaluation-driven selection. B4/eager/full-prefix/noKV/eval/dropout-off, BF16 base/FP32 LoRA, temperature1, RLOO denominator128, LR1e-5, weight-decay0, clip1 and strict original probability gates are unchanged. Save RNG after every group and checkpoints/lineage after each completed step. Owner3300seconds, external3400seconds, MAIN-only shared-GPU-flock launch.

## Task1 — implementation and CPU qualification (implemented; final seal records verification)

Write focused failing tests, implement the thin orchestration and commit receipts, then run actual tiny-HF/PEFT four-step tests, RNG round-trip and gate/zero-signal no-step tests. Reuse existing tested grammar/replay seams. Freeze only the approved32 training records and host-only gold, plus exact source/model/environment hashes. Produce SOURCE_MANIFEST, CPU_TESTS, a concrete READY command and the step-aware native evaluation artifact interface.

## Task2 — MAIN review and conditional launch (pending MAIN)

Deliver source manifest/READY hashes, test commands/results, report and exact checkpoint/qualification/binding interface. MAIN independently reviews, decides whether current evidence warrants launch, and alone starts the job under the shared GPU flock and3400second outer cap. A completed CPU preparation is not a training or accuracy result. No automatic resume or launch is part of this task.
