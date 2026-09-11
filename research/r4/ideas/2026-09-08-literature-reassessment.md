# RLM literature reassessment: decisions for one A100 40GB

Snapshot: 2026-09-08 UTC. This is a bounded primary-source audit, not an exhaustive bibliography.
The live queue and all three September 2 Markdown ideas memos were read first. No GPU, environment,
shared repository, or research queue was changed. Ten small source snapshots total 3,864,161 bytes;
their URLs, revisions, licenses, sizes, and SHA-256 hashes are recorded in the
[acquisition manifest](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/2026-09-08-literature/current-literature.BLEQ9B/PROVENANCE.json").

## Decision

Keep the existing training-client/renderer and execution-boundary calibration first. The literature
does not justify another full framework port before that bottleneck is understood. The next scientific
screen should measure whether the current controller can choose a decomposition when the prompt does
not supply its procedure, using paired context organizations with the same answer. Then select between
a behavior/reward intervention and a composition-coverage curriculum from the observed failures.

Three conclusions change how to interpret later gains:

- Native RLM SFT, RLM RLVR with length transfer, shared parent/child training, and generic
  model–harness adaptation all have published precedents. A contribution needs a specific mechanism,
  controlled transfer, or a better learning/cost tradeoff.
- Executing a supplied route, changing a route after observing context, and selecting among sampled
  programs are different capabilities. Current literature does not let us infer one from another.
- Exact final-answer scoring does not itself establish correct training credit. Policy actions,
  executed tool calls, recoverable tool errors, valid terminals, and trace trainability need separate
  accounting.

## Five selected sources: three additions and two revised assessments

### 1. Recursive Language Models v3 — revised claim boundary

[Zhang, Kraska, and Khattab, arXiv:2512.24601v3](https://arxiv.org/html/2512.24601v3),
revised 2026-05-11, already includes Qwen3-8B RLM SFT and Qwen3-4B MRCRv2 RLVR. The appendix specifies
32K–64K/2-needle training, 150 steps, batch 128 with four rollouts, and 512K–1M/8-needle evaluation.
The paper also varies decomposition examples and records syntax errors in successful as well as failed
trajectories. Thus native training and length/needle transfer are established prior-work claims;
error recovery and prompt dependence deserve explicit controls.

The [official training release](https://github.com/alexzhang13/rlm/tree/854e688fbba9d8f8989e3da9989812e4b6dfe270/training)
remains at the same commit as the September 2 cache; remote main was checked. It supplies a depth-one
local REPL/OOLONG training path, not the MRCR-specific experiment assets. Its README says generated
Python executes in a host subprocess. The existing safe local harness is the appropriate substrate.

**What changes:** prioritize a procedure-hint withdrawal screen and a code-tool-matched direct control.
A reduced MRCR run is a reproduction/adaptation. Length alone does not identify learned decomposition.

### 2. River — new, directly relevant to the reward/validity bottleneck

[Yao et al., Learning Generalizable Behaviors for Terminal Agents, arXiv:2608.22631v2](https://arxiv.org/html/2608.22631v2),
revised 2026-08-26. River combines environment filtering with optional behavior shaping. Its concrete
GRPO intervention adds a turn penalty *after* group normalization: `-0.05` when both command and
observation have Jaccard similarity above 0.8 with an earlier turn. Its mechanism interpretation is a
hypothesis supported by behavior analyses; it does not prove that every RL improvement is new planning.
The 8B RL runs used eight H200s for about 60 hours/400 steps.

The [author project page](https://terminal-river.github.io/) exposes the paper and illustrative verifier
failures. No author-linked training code or curated River dataset was verified in this bounded audit;
the page links the underlying TMax collection. Do not assume a ready single-GPU reproduction.

**What changes:** test reward integrity and observable repetitive behavior separately. Start by
measuring whether repeated no-progress inspection actually predicts our failures. Only then compare
terminal-only RLVR with a small, independently logged turn-shaping term.

### 3. From Reasoning Traces to Reusable Modules — new curriculum evidence, narrower planning claim

[Kong et al., arXiv:2606.18089v2](https://arxiv.org/html/2606.18089v2), revised 2026-07-05,
uses Llama-3.1-8B on deterministic string transformations with 24 skills and 10 routers. It reports
benefits from compound SFT traces that cover local interfaces, followed by RL on new compositions.
Crucially, the prompt contains the nested composition expression and function identifiers; function
definitions are hidden. This tests learning operations and executing supplied compositions. It does
not directly test discovering a decomposition from an underspecified task objective.

The appendix defines controlled support splits and an exact final-JSON-string reward. No author-linked
official implementation was verified through the paper and bounded author/title search. Use our
existing generators to test the curriculum principle, and describe it as an adaptation.

**What changes:** replace a primitives-only curriculum default with a matched comparison of isolated
skills versus compound traces covering adjacent interfaces. Hold out composition signatures, not just
new strings or seeds. Separately test whether route discovery transfers under a minimal prompt.

### 4. RLMOpt — new competitor and accounting warning for GEPA

[Satheesha et al., arXiv:2608.10471v1](https://arxiv.org/html/2608.10471v1), submitted
2026-08-11, lets a REPL agent inspect failures, propose prompts, allocate evaluations, and stop.
The implementation also imposes deterministic selection, regression floors, diagnosis gates, and
final polishing. Seed and polish evaluations do not consume its advertised agent search budget;
submodel analysis calls use a separate accounting category. The limitations explicitly acknowledge
that the comparison does not isolate adaptive search from these other changes. The optimizer is
GPT-5.1; a local 4B optimizer is an untested transfer.

The paper supplies prompts and tool schemas, but no author-linked code release was verified.
Our [GEPA sidecar design](../sidecars/gepa-three-route-v1/DESIGN.md)
already exposes proposal cost and currently requires an authenticated corpus/runner provider.

**What changes:** add a small agent-controlled search arm only after a working local comparator exists.
Charge seed, diagnosis, reflection, failed proposals, final polishing, and selection evaluations to
a common total budget. An adaptive stopping claim needs a fixed-schedule control under the same rules.

### 5. HELIX — revised interpretation of co-evolution and portfolio yield

[Fan and Huang, arXiv:2608.13951v1](https://arxiv.org/html/2608.13951v1), submitted
2026-08-14, reports one 65-candidate harness-evolution round and exports 438 verified training records.
The paper explicitly defines full-portfolio coverage as a post-hoc oracle/routing ceiling. The reported
learning result is data yield; actual model updates and subsequent rebuild rounds remain future work.
This supports collecting complementary traces, but does not establish that training on them improves
deployment accuracy.

[Official HELIX](https://github.com/HKUDS/HELIX/tree/b5adffa6065931b4d8833f6576188ce93006217f)
was checked at `b5adffa6065931b4d8833f6576188ce93006217f` (MIT). The inspected README/package describe
a TypeScript harness-composition and evaluation workspace with training-data contracts. It is not a
drop-in RLM LoRA trainer. No package was installed or executed.

**What changes:** distinguish fixed-harness pass@1, an oracle union, an executable selector, and
training benefit. Compare a diverse verified trace portfolio with equal-cost repeated sampling from
the best fixed harness before attributing gains to harness diversity.

## Citation checks that constrain originality

These are checks on sources already in the queue, not additional recommended acquisition projects.

- The existing inventory's title “Self-selecting Recursive Language Models” is incorrect.
  [arXiv:2603.15653v1](https://arxiv.org/abs/2603.15653v1) is *Recursive Language Models Meet
  Uncertainty: The Surprising Effectiveness of Self-Reflective Program Search for Long Context*
  (2026-03-07). Its search-versus-recursion challenge is already in the queue and remains necessary.
- [Reinforcing Recursive Language Models](https://www.alphaxiv.org/blog/reinforcement-learning-for-rlms)
  is a May 13 research report. Its single-paper section explicitly supplies the task strategy and says
  it replaced span-F1 rewards with rubric-based LLM judges because valid evidence could be missing from
  labels. Its reported result therefore does not reproduce our strict exact-terminal reward setting
  or show strategy discovery without hints. Its stated shared-policy advantage rule remains distinct
  from whether the cached implementation actually propagates credit correctly; this audit did not
  rerun the September 2 SkyRL credit investigation.
- [HASE, arXiv:2607.03935v1](https://arxiv.org/abs/2607.03935v1), already in the queue, explicitly
  trains a Qwen3-8B policy to generate solutions or edit harness components.
  [EvoHarness-RL, arXiv:2608.05446v1](https://arxiv.org/abs/2608.05446v1) learns external BPE-state
  use. HELIX's limited weight-training evidence must not be generalized into an assertion that nobody
  has trained model–harness systems. Generic co-adaptation, learned workspace use, and prompt evolution
  are preempted directions. A particular RLM transfer result may still be worthwhile.

No additional September 3–8 paper was verified that changes these priorities in this bounded search.
That is a search limitation, not a completeness claim.

## Ranked experimental changes

All numbers below are exploratory design proposals, not measured throughput or memory guarantees.
Use ONE A100 40GB with the already frozen 4B model/tokenizer/adapter identity from the current pilot.
Run comparisons in counterbalanced blocks on that device. Do not import the published multi-GPU
configurations unchanged.

### 0. Retain the existing client-path and boundary screen as the immediate prerequisite

The [queue](../RESEARCH_QUEUE.md) distinguishes tool-looking
assistant text from structured calls and separates `trace_trainable`, `terminal_valid`, and
`terminal_correct`. Retain this distinction. Renderer loss of a generated call is infrastructure
evidence; recovering from a syntax error returned as a tool observation can still be a meaningful
policy trajectory. A terminal-format failure can be a policy weakness while its trace remains
unsuitable for the current update contract.

Before proposing a broader reward change, tabulate policy-origin mistakes, executor/transport failures,
and missing action-token/logprob evidence. Do not silently reinterpret previously excluded episodes as
reward-zero training data. Any admission-policy experiment requires its own frozen contract.

### 1. Procedure hints × context organization: does the model choose a route?

Freeze 12 new open task groups with two meaning-preserving context organizations and two prompt
conditions: current procedural hints versus task objective/tools/budget only. Use two rollout seeds
(7 and 19): 96 episodes. The pair must require identical semantics and answers; change organization
or relevant-information density so an observation-sensitive route choice can be useful. Do not put the
route ID or intended algorithm in the minimal condition. Keep all group members together.

Measure exact success over all episodes, terminal validity, first executed route, adaptation after
inspection, calls/tokens, and route choice conditional on context organization. Use the existing
scripted routes as a competence reference. If the minimal arm fails while hinted execution works,
prioritize hint-withdrawal or planning training. If both fail, investigate tool execution or primitive
competence first. If both work, use harder compositions rather than larger contexts alone.

**Shape/readiness:** one 4B inference server, rootless executor; small prompt/manifest change after
the current client gate. Plan 1–3 hours; cap the screen at 3 GPU-hours and six turns/episode using
the pilot's existing per-turn token cap. Flush every episode. Output:
`exploratory/literature-followups-20260908/planning-screen/`.

### 2. Exact outcome × repeat-loop shaping, only where loops are observed

First score the screen's existing traces for repeated commands *and* repeated observations, without
changing rewards. If a substantive no-progress-loop cluster exists, use the same frozen mixed-reward
prompt groups for terminal-only and terminal-plus-loop-penalty updates. Start with one LoRA update per
arm from the same checkpoint. Log outcome reward, normalized group advantage, and shaping separately.
Do not award positive credit merely for calling tools or fitting a syntax template.

Evaluate paired unseen groups after each update: exact terminal success, repeated-loop share, valid
completion, calls, and premature answers. Promote only if loops decline without losing exact success.
If the local signature is serialized tool text rather than executed repetition, retire this shaping
intervention and fix the relevant client contract.

**Shape/readiness:** one GPU in sequential rollout → unload serving → update → unload trainer →
evaluation phases; preserve the behavior checkpoint/logprobs for each on-policy batch. Microbatch one,
LoRA, and bounded generation history need a memory smoke; do not silently truncate recorded policy
inputs. Existing two-GPU Prime topology is not
evidence this schedule is already implemented. Cap at 3 GPU-hours per arm, checkpoint at base and
every update. Output: `exploratory/literature-followups-20260908/loop-credit/`.

### 3. Compound-interface curriculum, with a separate planning transfer endpoint

Prepare two matched SFT datasets: isolated operations and compound trajectories covering the same
atomic inventory plus diverse adjacent operation interfaces. Match verified training tokens and base
checkpoint, and keep intermediate evidence available under the same harness. Evaluate both under
supplied procedures and minimal prompts on unseen compositions. If RL is then used, expose new
training compositions while preserving a third disjoint composition support for evaluation.

Measure exact answer transfer, retained primitive competence, procedure-adherence versus route-discovery
gain, and the weight × prompt/harness interaction. A win confined to supplied procedures should be
reported as composition execution. A minimal-prompt gain that survives new layouts is stronger evidence
for adaptive interrogation.

**Shape/readiness:** CPU split/export preparation first; existing local generators and LoRA trainer,
not a new third-party training stack. One 4B adapter at a time; initially cap at 100 SFT steps or
3 GPU-hours per adapter, whichever arrives first; checkpoint every 25 steps. Add RL only at a mixed
coordinate. Output: `exploratory/literature-followups-20260908/interface-curriculum/`.

### 4. Adaptive search × common evaluator, after the current provider exists

Use the same editable prompt components, score, candidate eligibility, split, and final-selection rule
for fixed-schedule reflective search and an agent that chooses inspection/proposal/stop actions.
Retain frozen and equal-budget local-mutation controls. Begin with two search seeds (7, 19) and
24 candidate-task evaluations per search arm. Count all inference and metric calls, including final
selection, separately from candidate count; compare quality at common cumulative spend.

The informative outcome is a held-out gain from allocating evidence/evaluations adaptively, not a gain
caused by an extra no-regression rule or undisclosed finalization stage. A 4B proposer may fail even
when a stronger proposer succeeds; that separates update generation from update use.

**Shape/readiness:** one inference server can serve proposer and solver sequentially with the same
weights; a separate model identity must be declared if used. The inspected GEPA sidecar is still an
adapter with an authenticated-provider prerequisite. Do not run its engineering fixtures as research.
Plan/cap 2–4 GPU-hours after that dependency exists. Checkpoint each proposal/evaluation. Output:
`exploratory/literature-followups-20260908/adaptive-search/`.

### 5. Harness portfolio × matched repeated sampling, contingent on complementary successes

Before training, compare three small frozen harness variants against three samples from the best
single variant, with equal aggregate call/token budgets. Use the same task groups and report both
deployable selection accuracy and the verifier oracle union. If diversity yields additional verified
solutions, train matched-token adapters from winner-only versus portfolio traces and cross both
adapters with all frozen harnesses, including the minimal prompt.

Promote only if a practical selector or trained policy captures the additional coverage on unseen
groups. Retire the training branch if an equal-cost repeated-sampling control provides the same
coverage, or if its useful successes are confined to known templates.

**Shape/readiness:** current safe harness plus prompt/observation variants; importing the full HELIX
runtime is unnecessary for this question. One 4B server; first screen 12 groups × three paired
portfolio-versus-fixed slots (72 trajectories), seeds 7/19/31 with variant assignment counterbalanced,
cap 2 GPU-hours. Later training uses the sequential schedule above and a new cap. Flush
each trajectory and preserve parent/group lineage. Output:
`exploratory/literature-followups-20260908/portfolio-yield/`.

## Promotion and interpretation

The common held-out unit is a task/context group. Report failures in total evaluation denominators and
show correctness conditional on valid completion separately. Match model calls and generated tokens
when comparing search/recursion; report wall time as an additional outcome. A recursive method that
receives additional samples needs an equal-sampling comparator.

The most defensible research target is a specific improvement in observation-conditioned route choice
or unseen composition/layout transfer, with a measured weight × harness interaction. Positive reward,
more tool use, shorter traces, an oracle portfolio union, or longer supported context are insufficient
by themselves. These proposals preserve the GPU-first exploratory lane: only the current small gate
and immutable run contract should precede the next informative run.
