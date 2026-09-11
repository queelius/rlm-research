# Hard-Curriculum One-Update RLM RLVR Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement
> this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CPU-preflighted, provenance-sealed sidecar that finds the first genuinely
mixed task-difficulty rung, performs at most one root-action-only LoRA policy-gradient update,
and computes a 24-pair held-out pre/post endpoint.

**Architecture:** Pure curriculum and analysis contracts live in `curriculum.py`; the CLI and
GPU-deferred runtime live in `rlvr_hard_curriculum.py`. The runtime vendors the proven pilot's
token/logprob, vLLM RPC, and update path while adding authenticated rung tasks and durable phase
state. A checked-in manifest and launch descriptor bind source and external inputs.

**Tech Stack:** Python 3.12 standard library for pure contracts and CLI; existing sealed
PyTorch/Transformers/PEFT/vLLM/RLM environment only at deferred launch; pytest and Ruff for CPU
verification.

**Spec:** `/project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-hard-curriculum-v1/DESIGN.md`

## Global Constraints

- Never initialize CUDA, open ports, start model servers, or mutate cached repos/shared envs
  during implementation, tests, or preflight.
- Controller temperature is exactly `0.8`; temperature is not a calibration dimension.
- Calibration has five ordered 24-episode rungs and a hard maximum of 120 episodes.
- Invalid training trajectories have `reward = null` and are excluded, never scored negative or
  zero.
- Held-out primary terminal success maps valid exact to 1 and every other terminal outcome to 0
  across all 24 pairs.
- The only trainable tokens are root/controller actions; prompt, observation, environment, and
  leaf tokens are masked.
- The optimizer step count is exactly one and durable state prevents a second step.
- Fixtures are engineering-only and cannot enter research analysis.
- This sidecar is outside a Git worktree, so verification uses immutable SHA-256 manifests rather
  than commits.

---

## File map

- `source/curriculum.py`: immutable rungs, deterministic records/tasks, strict verifier,
  calibration admission, advantages, held-out pairing.
- `source/rlvr_hard_curriculum.py`: paths/provenance, attempt state, launch/runtime adapters,
  action capture, masked one-step update, preflight and CLI.
- `source/test_curriculum.py`: pure generator/verifier/selection/pairing tests.
- `source/test_rlvr_hard_curriculum.py`: provenance, state, launch, masks/update-evidence tests.
- `fixtures/engineering_episode.json`: non-research smoke artifact.
- `manifest.json`, `launch.json`, `RUNBOOK.md`: seal and operations.

### Task 1: Pure task generator and verifier

**Files:**
- Create: `source/test_curriculum.py`
- Create: `source/curriculum.py`

**Interfaces:**
- Produces: `Rung`, `TaskRecord`, `CurriculumTask`, `RUNGS`, `generate_task(rung_id, seed,
  split)`, `recompute_gold(task)`, and `verify_terminal(task, output_text)`.

- [ ] **Step 1: Write RED generator tests**

Add tests that generate every rung twice, assert byte equality and unique IDs, exact shapes
`[(96,8),(128,10),(160,12),(192,12),(224,14)]`, disjoint calibration/held-out identities,
monotone mechanics, and `recompute_gold(task) == task.gold_value`. Mutate a record semantic class
and assert recomputation changes or detects stale identity.

- [ ] **Step 2: Run RED tests**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q source/test_curriculum.py`

Expected: collection fails because `curriculum` does not exist.

- [ ] **Step 3: Implement deterministic generator**

Use only local `random.Random(seed)` instances and canonical JSON SHA-256. Freeze class
definitions/templates and shuffle opaque label codes per task. Render the learned prompt envelope
and store structured records privately for independent recomputation.

- [ ] **Step 4: Add RED verifier tests**

Assert exact correct JSON is `(valid=True,reward=True)`, schema-valid wrong integer is
`(True,False)`, and malformed/extra-key/extra-text/noninteger outputs are `(False,None)`.

- [ ] **Step 5: Implement strict verifier and run GREEN**

Run the Task 1 command and require all tests pass.

### Task 2: Complete-rung admission and paired analysis

**Files:**
- Modify: `source/test_curriculum.py`
- Modify: `source/curriculum.py`

**Interfaces:**
- Produces: `EpisodeOutcome`, `RungSelection`, `select_first_rung(outcomes)`,
  `training_rows(selection, outcomes)`, `group_advantages(rewards)`, and
  `paired_endpoint(pre, post, expected_pair_ids)`.

- [ ] **Step 1: Write RED admission tests**

Construct all 24 planned identities for multiple rungs. Assert 23 rows cannot be selected; an
invalid row has null reward; 19 valid fails; rates below 0.2 or above 0.8 fail; fewer than two
mixed task groups fail; and the first qualifying complete rung wins even if a later rung is
closer to 50%.

- [ ] **Step 2: Implement admission and training projection**

Require exact expected task/rollout identity sets. Build advantages only within valid mixed
prompt groups and prove invalid and non-mixed rows are absent.

- [ ] **Step 3: Write RED paired-endpoint tests**

Build 24 pairs with exact, wrong-valid, and invalid outcomes. Assert the primary includes all 24
and maps invalid to terminal success 0; jointly-valid exact delta, validity delta, transitions,
raw rows, and invalid reasons are secondary. Assert 23 pairs, duplicate IDs, split mismatch, or
fixture provenance fails closed.

- [ ] **Step 4: Implement paired endpoint and run GREEN**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q source/test_curriculum.py`

### Task 3: Proven capture, mask, launch, and provenance contracts

**Files:**
- Create: `source/test_rlvr_hard_curriculum.py`
- Create: `source/rlvr_hard_curriculum.py`

