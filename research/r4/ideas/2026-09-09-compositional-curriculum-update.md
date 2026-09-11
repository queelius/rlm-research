---
schema: bounded-research-decision-note-v1
id: compositional-curriculum-update
as_of_utc: "2026-09-09T23:42:55Z"
status: literature_and_conditional_followups_not_ready
gpu_jobs_authorized_by_this_note: false
current_evidence:
  qsr_completed_training_windows: 12
  qsr_actual_optimizer_updates: 10
  qsr_selection_sha256: d9ca1faf43c280f4b882bd3b27ca0deaad7a40b3ca4d1ce570453d6e42b1a87c
  qsr_final_adapter_sha256: 61153a6b75a665f6ba198c3c8b8cb5343c1779feef6cab9e76f71baa47b04849
  qsr_efficacy_status: "Paired final evaluations running; no learning claim yet."
read_depth:
  curriculum_theory: "arXiv2606.27721v1 introduction, problem setup2.1 and limitations6.1; not proofs or a reproduction."
  procedural_chunking: "arXiv2607.07646v1 sections3.1–3.3,4 opening, appendicesA/B and prompt-description passages; not a code audit or reproduction."
  icrl: "arXiv2603.08068v1 sections2.1–2.3, algorithm1/reward table2 and setup3.1; not implementation or full experimental reproduction."
  bootstrap: "README complete and adaptive-context research design all479 lines."
  evolved_integrators: "README lines1–190 and targeted matching passages; not a new result audit."
local_source_pins:
  bootstrap_head: 7f79801073be7799a2318c414f29a764af1a1a0b
  bootstrap_readme_sha256: 440d387cd496dbbd0c5b10ca5badef7a3ec93ba58dd8168a8c2c15e125870592
  bootstrap_design_sha256: 133a041c617b82d0d285ad0a907a5c5a0cd4fdb94540f05a79b781129a250293
  evolved_head: 3badcecba2d92486a4a5a2d6b21e55f4d8bd2128
  evolved_readme_sha256: bdd8706a2ef22644ad0cb46b5b26fdb3d5e0d4a6b540b39f15775050c500b0d3
acquisition: "Primary web pages read; no new code, dependencies, datasets or weights downloaded."
---

# Learn useful procedures, then test whether they combine

The current RL run did obtain useful reward variation: it saved ten updates after
two initial no-op windows. The early all-zero result is therefore not evidence
that learning is impossible. The final matched evaluations must determine what,
if anything, improved. The already accepted four successors remain ahead of any
new training proposal.

## What the new reading contributes

**Curriculum theory.** A June preprint studies learning long computations by
composing shorter ones. Its RL result needs reference-model success at shorter
blocks rather than the whole long sequence. Crucially, its guarantees assume
deterministic transitions and a Markovian trained model; the limitations explicitly
exclude ordinary full-history Transformers from that result. This is motivation
for our tests, not a theorem about our RLM. [Primary setup and limitations](https://arxiv.org/html/2606.27721v1).

**Procedural composition.** A July study pretrains a small model from scratch on
known string-rewrite rules, then compares RL with rejection-based imitation.
The known grammar lets the authors distinguish valid combined procedures from
invalid shortcuts. Reward checks output syntax and final target, not every
intermediate transformation. Its setting, training scale and four-H100 hardware
are not our4B experiment. Main-text and appendix descriptions also differ on
whether the target symbol is model-visible; inspect actual code before attempting
a reproduction or adopting its task. [Methods and appendices](https://arxiv.org/html/2607.07646v1).

**Examples during RL.** ICRL gradually removes demonstrations from rollout
prompts and masks tool observations from policy loss. However, its reward combines
answer correctness with format/tool-use penalties; it is not an unchanged sparse
terminal-reward comparison. For us, fading examples would be a separate arm, with
the actual demonstration-bearing native prefix retained for likelihoods and
zero-example evaluation. Do not remove hints from recorded training prefixes or
call the resulting likelihood on-policy. [Algorithm and reward](https://arxiv.org/html/2603.08068v1).

## How this changes our next decision

Our hypothesis is not that ten, four or any particular number of updates should
produce general reasoning. It is that training needs to reach useful states and
practice meaningful transitions between them. Current evidence separates several
possibilities; these are our inferences, not conclusions of the cited papers.

| Forthcoming observation | Next useful comparison | What it would establish |
|---|---|---|
| Clearer role helps with the same raw evidence | Replicate that fixed harness change on new contexts before more SFT. | A prompt/runtime compatibility improvement, not newly learned planning. |
| Visible real predictions help, but the free root does not obtain them | Teach complete acquisition→use trajectories; compare SFT alone, RL alone and SFT→RL. | Whether a reachable starting procedure makes sparse-reward training useful. |
| Correct-format answers still mishandle visible evidence | Teach or test distinct count, distinct-user and weighted-sum operations before harder decomposition. | An operator/state-use bottleneck, not a demonstrated model-capacity limit. |
| RL improves supported queries but not held-out combinations | Vary combinations and intermediate-state practice, not merely repeat the same count curriculum. | Whether transferable composition, rather than answer style, can be learned. |
| All small-model arms remain weak after clear interfaces | Run a matched larger-model calibration before committing a long training campaign. | A model-package capability comparison; not an isolated parameter-count law. |

The original ninety-minute warm-start proposal under-reserves native rollout and
readout time. A new CPU feasibility review will use observed timings, consider a
fixed8–16-update SFT stage with intermediate checkpoints, and allow up to three
hours for the whole comparison. This is not approval to run it. More updates alone
do not add procedural diversity, and choosing the best held-out checkpoint would
invalidate the intended comparison.

## What to borrow from the neighboring projects

[The bootstrap design](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm-bootstrap/docs/superpowers/specs/2026-08-28-adaptive-context-research-program-design.md")
already asks the right larger question: can the same model choose useful ways to
inspect and decompose different inputs? Its strongest experimental principle is
to establish that different strategies actually help on different cases before
training an adaptive selector. Our immutable runs, question cards and derived
catalog follow that principle. We need not migrate this active campaign or import
an unrelated sequence of infrastructure gates.

[Evolved Integrators](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/evolved-integrators/README.md") offers
an inspectable, bounded candidate language, explicit parentage and separate
correctness/cost/complexity accounting. For a later harness search, prefer a small
set of meaningful changes—root role, record representation and observation
presentation—over unconstrained code mutation. Freeze selected candidates, then
cross old/new harness with old/new weights on new groups. Searching and evaluating
on the same exposed cases would be development evidence, not co-adaptation proof.

The remaining uncertainty is productive: do our failures come from unavailable
evidence, an awkward interface, or inadequate learned procedures? The queued jobs
were chosen to distinguish those explanations while the GPU continues working.
