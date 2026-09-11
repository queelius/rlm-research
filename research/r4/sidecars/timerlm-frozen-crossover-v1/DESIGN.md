# TimeRLM frozen-weight crossover v1

Status: approved design, 2026-09-02 UTC.

## Question and evidence boundary

This sidecar tests whether TimeRLM's file-backed Python harness improves AnomalyXL performance for
the exact same frozen `Qwen/Qwen3.5-4B` weights and paired tasks relative to a direct, uniformly
decimated text prompt. It is an inference crossover, not a paper reproduction or a training study.
Engineering fixtures validate software only and are never research evidence.

The official TimeRLM repository is read-only at commit
`31fcd847b7cb37a1f1e6859b1dca7973ed0eae74`. The official v1 harness imports the removed
`RolloutContext` name, while current verifiers exposes `ModelContext`. The sidecar therefore uses a
small semantic adapter around the released standalone `rlm` package and official AnomalyXL loader
and scorer. It does not port Prime-RL, copy the harness, or change official source.

## Frozen inputs

- Corpus: official seed-42 800-row precise AnomalyXL parquet, SHA-256
  `23659b11e7181f8aebeb96c4a7f396ea76d33a2ffb86ec66182e712fdcdf20af`, 344,449,211 bytes.
- Model: `Qwen/Qwen3.5-4B` revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, using the
  complete file inventory and hashes in its local research manifest.
- Tokenizer: cached `tokenizer.json`, SHA-256
  `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42`, with the cached chat
  template SHA-256 `a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715`.
- Official adapter sources: `timeseries_qa.py` SHA-256
  `7f15c282814c85db1db168f9ad650dc155559b76671da4b32af2c15b6e9f346f`, precise dataset/scorer
  adapter SHA-256 `8e5f21bcdd06b6d3351796075463ec5cfa5ae6c34f92c8697fca2d2630ee1bf1`, v1 taskset SHA-256
  `04189d808f1574e13d25da5b7d894024acfdeddf20324cf2f9437576349d2685`, v1 program SHA-256
  `6a3c708b13cfbeb9728528d70648f4acca60ee0a17b9898d296aab7a2d01c61d`, and standalone engine
  SHA-256 `d09e86a6c8931146ce477cfe3554e73d9c33a8eef26bc344a8d72fc449727c01`.

Preflight authenticates every declared local byte and requires the TimeRLM tracked worktree to be
clean. A research endpoint descriptor must additionally bind the serving command, engine version,
model path, model manifest SHA-256, tensor-parallel topology, tokenizer path, chat template, served
model name, decoding parameters, endpoint identity, and a launch-attestation SHA-256. Preparation
does not start or probe a server.

## Deterministic sample and sealing

The corpus contains 16 cells keyed by `(category, length, n_channels)`, each with 50 rows. Within
each cell, rows are ordered by `SHA256("timerlm-frozen-crossover-v1|" + row.id)`, then by row ID.
The first two rows form calibration and the next six form confirmation. The resulting immutable
sample has 32 calibration and 96 confirmatory rows. The sample plan stores row ID, source row index,
category, length, channel count, seed, rank, and split, but no answer or private anomaly fields.

Calibration may tune only operational settings already named in this design: concurrency, launch
health, and whether the fixed opportunity caps are feasible. It may not change prompts, decimation,
scoring, sampling, endpoints, arms, or confirmatory analysis. Confirmatory row IDs are unavailable
to scoring and aggregation APIs until an explicit sealed confirmation command. Calibration rows are
rejected from all confirmatory estimates.

## Arms and prompt semantics

Both arms use the same task question, system policy, cached tokenizer, model identity, decoding
parameters, opportunity caps, and official category scorer.

### A: direct uniformly decimated text

The direct prompt contains one line per actual channel and the task question. For a stride `s`, it
keeps indices `0, s, 2s, ...` and always includes the final original index, rendering every retained
value with its original index. A monotone search chooses the smallest stride whose complete chat
prompt fits the sealed context allowance; this is the best tokenizer-fitting uniformly sampled
view. The record retains stride, original/retained points per channel, retained-input fraction,
complete prompt SHA-256, and actual tokenizer count. Direct makes exactly one model call.

