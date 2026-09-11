# Executable RLM research from primary papers and official code

Snapshot: 2026-09-02 UTC. No GPU jobs or model downloads were run. “Claim” below means a
paper/blog/repository claim; “inference” means my proposed experiment, runtime, or feasibility
judgment. Repository commits and cached assets are frozen in the companion JSON inventory.

## Decision

Start with **GEPA over the existing three-route RLM harness**. It is the fastest clean test of
model–harness co-adaptation: the verifier already supplies exact feedback, GEPA can optimize an
arbitrary textual/programmatic candidate against local endpoints, and the test needs inference
only. In parallel, prepare—not yet launch—the **reduced MRCRv2 RLM RLVR reproduction**. That is
the most informative weight-training study, but current `rlm` and current `prime-rl` use
incompatible config schemas and the original repository does not release its MRCR environment.

## Ranked experiments

| Rank | Falsifiable experiment | Minimal intervention and paired baseline | Metrics | Two-A100 mapping | Estimated duration* |
|---|---|---|---|---|---|
| 1 | **GEPA × three-route harness.** Does verifier-guided evolution discover a harness that improves held-out route qualification without overfitting templates? | Wrap the current harness as a GEPA candidate and emit answer, trace, exact verifier score, feasibility flags, tokens, and latency as ASI. Compare with the frozen current harness and equal-metric-call random/local mutations on the same train/validation split. | Held-out exact score; per-route score; duplicate/invalid rate; model calls, input/output tokens, latency; train–validation gap. | One model replica per A100; coordinator on CPU. | 3–6 h for 50–100 metric calls. |
| 2 | **Reduced MRCRv2 RLM RLVR.** Does LoRA training at 32–64K/2 needles improve 8-needle and longer-context performance because the root learns orchestration, not merely code-assisted retrieval? | Port released MRCR CSV scoring into the original RLM depth-1 trainer; Qwen3-4B LoRA, frozen leaves/shared policy arm. Mandatory controls: direct/no-tool, direct+identical code tool, untrained RLM+code, trained RLM+code. Start with the cached 4–8K shard, then 32–64K. | Exact MRCR score by length×needle; tool calls; turns; child calls; token/latency tail; malformed/timeout rates. | A100-0 trainer, A100-1 vLLM inference via prime-rl; start 32K, batch 4–8, group 4, 20–50 steps. | Smoke 1–3 h; reduced run 6–18 h. |
| 3 | **Reasoning Gym weight×harness crossover.** Does RLVR improve compositional transfer specifically when the learned model controls an RLM decomposition harness? | Train Qwen2.5-1.5B or Qwen3-4B on procedurally generated low-complexity components. Evaluate the full 2×2: base/RLVR weights × direct/RLM harness, on held-out seeds and compound/curriculum extrapolation. | Exact reward, unseen-seed and unseen-composition accuracy; calls/tokens/latency; interaction effect with bootstrap CI. | Official topology is one training GPU plus one vLLM GPU. | 2–6 h at 100 steps; 12–30 h at 500 steps. |
| 4 | **Matched-budget RLM-family ablation.** Which inductive bias matters: open REPL search, SRLM trajectory selection, or Lambda-RLM typed decomposition? | Add (a) K=4 candidate-program selection and (b) the Lambda typed split/map/reduce controller around the same leaf model and exact scorer. Match total calls, generated tokens, and wall-clock cap; use original RLM as baseline. | Accuracy vs calls/tokens/wall time; selection oracle gap; route/depth distribution; failure and truncation rate. | One replica per A100; parallel candidates/subcalls. | 2–6 h inference-only. |
| 5 | **Audited tree-credit training.** Does broadcasting root outcome to every parent/child step outperform root-only outcome training? | Transplant SkyRL’s RLM environment only after adding a CPU test that proves root advantage is copied to every descendant. Compare root-only, explicit tree-broadcast, and Agent Lightning rollout aggregation under identical groups. | Root reward, child evidence F1, parent paper-selection F1, entropy/KL, token-normalized gain, instability. | Prefer Qwen3.5-2B or Qwen3-4B LoRA; one trainer plus one inference GPU. | 6–18 h after a 1–2 h CPU/config gate. |

