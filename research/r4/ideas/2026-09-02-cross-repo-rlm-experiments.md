# Runnable RLM experiments from evolved-integrators and SDB

Date: 2026-09-02. Read-only survey of clean trees at
`evolved-integrators@3badcec` and `structured-decomposition-benchmark@c7ee381`.
No GPU was used.

## What the evidence says

- SDB has already separated report production from report use. In DEV-004,
  natural workers were exact on 7/15 reports, advisory synthesis followed the
  tuple on 1/5 roots, and binding followed it on 5/5; raw and compute-matched
  direct each solved 2/5, advisory 1/5, and binding 3/5. Both `FOUND` roots
  failed everywhere. DEV-005 then repaired only 1/8 wrong reports, harmed 4/7
  correct reports, and produced zero wrong-to-correct tuple transitions.
  Evidence:
  `experiments/rq-001-fixed-decomposition-value/dev-004-fcr-natural-worker-screen/runs/dev-004-launch-attempt-001/RUN.md`
  and
  `experiments/rq-007-targeted-report-revision/dev-005-fcr-single-report-revision-oracle/runs/dev-005-launch-attempt-001/RUN.md`.
- Consequently SDB's current P0 is RQ-008: attach a locally checkable
  certificate, screen acceptance precision/coverage before synthesis, then
  compare verified reports against raw direct, compute-matched direct,
  advisory, binding, and exact-report oracle. It explicitly rejects another
  learned selector until the action has headroom.
- Evolved-integrators provides the complementary exact-feedback search bed.
  A5's structural-local harness produced 65 feasible children among 474
  evaluated children (13.7%), versus 9/134 (6.7%) for A4, but 712/1,186 valid
  proposals were duplicates (60.0%). A cautious `0.75 -> 0.750375` edit was
  slightly better on the 432-record held-out suite; an aggressive `0.75 ->
  0.77` edit saved 7.8% work but incurred six extra family-held-out misses.
  Evidence: `docs/presentations/beamer-a5-result-2026-08-28/evidence.md`.
- The A5 manifests bind two A100-PCIE-40GB devices and separate pinned 7B/14B
  endpoints. Observed active time was 10.2-13.7 min per 7B replicate and
  21.5-32.5 min per 14B replicate. The five 14B runs used 134-256 calls and
  34,364-58,360 generated tokens each. These are useful local timing priors.
- SDB's 32B BF16 worker is not a one-A100 job: its successful H200 record says
  weights alone used 61.03 GiB. On these 40GB A100s, map it tensor-parallel
  across both GPUs and run arms sequentially. DEV-004's 40 long-reasoning
  calls took 93.3 min on one H200, so A100 duration estimates below are ranges,
  not promises.
- No new SDB inference or training is currently authorized. Every SDB proposal
  below requires a fresh registered protocol; none may reuse the consumed
  DEV-004/005 plans or touch sealed data.

## Ranked experiments

### 1. Verified local certificates, then verify-and-bind (highest priority)

**Question.** Can evidence fix the worker-quality/report-use deadlock without
forcing the synthesizer to trust wrong reports?

For each FCR child, have the worker return its answer plus a complete transient
and one-cycle state trace. A public checker validates every transition against
that child's controller, cycle closure, READY offsets, and claimed prefix
hits; it returns only `accepted`, `rejected`, or `incomplete`, never a trusted
answer. First run a report-only screen on fresh open roots. Only if accepted
report precision and coverage pass frozen gates should synthesis run.

- Minimal intervention: add one certificate schema/checker with offline exact,
  plausible-wrong, incomplete, and parser-attack tests; extend the existing
  natural-worker renderer/grader and packet builder. Do not add routing or
  retries.
- Paired baseline: the same roots under natural answer-only workers; in the
  synthesis stage also raw direct, compute-matched direct with equivalent
  checker access, advisory, unconditional binding, and exact-report oracle.
