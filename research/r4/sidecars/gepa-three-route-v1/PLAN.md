# GEPA × Three-Route Sidecar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this
> plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CPU-verified, immutable launch adapter for matched-budget frozen, GEPA, and
random/local harness-search arms that refuses research execution until the authenticated corpus and
provider contract is available.

**Architecture:** A stdlib-only sidecar validates strict JSON inputs, external repository commits,
provider source hashes, task/group splits, and seed components. Typed core functions own canonical
records, append-only lineage, matched metric budgets, deterministic controls, decision rules, and
raw group analysis. A thin GEPA adapter imports the pinned external checkout only during a real
exploratory launch; fixtures test the same contracts without importing GEPA or contacting a model.

**Tech Stack:** Python 3.11+ standard library, pytest for development, external pinned GEPA at
launch, canonical JSON and SHA-256.

**Spec:** `DESIGN.md`

## Global Constraints

- Write only `/project/alex_phd/runs/rlm-research-r4/sidecars/gepa-three-route-v1`.
- Do not use GPUs, ports, network services, or mutate official cached repositories/shared envs.
- Pin GEPA commit `0632cdb5dcc052e690eab439e1b4a7e3e9cfe407`.
- Fixture outputs are engineering validation only and cannot enter research attempt paths.
- The +0.02 futility and +0.03 positive-launch thresholds are decision rules, not inferential
  significance; retain raw group-level outcomes for threshold reanalysis.
- Use one metric evaluation per candidate-task pair as the equal arm budget unit.
- Do not implement Task 9 corpus preparation, store publication, or production verifier behavior.

---

### Task 1: Strict immutable schemas and dependency authentication

**Files:**
- Create: `pyproject.toml`
- Create: `source/gepa_three_route/__init__.py`
- Create: `source/gepa_three_route/core.py`
- Create: `source/gepa_three_route/dependencies.py`
- Create: `tests/test_dependencies.py`
- Create: `study.json`
- Create: `dependency-contract.json`
- Create: `seed-candidate.example.json`

**Interfaces:**
- Produces `canonical_bytes`, `canonical_id`, `strict_load`, `Refusal`, `load_study`,
  `authenticate_dependencies`, and immutable `StudySpec`, `DependencyDescriptor`, `Task` values.
- Consumes no sidecar runtime code.

- [x] **Step 1: Write failing dependency tests**

Test that strict JSON rejects duplicate keys; fixtures cannot authenticate as research; external
commit/file/provider mismatches return a machine-readable `Refusal`; group splits are disjoint and
complete; task/group counts must be 108/36; seed components exactly match the declaration.

```python
with pytest.raises(Refusal) as error:
    authenticate_dependencies(descriptor, study, mode="research")
assert error.value.to_dict()["code"] == "DEPENDENCY_CORPUS_MISSING"
assert error.value.to_dict()["remediation"]
```

- [x] **Step 2: Run RED**

Run: `python -m pytest -q tests/test_dependencies.py`
Expected: collection failure because `gepa_three_route.dependencies` does not exist.

- [x] **Step 3: Implement strict schemas and authentication**

Use `json.loads(..., object_pairs_hook=...)`; reject bool-as-int, unknown/missing fields, non-absolute
dependency paths, unsafe provider references, stale hashes/commits, dirty external tracked trees,
split overlap, duplicate task/group IDs, and private gold fields. Import providers only after their
source bytes and callable names are authenticated. Return stable diagnostic codes and remediation.

- [x] **Step 4: Run GREEN**

Run: `python -m pytest -q tests/test_dependencies.py`
Expected: all dependency tests pass without importing GEPA or touching a GPU.

### Task 2: Append-only lineage, checkpoints, and cost envelopes

**Files:**
- Create: `source/gepa_three_route/lineage.py`
- Create: `tests/test_lineage.py`

**Interfaces:**
- Consumes canonical helpers and `Refusal` from Task 1.
- Produces `LineageLedger`, `append_record`, `validate_chain`, `write_checkpoint`,
  `load_checkpoint`, and canonical proposal/evaluation record builders.

- [x] **Step 1: Write failing lineage tests**

Require semantic record IDs, parent and previous-record links, complete calls/token/time metadata,
atomic content-addressed checkpoints, byte-identical resume, and rejection of mutation, truncation,
duplicate IDs, changed seal/budget, or missing raw group fields.

- [x] **Step 2: Run RED**

Run: `python -m pytest -q tests/test_lineage.py`
Expected: collection failure because `gepa_three_route.lineage` does not exist.

- [x] **Step 3: Implement append-only storage**

Write canonical JSONL with `os.open(..., O_APPEND|O_CREAT)` and `fsync`; re-read and validate the
entire chain before every resume. Checkpoints go to a same-directory temporary path, are fsynced,
renamed to `<sha256>.json`, and referenced by a checkpoint ledger record. Do not serialize gold.

- [x] **Step 4: Run GREEN**

Run: `python -m pytest -q tests/test_lineage.py`
Expected: all lineage tests pass.

### Task 3: Matched-budget control scheduler and preregistered analysis

**Files:**
- Create: `source/gepa_three_route/study.py`
- Create: `tests/test_study.py`

**Interfaces:**
- Consumes authenticated tasks/spec, canonical IDs, and lineage builders.
- Produces deterministic `mutate_candidate`, `Budget`, `Decision`, `group_outcomes`,
  `bootstrap_contrast`, and `evaluate_candidate` with a provider runner/verifier pair.

- [x] **Step 1: Write failing scientific-contract tests**

