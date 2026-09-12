---
id: idea:procedure-acquisition-before-more-rl
date: 2026-09-12
status: conditional_experiment_design
related_questions: [rq:rl-effective-feedback, rq:adaptive-decomposition, rq:transfer]
priority: after_fixed_sft32_readouts_and_targeted_reports
gpu_admission: false
---

# Learn to retrieve first; then learn when and how to change the procedure

The current root RL comparison changed weights and generated answers, but its
single exact high-dose answer came from printing a large portion of the input
and copying it. That is not yet evidence of learning a reliable retrieval plan.
The longer supervised run has now completed; its final checkpoint must be judged
by independently generated actions and answers, not its much lower teacher loss.

## What recent primary work changes about our plan

The [RLM paper, revision 3, Appendix A](https://arxiv.org/html/2512.24601v3#A1)
already reports RL on 32k–64k, two-needle MRCRv2 and evaluation on 512k–1M,
eight-needle inputs. It uses 150 steps, batch128, four rollouts per example,
4096 output tokens per turn and up to20 iterations. It also motivates focusing
training on the root rather than general-purpose helpers. Therefore, merely
showing RL or length transfer in an RLM is not our novelty claim. This is a
much larger training regime than our present diagnostic updates; a failed small
screen does not refute their result.

[Environment Tuning, revision 2, sections3.2–3.4](https://arxiv.org/html/2510.10197v2)
combines a staged curriculum, actionable error feedback and rewards for verified
turn-level progress. Its final stage removes extra feedback to match evaluation.
This suggests testing whether an aid remains necessary after learning, rather
than counting easier training behavior as transfer. Its tool-orchestration task
is not our retrieval/delegation task, and we have not reproduced its method.

[CacheRL, June2026 abstract](https://arxiv.org/abs/2606.14179v1)
reports limited RL gains beyond strong supervised training in its small-agent
setting. That is a reason to retain the supervised-only control, not a reason
to assume that our own RL cannot help. Only the abstract was reviewed here.

Sources checked September12,2026. Method facts above come from the identified
primary sections; the following decisions are our proposed experiments.

## Branch on observed behavior, not on optimism about training

If fixedcp32 fails even its training procedure, stop increasing the dose. Check
the actual deployed adapter, native first-action likelihood and prompt binding.
If those agree, change the demonstrations or starting model rather than replaying
the same training indefinitely.

If it retrieves correctly but alters the final answer while copying, separate
selection from delivery. Compare final-answer RL with a mechanism that returns
an explicitly selected text value without asking the model to regenerate it.
First verify which termination operations the actual research runtime exposes;
the existence of FINAL_TEXT in this repository does not prove it is exposed in
the native paper-runtime environment. A deterministic return is an established
design pattern, not automatically a new invention. No implicit answer fallback.

If retrieval and delivery both work, collect fresh grouped rollouts from this
usable policy before another RL update. Report mixed-reward groups, answer and
program diversity, actual gradient norm and effective weight movement. If almost
every attempt succeeds, move to a preselected harder training distribution instead
of applying an all-zero relative-reward gradient. Do not select held-out failures
as the new training set.

## The next transfer check should change a meaningful feature

A useful first comparison is the released starting model versus fixedcp32 on
longer, untouched conversations from the pinned official source. Choose contexts
by an outcome-blind hash ranking within a declared length band, exclude shared
conversation cores and target-response overlap with known optimization/evaluation
exposure, retain public text unchanged and preserve the original grader. Sixteen
paired contexts or eight with two trials is an exploratory screen, not a precise
population estimate. Keep source length separate from actual neural prompt length.

The question is whether a learned short-input program keeps working when a whole
input dump no longer fits. Expected shape: one A10040GB, sequential base/cp32,
two bounded evaluation stages of roughly10–20minutes each, immutable per-call
outputs, no further training or checkpoint selection. Final inputs/seeds/caps
require a sealed follow-on specification before launch.

Independently, the queued MuSiQue comparison tests whether focused helper requests
recover useful facts beyond equally long generic reports. A positive effect should
be repeated on new questions and then used to test a learned request/stop policy.
Neither a fixed call graph nor this exact-retrieval procedure alone demonstrates
general learned recursive decomposition.
