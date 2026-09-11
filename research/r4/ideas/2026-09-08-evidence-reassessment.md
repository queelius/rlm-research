# Evidence reassessment, 2026-09-08

The strongest demonstrated learning is narrow supervised route following. No inspected RLM RLVR
attempt performed an optimizer update. The live queue was last updated September 2 and still calls
completed audits active; its "ready" entries assume two GPUs, while this allocation has one A100
40GB. Campaign reports inspected here date to August 29; the September 2 sidecars and audits are the
latest completed evidence found at resumption.

## What the evidence establishes

- **SFT:** Matched adaptive-plan SFT trained four rank-16 adapters on 2,304 controller decision
  states each. Both fixed and adaptive arms followed their assigned routes in 288/288 held-out
  development episodes across two training seeds. Both scored 144/144 on visible questions;
  conditional counts were 134/144 fixed versus 144/144 adaptive. Adaptive conditional leaf-input
  tokens fell 67.8% (290,968 to 93,586). This supports executing taught synthetic routines and
  reducing leaf work. It does not establish strategy discovery, novel-structure/domain transfer,
  broad generalization, or RLVR benefit. The visible-gain promotion criterion failed at ceiling.
- **Real RLVR update, direct policy only:** Current-Prime Qwen3-4B completed four LoRA optimizer
  steps with finite nonzero gradients and broadcasts. The completed scorer audit corrects the
  held-out result to strict exact **1/8 before and 1/8 after**, paired delta zero. Official 2/8
  included a truncated gold mention in each evaluation. Across 88 traces, 27 were official-exact
  versus 13 strict-exact; all 14 false positives were 2,048-token truncations. Aggregate
  reconstruction found zero contaminated examples in the four admitted batches, so the evidence
  does not show that these four updates exploited that artifact.
- **RLM zero-update runs:** The easy masked pilot collected 72 episodes: 66 technically admitted,
  all correct; hence no group-relative signal and no update. The harder curriculum collected 120
  episodes and also made no update. The strict containerized Prime RLM pilot completed 40 units,
  but all 32 training outputs had strict reward zero, no structured tools, and no admitted batch.
  Passing token capture, container execution, broadcast, and cleanup demonstrates systems function;
  it is not evidence that RLM RLVR improves policy behavior.
- **Trainability versus policy error:** The later hard-curriculum audit found **18/18 retained
  completions technically trainable**, despite the original exact-two-turn/one-leaf gate rejecting
  them. Two were schema-valid wrong answers; nine malformed JSON and seven wrong-schema outputs
  were observable policy failures. A complete action/logprob trace with an observable incorrect
  final answer can receive reward zero, including format errors. The 102 exception rows discarded
  terminal output and remain excluded/null, because outcome and complete capture are unavailable.
  One shape flag must not stand for infrastructure validity, terminal parsing, and trainability.
- **Client confound:** Seven of eight eval outputs used executed structured `ipython` calls;
  zero of 32 train outputs did. Twenty-three train outputs instead serialized intended-looking
  `ipython` calls as assistant text. Client/rendering path, tasks, and temperature all changed
  together. Temperature alone is not an identified explanation.
- **Serving drift:** The controlled 416-call replay established temperature-zero semantic-map
  variation in 10/52 prompt/GPU/mode conditions, including sequential serving. All 416 originating
  aggregate answers stayed exact. The prefix crossover is **incomplete: 123/320 rows, all phase A**,
  all HTTP 200 and strict map-valid, without a terminal seal. Its cache-off concurrent arm already
  has two semantic maps on each of five sentinels (eight repeats each): prefix caching is not
  necessary for variation in this subset. Cache effect size and prevalence remain unidentified
  because GPU/cache are confounded and prompts were selected for instability.

## Three ranked executable directions and actual readiness

1. **Matched EvalClient/TrainClient qualification, one endpoint.** This directly distinguishes a
   client/rendering failure from temperature sensitivity. Use four frozen strict training tasks,
   temperatures 0/0.5/1, both clients, and two paired repeats: 48 calls, maximum 2,048 completion
   tokens each, one Qwen3-4B+step-0 LoRA server, approximately 30–60 minutes with a 90-minute cap.
   Record actual structured/executed tools, intended text calls, strict terminal schema/correctness,
   complete errors and traces, token/logprob coverage, and paired differences. Do not require
   mixed reward merely to finish this diagnostic. Each episode is its own recoverable checkpoint.
   Root has authorized a new `sidecars/strict-rlm-client-qualification-v2` fork and owns server
   lifecycle; this audit agent is implementing its driver/spec/tests. The exact command will be:

   ```bash
   /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
     /project/alex_phd/runs/rlm-research-r4/sidecars/strict-rlm-client-qualification-v2/driver.py \
     --endpoint-url http://127.0.0.1:18601/v1 \
     --model strict-rlm-qwen3-4b-v0 \
     --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/strict-rlm-client-qualification-v2/outputs/attempt-001
   ```

   **Readiness at audit:** implementation in progress. The old temperature sidecar is not
   launchable unchanged: missing `MANIFEST.json`, stale plan hash, qualification function never
   selected by the driver, and an unconditional two-GPU launcher. Its declared plan hash is
   `a89f98e69d64902f7766116374bb433e278d8d00df2c655344107dd9aae8e2e3`; current recomputation is
   `ae7cef44c722cb637f9287f101cf6ca6ee0cc723694b220409515d03a49df08e`.

