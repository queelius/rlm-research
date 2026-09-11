# TimeRLM executable audit and research use

Snapshot: 2026-09-02 UTC. Official repository commit
`31fcd847b7cb37a1f1e6859b1dca7973ed0eae74` was inspected read-only.

## Outcome

The AnomalyXL task substrate is immediately usable and provides a valuable independent test of
adaptive RLM context interrogation. Its isolated generator/scorer environment passes all 157 tests.
The exact documented seed-42 precise dataset was regenerated: 800 unique rows spanning 16K--131K,
1/2/16 channels, and five continuously scored task families. The 344,449,211-byte Parquet SHA-256 is
`23659b11e7181f8aebeb96c4a7f396ea76d33a2ffb86ec66182e712fdcdf20af`.

The official recursive harness is close to runnable but not reproducible from its declared lower
bounds alone. `mcp>=1.0` currently resolves MCP 2.1.1; that release renamed the imported
`streamablehttp_client`, so test collection fails. An external environment constrained to
`mcp>=1,<2` selected MCP 1.29.1 and restored the API. With project-volume UV/IPython/Jupyter scratch
paths, 92 of 93 harness tests pass. The remaining released inconsistency is deterministic:
`_should_include_git_history_guard()` returns `False` unconditionally, while the corresponding test
expects the guard for an IPython tool. No official source was modified.

The paper model, `Qwen/Qwen3.5-4B`, is cached at exact Hugging Face commit
`851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` with verified weight hashes. This means model, task
generator, gold scorer, and core harness are all locally available; a verifiers/training adapter
remains before GPU launch.

A direct import probe makes that adapter boundary concrete. TimeRLM's native v1 harness imports
`RolloutContext`, while current Prime-RL's pinned verifiers commit
`3ed6ef7c2cd4b08c3ddca426b4ea11a01c28d5b4` exposes `ModelContext`. Upstream renamed the type in
commit `c41a8b3354e73a2afffc01aed6efc4d1cb18abf1` on 2026-07-06; the TimeRLM snapshot is dated later
but still uses the old name. Thus current Prime-RL plus TimeRLM cannot be imported unchanged. A
standalone inference adapter can pin the pre-rename verifiers parent
`e3a90272e0ff637cd13784be9b0b9a8ef7796096`; a training study should instead port the small harness
surface to current `ModelContext` and regression-test setup, launch, trace, and reward semantics.

## Best first experiment

Run an inference-only matched crossover before training:

1. identical frozen Qwen3.5-4B weights with a plain prompt that receives a budget-matched decimated
   representation;
2. identical weights with the TimeRLM file-backed Python harness;
3. the same harness with explicit plot observations disabled versus enabled only if image serving is
   available;
4. a Python-harness control with the same call/token/wall-time caps but without the task-specific
   time-series prompt.

Use a group-balanced calibration slice to avoid floor/ceiling, then seal row IDs by category, length,
channel count, and generator seed. The primary endpoint is the official continuous category score,
not TimeRLM's composite reward, because its RLM reward also includes a length-efficiency term. Report
calls, input/output tokens, turns, wall time, invalid structured answers, and score per 1,000 output
tokens. This isolates harness benefit before attributing anything to RL.

If the frozen harness has measurable headroom and a nonzero success distribution, run short LoRA
RLVR with the official verifier. Cross the resulting checkpoint with both direct and RLM harnesses.
The weight-by-harness interaction answers whether training teaches a general time-series capability,
only better harness use, or both. If the base model collapses to no-anomaly answers, adopt the
released two-phase curriculum (negatives withheld first, then restored) as an explicit arm rather
than silently changing the data distribution.

## Reproducible artifacts

- Generator environment:
  `shared/environments/timerlm-anomalyxl-31fcd847.json`.
- Harness audit environment:
  `shared/environments/timerlm-rlm-harness-31fcd847.json`.
- Full generated data:
  `/project/alex_phd/research-cache/datasets/anomalyxl-31fcd847-release-seed42/`.
- Engineering smoke data:
  `/project/alex_phd/research-cache/datasets/anomalyxl-31fcd847-smoke/` (never research evidence).
- Frozen model:
  `/project/alex_phd/research-cache/models/Qwen--Qwen3.5-4B--851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a/`.

Do not claim an exact TimeRLM paper reproduction: the repository notes that its paper-time Prime-RL
patches are not included or pinned, and the released training configuration assumes four GPUs. The
proposed two-A100 study is a principled reduced adaptation with explicit provenance.
