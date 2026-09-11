# Child-role16 independent auditor implementation plan

**Goal:** Implement the already approved METHOD.md without reading run outcomes.
**Architecture:** Three analysis-only modules: pure attempt/outcome/pair projections,
native branch verification, and a terminal-only single-read orchestrator. Reuse the
stored eight-call operator-authored native qualification; do not rerun containers.
**Tech stack:** Python3.11, stdlib, qualified native Verifiers WireTrace. No installs.
**Spec:** METHOD.md, SHA e77b0f116e4c1a0fcf9566f965a308c8eb5ae8be684d51833662f4db6574bb26.

Scope is this existing isolated analysis directory, not a Git/source worktree.
No subagents, Git commits, live source edits, model/GPU/service calls or queue work.
The parent has approved inline implementation; no additional approval is inferred.

- [x] Write focused failing tests for audit_primitives.py: allowed cancellation versus
  prevented hooks, duplicate request IDs, missing records, completed scores after a
  later cap, and null-preserving paired differences.
- [x] Implement `funnel(requests, results, dispatch, binding, status=None)`,
  `outcome(record, metrics, attempted=False, prevented=False)`, and
  `pair_readout(plan, rows)`; keep wrapper IDs, request IDs and ordinals separate.
- [x] Write failing stored-native fixtures for audit_native.py:
  `project_episode(raw, attempts, binding, arm, suffix)`. Require four verified
  sampled calls per qualification arm; reject a cyclic parent, wrong physical
  prefix or inconsistent depth/alias. Partial evidence must not erase other calls.
- [x] Implement official-branch/token/mask/logprob/role and suffix checks, retaining
  sampled messages, tool observations, invocation identity and missing graph state.
- [x] Implement audit.py with explicit `--after-parent-terminal` opt-in and terminal
  artifact readiness checks before outcome reads. Authenticate frozen union once,
  read each new artifact once, materialize physical/graph/episode projections in
  METRICS and SOURCES before prose. After the parent trigger, write the concise
  REPORT and publication seal from these projections, with manual interpretation
  of flagged child-request conflicts. Unrun coordinates remain in the16-grid.
- [x] Run only these focused tests with the existing Prime interpreter, inspect the
  actual stored native fixture, publish AUDITOR_READY.json last. Do not run terminal
  analysis until the parent sends the terminal trigger.

Command: `CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python -m pytest -q test_audit.py`.
The fixture and test results are delivery/accounting qualification, never model
performance or measured likelihood. Any missing provenance remains explicit.
