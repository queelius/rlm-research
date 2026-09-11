# Query-sensitive RL Implementation Plan

> For agentic workers: use executing-plans inline; MAIN supplies review checkpoints. No subagents or GPU launch.

**Goal:** CPU-qualify an immutable 12-window root-only operator RL experiment and mandatory paired final readout.

**Architecture:** Unique `qsr_*` modules bind deterministic new records/queries to the existing native typed-child runtime. Reuse numerical TIS/Adam/checkpoint functions unchanged; new thin coordinator separates scheduled windows from actual updates and protects final-readout time.

**Tech stack:** Qualified native Python, existing training Python/PyTorch/PEFT, an27 service/lifecycle, unittest.

**Spec:** `DESIGN.md`; approved Option A only.

## Global constraints

- New external sidecar only; old/live sources unchanged. No GPU, services, locks or queue writes during preparation.
- 448 disjoint source groups against the pinned 53-manifest receipt; root-catalog novelty only, child-training-exposed.
- 12 × 3 × 8 training slots, 48 paired questions × two policies, fixed low66c/c32, no refill/shaping/forced recursion.
- Outer 14400 = work14100 + cleanup180 + margin120; training-side9000 and final5100 nested within work.
- Strict native endpoint availability differs from conservative training admission. Never fabricate a final from orchestrator completion.

## Task 1: Immutable data and native task seam

Create `qsr_study.py`, `qsr_data.py`, `qsr_native.py`, `test_data.py`, `test_native.py`.
Interfaces: `build()` returns PUBLIC/HOST_GOLD/GROUPS/PLANS/DIAGNOSTICS/PROVENANCE; `task(context, prompt, gold, name)` returns actual native task; `first_prefix(task)` returns native token IDs.

- [ ] Write failing independent count/distinct/weight truth-table test (`[2,1,7]` for two matching same-user records of weights2/5).
- [ ] Write failing split/schedule test: 448 unique groups, training288/final48, disjoint groups, six supported and three held-out cells.
- [ ] Implement deterministic hash selection, balanced metadata, semantic queries, host-only truth, and zero/best-constant/coincidence diagnostics.
- [ ] Write/run native conditioning test: operator/scope changes alter first prefix; mutated host labels/gold leave first prefix and real setup files identical.
- [ ] Implement native task using real four-field records and plain query; run focused tests.

## Task 2: Native collection, endpoint/admission and numerical seam

Create `qsr_collect.py`, `qsr_export.py`, `qsr_common.py`, `qsr_train.py`, `test_training.py`.
Interfaces: `planned(phase)`, `prepare_spec(...)`, `export_attempt(...)`, `generation(window, policy)`, qualified `train(args)`.

- [ ] Write failing availability tests: actual capped strict final scores; no-final trace completion stays NULL; authenticated wrong-route stays observed0 without execution.
- [ ] Implement exact physical final-branch check, planned missing rows, independent endpoint/admission fields and qualified root-only group export.
- [ ] Write failing cursor tests: noop preserves Adam/policy; actual update increments Adam exactly once; window12 can correspond to fewer updates.
- [ ] Bind unchanged numerical trainer to complete24-slot native export, current-policy hashes and persistent checkpoints; test literal masking/admission fixtures and native replay argv.

## Task 3: Owner, preparation and CPU acceptance

Create `owner.py`, `prepare.py`, `test_entrypoints.py`, `CPU_TESTS.json`, READY and operation report.
Interfaces: `owner.execute(output)`, `owner.verify`, fixed owner CLI `run --output outputs/attempt-001`.

- [ ] Write failing deadline test: no new learning consumes final reserve; both policies attempted even zero updates/learning failure.
- [ ] Implement owned service/train subprocess orchestration with initial384-slot ledger, complete/noop window receipts, retained partial failures, mandatory final blocks and owned teardown.
- [ ] Write composed actual-owner → suite → service/config/descriptor → intercepted outer/inner Popen CPU regression; no real processes or credentials printed.
- [ ] Freeze data/tasks/recipe/source closure after CPU tests; perform actual `owner.py verify` and exact owner/collector CLI test.
- [ ] Send MAIN source paths for review, then final hashes/test counts/report; no launch.

No repository commits are requested: this immutable external-sidecar handoff is the integration boundary.