- Metrics: accepted-report precision, coverage, complete accepted-tuple rate,
  tuple-implies-gold, final exact root accuracy, wrong-report propagation,
  rejection of correct reports, calls/tokens/latency/checker CPU work. Root is
  the independent unit; stratify by `FOUND`/`NONE`, LCM quartile, and position.
- GPU map/duration: Qwen3-32B tensor-parallel over both A100s. Five-root,
  15-call report screen: roughly 1-2.5 h; contingent 40-55-call endpoint screen:
  roughly 3-6 h. Retain every output and do not continue if the report gate
  fails.
- Readiness: near-term, but not executable until the new checker and protocol
  are frozen. This is exactly the repository's stated next action in
  `research/questions/rq-008-verified-report-use/QUESTION.md`.

### 2. Adaptive diagnose-then-edit for typed ODE evolution

**Question.** Can an RLM-style local diagnostic subcall reduce A5's 60%
duplicate share while preserving its improved feasible-child rate?

Freeze the A5 search, seed, model, evaluator, and split. Compare current A5
against a deterministic adaptive harness: use ordinary A5 generation by
default, but after a duplicate streak or an infeasible child, call a typed
`EditIntent` stage that selects one existing literal, direction, and bounded
magnitude from the parent and training-only fitness; a second stage emits the
whole candidate JSON. The route is fixed from observable history, never
validation feedback.

- Minimal intervention: add a closed `EditIntent` schema, a replayable
  two-call variation source, and one study definition/analysis. Existing
  candidate validation, exact evaluator, budget/split ledgers, catalog, and A5
  prompt remain the machinery baseline.
- Paired baseline: current `operator-structural-local-v4`, paired by the five
  existing search seeds and equal provider-call/generated-token/RHS/wall
  ceilings. Report progress per provider call rather than equal candidates.
- Metrics: feasible and unique-valid children/provider call, duplicate share,
  hard-failure tuple, Pareto hypervolume, survival by route, edit magnitude,
  final instance-heldout and family-heldout misses/RHS, and active time.
- GPU map/duration: one pinned Qwen3-14B replica/arm on each A100; CPU workers
  run exact ODE evaluation. Five paired replicates should take about 2.5-4 h
  wall from the observed 21.5-32.5 min/replicate, plus implementation preflight.
- Readiness: the fastest substantive two-GPU experiment. It needs a composite
  provider path but no new task generator, verifier, or model.

### 3. Context lens x decomposition headroom with the small local model

**Question.** Does scope restriction help a smaller model, or is apparent
decomposition value just extra calls?

On fresh open FCR roots, cross worker view (`local shard`, `complete root`) with
root procedure (`fixed three-worker decomposition`, matched repeated-direct
selection). Include single direct as the raw anchor. The child question and
answer contract are byte-identical across the two worker views.

- Minimal intervention: one full-root worker renderer beside the existing
  local renderer; reuse the exact child/root solvers, semantic parser,
  allocation logic, and graders. First calibrate a non-floor/non-ceiling
  difficulty for the pinned Qwen3-14B identity; do not reinterpret prior 32B
  outcomes as the baseline.
- Paired baseline: single direct and same-call/same-token repeated direct on
  every root. Keep the complete original visible to selection/synthesis.
- Metrics: exact child accuracy, all-three-correct rate, tuple-implies-gold,
  final root accuracy, `FOUND`/`NONE` accuracy, prompt/output tokens, latency,
  and accuracy per token. Use root-level paired intervals and retain failures.
- GPU map/duration: one 14B replica per A100, one lens per GPU, then swap lens
  labels or execution blocks to avoid device confounding. A five-root screen
  plus calibration is roughly 2-4 h; a 24-root development study roughly
  6-10 h.
- Readiness: small renderer/packet change. This combines RQ-005 with the I-01/
  I-02 headroom controls in `rlm-experiment-ideas/README.md`.

### 4. Harness-weight co-adaptation crossover on ODE proposal traces

**Question.** Does adaptation make the model specifically better at the
decomposed harness, or merely better at emitting controller JSON?