\*Durations are engineering estimates, not paper claims, and assume two local A100 40GB GPUs.
Long-context memory and rollout variance are the dominant uncertainty.

### Evaluation design that makes the claims identifiable

Use group splits, never row-random splits: hold out generator seeds, surface templates, context
length bands, needle counts, and at least one unseen composition of familiar primitives. Report the
full 2×2 weight×harness interaction, not only a winning diagonal. Freeze a model-call/token budget
and separately report wall time so parallel methods do not gain hidden compute. Bootstrap by task
group; keep invalid, timeout, and tool-error outcomes in denominators. The foundational lesson from
[intermediate representations for compositional generalization](https://arxiv.org/abs/2104.07478)
is directly relevant: representation/harness choice can itself drive out-of-distribution gains, so
typed Lambda-style representations must be crossed with weights rather than credited to training.

## RLM-family implementation comparison

### Original RLM v3

- **Claim/source:** [Recursive Language Models](https://arxiv.org/abs/2512.24601),
  [official code](https://github.com/alexzhang13/rlm).
- **Unit/context:** an iterative root writes Python into a persistent REPL. Raw context is stored
  as `context_0`; the root normally sees context type/character metadata, not raw context, unless a
  small separate `root_prompt` is supplied.
- **Queries/concurrency:** `llm_query`/`rlm_query` and batched variants; batched calls are parallel.
  Recursive children get fresh REPLs. Runtime guards cover depth, iterations, tokens, cost, time,
  and errors.
- **Observation:** stdout/stderr and variable names return to the model; code output is truncated at
  20,000 characters. Root history can be compacted.
- **Training:** `training/` integrates `verifiers` and prime-rl at depth 1. The current example is
  Qwen3-30B-A3B LoRA, 200 steps, 8,192 sequence length, four trainer plus four inference GPUs, with
  OOLONG spam 32–64K training and TREC 131K evaluation. Exact entry point:
  `uv run rl @ training/configs/rlm-qwen3-30b-example.toml`.
- **Datasets:** inference benchmarks include OOLONG, S-NIAH and CodeQA-style tasks; current training
  exposes OOLONG, not MRCRv2 or the LongBenchPro SFT trajectories.

### SRLM

- **Claim/source:** [Self-selecting Recursive Language Models](https://arxiv.org/abs/2603.15653).
  I found no author-linked official code repository as of this snapshot.
- **Unit/context:** K independently sampled executable REPL programs slice/query/aggregate the
  external context. Explicit recursive calls are not required.
- **Selection/budget:** plurality answer, verbalized confidence and reasoning length select among
  candidates. The paper reports BrowseComp+, OOLONG and LongBench-v2 results and up to 22% higher
  accuracy than RLM at matched wall time. Code-level observation truncation, runtime budget API,
  and training hooks cannot be verified without a release.

### Lambda-RLM

- **Claim/source:** [Lambda-RLM](https://arxiv.org/abs/2603.20105),
  [official code](https://github.com/lambda-calculus-LLM/lambda-RLM).
- **Unit/context:** a deterministic typed `Phi` recursion composes Split, optional relevance
  filtering, Map, and symbolic/LM Reduce. The detector receives metadata plus a 150-character
  context preview; full context remains in the REPL.
- **Queries/concurrency:** leaf execution is one LM query; inspected map/reduce loops are sequential,
  with no batch/parallel path. Planning computes depth/chunk/cost from context-window constraints,
  but there is no original-RLM-style live USD/token/turn guard.
- **Observation/training:** direct variable return rather than an iterative observation loop; no
  verifier or RL trainer. Benchmarks cover S-NIAH, OOLONG, BrowseComp and CodeQA. The paper reports
  29/36 wins over RLM and up to 4.1× lower latency.

### Recursive Agent Harnesses

- **Claim/source:** [Recursive Agent Harnesses](https://arxiv.org/abs/2606.13643). The paper says
  implementation/evaluation/scoring will be released; I found no official release to clone.
- **Unit/context:** each recursive unit is a full filesystem/shell/planning/subagent harness. The
  parent sees the task plus filesystem corpus, not the whole corpus in neural context. It uses
  structured calls for a few children and generated asynchronous scripts for many; children inherit
  spawn ability.
- **Evidence:** evaluated on 199 OOLONG-Synthetic tasks at 1K–4M tokens. Exact prompts are in the
  appendix, but code-level budgets, observation truncation, and training hooks remain unverifiable.

### SkyRL “Reinforcing Recursive Language Models”

- **Claim/source:** [official research report](https://www.alphaxiv.org/blog/reinforcement-learning-for-rlms),
  [official SkyRL code](https://github.com/NovaSky-AI/SkyRL). This is a research report, not an arXiv
  paper.
- **Unit/context:** parent and child are the same policy. Both run multi-turn Python REPL loops; raw
  context stays in the REPL, while the root question is re-injected ephemerally each turn. Children
  can receive a context override. `rlm_query_batched` dispatches children in parallel.
- **Budget/observation:** released environment defaults to 10 turns and a 180-second REPL timeout.
  stdout/stderr are returned without an explicit character truncation in the inspected RLM layer.
- **Training/data:** the released evidence-selection environment builds Parquet from
  `alphaXiv/multi-paper-synthetic`, scores parent evidence, logs child/paper-selection diagnostics,
  and flattens child and parent step-wise trajectories. Published launch uses Qwen3.5 evidence SFT,
  GRPO group 8, 32K prompt, six turns, four trainer GPUs and TP=4 inference: eight GPUs total.
- **Important audit result:** the report says child trajectories inherit the parent advantage and
  the config docstring says reward is propagated. At commit `955c3e2`, however, child environment
  rewards are explicitly `0.0`; the generator concatenates child outputs without rewriting rewards;
  and the generic trainer computes terminal advantages per trajectory. On literal inspection, that
  is not explicit parent-to-child advantage inheritance. The environment is transplantable; the
  claimed tree-credit rule is not safe to transplant until a regression test demonstrates it.

### TimeRLM

- **Claim/source:** [TimeRLM](https://arxiv.org/abs/2608.03391),
  [official code](https://github.com/OpenTSLM/TimeRLM).
- **Unit/context:** JSON/file-backed time series in persistent IPython with NumPy/SciPy, optional
  plots and optional recursive sub-RLM. The released RL evaluation normally disables recursion.
- **Hooks/data:** deterministic generators and continuous verifiers for five time-series tasks; 157
  CPU tests in the cached snapshot. The paper describes 300 steps, while its released “paper row”
  config specifies Qwen3.5-4B full-parameter, 400 steps, 64K, batch 128/group 8, two trainer plus two
  external inference GPUs. The README also says paper-time prime-rl patches are not included or
  pinned, so this is a useful benchmark substrate but not an immediate exact reproduction.

## Original RLM MRCRv2 reproduction audit

The v3 appendix reports: 750 English LongBenchPro tasks ×3 candidates = 2,250; filtering score-zero
and one-turn-or-shorter trajectories leaves 1,072. Each root turn becomes one SFT record; turns over
about 100K characters are removed; malformed final directives are programmatically repaired. The
appendix reports batch 64, 300 SFT steps and 48 H100-hours.

For MRCRv2 it reports Qwen3-4B, depth 1, 32–64K/2-needle training, 150 steps, batch 128 × four
rollouts, 4,096 output tokens per turn and 20 RLM iterations, with 512K–1M/8-needle evaluation every
50 steps. These are paper claims. The official `rlm` tree does **not** expose MRCR/MRCRv2 generation,
scoring, data, training config, LongBenchPro trajectories, or filtering/repair scripts. An open
[data-availability issue](https://github.com/alexzhang13/rlm/issues/158) corroborates that gap.

The official [DeepMind MRCRv2 release](https://github.com/google-deepmind/eval_hub/tree/master/eval_hub/mrcr_v2)
does expose generation/evaluation scripts and CSV URLs. Its source-text generator calls Gemini, but
released CSVs avoid that dependency. The smallest official 4–8K/2-needle shard is cached locally;
the 32–64K shard is 37,975,202 bytes and was deliberately not downloaded yet. MRCR’s own README
warns that tool access makes the task much easier, so every result must state the tool condition.

Recommended reduced protocol:

1. Validate parsing/scoring on the cached 4–8K shard and freeze held-out rows by source index.
2. Add the released 32–64K/2-needle shard only after the smoke gate. Use LoRA Qwen3-4B, depth 1,
   10–20 turns, batch 4–8, group 4, 20–50 steps; preserve the paper’s 4,096 per-turn cap where memory
   permits.
3. Evaluate frozen 4–8K/2-needle, 32–64K/2-needle and at least one longer 8-needle band. Treat
   512K–1M as a stretch gate, not a required first run on A100 40GB.
4. Run identical code/query tools for direct and RLM conditions. The decisive statistic is the
   trained-weight × harness interaction, not trained RLM versus an artificially tool-less direct arm.

## Training framework audit

### prime-rl

[Official prime-rl](https://github.com/PrimeIntellect-ai/prime-rl) is locally runnable without a
platform service: its current docs default to one trainer plus one inference GPU, and
`CUDA_VISIBLE_DEVICES=0,1 uv run rl @ rl.toml` is the intended topology. Official configs include
Qwen3-4B-Instruct LoRA rank 8 for wiki-search and Qwen3-4B LoRA rank 32 for alphabet-sort. W&B can
be disabled/offline; LoRA forces filesystem adapter synchronization into vLLM.

Two-A100 judgment: Qwen3-4B LoRA at short/moderate sequence length is structurally supported. An 8B
LoRA may fit with conservative sequence length and offload, but it is not the official example.
Single-trainer-GPU 32–64K activation memory and rollout tails require an empirical smoke gate.
Dependencies require Python 3.12, CUDA, vLLM, and submodules; some git dependencies use SSH URLs.
FlashAttention-3 is Hopper-only, so A100 needs FA2/another supported backend.

Exact blocker: current `rlm/training/configs/rlm-qwen3-30b-example.toml` uses older prime-rl keys
(`[[orchestrator.train.env]]`, `[inference.model]`, `[inference.parallel]`, `[trainer.ckpt]`), while
cached current prime-rl expects `[[orchestrator.train.source]]`, `[inference.vllm]`, and top-level
`[ckpt]`. The RLM training dependency is not commit-pinned. Pin a compatible prime-rl revision or
migrate and validate the config before launching.

### Agent Lightning

[Agent Lightning](https://arxiv.org/abs/2608.17528) separates a trainer, an HTTP gateway that records
real agent traces, and local/Kubernetes controllers. Its official Calc-X path runs locally on one
A100 with Qwen2.5-1.5B, GRPO batch 32/group 4, 4,096 prompt/2,048 response, FSDP CPU offload. It is a
credible phase-two adapter for the existing harness. Current v1 tests cover rollout aggregation and
rollout-level loss; a new per-turn or tree-structured credit rule would be our intervention, not an
official implementation claim.

## Minimal transplants worth testing

1. **SRLM selector:** K=4 or 8 existing RLM trajectories; compare single rollout, plurality,
   confidence×length and exact-verifier oracle at equal call budget.
2. **Lambda typed controller:** replace unconstrained decomposition with frozen typed split/map/reduce;
   keep leaf model, context and calls fixed.
3. **Parallelism-only ablation:** use original RLM’s batched child API with identical prompts/results;
   compare latency and tail failures against sequential Lambda-style mapping.
4. **Shared-policy root adaptation:** LoRA-train root/child shared weights while leaves remain frozen;
   cross with direct versus RLM harness to isolate true model–harness co-adaptation.

## Cached artifacts and limits

- Eleven official repositories were cloned; all tracked worktrees are clean. Exact commits/licenses
  are in the JSON inventory.
- Cached MRCR file: `mrcr_v2p1_2needle_in_(4096,8192)_dynamic_fewshot_text_style_fast.csv`,
  2,492,336 bytes, 34,392 lines, SHA256
  `81f5e08995cbf2c1d55947a80cb71ce1a62743819c0b48b85b4d4d3b30e725f5`.
- No weights, large training splits, GPUs, replay artifacts or `RESEARCH_QUEUE.md` were touched.
- SRLM and Recursive Agent Harnesses have no verified official code release, so they were not cloned.
- Runtime estimates and two-A100 fit are explicitly inferences; run CPU config/parser tests and a
  one-batch memory smoke before reserving a confirmatory window.
