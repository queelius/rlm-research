# State visibility, finalization and program selection: future tests

Focused primary-source reading, September9,2026. These are research-queue ideas,
not accepted model runs. Existing GPU RL and two waiting comparisons continue.
No new repository/model/data download or shared-environment change was needed.

## Published methods relevant to our failures

The updated [RLM paper, v3 (May11,2026), §2 and AppendixA](https://arxiv.org/html/2512.24601v3)
keeps intermediate values outside the neural context and can return a final
environment variable directly. Its training appendix explicitly describes
correcting final-answer/template mistakes in teacher traces. Thus direct
computed-answer return and root-interface SFT are established ideas, not ours.

[SRLM, v1, §2–3](https://arxiv.org/html/2603.15653v1)
compares multiple context-interaction programs using answer agreement, expressed
confidence and trajectory length. It reports advantages in its much larger-model
setup. Its evaluation uses a model judge and different tasks/budgets, so our
small-model exact-count results neither replicate nor contradict its headline.

[VISTA, v2, §3](https://arxiv.org/html/2606.30005v2)
makes context state visible through block handles, usage information and
archive/recovery tools while preserving accessible original payloads. This
provides a useful alternative to assuming the model can infer what is still
available from an accumulating transcript.

These short summaries describe the sources' methods, not independent validation
of their results. Retrieved versions are pinned by their URLs; this is a focused
method reading, not an exhaustive novelty review.

## Candidate experiments from our own evidence

### 1. Stop rephrasing a value that has already been computed

Our high-LR audit contains two complete correct returned maps implying6 followed
by final Answer:8. Other failures are malformed final text. A future matched
interface/teaching comparison could test whether the coordinating model can learn
to submit a computed Python scalar directly, instead of writing it again in a
later language-model turn. This would exercise a known RLM design choice.

Smallest useful first test: author paired initial-action demonstrations for the
same public tasks, with a precisely defined submit-value API and no gold in code;
compare freely learned use against the existing print-then-answer routine.
Preflight that the real runtime can terminate with the submitted value while
retaining truthful action/observation graphs. Do not fabricate a sampled final
reply or silently replace a wrong answer. Fixed starting weights and matched
training budgets,16 demonstrations/arm and24 paired fresh readouts are a plausible
single-A10030–40minute package, pending an actual code/shape assessment.

Promote only if end-to-end accuracy improves with real submission uptake, not
merely if a forced correct scalar is returned. Separate semantic helper errors,
wrong Python aggregation and restatement/format failures. If submission uptake
fails, first teach the API; do not label the terminal behavior beneficial anyway.
This is model–interface co-adaptation, not a new invention of computed output.

### 2. Provide retrievable evidence handles instead of early tempting totals

Our coverage-first comparison mainly avoids the harm of showing partial totals;
it barely improves over ordinary maps and costs more. A targeted memory-interface
test could expose source-backed coverage and stable handles to exact returned
maps, without displaying answer-like totals until requested. Compare unchanged
maps versus handle-plus-coverage at matched root weights and budget, on24paired
longer-context cases (about20–30minutes on oneA100, to be qualified).

The question is whether roots recover relevant details when needed and avoid
repeated child work without losing final correctness. Record actual accesses,
duplicate requests, omitted/unknown evidence and jointly correct cost. A shorter
prompt alone does not prove semantic efficiency. This should wait until current
whole-RLM representation and plan-teaching results clarify the bottleneck.

### 3. Select among programs using observable evidence, not self-confidence alone

Existing fresh rollouts can support a **post-hoc, zero-GPU feasibility analysis**
of budgeted program selection. Compare answer plurality with a rule using actual
source-backed relevant coverage and final syntax, keeping runtime unavailable
separate. Tune any rule on training/development groups only; reserve a separate
evaluation before a success claim. Exposed evaluation outcomes cannot become
selection-training labels and a test set simultaneously.

If an evidence-based ranking separates correct from wrong programs beyond
trivial formatting, freeze it and collect independent candidates with a matched
total generation budget. A16-task×4candidate32–45minute single-A100 follow-up is
plausible but not yet measured. Include a single-candidate and equal-budget
plurality baseline. Our coverage audit already shows full coverage is insufficient,
so it cannot be used as a substitute verifier.

## Current ranking

Finish the currently accepted training/fresh-source/plan contrasts. The separately
approved shifted-cue72 mechanism test is cheap and directly discriminating.
The same-map-API whole-RLM bridge is being refined before implementation.
Computed final-value submission is the next strong training/harness candidate
if faithful aggregation remains the bottleneck; state dashboards and program
selection remain queued ideas, not reasons to displace a ready experiment.
