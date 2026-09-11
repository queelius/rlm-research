# TimeRLM frozen crossover v1 runbook

## Status and non-claims

The CPU control plane is prepared but research inference is intentionally not launched. Local
corpus, model, tokenizer, TimeRLM source, sample plan, budgets, analysis, and attempt mechanics are
sealed. Research launch still requires:

1. an endpoint attestation proving the exact cached Qwen3.5-4B weights are served; and
2. an isolated hash-bound semantic provider satisfying `dependency-contract.json`.

This boundary is explicit because released TimeRLM v1 imports `RolloutContext`, while current
verifiers exposes `ModelContext`. The sidecar adapts only the official standalone `rlm` and
AnomalyXL scorer semantics; it does not claim a TimeRLM paper reproduction. Engineering fixture
scores are never research evidence.

## CPU-only verification

```bash
cd /project/alex_phd/runs/rlm-research-r4/sidecars/timerlm-frozen-crossover-v1

env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
  python -m pytest -q tests

env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
  python -m timerlm_crossover.cli preflight --engineering-only --json

env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
  python -m timerlm_crossover.cli fixture --output engineering-fixtures/manual-preflight-001

ruff check source tests tools
ruff format --check source tests tools
```

Preflight reads and hashes local files and inspects Git state. It does not import a model runtime,
enumerate GPUs, open/probe a port, or contact an endpoint. The fixture must report
`evidence_class="engineering_fixture"` and `research_evidence_eligible=false`.

## Rebuilding the public sample plan

The committed plan is already sealed. This audit command reproduces it from only six public parquet
columns; it never emits answer, channel values, or anomaly fields:

```bash
set -o pipefail
PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/timerlm-anomalyxl-31fcd847/bin/python -c \
  'import json,pandas as pd; p="/project/alex_phd/research-cache/datasets/anomalyxl-31fcd847-release-seed42/anomalyxl-precise/data.parquet"; cols=["id","category","length","n_channels","seed"]; df=pd.read_parquet(p,columns=cols); [print(json.dumps({"row_index":i,"row_id":r.id,"category":r.category,"length":int(r.length),"n_channels":int(r.n_channels),"seed":int(r.seed)},separators=(",",":"))) for i,r in enumerate(df.itertuples(index=False))]' \
  | env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
      python tools/build_sample_plan.py --input /dev/stdin --output /tmp/sample-plan.audit.json
sha256sum /tmp/sample-plan.audit.json sample-plan.json
```

Expected SHA-256 is `3e6b0c4289f8b59d54b5ef4aa3b19ecf6dfb3d49c7a83d5b5c2b7e52a4fc6efe`.

## Isolated provider environment

Do not install into TimeRLM, a shared environment, or the model cache. An operator should create a
fresh environment such as `/project/alex_phd/envs/timerlm-frozen-crossover-v1-launch` using cache
`/project/alex_phd/cache/uv-timerlm-frozen-crossover-v1`, install pinned serving/client,
transformers/tokenizer, parquet, official `anomalyXL`, `timeseries_qa`, and `rlm-harness` packages,
then publish a full package freeze as the provider environment lock. MCP must remain `<2` for the
released harness. The provider source and lock are authenticated before import.

The provider contract is deliberately small: `build_provider(endpoint, study)` returns an object
with `run(public_sample_row, arm)`. It loads the row by authenticated `row_index`, delegates direct
rendering and RLM workspace semantics to this sidecar, invokes only official scorer callables, and
returns the exact terminal/usage envelope. Hard counters must wrap every model request.

## Endpoint and two-A100 mapping

Launch instructions only—these were not run. Serve the single exact cached model with tensor
parallelism 2 across the two A100s. Both crossover arms must use this one endpoint and served model
identity; separate per-arm servers are forbidden. Start from `endpoint-descriptor.example.json`,
replace the engine version and attestation placeholders, record the exact command/process/GPU/model
hashes in the attestation, then compute both descriptor hashes out of band.

Authenticate without running a task:

```bash
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
  python -m timerlm_crossover.cli preflight \
  --endpoint-descriptor /absolute/path/to/endpoint.json \
  --endpoint-sha256 ENDPOINT_DESCRIPTOR_SHA256 --json
```

This will continue to report `SEMANTIC_PROVIDER_REQUIRED` until the provider descriptor is supplied
to a research command.

## Calibration, resume, and confirmation

Exact calibration launch command:

```bash
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
  /project/alex_phd/envs/timerlm-frozen-crossover-v1-launch/bin/python \
  -m timerlm_crossover.cli calibrate \
  --endpoint-descriptor /absolute/path/to/endpoint.json \
  --endpoint-sha256 ENDPOINT_DESCRIPTOR_SHA256 \
  --provider-descriptor /absolute/path/to/provider.json \
  --provider-sha256 PROVIDER_DESCRIPTOR_SHA256 \
  --attempt /project/alex_phd/runs/rlm-research-r4/attempts/timerlm-crossover-calibration-001
```

Resume adds `--resume` with every other argument byte-identical. A complete 64-pair calibration
publishes `confirmation-authorization.json`. Confirmation is a single sealed 192-pair evaluation:

```bash
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
  /project/alex_phd/envs/timerlm-frozen-crossover-v1-launch/bin/python \
  -m timerlm_crossover.cli confirm \
  --authorization /absolute/calibration/confirmation-authorization.json \
  --endpoint-descriptor /absolute/path/to/endpoint.json \
  --endpoint-sha256 ENDPOINT_DESCRIPTOR_SHA256 \
  --provider-descriptor /absolute/path/to/provider.json \
  --provider-sha256 PROVIDER_DESCRIPTOR_SHA256 \
  --attempt /project/alex_phd/runs/rlm-research-r4/attempts/timerlm-crossover-confirmation-001
```

Use `--resume` only after interruption. Never create a second confirmation attempt. Analyze only a
complete confirmation ledger:

```bash
env -u VIRTUAL_ENV CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source \
  python -m timerlm_crossover.cli analyze \
  --attempt /project/alex_phd/runs/rlm-research-r4/attempts/timerlm-crossover-confirmation-001 \
  --output /project/alex_phd/runs/rlm-research-r4/attempts/timerlm-crossover-confirmation-001/analysis.json
```

The primary result is the paired mean official score difference, RLM minus direct. The interval is
a descriptive paired-row bootstrap, not a significance claim. Raw pairs, retained-input fraction,
failures, and actual resource use remain available for reinterpretation.
