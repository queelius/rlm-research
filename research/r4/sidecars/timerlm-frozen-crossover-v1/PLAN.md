# TimeRLM Frozen-Weight Crossover Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CPU-verified, provenance-sealed inference sidecar comparing direct uniformly
decimated prompts with the official file-backed TimeRLM harness on paired AnomalyXL tasks.

**Architecture:** A standard-library control plane authenticates immutable inputs, seals the
stratified sample and opportunity budgets, renders direct prompts, adapts official standalone RLM
and scoring providers, records hash-linked attempts, and performs paired analysis. Heavy corpus,
tokenizer, scorer, and inference operations remain behind authenticated launch adapters; CPU tests
use narrow deterministic fakes and can never produce research evidence.

**Tech Stack:** Python 3.11+ standard library, pytest, Ruff, external isolated launch environment,
official TimeRLM and AnomalyXL sources by SHA-256.

**Spec:** `DESIGN.md` at approved SHA-256
`6c7e545625586cd77f106b77388882b09150baf609889bb87b96387f1f950014`.

## Global Constraints

- Write only `/project/alex_phd/runs/rlm-research-r4/sidecars/timerlm-frozen-crossover-v1`.
- Do not use GPUs, open/probe ports, launch inference, or mutate cached repositories/shared envs.
- Official TimeRLM commit is `31fcd847b7cb37a1f1e6859b1dca7973ed0eae74` and must be clean.
- Corpus is exactly 800 rows, 344,449,211 bytes, SHA-256
  `23659b11e7181f8aebeb96c4a7f396ea76d33a2ffb86ec66182e712fdcdf20af`.
- Sample exactly 2 calibration and 6 confirmatory rows from each of 16 cells.
- Both arms use sealed ceilings of 900 seconds, 15 calls, 24,576 generated tokens, and 262,144
  cumulative context tokens per task; actual use is always recorded.
- Fixtures are engineering-only and never research evidence.
- This directory is not a Git worktree; manifest sealing replaces per-task commits.

---

### Task 1: Strict schemas, canonical identities, and provenance authentication

**Files:**
- Create: `pyproject.toml`
- Create: `source/timerlm_crossover/__init__.py`
- Create: `source/timerlm_crossover/core.py`
- Create: `source/timerlm_crossover/provenance.py`
- Create: `study.json`
- Create: `endpoint-descriptor.example.json`
- Test: `tests/test_provenance.py`

**Interfaces:**
- Consumes: immutable paths and hashes from `DESIGN.md`.
- Produces: `canonical_bytes`, `canonical_id`, `strict_load`, `Refusal`, `BudgetSeal`,
  `EndpointDescriptor`, `load_study`, `engineering_preflight`, and `authenticate_endpoint`.

- [x] **Step 1: Write failing provenance tests**

Test strict JSON duplicate/non-finite rejection; exact study fields and budgets; design, corpus,
model-manifest, tokenizer, chat-template, official-source, commit, and clean-worktree checks; endpoint
descriptor unknown/missing fields, stale descriptor hash, model path/name/hash drift, decoding drift,
and fixture-as-research rejection. Assert every refusal has stable code and remediation.

```python
with pytest.raises(Refusal) as error:
    authenticate_endpoint(path, study, mode="research")
assert error.value.code == "ENDPOINT_ATTESTATION_MISSING"
assert error.value.to_dict()["remediation"]
```

- [x] **Step 2: Run RED**

Run: `PYTHONPATH=source python -m pytest -q tests/test_provenance.py`
Expected: collection fails because `timerlm_crossover.provenance` does not exist.

- [x] **Step 3: Implement strict provenance boundary**

Use duplicate-detecting `json.loads`, canonical compact sorted JSON, SHA-256, exact-field schemas,
absolute paths, full commits/digests, bool-safe integer validation, and typed JSON refusals. Preflight
uses only filesystem reads and `git`; it never imports model/runtime packages or contacts endpoints.
Endpoint authentication requires a descriptor hash supplied out-of-band and exact agreement with
the sealed model/tokenizer/decoding/budget identity.

- [x] **Step 4: Run GREEN**

Run: `PYTHONPATH=source python -m pytest -q tests/test_provenance.py`
Expected: all provenance tests pass.

### Task 2: Deterministic stratified sample plan

**Files:**
- Create: `source/timerlm_crossover/sampling.py`
- Create: `tools/build_sample_plan.py`
- Create: `sample-plan.json`
- Test: `tests/test_sampling.py`

**Interfaces:**
- Consumes: public row envelopes `row_index`, `row_id`, `category`, `length`, `n_channels`, `seed`.
- Produces: `stratum_id`, `rank_rows`, `build_sample_plan`, `validate_sample_plan`, and the sealed
  128-row public sample plan.

- [x] **Step 1: Write failing sampling tests**

Create synthetic 16×50 public rows. Assert rank key is
`SHA256("timerlm-frozen-crossover-v1|" + row_id)`; each cell contributes ranks 0–1 to calibration
and 2–7 to confirmation; totals are 32/96; all identities are unique; source order does not alter
the plan; private/gold fields are rejected; and no calibration ID can pass a confirmatory selector.

