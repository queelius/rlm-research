# Equal-row root interface SFT Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans after MAIN approval, inline with focused TDD. This document does not authorize implementation, agents or GPU work.

**Goal:** Implement the single weighting comparison in DESIGN.md: one new equal-row four-step SFT root and fresh48 paired readout against existing token-normalized final4.

**Architecture:** Keep all original frozen sources and data. A small private training wrapper reuses the authenticated original run/load/Adam/checkpoint loop, changing only update weighting and new provenance identity. Reuse the qualified two-alias local native collector/lifecycle with an explicit arm→checkpoint binding and fresh-plan overlay; no new runtime framework.

**Tech Stack:** Existing Prime native interpreter and existing training venv, PyTorch/PEFT, rootless local image8cfe, existing WireTrace/typed-child hooks.

**Spec:** [DESIGN.md](DESIGN.md).

## Global constraints

- Proposal only until MAIN approves; parent alone owns acceptance, GPU, process/service lifecycle and shared queue.
- Exact32 frozen rows/473210 start/training seed981284002/order/LR1e-4/four updates; only scalar loss weighting changes.
- No grammar, prompt, terminal cue, data, API, sampling budget or final-checkpoint selection changes.
- Fresh24 evaluation coordinates per arm; exposed8 context clusters; no old outcome pooling.
- Work3180/inclusive3300/outer3330s; training600/process900, readout900 each, four workers.
- All source/data/run outputs additive under this sidecar; no edits to frozen prior sidecars. No new installs, broad tests or host execution of generated code.

## Task 1: Pin the one loss delta and immutable input binding

Files to create after approval: study.py, train.py, tests/test_loss.py, RECIPE.json, INPUTS.json.

- [ ] Authenticate the original train.py b333d787bde61b9f42cd5bfba426dd3909d5733a4ea55ae693f547ca429597a7, source/data closure and both named checkpoint lineages once.
- [ ] Write a two-row unequal-length RED fixture. For row counts1 and3 and CE sums2 and12, token mean must be3.5, equal-row mean3.0; row masses must be1/2 each. Verify prefix/observation/child gradients remain zero and all target counts include only labels[1:] != −100.
- [ ] Implement only the effective-batch scalar weighting seam: row loss contribution = summed_current_action_CE / (len(rows)*shifted_target_count). Keep clip1, Adam and forward/microbatch order unchanged. Keep a separate token-mean monitor and all actual floating coefficients/weighted contributions; reject zero/nonfinite denominators or loss.
- [ ] Privately reuse original run/verify/checkpoint helpers. Override verify only to append the new loss/source identity after original authentication; never label the new checkpoint with the old intervention identity alone. No pretrained-model initialization change.
- [ ] Run one tiny real CPU optimizer/masking/save-state test and coefficient checks; do not optimize a real model on CPU or GPU. Freeze exact four batch row IDs against WEIGHTING_AND_SEED_AUDIT.json; test fresh optimizer/cursor0 and checkpoint4 fixed selection.

## Task 2: Fresh paired plan with unchanged physical prompts

Files to create after approval: readout.py, launch.py, tests/test_readout.py, prepared/PLAN.json, prepared/PROMPTS.json, PREPARED.json.

- [ ] Write RED fixtures for source-coordinate pairing, fresh seed mapping, exact arm binding, and a deliberately changed child/model/first-prefix rejection.
- [ ] Build24 coordinates from frozen EVAL_PLAN_FINAL.json: preserve every task/context/family/repeat and map only the declared fresh seed by stratum/order. Copy exact frozen prompt IDs with source-coordinate crosswalk, rather than reconstruct a different tool serialization. Freeze48 arm coordinates and the equal_row→global_target_token phase order.
- [ ] Adapt the existing native collection seam privately to accept this exact plan and one of two authenticated fixed-final checkpoints. Both actual services expose only that root and unchanged c32de. Use root-interface-sft-local-runtime-v1 configure_interface and the accepted PID/start/UID/PGID/descendant release helpers unchanged.
- [ ] Before calls verify actual /models and endpoint adapter/config/base/binding; preserve pretransport typed evidence, native sampled IDs/logprobs/finish reasons, raw episode and graph. Sampling/protocol semantics unchanged. Never synthesize a descriptor or alter old endpoint metadata.
- [ ] Keep one shared deadline through training, both services and cleanup. Per-case raw writes and terminal/STOP status distinguish unavailable, completed malformed, timeout and unrun. Release owned services before final independent CPU analysis.
- [ ] Run focused plan/binding/parser/cap fixtures and a CPU-only composed namespace/physical-prefix check. Reuse the already qualified rootless/native seam; no extra model probe is required merely to publish CPU readiness.

## Task 3: Source seal and parent handoff

Files to create after approval: RUNBOOK.md, READY.json; later parent-owned output outputs/attempt-001.

- [ ] Check that exact32 row bytes, four batches, training seed and all named constants match the original except loss identity. Freeze new source hashes plus baseline weight closure and coefficient ledger; no placeholders in executable binding.
- [ ] Publish READY last with exact parent launch argv, real interpreters, caps, fixed output and source closure. Parent independently reads the small source and freezes acceptance before launching.
- [ ] Independently audit terminal new training/result and fresh readout once outside GPU lock: actual coefficients/sums/row counts/gradients/deltas/Adam cursor; strict24 paired task metrics, context clusters, format/copying/coverage, nulls and physical cost. Do not promote diagnostics to reward or treat a same-seed rerun as deterministic.
- [ ] Stop at the fixed final4 and sealed48 readout. Any next data intervention or seed replication is a new MAIN decision, not an automatic extension.

Implementation stop here: only DESIGN/PLAN and read-only coefficient/seed evidence are currently authored.
