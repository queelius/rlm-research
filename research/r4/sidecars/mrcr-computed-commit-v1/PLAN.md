# Computed-string commitment implementation plan

**Goal:** Queue the six-document shared-prefix terminal comparison.
**Architecture:** A new owned sidecar supplies a narrow nano overlay and collector.
Reuse the qualified rootless mount boundary, MRCR task loader, native TrainClient
and exact original-adapter conversion proof. No GPU/service ownership is delegated.
**Spec:** DESIGN.md (parent-approved decision).
**Isolation:** This new external sidecar is the requested isolated workspace;
no core worktree, shared environment install, image overwrite or Git commit.

## 1. Real submission channel (TDD)
- [x] Save the three inspected pinned upstream files under inputs/upstream.
- [x] Write test_repl.py cases that invoke actual IPythonREPL in an owned container:
  exact Unicode/newline bytes, stdout spoof ignored, non-string/duplicate/oversize,
  submission followed by exception, caught helper error and next-cell reset.
- [x] Run unchanged-source cases and observe missing submission assertions fail.
- [x] Implement kernel state plus structured Jupyter reply extraction in
  submission.py and an exact-hash overlay.py; run the same tests green.
- [x] Test that the paired finalizer persists one candidate before exactly one
  restatement call, never executes its tool request, and preserves failed final data.

## 2. Paired native collector and inputs
- [x] Build mrcr_computed_commit_v1.py task/harness subclass and driver.py using
  existing MRCR data/boundary and native-client imports.
- [x] Freeze public contexts/questions/seeds and size cap before copying host gold.
- [x] Capture every native wire request/response and complete episode; perform
  descriptor/disk/full-conversion/live alias-root-parent checks before model calls.
- [x] Enforce five-prefix/six-total calls, no reruns and a twenty-minute global cap.
- [x] Focused tests cover mount isolation, pairing and separate scoring validity.

## 3. Qualification and handoff
- [x] Run actual rootless/native deterministic CPU-provider proof through the
  collector, asserting one shared computation, accepted bytes and one restatement.
- [ ] Freeze input/source/runtime hashes and qualification artifacts.
- [ ] Publish READY.json last, with RUNBOOK.md run command accepting an actual
  original-weight endpoint descriptor; default a new outputs/attempt-001.

Final sealing is executed by seal.py; READY.json, not this pre-seal checklist,
records completion. Parent reviewed the finalizer/driver/capture boundary.
The approved common task-system suffix and final input/output-budget diagnostic
are included in the final six-native-call proof. Previous tasks and reconstructed
pre-amendment source remain under inputs; no GPU/model call was made in preparation.
