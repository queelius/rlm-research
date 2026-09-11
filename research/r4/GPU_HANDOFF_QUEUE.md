# Rolling GPU handoff queue

Updated: 2026-09-02 21:32 UTC. This is an adaptive launch queue, not a commitment to finish weak
arms. Idle reserved GPU time is treated as an irreversible cost; CPU preparation, downloads, tests,
and analysis should overlap accelerator jobs.

## Active

**Both 40 GB A100s:** trusted-synthetic prefix-cache crossover attempt 007 is live. It launched at
21:29:21 UTC after preserving the 29-row thinking-enabled attempt 006 as a zero-admission diagnostic.
GPU0 runs cache-on at port 8441 (PID 772399), GPU1 runs cache-off at port 8442 (PID 772403), and
phase-A driver PID 773854 is checkpointing every response. The strict TrainClient temperature/
adherence sidecar and boundary-factorial sidecar continue sealing in parallel. The unsafe MRCR v1
path remains blocked.

## Automatic next

Hard-RLVR and the strict Prime smoke are terminal; the direct-policy arm is not being extended.

1. Complete the safe prefix-cache crossover already being handed off to both GPUs.
2. Launch the strict, frozen-policy RLM temperature/adherence calibration as soon as its exact
   TrainClient/Qwen3-renderer/custom-inference contract, rootless scheduler, and manifest are sealed.
   Do not substitute the EvalClient path: the pilot exposed a client-path tool-call mismatch.
3. Stage the controlled RLVR boundary factorial as the next training-path experiment.
4. Keep MRCR blocked until its generated-code executor is containerized and resealed.

The direct-policy baseline uses the exact selected OOLONG rows and scorer but inlines the 4K context
into a normal text prompt. It is neither an RLM arm nor compute-matched to one; its purpose is to
exercise current Prime end to end and provide a clearly labeled reference condition.

## Completed predecessors

- The controlled replay reached 416/416 unique, HTTP-200, valid-JSON responses, was fsync'd, and
  released ports 8421/8422 cleanly.
- RLVR attempt 001 stopped at 12/72 calibration episodes because vLLM's default log-probability
  token strings lacked unambiguous numeric IDs. No optimizer step occurred. The evidence is retained;
  the minimal explicit-token-ID launch fix has a regression test.
- Corrected RLVR attempt 002 completed 72/72 calibration episodes. All 66 valid trajectories were
  exactly correct and six high-temperature trajectories were invalid, so the sealed mixed-reward
  rule performed no update. This arm is retired until a harder valid curriculum is sealed.
- Prime output attempt 8 failed before rollouts because the inherited launch environment hid the
  bundled CUDA compiler behind an inaccessible home path and targeted quota-full home caches. The
  deterministic CUDA/project-cache launch fix passes 18 tests; attempt 9 is the clean retry.
- Prime RLM attempt 9 passed non-eager compilation and step-0 LoRA broadcast, then every episode was
  rejected before a model turn because the current `rlm` harness declares `NEEDS_CONTAINER` and no
  supported container runtime is installed. Prime's zero-output gate stopped the run with no update;
  logs, metrics, traces, and the step-0 adapter are preserved and all processes were cleaned.
- Direct-policy attempt 1 loaded inference and trainer successfully, but Verifiers' hardcoded home
  runtime cache hit the full quota during task setup. All episodes were invalid and no update
  occurred. The exact traceback and artifacts are retained; this is a runtime-state failure, not a
  result about OOLONG difficulty or the policy.
- Direct-policy attempt 2 loaded both models and reached harness bootstrap. The project-local runtime
  cache worked, but Verifiers' unconditional `uv` reinstall targeted `$HOME/.local/bin` and failed
  before requests. No update occurred; the exact evidence is retained and processes were cleaned.
- Direct-policy attempt 3 completed four real LoRA updates and exited cleanly. Official heldout
  reward was unchanged at 2/8 before and after, with 16/16 valid eval traces and 72 valid train
  traces. The official substring fallback produced at least one nominal success without a required
  final answer, so a strict read-only reward audit is in progress before interpreting the result.
- Hard-RLVR attempt 002 completed 120/120 planned episodes and stopped with
  `no_calibration_coordinate`: 0 valid, 120 null rewards, 102 model-execution failures, 18
  wrong-shape trajectories, and zero optimizer steps. Both replicas shut down and ports 18431/18432
  were verified free. The first 96-record/eight-label coordinate was already below the validity
  floor, motivating the controlled boundary factorial rather than harder monotone rungs.
- The strict rootless Prime RLM smoke completed 8 step-0 eval and 32 training outputs, then fired its
  all-complete-groups-constant gate. Eval at temperature zero used Python and produced a valid
  terminal schema in 7/8 cases; training at temperature one did neither in 32/32 cases. Seven complete
  groups had strict rewards `[0,0,0,0]`, no update occurred, and cleanup proved GPUs, ports,
  processes, and containers were released. Four strict-invalid training outputs nevertheless earned
  positive official reward, so the old official-reward smoke is retired rather than used as filler.
- An additive trace audit found that 23/32 training outputs contained an intended-looking `ipython`
  call serialized as assistant text and 9/32 contained other text/code; none were structured tool
  calls. Eval had 7/8 structured tool calls. This makes the TrainClient/renderer path the immediate
  mechanism to preserve while sweeping temperature, rather than treating temperature as already
  causal.

## Inference-only fallback / follow-on

1. Frozen strict-RLM TrainClient temperature/adherence calibration across temperatures 0, 0.2, 0.5,
   0.8, and 1.0, using two inference replicas and the authenticated rootless runtime. The exact
   Qwen3 train renderer and custom inference path must remain fixed so the sweep first proves tool-call
   preservation and then distinguishes sampling effects from task difficulty.
2. GEPA versus frozen and equal-budget random/local mutation on the exact three-route harness, once
   the authenticated corpus/verifier/runner provider exists.
3. TimeRLM frozen-weight crossover on the regenerated 800-row AnomalyXL corpus: plain decimated
   prompt versus file-backed Python harness, with identical weights and explicit call/token/time
   budgets. Exact Qwen3.5-4B weights and task data are already local.
4. Adaptive diagnose-then-edit ODE search with one Qwen3-14B arm per GPU if the two text-context
   providers above are blocked.

## Preparation rule

Keep at least two executable jobs staged. Every GPU job must write durable phase checkpoints and a
terminal result/failure record. At every handoff, verify exact PIDs, ports, MIG UUIDs, checkpoint and
input hashes; terminate only the released job's process groups. Update `RESEARCH_QUEUE.md` from the
observed signal and retire arms that repeatedly fail to answer a decision-relevant question.