2. **One-GPU boundary factorial followed immediately by one masked update if signal exists.**
   Freeze the existing inventory at
   `sidecars/rlvr-boundary-factorial-v1/outputs/stage-a-attempt-001/inventory.json`. Cross
   64/80/96 records, coarse/fine ontology, and 4-turn/1-subcall versus 6-turn/2-subcall on the same
   server in counterbalanced blocks, with two task groups and three paired sampling seeds per
   cell (72 rollouts). This isolates the previous confounded difficulty jump. Preserve 610000/
   610001 task seeds and 940260100–102 sampler seeds. Existing host function
   `source/boundary_factorial.py:_run_container_episode` already accepts a single endpoint; the
   CLI collector instead requires two distinct endpoints/GPUs. Create a new serial-topology
   attempt rather than falsifying endpoint identity. About 45–90 minutes on one Qwen3-8B server;
   checkpoint every trajectory. Relax neither token capture nor infrastructure accounting.
   Correct the new attempt's reward semantics: complete malformed outputs are negatives, shape is
   descriptive. Existing `normalize_episode` still sets malformed completed outputs to null.

   **Readiness:** tasks, generator, container worker, model/adapter, and trainer exist; one-GPU
   collector and complete action export remain small required changes. Do not rerun the original
   all-zero hard curriculum. When a same-task group contains genuine positive and negative
   trainable outcomes, the existing one-GPU optimizer entry point is:

   ```bash
   CUDA_VISIBLE_DEVICES=0 \
   /project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python \
     /project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-e2e-pilot-v1/source/rlvr_pilot.py \
     train --group /absolute/new-attempt/training-group.json \
     --output /absolute/new-attempt/training
   ```

   Use its declared `5e-6` one-step recipe, retain checkpoint/optimizer/RNG state, and compare
   separate frozen tasks before/after. A mixed group is necessary for group-relative gradients;
   multiple confirmatory qualification rounds are not necessary for this exploratory update.

3. **Task-sensitive serving control on one GPU, only when an inference slot is available.**
   Reuse exact sentinels 0/1/5/6/8 from `exploratory/controlled-replay-20260902/spec.json`, but ask
   downstream count/argmax questions whose answers depend on the changed labels. Cross cache
   on/off with sequential/width-eight request dispatch in fresh-server ABBA blocks on the same
   GPU; 4 repeats per sentinel/cell (80 responses) first, 30–60 minutes, fixed temperature zero,
   seed zero and model snapshot. Save every response. Promote only if a task answer changes or
   serving-state variation materially alters an apparent checkpoint effect. This measures the
   practical impact missing from 416/416 unchanged originating answers.

   **Readiness:** prompt/variant assets and analysis are ready, but the existing
   `exploratory/prefix-cache-crossover-20260902/scripts/launch.sh` hardcodes two expired MIG UUIDs
   and appends to the interrupted result. A new one-GPU wrapper is required; there is no honest
   drop-in launch command for the current allocation. Do not delay an actual trainable RLVR
   update to finish a cache mechanism study.

MRCR, TimeRLM and GEPA should not displace these runs: their current sidecars still lack a safe
execution/provider boundary or the authenticated production corpus/provider. Existing engineering
fixture scores do not qualify as experiments.

## Source seals

Paths below are relative to `/project/alex_phd/runs/rlm-research-r4/`. SHA-256 values were read at
audit time; no source, queue, GPU, server, or historical run was changed by this audit.

| Source | SHA-256 |
| --- | --- |
| `RESEARCH_QUEUE.md` | `20c9672f6e91a1df79ad6c08d605a576be5edcb4d7a6e2b274624a59c0a1981f` |
| `analyses/direct-oolong-reward-audit-v1/FINDINGS.md` | `6d1bcd58bf47c05b40db65ea0f0ee8a2905e0fdf1f7d7f65d11a0ba9d8b1ecc5` |
| `analyses/hard-rlvr-terminal-audit-v1/FINDINGS.md` | `3b6d3c40083127bc6ec4210f02203755958f54bbb04446d00219cb17c8fa8413` |
| `exploratory/controlled-replay-20260902/artifacts/analysis.md` | `3abfdca9b1dc7e5425582fa353f8dc1bd9377042351001181c1c8ae16987da0e` |
| `exploratory/prefix-cache-crossover-20260902/artifacts/responses.jsonl` | `09e999ba82fc3a277849ccae067b7296c3aee6d32e48616ffa30ef78f876e3f2` |
| `sidecars/prime-rlm-strict-pilot-v1/outputs/qwen3-4b-oolong-rlm-strict-smoke-v1/CLIENT_PATH_AUDIT.md` | `49db9e1599aa6bdf5219c99a91d8698d683dc2a9fcf47f993d357057a9445798` |
| `sidecars/strict-rlm-temperature-adherence-v1/src/strict_rlm_temperature_adherence_v1/design.py` | `414094e987133357bd6581896f36620d3ab80a8449e31422a60907e26943cec7` |
| `sidecars/strict-rlm-temperature-adherence-v1/src/strict_rlm_temperature_adherence_v1/driver.py` | `326fe64512c0e7b425cf4e2d28e7c8a885cc0bd85e884b039f9e9519287b3838` |
| `sidecars/rlvr-boundary-factorial-v1/source/boundary_factorial.py` | `58fd42609dc1cae1850feaf3ec90c6f2e46b5a35927ac81dff868505b88d23de` |
| `campaigns/adaptive-context/studies/3521607a72229a88bb2ceec183efe07ae7ff34e89bdcff19153766ac15199ad5/analyses/360589aa57711afec25de42d6ef0f6970e19a2018898ce4ce920fe97b7574767/report.md` | `61b1ebe64f760910c1dfa4272a87f6a6b49216d43c056093e4c5978cf490f469` |

Scientific scope was also checked against
`/project/alex_phd/repos/rlm-bootstrap/docs/superpowers/specs/2026-08-28-adaptive-context-research-program-design.md`
and `/project/alex_phd/repos/rlm/docs/RESEARCH_OPERATIONS.md`.