Require identical task order and request for all arms, one budget unit per attempted candidate-task,
equal GEPA/random discovery budget, deterministic random mutations, no confirmatory access during
exploration, infrastructure failures retained in denominators, raw route/organization/token-band
group outcomes, deterministic group bootstrap, and exact futility/overfit/positive decision rules.

```python
decision = exploratory_decision(frozen=.50, gepa=.53, random=.52, invalid_delta=.01, audit_ok=True)
assert decision.code == "POSITIVE_LAUNCH"
assert decision.is_significance_test is False
```

- [x] **Step 2: Run RED**

Run: `python -m pytest -q tests/test_study.py`
Expected: collection failure because `gepa_three_route.study` does not exist.

- [x] **Step 3: Implement scheduler and analysis**

Use a local `random.Random(study.random_seed)` and a finite, logged operator set. Validate runner and
verifier envelopes exactly; compute output/event hashes; append every attempt before aggregation.
Bootstrap group IDs with replacement using the frozen seed and emit raw group rows alongside all
aggregates. Label thresholds `decision_rule`, never `p_value` or `significant`.

- [x] **Step 4: Run GREEN**

Run: `python -m pytest -q tests/test_study.py`
Expected: all study tests pass.

### Task 4: GEPA adapter and resumable exploratory orchestration

**Files:**
- Create: `source/gepa_three_route/gepa_adapter.py`
- Create: `source/gepa_three_route/orchestrate.py`
- Create: `tests/test_gepa_adapter.py`
- Create: `tests/test_orchestrate.py`

**Interfaces:**
- Consumes authenticated provider callables, Task 2 lineage, and Task 3 evaluator.
- Produces `ThreeRouteGEPAAdapter`, `run_exploration`, `run_confirmation`, and
  `run_engineering_fixture`.

- [x] **Step 1: Write failing adapter/orchestration tests**

Use fake in-process providers and a fake optimize callable to assert GEPA train/development routing,
reflective records without gold, proposer cost lineage, exact `max_metric_calls`, pinned GEPA API
kwargs, result-parent lineage, random control parity, checkpoint resume equality, explicit confirm
gate, and fixture attempt-path exclusion.

- [x] **Step 2: Run RED**

Run: `python -m pytest -q tests/test_gepa_adapter.py tests/test_orchestrate.py`
Expected: collection failure because adapter/orchestration modules do not exist.

- [x] **Step 3: Implement adapter and orchestrator**

`ThreeRouteGEPAAdapter.evaluate` calls the shared evaluator and returns external GEPA
`EvaluationBatch` when GEPA is present, or an injected compatible batch factory in tests.
`make_reflective_dataset` emits prompt/output/reason/trace hashes and score, never gold. A wrapped
proposal provider logs its model calls/tokens/time. Call pinned `gepa.optimize` with `run_dir`,
`write_agent_state=True`, `cache_evaluation=False`, frozen seed, full validation, strict improvement,
and exact discovery budget. Run the random control from its own checkpoint with the same metric
budget. Confirmation evaluates selected frozen/GEPA/random candidates once on sealed groups.

- [x] **Step 4: Run GREEN**

Run: `python -m pytest -q tests/test_gepa_adapter.py tests/test_orchestrate.py`
Expected: all tests pass.

### Task 5: CLI, actionable refusal, manifest, runbook, and CPU preflight

**Files:**
- Create: `source/gepa_three_route/cli.py`
- Create: `tests/test_cli.py`
- Create: `RUNBOOK.md`
- Create: `manifest.json`

**Interfaces:**
- Consumes all prior tasks.
- Produces `python -m gepa_three_route.cli {preflight,fixture,explore,confirm}` and immutable handoff.

- [x] **Step 1: Write failing CLI tests**

Assert JSON diagnostics and nonzero exit status for missing provider/corpus, source drift, fixture
research misuse, dirty external repos, and confirmation without a positive gate. Assert preflight
is read-only, fixture run is deterministic, resume is idempotent, and success output includes every
artifact/hash and exact future launch command.

- [x] **Step 2: Run RED**

Run: `python -m pytest -q tests/test_cli.py`
Expected: collection failure because `gepa_three_route.cli` does not exist.

- [x] **Step 3: Implement CLI and documentation**

Catch only typed refusal errors at the boundary and emit one canonical JSON object. `preflight`
authenticates sidecar/external pins and descriptor without model calls. `fixture` requires an output
under `engineering-fixtures/`. `explore`/`confirm` require research descriptors and attempt paths.
RUNBOOK documents external environment construction, no-port CPU verification, dependency blocker,
launch/resume/confirm commands, outputs, decision rules, and recovery. Generate manifest hashes only
after every immutable file is final; exclude caches, attempts, checkpoints, and the manifest itself.

- [x] **Step 4: Run all CPU tests and preflight**

Run:

```bash
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONPATH=source python -m pytest -q tests
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONPATH=source python -m gepa_three_route.cli preflight \
  --engineering-only --json
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONPATH=source python -m gepa_three_route.cli fixture \
  --output engineering-fixtures/preflight
```

Expected: tests pass; preflight reports pinned source authenticity plus the actionable missing
research-provider blocker; fixture completes only under `engineering-fixtures/`.

- [x] **Step 5: Verify immutable manifest**

Run a stdlib verification script that parses strict JSON, recomputes every manifest hash, confirms
all external repository commits/worktrees remained unchanged, asserts no sockets/GPU artifacts in
the sidecar, and prints the exact launch blocker and command.
