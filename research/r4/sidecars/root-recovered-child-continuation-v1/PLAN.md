# Recovered Child Exclusion Continuation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. No subagent or GPU delegation is needed.

**Goal:** Prepare an immutable exclusion-only continuation from actualstep3 through originally declaredstep8 and selection/transfer.

**Architecture:** `native_amendment.py` preserves the original exporter result while adding verified exclusion metadata and rebuilding its group; `train.py` reuses the original trainer with an explicit new native-verifier entry point; `driver.py` owns a fresh3h lifecycle and immutable prior references. Original campaign modules are read-only imports.

**Tech Stack:** Existing Python3.12 native/Prime and HF-training environments; standard library; original Verifiers physical graph; original torch/PEFT trainer only at future parent launch.

**Spec:** [DESIGN.md](DESIGN.md).

## Global constraints

- No V2 source/output/STOP mutation; no GPU calls during preparation.
- Exactly29 old round04 admissions, no new recovered-episode training credit.
- Exact original plans, fixed c32de child, step3 Adam/RNG, loss/guards/selection retained.
- New10800s budget starts only at future launch; checkpoint after every actual update.

## Task1: Reclassification and prepared export

- [ ] Add `test_amendment.py` with a regression that rebuilds actual round04 and requires no false integrity failure,29 admitted IDs unchanged and endpoint0 distinct from unobservable null. Run against the old `campaign_native.rebuild_export` before the new facade exists; expect the observed integrity entry to fail the assertion.
- [ ] Implement `native_amendment.rebuild_export(attempt)` around original `rebuild_export`; add strict `verify_failed_call(call,audit,binding,seed)` and whole successful-graph replay. Every old row field remains equal; attach only `admission_metadata`.
- [ ] Add focused rejection tests by mutating the actual failed-call fixture in memory: alias, hash, depth, HTTP status, missing ID, claimed completion, wrong prompt length; retain fatal original unknown failures.
- [ ] Run actual CPU reclassification and seal `prepared-round04/{EPISODES,GROUP,MANIFEST}.json` plus equality/admission report after source freeze.

## Task2: Verified continuation and exact trainer dispatch

- [ ] Add CPU tests for original round04 reuse, pending steps4..8, validation4/6/8, original prior0/2 selection, new launch deadline and no duplicate checkpoint update.
- [ ] Implement `driver.py prepare|verify|run|resume` and frozen `AMENDMENT.json`/`PRIOR.json`; implement original-policy authentication using actual checkpoint/commit helpers without calling old mutating coordinator recovery.
- [ ] Implement `train.py` as a wrapper around original `campaign_train.train`; its authenticated native proof command must route only the exact expected old verify invocation to `native_amendment.py verify-export`, and add continuation identity to the saved training input binding.
- [ ] Retain lifecycleV2 owned process cleanup and exact generation/checkpoint logic; new output contains only referenced prior stages and new future artifacts.

## Task3: Focused qualification and READY

- [ ] Run native/export verification and trainer CPU preflight with CUDA hidden; qualify inherited lifecycle tests and a tiny CPU persistent-Adam/recovery test if its seam is used, not a broad suite.
- [ ] Verify source/spec and actual prior input hashes, exact29-row equality, source path map, and no unfinished old stages/checkpoints. Preserve original STOP.
- [ ] Publish `QUALIFICATION.json`, README commands and `READY.json` last. Parent review/launch is the handoff; no automatic GPU start or old branch integration.