After experiment 2, export exact-audited proposal episodes. Train two LoRA
adapters from the same Qwen2.5-Coder-7B base and matched token budget: (a)
successful whole-candidate A5 outputs, and (b) successful diagnostic plus edit
traces from the adaptive harness. Evaluate base, direct-SFT, and harness-SFT
checkpoints under both one-shot A5 and adaptive diagnose-then-edit inference.

- Minimal intervention: immutable episode exporter, replicate/lineage-grouped
  train/dev split, PEFT training recipe, adapter identity in model metadata,
  and the 3-checkpoint x 2-harness analysis. Never train on validation/OOD or
  failed-run omissions.
- Paired baseline: base checkpoint and direct-self-SFT are mandatory; the
  causal estimand is the interaction (gain from adaptive harness after
  harness-SFT minus the same gain at base/direct-SFT), not the best cell.
- Metrics: exact parse/validation, feasible and novel candidates/call, search
  progress, family-heldout misses/RHS, training tokens, rollout tokens, and
  total GPU-hours. Group evaluation by search replicate, not child.
- GPU map/duration: train direct-SFT on GPU0 and harness-SFT on GPU1; then run
  paired inference cells in waves. For 7B LoRA, budget a 100-step smoke first;
  planning range is 2-6 h training plus 3-6 h evaluation (5-12 h wall total).
- Readiness: second-wave. Existing A5 has only 65 feasible children, so the
  adaptive arm must first produce enough nonduplicate successful traces; do
  not oversample the repeatedly rediscovered `0.750375` child.

### 5. Structural compositional-OOD matrix for adapted harness users

**Question.** Do gains survive new compositions rather than memorized task
templates or easy answer status?

Use SDB's template ownership and semantic fingerprints to create an open
training split and untouched evaluation strata that hold out cycle templates
and one joint-LCM quartile while balancing `FOUND`/`NONE` and child position.
Evaluate the frozen checkpoints from a later FCR adaptation study under direct
and fixed-decomposition inference. Rotate the held-out quartile across four
predeclared folds; all conditions for a root remain together.

- Minimal intervention: four immutable split manifests and an analysis over
  existing deterministic generation/dual solvers. No new task semantics.
- Paired baseline: base versus adapted checkpoint crossed with direct versus
  fixed decomposition, at matched calls/tokens. Include within-template new
  instances to distinguish IID from compositional transfer.
- Metrics: exact root accuracy, worst-stratum accuracy, IID-to-template and
  IID-to-quartile gaps, decomposition-by-adaptation interaction, report error
  taxonomy, calls/tokens/latency. Root-level hierarchical bootstrap; never
  treat worker reports as independent roots.
- GPU map/duration: one checkpoint/harness cell per A100 in alternating waves;
  roughly 4-8 h for a 24-root x four-cell open screen with a 14B-class model.
- Readiness: successor only. Register after an adaptation method passes an IID
  gate; preserve sealed IID/OOD sets.

## Recommended sequence

Run **1** as the scientific bottleneck test and **2** as the immediately useful
two-A100 systems experiment; they are independent. Then run **3** to establish
small-model decomposition headroom. Permit **4** only if experiment 2 yields
diverse successful traces, and permit **5** only after an adaptation cell wins
on open IID data. This sequence avoids training a policy around an action that
has not demonstrated value—the failure mode already exposed by DEV-005.

## Key local sources

- `structured-decomposition-benchmark/STATUS.md`, `PROGRAM_HANDOFF.md`,
  `docs/EVALUATION.md`, `data/specs/{TASK_FAMILY_CONTRACT,SPLIT_POLICY}.md`,
  `research/questions/rq-008-verified-report-use/QUESTION.md`, and the DEV-004/
  DEV-005 experiment/run records.
- `evolved-integrators/README.md`,
  `docs/research/2026-08-25-program-search-roadmap.md`,
  `studies/ode_integrator/{README.md,definitions,analyses,prompts}`,
  `runs/analyses/a5-structural-local-strict-validation/analysis.json`, and A5
  resolved-study/budget ledgers under `runs/structural-local-ode/`.
