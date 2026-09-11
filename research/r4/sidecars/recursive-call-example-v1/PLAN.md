# Recursive-call example implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline, as the parent explicitly
> requested CPU preparation without additional confirmation. No GPU or container launch.

**Goal:** Freeze a 12-episode, development-only test of adding one executable recursive-call
example to the existing abstract procedure, measuring actual child sessions separately from
mentions and executed-code attempts.

**Architecture:** Import the sealed plan-hint-crossover driver read-only and reuse its
containerized run loop, request constructor, taskset, checkpointing and budget enforcement.
Patch only the imported module's process-local prompt and summary callbacks; never its file.
The new sidecar owns its prompts, fresh seeds, spec and output directory.

**Tech Stack:** Existing pinned Prime/verifiers environment, Python 3.12; no installs.

**Spec:** Parent-approved additive example: same abstract procedure, followed by an executable
ipython cell that parses context records, passes the first four questions to `await rlm`, and
prints `child.answer`. Development source IDs 12000008, 12000009, 12000025; two paired seeds.

## Global constraints

- Preserve every existing baseline source/spec/output byte.
- Do not use source-heldout outcomes for prompt or training choices.
- Same EvalClient, temperature 0.5, 2048-token call cap, nano-RLM 4ef3438, depth 1,
  setup/rollout/finalize/scoring 300/900/60/60 seconds, four concurrent pairs and image.
- Twelve rollouts and a 30-minute study cap; matched arm budgets and no answer/gold leakage.
- New model/adapter assignments require their own descriptor and immutable spec.

## Task 1: Narrow adapter and CPU seal

Files: create driver.py, tests/test_example.py and README.md in this sidecar only.

Interfaces: `load_tasks()` returns the three native development tasks; `with_prompt(task, arm)`
clones only TaskData.prompt; `build_plan(tasks)` returns twelve fresh counterbalanced rows;
`example_metrics(episode, wall_seconds)` exposes mention, executed call-cell and child-session
evidence separately; `make_spec(descriptor, weight_condition)` seals the actual inputs.

- [x] Write focused tests for 12-row development-only pairs and seeds disjoint from the
  56-row baseline; exact additive prompt diff; executable example with a fake async rlm
  returning an object with `.answer`; and child-session counts versus mere mentions.
- [x] Run those tests with CUDA_VISIBLE_DEVICES='' and observe missing-feature failures.
- [x] Implement the adapter around the unchanged imported baseline runner. The runtime
  callback assignments are `base.with_prompt = with_prompt`,
  `base.crossover_metrics = example_metrics`, `base.summarize = summarize`; retain original
  function references before assigning to avoid recursion.
- [x] Run the focused tests, syntax/style checks and CPU make_context/config validation.
- [x] Freeze `PREPARED_BASELINE_SPEC.json` without overwrite for the known baseline adapter;
  an assigned updated adapter will receive a separately named spec and descriptor.
- [x] Verify the actual recursion API from pinned local source snapshots and upstream tests,
  record their URL/revision/MIT-license/checksums, and provide the no-GPU launch command.

No Git commit or worktree is required: the user explicitly scoped this to a new isolated
research sidecar outside the source repository. No shared source files will be edited.