```python
plan = build_sample_plan(reversed(rows))
assert Counter(row["split"] for row in plan["rows"]) == {
    "calibration": 32,
    "confirmatory": 96,
}
```

- [x] **Step 2: Run RED**

Run: `PYTHONPATH=source python -m pytest -q tests/test_sampling.py`
Expected: collection fails because `timerlm_crossover.sampling` does not exist.

- [x] **Step 3: Implement and seal sampling**

Implement exact schemas and deterministic sorting. `tools/build_sample_plan.py` accepts one JSONL
stream of public envelopes and writes canonical JSON; it never receives gold. Use the existing
read-only isolated AnomalyXL environment with `PYTHONDONTWRITEBYTECODE=1` only to stream the six
public columns from the authenticated parquet into the tool. Authenticate the resulting 16 cells,
50 source rows per cell, 128 selected rows, and 32/96 split before writing `sample-plan.json`.

- [x] **Step 4: Run GREEN and verify real plan**

Run: `PYTHONPATH=source python -m pytest -q tests/test_sampling.py`
Then run the CPU-only public-column extraction and `tools/build_sample_plan.py` command documented in
`RUNBOOK.md`; expected: exactly 128 selected public identities, no private columns.

### Task 3: Direct renderer, semantic adapters, and hard budget enforcement

**Files:**
- Create: `source/timerlm_crossover/budgets.py`
- Create: `source/timerlm_crossover/direct.py`
- Create: `source/timerlm_crossover/adapters.py`
- Test: `tests/test_budgets.py`
- Test: `tests/test_direct.py`
- Test: `tests/test_adapters.py`

**Interfaces:**
- Consumes: `BudgetSeal`, a tokenizer counter callable, public task/question, series, endpoint call
  callable, official RLM invocation callable, and official scorer callable.
- Produces: `BudgetAccount`, `audit_usage`, `retained_indices`, `render_direct`,
  `find_best_uniform_view`, `run_direct`, `prepare_rlm_workspace`, `run_rlm`, and `score_official`.

- [x] **Step 1: Write failing budget and renderer tests**

Assert `BudgetAccount.reserve_call` refuses the next call/context/output reservation above the seal;
`audit_usage` rejects provider actuals above or differing from the sealed arm budget for either arm;
direct always makes one call; indices include zero and the final point; the chosen stride fits and
the next-denser stride does not; all channels share indices; retained fraction is exact; prompt and
token counts are bound; and impossible fixed prompt overhead fails before an endpoint call.

```python
view = find_best_uniform_view(series, question, counter=fake_counter, context_limit=120)
assert fake_counter(view.prompt) <= 120
assert view.stride == 1 or fake_counter(render_with_stride(series, question, view.stride - 1)) > 120
```

- [x] **Step 2: Run RED**

Run: `PYTHONPATH=source python -m pytest -q tests/test_budgets.py tests/test_direct.py`
Expected: collection fails because budget/direct modules do not exist.

- [x] **Step 3: Implement budgets and direct view**

Use immutable counters and refuse before increment. Render `(original_index,value)` pairs with
channel names in stable source order. Search integer stride monotonically for the smallest fitting
complete chat prompt. Bind `stride`, point counts, retained fraction, prompt SHA-256, tokenizer
count, and tokenizer ID. `run_direct` passes remaining sealed limits to one endpoint call and audits
the complete returned usage.

- [x] **Step 4: Run adapter RED**

Write tests asserting the RLM workspace contains canonical full-resolution `context.json`, the
official prompt semantics, no image/sub-agent/MCP options, exact budget environment, normalized
session hashes/usage, and official scorer pass-through without alternate scoring. Run:
`PYTHONPATH=source python -m pytest -q tests/test_adapters.py`; expected missing module/functions.

- [x] **Step 5: Implement narrow semantic adapters and run GREEN**

Keep external work behind injected callables. The production launch provider imports the official
standalone `rlm`/AnomalyXL packages only after authentication. The sidecar prepares inputs and
validates outputs; it does not reproduce anomaly algorithms. Run all three Task 3 test files and
expect them to pass.

### Task 4: Append-only attempt ledger, checkpoints, and paired scheduler

**Files:**
- Create: `source/timerlm_crossover/ledger.py`
- Create: `source/timerlm_crossover/attempt.py`
- Test: `tests/test_ledger.py`
- Test: `tests/test_attempt.py`

**Interfaces:**
- Consumes: authenticated study/sample/endpoint identities and arm runner callables.
- Produces: `Ledger`, `AttemptSeal`, `create_attempt`, `resume_attempt`, `next_pairs`,
  `record_terminal`, `write_checkpoint`, and `run_split`.

- [x] **Step 1: Write failing ledger tests**

Require semantic record IDs, previous links, parent IDs, fsync append, complete terminal usage,
content-addressed atomic checkpoints, chain validation, and refusal on mutation, truncation,
duplicates, stale seals/checkpoints, changed budgets, or overwritten terminal pairs.

- [x] **Step 2: Run RED**

