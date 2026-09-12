---
schema: rlm-v3-mrcr-rlvr-primary-review-v1
date_utc: 2026-09-12
paper: arxiv:2512.24601v3
paper_revision_date: 2026-05-11
scope: Qwen3-4B MRCRv2 RLVR result and released reproduction surface
status: verified_lead_but_not_reproduction_ready
source_scope:
  - arXiv v3 HTML and PDF, especially Figure 3 and Appendix A
  - official alexzhang13/rlm repository snapshot 854e688fbba9d8f8989e3da9989812e4b6dfe270
  - official Google DeepMind MRCRv2 release at eval_hub d5637d5cfb420a040ad550b2125c6aa23f71f9e4
  - official Qwen model card and MIT OASYS Hugging Face organization inventory
proposal_status: proposed_not_ready
gpu_shape: 1xA100-40GB
pilot_cap_seconds: 3900
checkpoint_policy: save_only_prestep_and_single_qualified_lora_update
---

# RLM v3 MRCRv2 RLVR: what is actually specified

## Bottom line

The May 11 v3 paper adds a real Qwen3-4B RLVR result, but it does **not** release a
reproducible MRCR training recipe. No official 4B MRCR checkpoint or exact MRCR training
environment was found.

This sharpens an already recorded lead rather than opening a ready reproduction. A one-A100
adaptation can still be a useful **mechanics and decomposition smoke test**, because MRCR has a
local deterministic target and needs no semantic classifier. It should not displace currently
ready experiments until a small frozen split and root-trajectory collector are prepared.

## Verified paper facts

- arXiv v3 was submitted May 11, 2026. In the main text and Figure 3(b), the model is
  `Qwen3-4B-Instruct-0527` in a depth-1 RLM. Training uses the 32K--64K, two-needle MRCRv2 split;
  evaluation uses the 512K--1M, eight-needle split. The plot reports length/needle transfer, but
  the paper does not tabulate exact plotted scores.
- Appendix A specifies 150 RL steps, batch size 128, four rollouts per example, at most 4,096
  output tokens per turn, and at most 20 RLM iterations. Evaluation occurs every 50 steps,
  including step 0. Training ran through `prime-rl` on Prime Intellect Lab.
- The text calls this “purely” RLVR. Therefore no **task-specific** SFT warm start is reported;
  this does not mean the base instruction model lacked prior post-training.
- MRCRv2 asks for the ordinal occurrence of one repeated writing response and a required random
  prefix. The released official metric gives zero if the prefix is absent, then applies
  `difflib.SequenceMatcher` to the predicted and target contents. The RLM paper does not say
  whether it used this exact current metric or another verifier.

