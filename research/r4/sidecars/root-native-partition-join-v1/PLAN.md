# Native Join Implementation Plan

> For agentic workers: execute inline with the executing-plans skill; no subagents are authorized. Steps use checkboxes for review.

Goal: deliver CPU-qualified, executable READY for the approved48-root experiment without launching it.

Architecture: pure protocol/world/scoring module; a pinned released-base service adapter; a native task/tool-inventory seam; acquisition plus four-worker root collector; a bounded owner and additive preparation/seal driver. All authored files stay in this sidecar.

Tech stack: existing prime-rl Python3.12, verifiers native ACP RLM/IPython, qualified an27 rootless runtime, Qwen native renderer and released-base vLLM service.

Spec: DESIGN.md. Global constraints: 48 planned roots,24 model extractions,4 worlds,2 paired seeds;1800-second outer cap; strict whole native final; no source repairs, retries, model/GPU/service/queue action during preparation.

## Task1 — independently testable protocol

- [ ] Create test_protocol.py first. Assert48 rows,8 six-cell paired blocks,16 direct rows and record/partition conservation; independently reconstruct A/B sets and cross/co-located properties. Assert malformed/duplicate/unsorted final rejection, missing-final NULL, acquisition failures not host repaired.
- [ ] Run `python -m unittest -v test_protocol`, retain expected missing-module failure.
- [ ] Create protocol.py exposing `worlds()`, `plan(worlds)`, `oracle(records, products)`, `extraction(raw, chunk)`, `score(content, gold, customers, available=True)`, and representation rendering.
- [ ] Rerun the focused tests; resolve only material contract defects.

## Task2 — native and owned execution seams

- [ ] Create test_native.py and test_owner.py with real native request rendering, task setup bytes and actual CLI composition; stub only model transport and process launch.
- [ ] Run each failing test before adding its implementation.
- [ ] Create study.py/service adapter with qualified module namespaces; native.py for task and private tool-inventory override; collect.py for actual acquisition/native roots and planned NULLs; owner.py for1650/1770/1800 clocks and exact attempt output binding.
- [ ] Test the genuine native authored fixture, no-tool blocked execution, pair request/file equality, source-failure direct continuation and collector cancellation inventory. No generated code fixtures: only human-authored deterministic test programs.

## Task3 — prepare and seal

- [ ] Create prepare.py freezing worlds/host-only gold/plan/static extraction bodies/source pins and CPU-rendering proofs.
- [ ] Run focused protocol/native/owner tests and source syntax qualification; preserve failures additively.
- [ ] Write READY.json only after source closure, exact owner→service→collector entry and native pair qualification pass. Verify manifest freshly and send READY/source paths to MAIN for acceptance; do not launch.

No Git branch/commit/worktree changes: MAIN explicitly selected a new external sidecar as the isolated research workspace. No environment installation or broad baseline tests, per task scope.

Execution status: Tasks1–3 implementation and qualification are complete.18 focused tests passed (CPU_TESTS_FINAL_V2.json); qualification-007 independently reran the actual native source-matching root/child/tool/disabled-final fixture in40.841s. READY_V2.json is the acceptance handoff; READY.json is a rejected draft retained unchanged. Neither is evidence of a scientific model run. Checkbox steps above retain the original pre-implementation plan rather than rewriting its history.
