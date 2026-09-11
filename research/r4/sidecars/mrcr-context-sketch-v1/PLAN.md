# MRCR Context-Sketch Ablation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CPU-verified, provenance-sealed runner for a paired vanilla-versus-sketch MRCR
RLM ablation with a separately labeled direct full-context reference.

**Architecture:** A small Python package authenticates official bytes, constructs the deterministic
sample and task-blind sketches, prepares immutable attempt workspaces, executes three arms through
an injected Responses transport, appends hash-chained terminal records, and analyzes paired results.
Research HTTP execution is gated by a descriptor byte hash; an in-process fixture exercises the
same orchestration without inference.

**Tech Stack:** Python 3.12, standard-library CSV/JSON/HTTP/hash/fsync primitives, Transformers
5.6.2 for the exact cached tokenizer, pytest, Ruff, uv.

**Spec:** `DESIGN.md`

## Global Constraints

- Do not start inference, open a port, use a GPU, or mutate any cached repository/model/dataset.
- Exact model revision: `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`.
- Exact RLM caps for both treatment arms: 8 calls, 2,048 output tokens per call, 16,384 generated
  tokens, 262,144 total reported tokens, and 600 seconds.
- The sketch consumes only the context body and is deterministic at no more than 4,096 UTF-8 bytes.
- Direct is an external full-context reference and is never called compute-matched.
- Every research descriptor is authenticated by caller-supplied SHA-256 before use.
- Every terminal record is append-only, fsynced, and recoverable without duplicate execution.

---

### Task 1: Frozen provenance and sample selection

**Files:**
- Create: `pyproject.toml`, `study.json`, `source/mrcr_context_sketch/{__init__,canonical,provenance,data}.py`
- Create: `tests/test_provenance.py`, `tests/test_data.py`
- Create: `data/sample-plan.json`

**Interfaces:**
- Produces `sha256_file(path)`, `authenticate_frozen_inputs()`, `load_source_rows()`,
  `split_context_and_task(row)`, and `build_sample_plan()`.

- [ ] Write failing tests that reject a changed source hash, prove exact 8+16 selection per band,
  four-stratum balance, split disjointness, stable IDs, and exact final-task suffix removal.
- [ ] Run `uv run pytest tests/test_provenance.py tests/test_data.py -q` and observe missing APIs.
- [ ] Implement only the authenticated constants, canonical hashing, CSV parser, and deterministic
  positional-quartile selector needed by those tests.
- [ ] Re-run the focused tests and generate `data/sample-plan.json` from authenticated sources.

### Task 2: Task-blind sketch and arm requests

**Files:**
- Create: `source/mrcr_context_sketch/sketch.py`, `source/mrcr_context_sketch/study.py`
- Create: `tests/test_sketch.py`, `tests/test_study.py`

**Interfaces:**
- Produces `build_context_sketch(context_body: str) -> str`,
  `build_arm_request(row, arm, context_relpath)`, and `arm_order(pair_rank)`.

- [ ] Write failing tests for deterministic output, a 4,096-byte upper bound, metadata/task/answer
  invariance, nine fixed sample positions, identical vanilla/sketch requests after removing the
  treatment block, identical RLM caps, exact direct input, and rotating arm order.
- [ ] Run the two focused files and verify failures are due to absent production functions.
- [ ] Implement the smallest sketch and request builders satisfying those observable contracts.
- [ ] Re-run focused tests and refactor duplicated request constants while green.

### Task 3: Exact official scorer and paired analysis

**Files:**
- Create: `source/mrcr_context_sketch/scoring.py`, `source/mrcr_context_sketch/analysis.py`
- Create: `tests/test_scoring.py`, `tests/test_analysis.py`

**Interfaces:**
- Produces `mrcr_v2_metric(prediction, target)`, `score_terminal(...)`, and
  `analyze_records(records, seed=...)`.

- [ ] Write failing tests that AST-extract the official function and establish parity on exact,
  missing-prefix, repeated-prefix, partial, empty, and non-string predictions.
- [ ] Write failing paired-analysis tests for sketch-minus-vanilla orientation, failure-as-zero,
  split exclusion, resource totals, deterministic bootstrap, and direct-reference labeling.