Primary sources: [RLM v3 HTML](https://arxiv.org/html/2512.24601v3),
[RLM v3 PDF](https://arxiv.org/pdf/2512.24601v3), and
[Google DeepMind's MRCRv2 metric](https://github.com/google-deepmind/eval_hub/blob/d5637d5cfb420a040ad550b2125c6aa23f71f9e4/eval_hub/mrcr_v2/run_evaluation.py).

## What is trained: root versus leaf remains under-specified

The paper defines an RLM around one model M which generates root code and invokes M recursively,
so root and child calls are described as one shared policy. It does not state which generated
tokens receive policy-gradient loss in the MRCR run.

The **current** official training harness is informative but not proof of the May experiment. Its
`RLMTrainEnv` stores root completions in the multi-turn trajectory. Recursive calls are routed
through a proxy to the same trainer inference service and recorded as call metrics; they do not
appear as ordinary root trajectory turns. The most defensible reading of that current code is:
the live policy produces both root and child calls, terminal correctness rewards the episode, but
the directly optimized sequence is the root trajectory. The released files do not establish that
this was the exact v3 MRCR loss boundary.

Code inspected at `854e688fbba9d8f8989e3da9989812e4b6dfe270`:

- [`training/src/rlm_train/env.py`](https://github.com/alexzhang13/rlm/blob/854e688fbba9d8f8989e3da9989812e4b6dfe270/training/src/rlm_train/env.py)
- [`training/src/rlm_train/proxy.py`](https://github.com/alexzhang13/rlm/blob/854e688fbba9d8f8989e3da9989812e4b6dfe270/training/src/rlm_train/proxy.py)

## Released artifact inventory

| Artifact | Availability and revision | License / limitation |
|---|---|---|
| RLM paper | v3, May 11, 2026 | CC BY 4.0 on arXiv |
| Official RLM code | local inspected snapshot `854e688` (Aug 25, 2026) | MIT; current example is OOLONG with Qwen3-30B, not the 4B MRCR run |
| MRCRv2 data/generator/metric | `google-deepmind/eval_hub` HEAD `d5637d5`; selectable 2/4/8-needle length buckets | Apache-2.0; current public release postdates the original benchmark and is not identified as the paper's exact training bytes |
| Paper's 32K--64K two-needle file candidate | GCS object generation `1752091032747413`, 37,975,202 bytes, MD5/ETag `630f15242ff0cc9ac322e0264e732d8c` | Not downloaded in this pass; must be frozen and row-audited before use |
| Paper's 512K--1M eight-needle file candidate | GCS object generation `1752100869974551`, 1,524,193,914 bytes, MD5/ETag `64b73508e149de2f92a6a0a9c90832ae` | Intentionally not downloaded for this review |
| Exact 4B MRCR checkpoint/config | not found in the paper, official repository, or `mit-oasys` Hugging Face inventory | Third-party 4B RLM checkpoints are not paper artifacts |
| Qwen 4B base weights | `Qwen/Qwen3-4B` is public | Apache-2.0; paper's `Instruct-0527` naming should be resolved by config/tokenizer hash, not name similarity |

Official release sources: [RLM repository](https://github.com/alexzhang13/rlm),
[MRCRv2 README](https://github.com/google-deepmind/eval_hub/blob/d5637d5cfb420a040ad550b2125c6aa23f71f9e4/eval_hub/mrcr_v2/README.md),
[MRCRv2 downloader](https://github.com/google-deepmind/eval_hub/blob/d5637d5cfb420a040ad550b2125c6aa23f71f9e4/eval_hub/mrcr_v2/download.sh), and
[Qwen3-4B model card](https://huggingface.co/Qwen/Qwen3-4B).

## Smallest useful one-A100 pilot

This is an adaptation, not a reduced reproduction.

**Question.** On unseen MRCR rows, can one root-only LoRA RLVR update improve retrieval of the
correct ordinal response, and does any improvement survive a simultaneous increase in context
length and needle count? This removes our TREC helper's semantic-label bottleneck while retaining
a verifiable external-context action problem.

**Frozen design before any model outputs.** Use the already cached
`Qwen3-4B-Instruct-2507` base as both root and fixed child generator, with no TREC adapter. Select
eight non-overlapping 32K--64K/two-needle training rows and sixteen held-out 64K--128K/eight-needle
rows from the official release by a prespecified seed; store row hashes, GCS generation, tokenizer
hash, prompt renderer, and source-row IDs. The longer held-out tier is deliberately smaller than
the paper's 1M tier and must be labeled so. Depth is 1; external context stays outside the neural
prompt. Cap each root trajectory at six iterations, 2,048 tokens per turn, and a fixed sub-call
budget. Do not execute untrusted downloaded code; only the pinned local parser/verifier operates
on data.

**Adaptive run.** First collect four on-policy rollouts for each of the eight training rows
(32 trajectories) and score with the pinned official metric. Stop without training if there are
fewer than two mixed-reward groups, if protocol errors occur, or if the unchanged policy is at a
0.90 mean-score ceiling. Otherwise perform exactly one LoRA update from the unchanged base using
the repository's already qualified sequence-loss path, then evaluate unchanged and updated roots
on the same sixteen held-out coordinates and seeds. Child weights stay fixed, so the comparison
targets learned root inspection/decomposition rather than child content learning.

**Metrics.** Primary: paired held-out official MRCR score. Secondary: exact-match count, required
prefix validity, available finals, root iterations, REPL inspections, child calls, and physical
prompt/completion tokens. Report mixed/all-correct/all-wrong training groups separately. Inspect
whether successful trajectories actually read the external context; high score from a hard-coded
host answer path is invalid.

**Decision rule.** Promote to a fresh 128K--256K replication only if the updated root gains at
least 0.10 mean score or three net exact wins on the sixteen paired rows, with no loss of prefix or
completion availability and authenticated context use. Otherwise retire MRCR as a near-term RL
mechanics route. In particular, Google DeepMind warns that code access makes MRCR substantially
easier; a ceiling result would show that this benchmark is too weak for learned decomposition,
not that the RLM paper is contradicted.

**Compute and checkpoints.** One A100-40GB, 3,900 seconds total hard cap: 900 seconds initial
collection, 1,200 seconds one-update HF phase, and 900 seconds per pre/post evaluation service
allowance. Service and HF scoring/training must be sequential, never co-resident. Persist the
unchanged checkpoint identity, raw trajectories and rewards, action masks/log-probabilities,
single updated LoRA checkpoint, optimizer/RNG receipt, and all terminal failures. No later or best
checkpoint selection.

## Why this does not replace the current classifier program

MRCR's reward and host truth are cleaner, so the pilot is easier to interpret as an RL mechanics
test. Its decomposition demand is weaker: the RLM can use ordinary string parsing, and the official
dataset documentation explicitly says code tools make the task considerably simpler. Our TREC
setting instead tests semantic leaf work and aggregation. A positive MRCR pilot would show that a
root policy can learn an external-context procedure under clean reward; it would not establish
learned semantic recursion. A negative or ceilinged calibration should end this lead quickly.

## Local comparison and provenance

The existing research plan already recorded the 32K--64K/two-needle to 512K--1M/eight-needle
headline. New in this review are the exact Appendix A budgets, the missing-method inventory, the
current official root-trajectory seam, and the absence of an official 4B MRCR artifact.

- Existing plan SHA-256: `5aea22223f27d110d6a434145aa7c77138ef16f3286b1b1eb8e2cabd9c0d367c`
- Historical queue snapshot SHA-256: `ceb48eef93caeeb3bd522a17821f96b7d126786350c288c14befdcffaf11f06d`
- Local official `env.py`: `0caf3bfb2162ca884f34f0e6786f7bf546df0fa90e67f828039460f5f2f11efd`
- Local official `proxy.py`: `957636eda86fb2020378d4ada47e4099dfbd49d219754d53cc79aae517a538ea`
- Local official OOLONG env: `d7754e448399101035464b155c969303f321a872798dc94ffa35d0d87d3c9ad7`

Uncertainties are not filled from adjacent work: the later official OOLONG example and the
third-party Steno training artifacts cannot supply the paper's missing MRCR optimizer, reward,
hardware, or loss-boundary details.