Run: `PYTHONPATH=source python -m pytest -q tests/test_ledger.py`
Expected: collection fails because `timerlm_crossover.ledger` does not exist.

- [x] **Step 3: Implement ledger and run GREEN**

Use `os.open(O_APPEND|O_CREAT)`, one canonical line plus `fsync`, whole-chain validation before
resume, same-directory temporary checkpoint plus fsync/rename, and pair uniqueness keyed by
`(split,row_id,arm)`. An attempt directory is created only after authentication.

- [x] **Step 4: Write scheduler RED tests**

Assert alternating arm order by row rank, identical row IDs and budget seals, invalid/failure score
zero, interruption/resume equality, completed-pair skipping, no fixture/research namespace crossing,
and exact 64 calibration / 192 confirmation terminal counts. Test an injected interruption and
byte-identical resumed terminal outcome.

- [x] **Step 5: Implement scheduler and run GREEN**

The scheduler loads series/gold only for the current authenticated row via the provider. It logs an
attempt record before invoking an arm and one terminal record for every outcome. It never retries a
terminal pair. Run both Task 4 files; expected all pass.

### Task 5: Split gate and paired confirmatory analysis

**Files:**
- Create: `source/timerlm_crossover/analysis.py`
- Test: `tests/test_analysis.py`

**Interfaces:**
- Consumes: complete terminal records and the authenticated sample plan.
- Produces: `authorize_confirmation`, `pair_rows`, `paired_bootstrap`, and
  `analyze_confirmation`.

- [x] **Step 1: Write failing analysis tests**

Require explicit authorization after complete 32-row paired calibration and zero accounting audit
failures; reject calibration IDs from confirmatory input; require both arms exactly once for all 96
rows; retain all raw pairs; compute paired mean RLM-minus-direct; deterministic row bootstrap;
category/cell summaries; invalid/failure rates; opportunity versus actual usage; and score per 1,000
tokens without division errors.

```python
with pytest.raises(Refusal) as error:
    analyze_confirmation([calibration_record], sample_plan)
assert error.value.code == "CONFIRMATORY_SPLIT_CONTAMINATION"
```

- [x] **Step 2: Run RED**

Run: `PYTHONPATH=source python -m pytest -q tests/test_analysis.py`
Expected: collection fails because `timerlm_crossover.analysis` does not exist.

- [x] **Step 3: Implement paired analysis and run GREEN**

Join only by authenticated row ID, keep failures at score zero, resample paired row objects with a
frozen seed, label the interval descriptive/non-significance, and serialize every raw pair. Run the
focused file; expected all pass.

### Task 6: CLI, engineering dry-run, runbook, and immutable manifest

**Files:**
- Create: `source/timerlm_crossover/cli.py`
- Create: `tests/test_cli.py`
- Create: `RUNBOOK.md`
- Create: `dependency-contract.json`
- Create last: `manifest.json`

**Interfaces:**
- Consumes: all prior components.
- Produces: `python -m timerlm_crossover.cli {preflight,fixture,calibrate,confirm,analyze}` and an
  immutable launch handoff.

- [x] **Step 1: Write failing CLI tests**

Assert one canonical JSON diagnostic and exit 2 for missing/stale endpoint descriptor, source drift,
attempt collision, confirmation without authorization, sample contamination, or fixture misuse.
Assert preflight opens no network connection, fixture is deterministic and ineligible for research,
resume is idempotent, and successful output names all artifact IDs/hashes.

- [x] **Step 2: Run RED**

Run: `PYTHONPATH=source python -m pytest -q tests/test_cli.py`
Expected: collection fails because `timerlm_crossover.cli` does not exist.

- [x] **Step 3: Implement CLI and documentation**

Catch only `Refusal` at the CLI boundary. `preflight --engineering-only` authenticates local inputs
without an endpoint. Research commands require an endpoint descriptor plus out-of-band descriptor
SHA. `fixture` writes only below `engineering-fixtures/`. RUNBOOK records the isolated environment,
public sample-generation command, CPU verification, dependency refusal, exact calibrate/resume/
confirm/analyze commands, two-A100 server mapping as launch instructions only, recovery, outputs,
and explicit non-claims.

- [x] **Step 4: Run complete CPU gates**

```bash
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
  python -m pytest -q tests
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
  python -m timerlm_crossover.cli preflight --engineering-only --json
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
  python -m timerlm_crossover.cli fixture --output engineering-fixtures/preflight
ruff check source tests tools
ruff format --check source tests tools
```

Expected: all tests/lint pass; preflight reports local authenticity and the missing endpoint launch
gate; fixture completes with `research_evidence_eligible=false`.

- [x] **Step 5: Seal and verify immutable manifest**

Generate `manifest.json` only after runtime/tests/docs/configs/sample plan are final. Include approved
design SHA, every immutable sidecar file hash, external source/model/corpus pins, and explicit
exclusions for manifest self-hash, mutable plan, caches, fixtures, attempts, and checkpoints. Run a
stdlib verifier that recomputes all hashes, confirms external Git state is unchanged, confirms no
GPU/socket code in the sidecar, prints the exact endpoint blocker and future launch command, and
exits zero.
