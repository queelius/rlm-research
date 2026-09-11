# Root warm-start reference implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline; MAIN prohibits subagents and owns launch. Checkboxes track independently testable deliverables.

**Goal:** Prepare the approved three-fixed-root24 native diagnostic without launching it.

**Architecture:** Isolated source namespace over qualified QSR native task/capture and the unchanged an27 two-LoRA owner/service. Each phase uses one fixed root plus c32; no new routing protocol. New protocol constructs exactly eight source-pinned blocks; independent native capture preserves raw attempts and finals.

**Tech Stack:** Existing Python3.12 native environment, native verifiers/renderer, immutable an27 lifecycle, JSON artifacts, focused pytest.

**Spec:** ../../ideas/2026-09-09-root-warmstart-reference-feasibility.md and MAIN approval; DESIGN.md carries the exact implemented contract.

## Global constraints

Only this sidecar and allocation5780 report may change. No GPU/services/locks/queue, installs, old artifact edits, sampled-code execution, new base binding or hidden role/prompt changes. Pause on MAIN record-interface relay. 24 roots;857/efab/66c;4 contexts;8 paired blocks;fresh one seed/block. Explicit2048/8192,4workers,120s episodes.1800outer/1650work/1770owned;3 phases≤480 including startup≤180 and collection≤300;release≤90. All slots planned before startup.

## Task1: Exact protocol and fixed binding

Create `study.py`, `protocol.py`, `test_protocol.py`, `DESIGN.md`. Test first: eight selected blocks/24 root rows, exact files and all-only wording delta, identical paired seeds, independent scalar oracle, strict0 versusNULL,857/efab/66c+c32 exact path/hash binding. Run `python -m pytest -q test_protocol.py` to see missing implementation fail; implement only these contracts, rerun. Produce `build()` mapping inputs and `binding(arm)` for collector/owner.

- [x] Protocol/binding test-first and green.

## Task2: Native collector and clock owner

Create `native.py`, `collect.py`, `owner.py`, `test_entry.py`, `test_collect.py`, `test_lifecycle.py`. Tests must execute `owner.collector_argv` through actual collector parsing and exact paths; controlled external launch stub must exercise actual qualified wrapper entry. Check `phase_deadlines(start, work)` never exceeds480/180/300/work and release90/owned. Test invalid/NULL finals and attempted/returned cost separately. Native task must verify actual records/context/query file bytes and first messages/tools/prompt IDs; explicit2048 outgoing tokens. Reuse exact trusted-depth routing and typed children; no bootstrap/root override needed. Native authentication uses qualified full-branch capture, not last-record guessing.

- [x] Native/collector/owner focused red-green checks.

## Task3: Source preparation, actual authored native fixture, closure

Create `prepare.py`, `qualify_native.py`, `test_native.py`. `prepare.py inputs` writes immutable inputs once and computes zero/bestconstant distributions before outcomes, exact selected group manifest, native prefixes, and bounded seed-collision receipt. Run one CPU-authored real native3-call fixture (root→typed c32 child→root final), with no sampled code. Confirm actual root/child aliases, typed child grammar, native prefixes, file contents,2048 root cap, and complete branch identity. Run only focused sidecar tests and actual owner verify. Seal READY after source/input/test/fixture closure, canonical JSON write-read identity check. Final handoff gives hashes and MAIN-only command; do not launch.

- [x] Inputs/native fixture verified:24 prefixes, zero/bestconstant4/8, actual authored3-call native proof.
- [ ] Focused tests and READY seal; allocation report sent to MAIN.
