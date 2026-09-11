# Published RLM8B Reference Implementation Plan

> Agentic execution: use executing-plans inline. No subagents, GPU launch or active-source edits are authorized.

**Goal:**48 immutable paired actual historical-RLM endpoints, with safe isolated execution and native/physical provenance.

**Architecture:** Historical official RLM runs inside the qualified image; a small Unix-socket client talks to an outside authenticated native recorder. Existing allocation service ownership is reused through explicit aliases. The two full-weight8B policies run sequentially, no LoRA and no fallback final request.

**Tech stack:**Host Python3.12.12/worker Python3.11.16, pinned historical official scaffold, qualified rootless Podman/image, vLLM0.28, existing native tokenizer, stdlib Unix HTTP transport.

**Spec:**../../ideas/2026-09-10-published-rlm8b-intended-scaffold.md, SHA57c98ded0039a0bb49565d602a654f48b3c2c0c2a223f1f8608be16e04e23273, approved by MAIN. Earlier design-only status is historical; CPU implementation is now approved. No READY/acceptance implies GPU launch permission.

## Global constraints

24tasks/policy,all8readout04–11,23nonzero+1zero.3600outer/3330work/3480owned;2×1620policy including release+90finalization;150cleanup+120outermargin.12root turns/36children/48physical calls/120s endpoint/two endpoints. Root8192child4096/context32768/maxseq2. Same released template, no guided grammar/forced acquisition/gold maps. SDK retries0. Root+leaf weights change together. Source and runtime ancestors stay unchanged.

Main identified seed collision in the approved design. An additional candidate981671xxx also occurs in an older calibration artifact. Implementation uses master2026091001/task2026091101–124; the exact prepared-source inventory scan returned no matches before this declaration. Save its receipt before seal. No task or source selection changes.

## Task 1 — Frozen source/task/interface data

Files:rv_study.py,rv_protocol.py,prepare_inputs.py,paper_prompt.py,qualify_inputs.py,inputs/,test_protocol.py.

- [x] Test literal three-operator truth, exact48coordinates and label-mutation prompt invariance; malformed strict0 versus unavailable NULL.
- [x] Materialize paper2512.24601v2 AppendixC full base prompt+8Bdiff, save raw/source receipt; no default historical prompt substitution.
- [x] Use `plan()`→48coordinate dictionaries,`task(row)`→public context/query,`score(final,available,gold)`→strict result; freeze unchanged original files and public tokens.
- [x] Verify new seed inventory and no selected-data changes; preserve all23nonzero+1zero.

## Task 2 — Actual isolated historical worker

Files:worker.py,container_runner.py,test_worker.py,test_native_worker.py.

- [x] Test fake-provider actual context→child→observed result→FINAL/FINAL_VAR; assert strict result and physical evidence, not only imported names.
- [x] Read historical execution path before running it. Implement exact custom prompt and explicit official module import in fresh container.
- [x] Run qualified wrapper/image with read-only source/task mounts, no network/home/project/secrets/model mounts, ephemeral state and only a Unix inference socket.
- [x] Client uses outside collector for fixed sampling/seeds/caps/raw checkpoints; no fallback completion. Prove actual worker cannot read the host canary and gets genuine expected child output. Do not execute sampled code in host/auditor.

## Task 3 — Native collector and composed owner/service

Files:collect.py,service.py,owner.py,test_entry.py,test_native.py.

- [x] Tests intercept actual vLLM Popen beneath service/config/descriptor composition for both exact weight paths, native template, inherited assigned GPU; collector remains CPU.
- [x] Authenticate raw prompt/output token and text agreement with no salvage; preserve all physical attempts and one row per planned coordinate.
- [x] Owner preserves policy2 reservation after ordinary policy1failure, stops later phases on MAIN cancellation, releases each service/container, and records all48 planned NULLs before startup. No existing attempt reuse.

## Task 4 — READY and CPU handoff

Files:create READY.json,CPU_REPORT.json,IMPLEMENTATION.md and allocation5780/published-rlm8b-implementation.md.

- [x] Focused16tests passed18.67s, with real isolated fake-provider fixtures and exact composed owner/service/GPU environment interception.
- [ ] Finish exact source/data/model/template/runtime pins and actual owner verify CLI; READY records completion.
- [x] Report changed seeds, historical-vs-publication scope, native mapping-to-flat-token correction, dependency qualification, failed red tests and preserved earlier fixtures.
- [x] No broad suite, GPU fit test, current queue mutation, source cleanup or automatic reroll.