**Interfaces:**
- Consumes: all Task 1/2 contracts.
- Produces: `capture_response_turn`, `build_causal_turn`, `build_server_command`,
  `server_environment`, `verify_external_inputs`, `prepare_attempt`, and `preflight`.

- [ ] **Step 1: Write RED action-capture and mask tests**

Use a minimal raw-token Responses payload. Assert `input_ids = prompt + action`, prompt labels
are `-100`, action labels match action IDs, loss mask is zero then one, and mismatched raw/logprob
token IDs fail. Assert leaf/environment values cannot be inserted as action tokens.

- [ ] **Step 2: Implement the proven token contracts**

Port the prior `CausalTurn`, `CapturedResponseTurn`, `build_causal_turn`, and
`capture_response_turn` behavior without broadening accepted response shapes.

- [ ] **Step 3: Write RED launch/provenance tests**

Assert command contains `--return-tokens-as-token-ids`, temp is absent from server startup,
RPC paths are short and attempt-bound, cleanup refuses unsafe paths, CUDA is not touched by
preflight, and each changed input/source/bundle row produces a machine-readable refusal.

- [ ] **Step 4: Implement launch and authenticated input checks**

Strictly parse the bundle inventory, adapter files, repo commits, upstream pilot source hashes,
and local manifest/source hashes. Generate a structured refusal with code, field, expected,
observed, and remediation.

- [ ] **Step 5: Write RED task-window/attempt tests**

Use a fake counter to prove overflow refusal and real tokenizer preflight for all 52 possible
tasks (20 calibration plus 32 held-out across rungs). Assert `prepare` refuses overwrite and
writes read-only spec/task/launch files.

- [ ] **Step 6: Implement attempt preparation and run GREEN**

Run both focused test files and require all tests pass.

### Task 4: Durable phases and restart-safe one-step evidence

**Files:**
- Modify: `source/test_rlvr_hard_curriculum.py`
- Modify: `source/rlvr_hard_curriculum.py`

**Interfaces:**
- Produces: `AttemptLedger`, `write_episode`, `complete_phase`, `validate_resume`,
  `validate_update_evidence`, and deferred `train_one_step`.

- [ ] **Step 1: Write RED durable-state tests**

Assert identical episode replay is idempotent, conflicting bytes refuse, incomplete phase cannot
be skipped, marker input hash mismatch refuses, terminal failure refuses resume, completed
training skips rather than steps, and a partial checkpoint without a completion marker refuses.

- [ ] **Step 2: Implement atomic append-only state**

Use fsync + replace for immutable JSON artifacts and append-only JSONL ledger entries. Bind every
phase marker to sorted input artifact hashes and validate the full chain on resume.

- [ ] **Step 3: Write RED update-evidence tests**

With small CPU fake tensors/metadata, reject drift above 0.5 max or 0.1 mean, mask leaks,
nonfinite/zero gradient, optimizer steps other than one, unchanged adapter hash, zero changed
tensors, changed base shard inventory, and missing checkpoint hashes. Accept one complete valid
evidence object.

- [ ] **Step 4: Port and harden deferred update path**

Retain the proven clipped PG computation, root-action selection, PEFT-only trainables, gradient
and parameter checks. Add optimizer-state step assertion, base inventory before/after comparison,
and durable `training-complete.json` written only after checkpoint authentication.

- [ ] **Step 5: Run GREEN focused tests**

Run both focused test files and require all tests pass.

### Task 5: Orchestration, seal, documentation, and CPU preflight

**Files:**
- Modify: `source/rlvr_hard_curriculum.py`
- Modify: both test files
- Create: `fixtures/engineering_episode.json`
- Create: `manifest.json`
- Create: `launch.json`
- Create: `RUNBOOK.md`

**Interfaces:**
- Produces CLI commands `seal`, `preflight`, `prepare`, `run`, `resume`, and `audit`.

- [ ] **Step 1: Write RED CLI/preflight tests**

Assert preflight emits status/diagnostic JSON, fixtures are labeled and rejected by analysis,
launch is exact but deferred, `run` requires authenticated prepared state plus explicit GPU/port
arguments, and CPU commands reject a nonempty `CUDA_VISIBLE_DEVICES`.

- [ ] **Step 2: Implement orchestration and docs**

Calibration runs fixed rung order and completes all 24 identities before selection. Held-out pre,
one update, held-out post, and analysis use durable phase markers. Document exact prepare,
preflight, launch, resume, audit, expected duration, output semantics, and stop criteria.

- [ ] **Step 3: Seal source and external inventory**

Compute canonical manifest and launch descriptors with exact file paths, sizes, hashes, commands,
environment contracts, design hash, prior evidence hashes, and `research_evidence=false` for the
fixture. The manifest excludes only itself from its local file inventory.

- [ ] **Step 4: Run exact CPU verification**

Run:

```bash
cd /project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-hard-curriculum-v1
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' python -m pytest -q source/test_curriculum.py source/test_rlvr_hard_curriculum.py
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' python source/rlvr_hard_curriculum.py preflight --json
ruff check source/curriculum.py source/rlvr_hard_curriculum.py source/test_curriculum.py source/test_rlvr_hard_curriculum.py
ruff format --check source/curriculum.py source/rlvr_hard_curriculum.py source/test_curriculum.py source/test_rlvr_hard_curriculum.py
```

Require tests, preflight, Ruff check, and Ruff format-check all pass without CUDA or network.

- [ ] **Step 5: Audit immutable hashes**

Run `python source/rlvr_hard_curriculum.py audit --json`, require `status=ready`, and record the
design, plan, manifest, launch, source, tests, and runbook SHA-256 values in the final report.