- [ ] Run focused tests to observe missing functions, then implement only the scorer and summaries.
- [ ] Re-run focused tests and preserve all task-level paired outcomes in the returned report.

### Task 4: Descriptor authentication and capped Responses transport

**Files:**
- Create: `endpoint.example.json`
- Create: `source/mrcr_context_sketch/endpoint.py`, `source/mrcr_context_sketch/transport.py`
- Create: `tests/test_endpoint.py`, `tests/test_transport.py`

**Interfaces:**
- Produces `authenticate_descriptor(path, expected_sha, attempt)`, `HTTPResponsesTransport`,
  `FixtureTransport`, and normalized `CallOutcome` records.

- [ ] Write failing tests for descriptor SHA mismatch, non-loopback URLs, wrong model/manifest/RLM
  identity, mismatched workspace/trace paths, missing launch attestation, timeout/error envelopes,
  RLM header parsing, and post-call cap rejection.
- [ ] Run focused tests and observe contract-specific failures.
- [ ] Implement strict schema authentication and injected transports; do not probe during preflight.
- [ ] Re-run focused tests and confirm fixture transport never opens a socket.

### Task 5: Immutable attempts, ledger, checkpoint, and resume

**Files:**
- Create: `source/mrcr_context_sketch/attempt.py`, `source/mrcr_context_sketch/ledger.py`
- Create: `tests/test_attempt.py`, `tests/test_ledger.py`

**Interfaces:**
- Produces `prepare_attempt(path)`, `Ledger.append_terminal(record)`, `Ledger.resume()`,
  `pending_keys(split)`, and atomic content-addressed checkpoints.

- [ ] Write failing tests for exclusive attempt creation, immutable workspace hashes, canonical
  request files, hash-chain mutation/truncation/duplicate rejection, stale checkpoints, fsync seam,
  and byte-identical idempotent resume.
- [ ] Run focused tests and observe absent behavior.
- [ ] Implement preparation, atomic writes, append+flush+fsync, validation, and pending-key recovery.
- [ ] Re-run focused tests, including interruption after append but before checkpoint replacement.

### Task 6: Orchestrator, CLI, and engineering fixture

**Files:**
- Create: `source/mrcr_context_sketch/runner.py`, `source/mrcr_context_sketch/cli.py`
- Create: `tests/test_runner.py`, `tests/test_cli.py`
- Create: `engineering-fixtures/README.md`

**Interfaces:**
- Produces CLI commands `preflight`, `prepare`, `fixture`, `run`, `analyze`, and `verify-manifest`.

- [ ] Write failing end-to-end tests proving three-arm execution, trace binding, descriptor-before-
  transport ordering, calibration-before-confirmation, explicit `--confirm`, resume skipping,
  fixture exclusion, and a complete task-level analysis artifact.
- [ ] Run focused tests and observe missing orchestration.
- [ ] Implement sequential orchestration through the injected transport and expose the CLI.
- [ ] Run fixture twice, proving the second invocation resumes without another fake model call.

### Task 7: Runbook, isolated environment, and immutable seal

**Files:**
- Create: `RUNBOOK.md`, `uv.lock`, `scripts/seal_manifest.py`, `MANIFEST.json`
- Create: `tests/test_manifest.py`

**Interfaces:**
- Produces a reproducible CPU environment, exact future launch commands, and a manifest over only
  immutable authored/data/provenance files.

- [ ] Write a failing manifest test that rejects drift and excludes attempts, outputs, trajectories,
  checkpoints, engineering fixture results, `__pycache__`, pytest, Ruff, and uv caches.
- [ ] Create the isolated environment at `/project/alex_phd/envs/mrcr-context-sketch-v1` using
  `/project/alex_phd/cache/uv-prime`, then lock dependencies without touching shared environments.
- [ ] Document preflight, prepare, vLLM/RLM launch, descriptor sealing, calibration, confirmation,
  resume, analysis, stop rules, output schema, and the direct-reference caveat.
- [ ] Run all pytest tests, Ruff check, Ruff format check, CPU preflight, fixture/resume, and shell
  syntax checks; then seal once and verify every manifest hash independently.