### B: full-resolution file-backed Python/RLM

The task workspace receives the exact full-resolution series as canonical `context.json`. The
released standalone `rlm.run` loop drives a persistent IPython kernel against the same endpoint.
The task note is semantically identical to the official v1 `_build_note`; images, MCP, skills,
sub-agents, and automatic context compaction are disabled. The model returns one final JSON object.
The adapter records the official session log/meta hashes, turns, tool outcomes, usage, and answer.

The semantic adapter is intentionally narrow: construct the official prompt, create the exact
workspace file, set the released documented budget variables, invoke `rlm.run`, normalize its
answer/usage/session records, and score with `AnomalyXL.score_answer`/`score_metrics` in an isolated
launch environment. It contains no alternative anomaly logic.

## Matched opportunity budgets

Each paired task-arm attempt has the same hard ceilings:

- wall clock: 900 seconds;
- model calls: 15;
- generated tokens: 24,576;
- cumulative context/input tokens: 262,144.

The endpoint request wrapper owns the counters and refuses a request that would exceed any sealed
ceiling. A post-attempt audit independently rejects reported usage above the seal. Direct remains a
single-call method and may leave budget unused; the ceilings represent equal opportunity, not forced
consumption. Actual wall time, calls, generated tokens, context tokens, cached tokens, tool turns,
and stop reason are mandatory outcomes. Neither an arm nor a provider may silently substitute a
different budget.

## Scoring and analysis

The primary endpoint is the mean paired row difference
`official_continuous_score(RLM) - official_continuous_score(direct)` on the 96 confirmatory rows.
A deterministic paired bootstrap resamples row IDs and reports a percentile interval without
calling it a significance test. All 96 raw paired outcomes remain available.

Secondary summaries are cell/category differences, invalid structured-output rates, failure rates,
wall time, calls, retained-input fraction, and score per 1,000 generated and context tokens. Failed,
timed-out, invalid, and budget-exhausted attempts remain in the denominator with score zero. Results
must distinguish opportunity caps from actual use.

## Durable attempt semantics

An attempt directory is created only after all inputs authenticate. Its seal binds the sidecar
manifest, study, sample plan, corpus, model/tokenizer, endpoint descriptor, adapter sources, arm
order, and budgets. Records are canonical JSONL with semantic IDs, a previous-record hash, parent
IDs, and fsync after every append. Each task-arm terminal record binds request, output, usage,
workspace/session hashes, official scorer result, and error state.

Checkpoints are content-addressed, written atomically, and referenced by the ledger. Resume validates
the entire chain and seal, skips only completed task-arm pairs, and never overwrites a terminal
record. Duplicate pairs, mutation, truncation, changed order, source drift, stale checkpoint state,
or a second confirmation attempt fail closed. Arm execution order alternates deterministically by
row rank to reduce temporal confounding while preserving pairing.

## Launch gates and CPU validation

Engineering preflight verifies manifests, hashes, task plan, budget schema, adapter contract, clean
official source, and endpoint descriptor shape without opening a port. A dry-run exercises fake
in-process endpoint and scorer seams under `engineering-fixtures/`; it is labeled
`research_evidence_eligible=false`.

Research launch additionally requires the isolated environment lock, exact scorer import probe,
authenticated endpoint launch attestation, available attempt path, successful 32-row calibration,
zero unresolved usage/accounting mismatches, and explicit confirmation authorization. Inference is
not launched during sidecar preparation.

CPU tests cover strict parsing, provenance drift, complete stratification, split exclusion, direct
decimation maximality, retained fraction, workspace semantics, official scorer envelope adaptation,
budget refusal and post-audit for both arms, paired analysis, append-only recovery, idempotent
resume, fixture exclusion, endpoint gating, and immutable manifest verification. Ruff check and
format-check are required before sealing.
