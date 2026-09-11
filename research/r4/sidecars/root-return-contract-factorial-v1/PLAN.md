# Return-contract factorial implementation plan

> **For agentic workers:** Use superpowers:executing-plans for this bounded inline preparation.
> The main coordinator has approved the design; it owns launch and acceptance. No delegation,
> core worktree edits, GPU calls or service changes are part of preparation.

**Goal:** Queue an authenticated 96-episode root-weight × interface-instruction comparison.

**Architecture:** One study module reconstructs immutable tasks and verifies two root bindings;
one driver wraps the existing native collector and qualified two-alias lifecycle. A small analysis
module reports paired/context-cluster summaries. Existing sources remain read-only imports.

**Tech Stack:** Python 3.12 qualified Prime environment, verifiers native TrainClient, rootless nano.

**Spec:** [DESIGN.md](DESIGN.md)

## Global constraints

Own only this external sidecar; preserve frozen sources, prompts, gold, contexts and episode budgets.
96 episodes, 3600 seconds overall, eight pair workers, two sequential root-weight services.
Original857a7 / finalstep8 473210b1, fixed childc32de; native T=.5/full support/max2048.
No output repair, training, GPU activity during preparation or generated-code execution on host.

## Task 1: Freeze study inputs and identity seams

Files: `study.py`, `test_study.py`, `inputs/PLAN.json`, `inputs/TASKS.json`, `SPEC.json`.
Interfaces: `with_prompt(task, arm)`, `build_plan(tasks)`, `binding_for(policy)`, `verify()`.

- [ ] Write and run failing tests for exact suffix delta, balanced 96-coordinate pairing,
  wrong policy rejection and native sampler/renderer identity.
- [ ] Implement only the named study helpers, authenticate inherited sources and final checkpoint,
  then rerun those tests. Preserve all intended differing task/prompt hashes in frozen inputs.

## Task 2: Reuse collection and service lifecycle

Files: `driver.py`, `qualify.py`, `test_study.py`.
Interfaces: `collect(spec_path, output)` and parent-only `driver.py run --output NEWDIR`.

- [ ] Test the private collector patch restores imported functions, and actual binding is not
  faked or relaxed. Use inherited `installed_hooks`, task runtime and source authentication.
- [ ] Use frozen lifecycle V2 `start_service`/`stop_service` with the exact owned service request;
  native collection runs in a CPU subprocess. Bound all transitions by one deadline.
- [ ] Run two real CPU rootless fake-provider root→child→root episodes, one per instruction arm;
  verify physical IDs/roles via the frozen exporter, with zero GPU/model calls.

## Task 3: Focused evidence and handoff

Files: `analysis.py`, `RUNBOOK.md`, `READY.json`.
Interfaces: `summarize(records, plan)` and `analysis.py --output ATTEMPT`.

- [ ] Test pair missingness and six-context grouping without inventing rewards or parse results.
- [ ] Freeze sources/spec/inputs/qualification hashes; rerun the focused test file and read-only
  `driver.py verify`. Publish READY only after these observations exist.
- [ ] Send exact qualified environment, launch path, output, cap and ownership/release semantics
  to the main coordinator. No launch, Git integration or shared-source modification is authorized.
