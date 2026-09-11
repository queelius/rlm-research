---
schema: rlm-literature-decision-note-v1
id: "idea:routine-transfer-to-adaptive-training"
updated_utc: "2026-09-10T19:43:00Z"
status: conditional_followups_not_implemented
related_questions: ["rq:controller", "rq:sufficient-interface", "rq:continuation"]
read_depth: targeted_primary_methods_and_implementation_sections
gpu_calls_for_this_review: 0
supersedes: []
inputs:
  bootstrap_handoff_sha256: 01c763a5474536438fb268dc0af5e00108bdbe00c945a586afe6eb9092779366
  lambda_comparator_sha256: 1ad2db9c4649cd2a1477e59b2d61ae2d90e6a713b68f854646dc651231d537a8
---

# What comes after teaching a useful routine?

The controller has learned to execute several requested calculations and can cope
with changed names, weights and thresholds. That is worth pursuing, but it is not
yet a controller that invents a good decomposition for a new long document.
The active scale comparison, queued composed-task RL and child-interface tests
separate three obstacles: planning/acquisition, reliable subtask answers, and
learning from the resulting reward. This note refines existing ideas, not a claim
that these directions were newly discovered.

## What the primary sources actually add

**EvoHarness-RL** separates learning workspace actions from optimizing their use.
Its state tracker is partly deterministic; the model learns when to consult state,
record progress and use experience. SFT uses successful external-teacher
trajectories, not pure self-training. Its RL objective combines success with
efficiency, diversity, repetition and format terms. Experience consolidation uses
another model between epochs while the store stays fixed within a rollout batch.
Its implementation reports eight H200s, so it is not a drop-in one-A100 recipe.
These details rule out describing its result as terminal-only RL or autonomous
code-harness evolution. MAIN read the introduction, sections2–3.2 and appendixC;
did not reproduce results or inspect its repository in this refresh.
[Methods and implementation](https://arxiv.org/html/2608.05446v1).

**Harness-RL** constructs training records from exact per-call inputs, outputs and
sampling probabilities; its prefix trees represent token visibility, not causal
execution. It proposes separate routing of action and argument gradients and
includes process rewards. Our current root-only terminal update is a different
intervention. This reread reinforces the existing recording/masking design; it
does not warrant importing new gradient machinery before observing our RL outcome.
MAIN reread sections3.2–3.3, not the whole paper or implementation.
[Methods](https://arxiv.org/html/2608.29641v1).

**Chained RLM** motivates fresh root invocations with compact carried state and
retrievable artifacts rather than an ever-growing dialogue. Its initial reported
comparisons also change test-time computation, so they do not isolate a reset or
memory effect. A useful local test must keep information and compute explicit.
MAIN read the main body through the conclusion in this session, not all figure
pixels or a reproduced implementation.
[Primary paper](https://arxiv.org/html/2608.05124v1).

**Lambda-RLM** motivates a supplied split/map/reduce comparator, not evidence that
our root learned a plan. Its code chooses among task types and predefined
compositions; our conditional-weight task requires an explicitly added reducer.
The prepared proposal therefore uses actual child predictions with a transparent
host-supplied algorithm, labeled as an engineering ceiling.
[Exact source review](2026-09-10-lambda-rlm-supplied-plan-comparator.md),
[primary paper](https://arxiv.org/html/2603.20105v1).

## How rlm-bootstrap changes the question

MAIN reread the complete local
[bootstrap handoff](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm-bootstrap/rlm_self_training_experiment_handoff.md").
Its clean question is whether the same model can improve from its own successful
scaffolded trajectories. The plain-model self-training control matters: more
training alone must not be credited to recursion. Our latest authored root-action
SFT is a useful starting competency, but is not that experiment.

The neighbor project is inspiration, not a requirement to move the current work
or adopt all of its infrastructure. Preserve one training generation, a fixed
harness, observations as context rather than targets, and an untouched transfer
readout for a future bootstrap comparison.

## Ranked conditional decisions

1. **If larger contexts fail before sufficient evidence is acquired:** prioritize
   a supplied-plan ceiling, then training on genuine multi-batch acquisition
   trajectories. The existing eight-episode ceiling proposal uses four clusters
   at64/256 records with the same c32 child and a supplied reducer. One A100,
   at most1800 seconds. A high ceiling with poor free-root performance motivates
   a planning curriculum. A low ceiling with complete acquisition instead sends
   priority to child quality. It is not a matched-compute or learned-planning claim.

2. **If acquisition succeeds but retained evidence is lost:** test continuation
   using the same actual evidence as an ordinary history, compact visible state,
   or retrievable artifact. This refines the already proposed state-use study;
   it is not a new memory novelty claim. Candidate24 paired roots on eight
   training-disjoint contexts, at most1800 seconds on one A100. Promote only if
   correct executed reductions improve, not merely file reads or repeated calls.
   Freeze summaries using actual predictions; never repair with host labels.

3. **If composed RL makes few or no updates because groups are uniformly
   successful:** treat that as curriculum/reward-variation evidence, not optimizer
   failure. Preserve the present run. A separate fixed harder acquisition set
   could raise record count without adding new operators. Candidate48 tasks,
   four samples each and at most eight updates,7200 seconds on one A100.
   Freeze its inputs without choosing individual examples by protected outcomes.
   Require mixed authentic rewards and report their coverage before calling it
   a useful training experiment.

4. **If terminal scores improve without correct execution:** do not promote the
   checkpoint as better decomposition. Design a separate comparison of terminal
   correctness versus an execution-grounded reward only after a concrete verifier
   can recognize equivalent valid programs without judging by variable names.
   Manual audit is a measurement tool, not yet an automated training oracle.
   A24-trajectory CPU feasibility screen comes before any shaping experiment.

5. **If free root behavior becomes reliably successful on varied training tasks:**
   return to the bootstrap question. A one-generation self-trajectory SFT run
   should use fresh training-only rollouts, include all acquisition costs and
   compare against unchanged weights and a plain-self-training control. Candidate
  192 rollouts plus matched small SFT updates and paired transfer readout,
  3–5 hours on one A100, checkpoint every update. This is a future design
   envelope, not an accepted run or a promised throughput.

No candidate above changes the accepted queue. Costs are prospective caps, not
measurements. A finished report must state which decision it changes and link to
its successor; generic co-adaptation, external state and structured output are
already established ideas, not standalone novelty claims.
