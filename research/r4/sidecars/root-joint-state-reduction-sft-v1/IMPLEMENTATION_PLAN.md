# Joint state reduction SFT implementation plan

> For agentic workers: use executing-plans inline; MAIN explicitly owns other agents and GPU execution.

Goal: implement the approved 16-trajectory, two-loss-arm, 84-endpoint experiment without altering frozen sources.

Architecture: new uniquely named `joint_*` modules reuse qualified native capture, checkpoint and an27 lifecycle seams. Local protocol adds genuine cumulative state; local owner pins the whole dependency closure and shares one inclusive clock. External sidecar is the explicitly assigned isolated workspace; no repository branch changes.

Tech stack: existing native Python/verifiers renderer and train Python/PyTorch/PEFT, no installs.

Spec: `../../ideas/2026-09-09-joint-acquisition-reduction-sft-design.md` SHA326cf25dadcb6bc3afc7f472a8d7f97d31b640d333d308c5cc4e04f946dc6e7d.

Constraints: CPU preparation only; low66c/c32 unchanged; 16 genuine captures/40 child calls/72 authored turns; two independent four-update arms; no map literals in reductions; wrong labels retained; 84 preplanned endpoints; one A100; outer5400/work5100/owned5280/cleanup180/outermargin120 seconds. All stage limits intersect the shared work deadline and include preceding releases, not additive promises. Private credential check before output/process work. No retries or substitution.

## Task 1: protocol and frozen plans

Files: `test_protocol.py`, `joint_protocol.py`, `joint_study.py`, `prepare.py`.
- [x] Test generated authored producer actions by executing them with a CPU fake child in one namespace: successive updates retain all16 IDs; generated reduction filters actual user and prints a count from deliberately wrong labels unchanged. No sampled model code is executed.
- [x] Test target spans with real native tokenizer: code identifiers belong to mechanism, quoted user/category strings do not.
- [x] Implement 16 train and8 controlled plans balanced across width/scope; first4 train cover all width×scope cells;16 free and4 training diagnostics, disjoint raw train/readout groups.
- [x] Render/freeze native prompts and pin original inputs.

## Task 2: native capture and learning

Files: `collect.py`, `joint_learning.py`, `train.py`, `joint_binding.py`, `test_learning.py`, `test_native.py`.
- [x] Test per-trajectory producer mass does not scale with number of batches, terminal masks remain actual native suffixes, and missing planned endpoints retain NULL.
- [x] Adapt immutable collector into local unique-import module; controlled and training-diagnostic source prefixes replay exact whole native requests; completed provider final checks stay qualified.
- [x] Adapt current-action loss to selected weighted roles; initial fixed4 mechanism/cost gate; four full16 passes and original checkpoint ancestry for each independent arm.

## Task 3: composed owner and seal

Files: `owner.py`, `test_entrypoints.py`, `CPU_TESTS.json`, `READY.json`.
- [x] Test actual owner argv through collector parser and actual owner dependencies→start_service→config/descriptor creation→intercepted subprocess.Popen; retain real local configuration provider and lifecycle identity behavior, no GPU/service startup.
- [x] Implement all84 planned NULL rows before launch, shared5100 work/5280 owned/5400 outer with180 owned cleanup and120 outer margin; retain per-phase/call failures and cleanup records.
- [x] Run only focused CPU tests and native CLI verify; freeze exact source/input map and READY; MAIN reviews/accepts separately. No Git commit requested for external artifacts.
