# Selective Recheck Implementation Plan

> **For agentic workers:** Execute inline with test-driven development; no GPU launch is authorized.

**Goal:** Prepare and seal a 24-call confidence-versus-uniform c32 recheck sidecar after exact ceiling admission.

**Architecture:** A CPU preparer authenticates the frozen ceiling, extracts label-only mean log probabilities, freezes selections/repacks/requests, and writes immutable inputs. A thin collector reuses the qualified native call machinery and applies strict no-fallback episode merging and the public J1 reducer. An owner reuses the qualified one-A100 service chain. A prospective auditor is frozen before outcomes.

**Tech Stack:** Python 3.11/3.12 standard library, CPU-only `tokenizers`, pytest, existing qualified native collector/service wrappers.

**Spec:** `DESIGN.md` plus `DESIGN_AMENDMENT_NO_FALLBACK.md` in this directory.

## Global constraints

- New sidecar: `root-supplied-plan-selective-recheck-v1`; do not edit ceiling or other producers.
- No GPU/service launch; READY requires MAIN ceiling adoption and exact terminal/report/final pins.
- TDD for selection, strict merge failures, and actual owner-entry fake transport.
- Exactly 24 new calls, no retry/reroll/fallback, one A100, outer cap 1,800 seconds.

### Task 1: Additive amendment and admission/selection tests

- [ ] Write failing tests for exact pin admission, 1,280 span recovery, label-blind selection, fixed budgets, hashes, repacks, and seeds.
- [ ] Run focused tests and verify missing implementation failures.
- [ ] Implement the minimal preparer/protocol and rerun to green.

### Task 2: Strict collector and reducer

- [ ] Write failing tests for valid selected-only overwrite, unavailable episode NULL, authenticated-invalid observed failure, and no partial salvage/fallback.
- [ ] Implement the thin qualified collector and episode summaries; rerun to green.

### Task 3: Owner and real entry seam

- [ ] Write a failing CPU fake-transport test that enters the actual owner/collector path with a nonempty prepared call.
- [ ] Reuse the qualified service owner and implement only the study binding needed for the new sidecar.
- [ ] Run the focused seam test to green without starting a service or importing GPU libraries.

### Task 4: Prospective audit and seal

- [ ] Write the pre-outcome native/selection/merge/cost audit method.
- [ ] Freeze source/input hashes and tests; require MAIN ceiling adoption before READY.
- [ ] Verify all tests, immutable identities, no active process, and report READY to MAIN without launching.
