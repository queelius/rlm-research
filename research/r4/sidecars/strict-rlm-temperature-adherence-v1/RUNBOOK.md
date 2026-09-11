# Strict RLM temperature/adherence calibration

## What this answers

The stopped strict Prime smoke compared held-out tasks at temperature 0 with training tasks at
temperature 1. It therefore could not tell whether the striking adherence difference came from
temperature or from different tasks. This inference-only calibration removes that confound.

It holds the exact 16 strict **training** task IDs, Qwen3-4B snapshot, step-0 rank-8 LoRA,
nano-RLM commit, strict scorer, rootless container image, call depth, and non-temperature request
options fixed. Each task is sampled four times at each temperature 0.0, 0.2, 0.5, 0.8, and 1.0.
Every four-response task-temperature group is split two-and-two across independent vLLM servers
on GPUs 0 and 1; the endpoint assignment and temporal order swap deterministically across blocks.

Primary outcomes are Python use and strict terminal validity. Strict correctness, recursive calls,
official-score disagreement, errors, turns, tokens, wall time, endpoint, seed, phase, and order are
also recorded. A group with both correct and incorrect strict rewards is immediately useful for a
later group-relative RLVR update. This exploratory run does not update weights.

The non-temperature request contract matches the stopped Prime **training** path: top-p 1,
top-k -1, min-p 0, logprobs and token-ID return enabled, cache salt `"0"`, and 2,048 maximum
completion tokens. The paired deterministic request seed is the deliberate new blocking factor;
it is held across temperatures for each task/repeat and recorded with endpoint, phase, and order.

## Safety and provenance boundary

Generated Python never executes on the host. Every episode uses the current Verifiers
`RLMHarness(version=4ef3438, max_depth=1)` and its proven setup path inside a newly provisioned,
authenticated rootless container. The sealed runtime is appropriate only for the trusted OOLONG
setup with unrestricted network access; it is not a production hostile-code sandbox.

`data/SPEC.json` binds all 16 task keys/hashes, the 320-coordinate plan hash, source/scorer/model/
LoRA/runtime hashes, request options, and stop rules. `MANIFEST.json` seals authored files but
excludes outputs and generated caches.

## CPU-only verification

```bash
root=/project/alex_phd/runs/rlm-research-r4/sidecars/strict-rlm-temperature-adherence-v1
strict=/project/alex_phd/runs/rlm-research-r4/sidecars/prime-rlm-strict-pilot-v1
official=/project/alex_phd/runs/rlm-research-r4/sidecars/official-rlm-prime-pilot-v1
rlm=/project/alex_phd/research-cache/repos/rlm
export PYTHONPATH="$root/src:$strict/src:$official/src:$rlm:$rlm/training/src:$rlm/training/environments/oolong"

CUDA_VISIBLE_DEVICES='' /project/alex_phd/envs/prime-rl-5990b1b/bin/pytest -q "$root/tests"
/project/alex_phd/envs/prime-rl-5990b1b/bin/ruff check "$root"
/project/alex_phd/envs/prime-rl-5990b1b/bin/ruff format --check "$root"
CUDA_VISIBLE_DEVICES='' "$root/scripts/launch.sh" dry-run
```

## Exact two-GPU launch

Launch only after both GPUs and ports 18601/18602 are released by the current owner:

```bash
/project/alex_phd/runs/rlm-research-r4/sidecars/strict-rlm-temperature-adherence-v1/scripts/launch.sh full
```

The launcher starts one exact vLLM+v0-LoRA server per GPU and one CPU driver per endpoint. It
refuses source/hash/image/port drift, stale rootless containers, or output overwrite. Expect about
45--120 minutes based on the earlier 40-episode systems run; the hard per-replica wall cap is six
hours. Each completed episode is fsync'd to its own atomically renamed JSON file. Interruptions
preserve completed coordinates.

Both servers inherit the proven Prime CUDA 13 `CUDA_HOME`/`CUDA_PATH`/binary environment. Each
replica gets a distinct project-volume vLLM, XDG, TorchInductor, Triton, and Humming cache tree, so
their non-eager compilation cannot race through shared writable cache files.

Resume only the same output and topology:

```bash
/project/alex_phd/runs/rlm-research-r4/sidecars/strict-rlm-temperature-adherence-v1/scripts/launch.sh full --resume
```

The run stops a replica when its execution error rate exceeds 25% after at least 20 units, at six
hours, or immediately on endpoint/hash failure. Adherence or reward remaining zero is a result,
not a systems stop condition.

Outputs land under `outputs/strict-rlm-temperature-adherence-v1/`: full episode records by
replica, server/driver logs, status files, `analysis.json`, and `ANALYSIS.md`. Analysis must treat
temperature as a within-task comparison and inspect the recorded endpoint/order fields before
attributing a transition to sampling.
