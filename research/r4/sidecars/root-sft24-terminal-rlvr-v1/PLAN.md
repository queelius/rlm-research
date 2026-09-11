# SFT24 Terminal-RLVR Warm Start Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CPU-qualified, MAIN-launch-only eight-window terminal-RLVR campaign starting from exact operator SFT24, followed by a fixed paired composition96 readout.

**Architecture:** A new isolated namespace composes the sealed QSR native collector, exporter, and numerical trainer. It changes only the starting root, fixed eight-window plans/current clarified questions, and composition readout data; a new owner applies hard shared clocks, bounded cleanup, and raw disk-union accounting.

**Tech Stack:** Python 3.12, existing an27 native runtime, qualified QSR TIS/PPO trainer, Qwen3-4B plus rank-8 LoRA, pytest.

**Spec:** `../../ideas/2026-09-10-sft24-terminal-rlvr-warmstart-design.md`

## Global constraints

- Exactly eight training windows, 192 planned episodes, fixed c32, strict terminal reward, and no shaping, refill, forced recursion, retries, or outcome-selected checkpoint.
- Exact SFT24 adapter `94022838…`; fresh RL Adam0 distinct from SFT step24.
- Exactly 96 new-seed readout endpoints over all 48 frozen composition questions.
- 10,800 s outer / 10,680 owned / 10,500 work; reserve 5,100 s final and cap training side at 5,400 s.
- MAIN alone launches GPU work.

---

### Task 1: Frozen data and lineage

**Files:** Create `warm_study.py`, `warm_prepare.py`, `test_inputs.py`, and `inputs/*.json`.

**Interfaces:** Produce `fixed_start()`, `candidate_plan(window)`, `data()`, and unified training/readout task tables consumed by all later components.

- [ ] Write failing tests for exact SFT24 hashes, fresh-RL-step separation, training00–07, 192 unique fresh coordinates, six-cell balance, 3/21 zero/nonzero groups, composition48 byte identity, paired96 readout, and integer seed collision scans.
- [ ] Run the focused tests and confirm missing modules/functions fail.
- [ ] Implement deterministic input construction and source receipts without reading composition outcomes.
- [ ] Run the focused tests and confirm they pass.

### Task 2: Native collection, export, and numerical training composition

**Files:** Create `warm_native.py`, `warm_common.py`, `warm_collect.py`, `warm_export.py`, `warm_train.py`, `test_native.py`, and `test_training.py`.

**Interfaces:** Preserve QSR `make_task`, `exact_turns`, export authentication, mixed-group admission, root-only masks, and TIS/PPO guards while accepting the new frozen namespace and fresh RL cursor 0–8.

- [ ] Write failing tests for exact current clarified first prefixes, gold mutation invariance, original native IDs/logprobs, c32 role binding, complete24-only admission, no-op cursor behavior, and SFT24→fresh-Adam generation identity.
- [ ] Run them and confirm failures arise from absent composition code.
- [ ] Implement the smallest pinned namespace adapters around QSR sources; keep numerical source bytes unchanged.
- [ ] Run the focused tests and confirm they pass.

### Task 3: Hard-clock owner and complete accounting

**Files:** Create `warm_owner.py`, `test_owner.py`, and `test_service.py`.

**Interfaces:** `execute(output)` attempts fixed windows while preserving final reserve, selects only the last committed RL checkpoint, attempts both final arms, releases every service, and writes planned inventory plus full raw-cost union.

- [ ] Write failing tests for 5,400/5,100 shared-clock boundaries, ≤30-second cleanup, continuation after ordinary no-op/failure where safe, all checkpoint/no-op cursors, all192+96 NULL slots, and REQUEST/RESPONSE/RESULT/FAILURE/physical accounting.
- [ ] Run and confirm the owner contracts fail before implementation.
- [ ] Implement the owner without copying QSR's broad cleanup alarms; preserve partial raw artifacts and separate response, native-final, and admission counts.
- [ ] Run and confirm owner tests pass.

### Task 4: End-to-end CPU qualification and immutable READY

**Files:** Create `test_composition.py`, `seal.py`, `CPU_REPORT.json`, and `READY.json`.

**Interfaces:** Verify actual owner→service→collector→export→trainer arguments and stop before external process/model execution.

- [ ] Write failing intercepted-process fixtures that require the real service configuration, exact first prompt, exporter replay, trainer group/generation inputs, and paired readout binding.
- [ ] Run and confirm the fixtures catch incomplete namespace or runtime composition.
- [ ] Fix only demonstrated composition seams, then run all focused tests with GPU visibility empty.
- [ ] Seal transitive source/input/model/checkpoint pins, exact owner/verify argv, test output, and `CPU_READY_NOT_LAUNCHED`; run a fresh verify and report hashes to MAIN.
