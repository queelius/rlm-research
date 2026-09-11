---
schema: rlm-literature-to-experiment-note-v1
id: idea:after-operator-sft-rlvr
created_utc: "2026-09-10T05:00:00Z"
status: design_candidates_not_launch_approved
question_ids: ["rq:controller", "rq:reduction", "rq:sufficient-interface"]
local_evidence:
  report: ../analyses/root-operator-dose-continuation-live-2026-09-10/REPORT.md
  report_sha256: c67c2b7430b69a890d9a51f0be14d3084fc45439210284fca1454708b84a749e
  accounting_erratum: ../analyses/root-operator-dose-continuation-live-2026-09-10/ACCOUNTING_ERRATUM.md
  erratum_sha256: 949d6c5b74c6eb5286dff38b2155200ec825b3b51fb43a07b371b77506083090
sources:
  - url: https://arxiv.org/html/2606.26027v1
    read_depth: Main methods/results and appendices A-C; full paper/code not audited.
  - url: https://arxiv.org/html/2510.10197v2
    read_depth: Main curriculum/feedback/reward methods, result table and appendix B; full paper/code not audited.
  - url: https://arxiv.org/html/2609.05837v1
    read_depth: Main collection/distillation/weighting/results and appendices D-F through training-objective description; full paper/code not audited.
retrieved_date: "2026-09-10"
acquisitions: No repositories, datasets or model weights acquired for this note.
---

# Use the new procedural foothold to ask a better RL question

## What changed locally

The fixed24 root now acquires child predictions and faithfully computes all29 of
its correct answers. Earlier terminal-reward experiments often lacked that
foothold and favored zero answers. A warm-start RL comparison is therefore more
informative now, conditional on the new-context test supporting transfer. This
does not retroactively invalidate the earlier negative runs or prove that RL
will improve the new checkpoint.

The remaining errors have different causes: five final answers faithfully use
wrong child predictions, other runs fail to finish, and reliable multi-batch
accumulation is unproven. A single 'bad trajectory' label loses that distinction.

## Relevant primary literature

**Structural collapse and supervision.** Hao et al. study Qwen2.5-1.5B and
Qwen3-1.7B tool-use RL. Their final-checkpoint results favor interleaved corrective
supervision over several alternatives, but format/content transfer remains weak.
Importantly, their Qwen3 rollout adds an empty thinking prefix and removes it
during optimization; their hint method also changes conditioning between sampling
and training. These details complicate interpreting collapse as an inherent RL
limitation. We should preserve actual sampled prefixes and distinguish training
instability from interface mismatch. Source: [methods, results and appendices B-C](https://arxiv.org/html/2606.26027v1).

**Environment tuning.** Lu et al. combine syntax training, corrective environment
feedback, progress rewards and a final stage without augmented feedback. Their
initial reward requires at least one tool call; later rewards evaluate task
progress. This is prior art for learning with temporary scaffolding, not evidence
that an optional helper will be adopted. Their augmentation uses an LLM generator
and judge; that judge is not an exact no-leakage guarantee. Source: [curriculum and feedback methods](https://arxiv.org/html/2510.10197v2).

**Learning from partially useful trajectories.** AgentBrew reconstructs tasks from
observed actions/results, then weights action-level SFT by changes in an inferred
task's likelihood. It reports Qwen3-32B average task accuracy9.5→18.2 across three
applications. Despite 'raw' collection, maximum-turn trajectories are discarded.
The method is weighted SFT, not policy-gradient RL. Its within-trajectory
max-normalization removes absolute credit scale; small positive raw credits alone
cannot guarantee a trajectory receives negligible weight. Statistical
predictiveness is also not causal usefulness. Source: [methods, results and appendix D](https://arxiv.org/html/2609.05837v1).

## Ranked candidate experiments — our proposals, not published findings

1. **Can terminal-reward RL improve a root that already uses evidence?** Start
   from exact24, not an automatically selected intermediate checkpoint. Preserve
   the existing model/interface/child and use a new group-disjoint training panel
   with naturally occurring successes and failures. Compare fixed pre-RL and
   fixed post-RL weights on a separately frozen panel with new paired samples.
   Initial compute envelope: one A10040GB, eight genuine updates, roughly1–3hours
   including rollouts and readouts, checkpoint every update. Exact data, objective,
   old-policy likelihoods, seeds and time cap must be approved before launch.
   Promote only if nonzero accuracy and genuine evidence use improve without
   merely moving probability into invalid or constant outputs. Retire/pivot if
   reward groups lack variation or protocol failures erase the signal. A later
   SFT-anchor arm can test whether supervision preserves useful behavior; it is
   not a prerequisite to this first informative run.

2. **Does preserving acquired state help at a scale requiring several batches?**
   First measure fixed24 on a small, structurally admitted16/64/128-record scale
   ladder with actual child widths and map coverage recorded. Do not declare
   several calls mandatory merely to reward the intended algorithm. If overwrites
   or lost observations dominate, compare a retained-result handle against the
   ordinary interface on paired tasks. A handle must expose only genuine returned
   content; no gold, aggregation answer or hidden repair. Initial ladder cap:
   one A100,24 endpoints, about20–40minutes. Promotion requires faithful use of
   multiple actual batches, not call count alone. Scale and new contexts must be
   separately described; long-context admission failures are evidence too.

3. **Can we retain useful steps from unsuccessful trajectories?** A CPU-first
   inventory can separate correct acquisition/reduction steps from bad semantics,
   stopping failures and unsupported literal answers. Compare equal-budget SFT
   on successful-only trajectories with evidence-consistent steps from both
   successful and unsuccessful training trajectories. Keep evaluation traces out
   of the training pool, or explicitly retire that panel to exploration. Never
   relabel an original failed test as successful after inventing a hindsight task.
   Initial conditional envelope: two short LoRA arms plus paired readout, one
   A10040GB, about2–3hours; exact exposure matching and source admission remain
   unsolved design work. Promote only with new-context execution gains; do not
   confuse an LLM's credit estimate with a verifier.

Fresh primitive/composition transfer and the already approved checkpoint readout
remain ahead of these candidates. They determine whether the next bottleneck is
transfer, optimization dose, state accumulation, termination or child semantics.
