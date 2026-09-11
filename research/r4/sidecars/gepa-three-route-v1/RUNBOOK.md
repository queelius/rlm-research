# GEPA × three-route v1 runbook

## Current status

The sidecar is CPU-verified and **not research-ready yet**. Its intentional launch blocker is
`AUTHENTICATED_PROVIDER_PENDING`: Task 2 provides the exact three-route generator, but no persisted
authenticated 36-group/108-task corpus or production loader/verifier/runner/proposal provider exists.
The sidecar will not regenerate that boundary, import test Oracle code, or treat engineering fixtures
as data.

Pinned inputs:

- GEPA: `/project/alex_phd/research-cache/repos/gepa` at
  `0632cdb5dcc052e690eab439e1b4a7e3e9cfe407`.
- Three-route generator commit:
  `66fcd3c05b929b63205b33c4f741f38e1c43b410`; source SHA-256
  `2489217efe189b25091629c0a43d40c344372a5ac1b97318f1ad4ccd29d7cfaf`.
- Sealed three-route config SHA-256:
  `f0f974b5c3153ee71f7b2e625aafeca010dce6c1e0546849910036b4506452b3`.
- The exact missing provider contract is [dependency-contract.json](../../../../ARTIFACTS.md#unpublished-files "Not published: dependency-contract.json").

## CPU-only verification

These commands do not import GEPA, open ports, contact a model, or enumerate/use GPUs:

```bash
cd /project/alex_phd/runs/rlm-research-r4/sidecars/gepa-three-route-v1

env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONPATH=source \
  python -m pytest -q tests

env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONPATH=source \
  python -m gepa_three_route.cli preflight --engineering-only --json

env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONPATH=source \
  python -m gepa_three_route.cli fixture \
  --output engineering-fixtures/manual-preflight-001
```

The fixture output must say `evidence_class="engineering_fixture"` and
`research_evidence_eligible=false`. It is an engineering check only. Never copy it beneath a research
attempt, merge it with research JSONL, or cite its scores.

## Publishing the future dependency descriptor

The upstream authenticated preparation task must first publish:

1. one immutable corpus artifact whose authenticated replay returns exactly 108 public tasks in 36
   groups;
2. one source file containing callable loader, exact verifier, candidate-aware runner, and audited
   GEPA proposal provider;
3. one exact frozen seed-candidate JSON object;
4. one strict descriptor with every byte hash, semantic identity, provider reference/contract, and
   disjoint 18/9/9 exploratory-train/development/confirmatory group inventory.

The callable signatures are frozen in [DESIGN.md](DESIGN.md). The loader performs upstream replay
before returning tasks. Public task envelopes contain only task/group ID, prompt, route,
organization, and nominal tokens. The verifier alone may access private gold; sidecar records retain
only its binary outcome, reason, observed answer, and gold digest.

Authenticate a descriptor without launching:

```bash
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONPATH=source \
  python -m gepa_three_route.cli preflight \
  --descriptor /absolute/path/to/three-route-gepa-dependencies.json \
  --json
```

Any refusal is one JSON object with `ok=false`, stable `code`, `message`, `remediation`, and
structured `details`. No attempt directory is created before authentication succeeds.

## External launch environment

Do not install into either cached repository or a shared environment. A launch operator may prepare
a separate environment and cache; these commands are instructions only and were not run by this
sidecar task:

```bash
uv venv --python 3.12 /project/alex_phd/research-cache/envs/gepa-three-route-v1

UV_CACHE_DIR=/project/alex_phd/research-cache/uv/gepa-three-route-v1 \
  uv pip install --python /project/alex_phd/research-cache/envs/gepa-three-route-v1/bin/python \
  /project/alex_phd/research-cache/repos/gepa
```

Before launch, repeat preflight with that interpreter and the descriptor. Preflight requires the
cached GEPA tracked worktree to be clean and at the pinned commit.

## Exact exploratory launch command

The sidecar itself remains CPU/client-only. The authenticated runner/proposal provider owns any
remote model endpoints; their model/renderer/harness identities are sealed by the descriptor.

```bash
cd /project/alex_phd/runs/rlm-research-r4/sidecars/gepa-three-route-v1

env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' \
  PYTHONPATH=/project/alex_phd/runs/rlm-research-r4/sidecars/gepa-three-route-v1/source:/project/alex_phd/research-cache/repos/gepa/src \
  /project/alex_phd/research-cache/envs/gepa-three-route-v1/bin/python \
  -m gepa_three_route.cli explore \
  --descriptor /absolute/path/to/three-route-gepa-dependencies.json \
  --attempt /project/alex_phd/runs/rlm-research-r4/attempts/gepa-three-route-v1-attempt-001
```

Matched budget is 432 candidate-task metric evaluations for GEPA and 432 for deterministic
random/local mutation. Frozen is evaluated once on all exploratory tasks. Every attempted pair
consumes a unit, including invalid and infrastructure outcomes. Model calls, input/output/cached
tokens, proposal-model cost, and elapsed time are retained as audits.

Resume after interruption with the same inputs and directory:

```bash
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' \
  PYTHONPATH=/project/alex_phd/runs/rlm-research-r4/sidecars/gepa-three-route-v1/source:/project/alex_phd/research-cache/repos/gepa/src \
  /project/alex_phd/research-cache/envs/gepa-three-route-v1/bin/python \
  -m gepa_three_route.cli explore \
  --descriptor /absolute/path/to/three-route-gepa-dependencies.json \
  --attempt /project/alex_phd/runs/rlm-research-r4/attempts/gepa-three-route-v1-attempt-001 \
  --resume
```

GEPA resumes from `attempt/gepa`; the sidecar reconstructs consumed metric units from the validated
lineage. The control resumes from its latest content-addressed checkpoint. A terminal result is
idempotently returned, never overwritten.

## Confirmatory launch

Do not run this command unless `exploratory-result.json` records `POSITIVE_LAUNCH` and
`proceed_to_confirmation=true`:

```bash
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' \
  PYTHONPATH=/project/alex_phd/runs/rlm-research-r4/sidecars/gepa-three-route-v1/source:/project/alex_phd/research-cache/repos/gepa/src \
  /project/alex_phd/research-cache/envs/gepa-three-route-v1/bin/python \
  -m gepa_three_route.cli confirm \
  --descriptor /absolute/path/to/three-route-gepa-dependencies.json \
  --exploratory-result /project/alex_phd/runs/rlm-research-r4/attempts/gepa-three-route-v1-attempt-001/exploratory-result.json \
  --output /project/alex_phd/runs/rlm-research-r4/attempts/gepa-three-route-v1-confirmatory-001
```

This evaluates frozen, selected GEPA, and selected random/local candidates exactly once per sealed
confirmatory task. The primary endpoint is group-macro exact accuracy; primary contrast is GEPA
minus frozen. Group-bootstrap intervals use the preregistered seed. Raw per-group outcomes are always
published, so alternative thresholds can be computed without new model calls.

The +0.02 half-budget futility rule and +0.03 positive-development-gain rule are operational
decisions, **not** p-values or claims of inferential significance. Other stops are >5%
infrastructure failures, >0.10 train–development overfit gap, >0.02 invalid-rate increase, identity
drift, lineage failure, or private-gold exposure.

## Attempt artifacts

- `lineage.jsonl`: append-only seal, proposal, evaluation, and checkpoint chain.
- `gepa/`: native pinned-GEPA checkpoint/resume state and agent-readable iterations.
- `gepa-result.json`: candidate pool, parents, validation scores, and metric-call count.
- `random-checkpoints/<sha256>.json`: content-addressed control state.
- `exploratory-result.json`: selected candidates, exact arm budgets, raw group outcomes, decision
  rule output, and ledger tail.
- `confirmatory-result.json`: raw group outcomes and preregistered contrasts.

Never edit an attempt. On authentication or chain failure, preserve it and start a new numbered
attempt only after diagnosing the machine-readable refusal.
