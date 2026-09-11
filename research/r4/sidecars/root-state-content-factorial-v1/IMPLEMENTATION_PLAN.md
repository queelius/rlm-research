# State-content factorial Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax.

**Goal:** Prepare one paired64-endpoint observation/action visibility comparison while the GPU runs leaf96.
**Architecture:** New protocol and input freeze, with narrowly adapted proven restart runtime/collector. Old sources and outcomes remain immutable.
**Tech Stack:** Existing native Python3.12/vLLM/Verifiers environment, CPU pytest, pinned low66c/c32.
**Spec:** DESIGN.md

## Global Constraints

- All16 pre-correction source states; four arms P0V0/P0V1/P1V0/P1V1;64 endpoints.
- Same files/goal/metadata and fresh runtime in every arm; no future/private/gold/readout contents.
- Outer3000/work2700/owned2880/collection2400/startup300/cleanup180 seconds.
- Per-endpoint180s/four workers/native8192 context/2048 output; no full-repo tests or Git mutation.

---

### Task 1: Factorial protocol and source-independent tests

Files: protocol.py,test_protocol.py. Consumes frozen packages and source-state dictionaries.
Produces prompt(goal,files,arm),plan(states),digest(value),null_row(row,reason).

- [x] Create tests asserting identical common files, selective action/observation markers, no package mutation,
  64 unique coordinates,16 shared seeds, exactly four rotations, and missing slots remain NULL.
- [x] Run CPU pytest before implementation; expected import failure.
- [x] Implement exact pure protocol. Example: `assert "OBSERVATION_MARKER" not in prompt("goal",files,"P1V0")`.
- [x] Rerun focused tests; all pass. Checkpoint code plus source hashes; no Git commit.

### Task 2: Freeze actual inputs and reuse proven native entrypoints

Files: study.py,collect.py,owner.py,prepare.py,test_native.py.
Consumes immutable root-artifact-restart-v1 READY,STATES,PACKAGES,SOURCE_CUTS,PUBLIC,HOST_GOLD,
NATIVE_TEMPLATE,BINDING. Produces64 native prompts and exact new output namespace.

- [x] Copy the reviewed restart study/collector/owner via apply_patch with explicit ancestry hashes and
  exact count/deadline/name substitutions. No service-provider rewrites.
- [x] Prepare only the new paired PLAN/PROMPTS; verify all original input/source pins before copying.
- [x] Test actual owner collector_argv roundtrip, all64 native renderer prefixes and canonical setup files
  equal across four arms. Example: `assert len(plan)==64 and len({r["id"] for r in plan})==64`.
- [ ] Run native CPU tests, actual owner verify, then seal READY with code/input/version/seed provenance.
  Checkpoint source and READY, no launch from prepare.py.

### Task 3: MAIN acceptance and GPU handoff

Files: new operations parent PLAN/ACCEPTANCE/handoff, separate immutable outputs/attempt-001.
Consumes freshly verified READY and exact current predecessor identity. Produces bounded run artifacts.

- [ ] MAIN reads all changed scientific/entrypoint code and native test results.
- [ ] Bind coordinator7d329424… to exact current predecessor and new output namespace; prepare acceptance-template.
- [ ] Approve one3000s attempt, privately inherit existing credential, launch accepted waiter.
- [ ] Monitor actual native results/terminal, not memory alone. Independently audit results while next training runs.
