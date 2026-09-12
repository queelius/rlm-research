---
id: checkable-working-state-before-deeper-recursion
date: 2026-09-12
status: conditional_exploratory_proposal_not_gpu_admitted
priority: after_current_rl_replication_and_controller_calibration
question: Does a compact record of checked evidence help more than an additional agent conversation?
motivating_local_results:
  - helper_accuracy_and_final_aggregation_are_distinct_bottlenecks
  - changing_keyed_handoffs_has_helped_in_several_models
  - root_controller_calibration_is_still_being_repaired
primary_sources:
  - url: https://arxiv.org/html/2608.05124v1
    revision: v1
    title: Chained Recursive Language Models for Multi-Iteration Reasoning
    published: 2026-08-05
    retrieved: 2026-09-12
    cache: /project/alex_phd/research-cache/literature/chained-rlm-2608.05124v1/paper.html
    sha256: 7ca2d3790be38591ff71767c08f9ae0aca10f31759d9524ef4c900b1c4e20c2b
    license: arxiv_perpetual_nonexclusive_license
    read_scope: main_architecture_and_experiment_sections_not_independent_reproduction
  - url: https://arxiv.org/html/2606.10507v1
    revision: v1
    title: Hierarchical Planning and Information Folding for Long-Horizon LLM Agent Learning
    published: 2026-06-09
    retrieved: 2026-09-12
    cache: /project/alex_phd/research-cache/literature/hipif-2606.10507v1/paper.html
    sha256: bf5e19d6e73c5bbc874fc95085911230444569be3dd4dac420d79664fc23bb78
    license: CC-BY-4.0
    read_scope: methods_3_1_to_3_3_results_and_appendix_B_not_independent_reproduction
acquisition_scope: public_paper_html_only_no_code_executed_no_dataset_or_weights_downloaded
---

# Make intermediate work easier to check before adding more agents

## What the primary papers contribute

Chained RLM passes text summaries and saved working files between fresh instances
of the same model. It reports improvements with GPT-5-mini but also greater
resource use. Its first-version comparison does not establish that fresh context
beats a compute-matched continuing root. The paper explicitly does not train the
model. This is prior art for artifact-based continuation, not evidence that our
small model will benefit from it. [Primary paper](https://arxiv.org/html/2608.05124v1).

HIPIF trains a model to propose, complete and replace subgoals, retaining a
finished subgoal and its final observation instead of its entire history.
It combines terminal rewards with rule-based penalties for observable problems,
including repeated ineffective actions. Its experiments use embodied text
environments and eight A100s, not our one-GPU RLM news task. The methods motivate
testing working-state design, but their gains do not isolate a universal benefit
of summarization or recursion. [Primary paper](https://arxiv.org/html/2606.10507v1).

## Our proposed comparison, not a claim from those papers

Our evidence-selection screen asks whether a root can request only the helper
labels it needs. Its result may reveal a different problem: the root does not
keep track of what has already been checked. Another child would then inherit
the same confusion. A small change to the RLM could expose a persistent evidence
ledger: requested record identifiers, actual returned values, pending requests
and the current proposed answer. This ledger contains observations, not a host
solution, gold labels or a claim that observed labels are correct.

For example, suppose a task asks how many users asked at least two location
questions. Once two relevant questions have been found for a user, further
questions from that user need not be classified. A useful ledger could show
which users already satisfy the condition and which still need evidence. The
model must discover this stopping rule; the harness must not encode this
task-specific algorithm for it. A simpler neutral ledger would record only
requested identifiers and their returned labels.

The smallest informative initial comparison is the current root interface
against that same interface with a neutral persistent ledger. Keep model weights,
questions, authentic saved helper labels, physical root-call cap and sampling
seeds paired. Charge ledger rendering tokens. Begin with the frozen familiar
contexts as a mechanism screen, followed by new context groups only if promising.

Measure exact answers, agreement with the supplied labels, unavailable episodes,
duplicate requests, known evidence usage and physical root tokens separately.
Do not interpret saved-map agreement as proof of correct reasoning. Distinguish
avoiding redundant requests from merely stopping too early.

Only if a ledger helps should we add a second comparison: continuing the same
root versus handing the same ledger to a fresh root. Match total generation
budget and access to source evidence. That comparison separates the value of
the working state from the cost and benefit of a new conversation. Free-form
summaries are a later arm, not a simultaneous change in the first experiment.

## Decision and compute boundary

No GPU job is admitted by this note. Reuse the controller's measured runtime
once its repaired screen completes; an initial 24 paired problems means 48 root
episodes on one A100. Freeze seeds, prompt bytes, maximum total calls, token cap
and checkpoint/output paths before launch. Stop this direction if improved
bookkeeping does not change the relevant errors. Promote only an accuracy/cost
trade-off that survives another context group and a second model or training seed.

Possible publication angle: which information must cross an RLM boundary, and
when does extra recursion help beyond simply preserving that information?
Artifact handoffs, subgoals and folding are established ideas; our contribution
would have to be a controlled finding or useful specific mechanism, not a new
name for them.
