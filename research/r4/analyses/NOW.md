---
schema: research-current-brief-v1
updated_utc: 2026-09-12T16:00:00Z
status: active_exploratory_research
claim_level: two_training_seed_RL_gain_same_panel_needs_new_example_test
---

# Research in plain language

## Current decisions — September 12, 16:00 UTC

The repeated RL gain remains our strongest new training result: the starting helper
got422/512 news labels right, two RL runs got437 and436, and supervised training
got427. The two RL runs agree on511 answers. We still need the separately frozen
official-test comparison before calling this a gain on new examples.

The earlier question-classification skill appears intact on a small, previously
evaluated panel:121/128 at the start,122 after RL,121 after supervised training.
RL changed only one answer, from wrong to right. This is a useful retention check,
not proof of broad transfer. See the
[source-to-raw audit](helper-trec-retention-b4-independent-2026-09-12/SOURCE_TO_RAW_RESULT.json).

Controller exploration exposed a different bottleneck. On32 trials retrieving
answers from one long conversation, none returned the exact requested answer.
Many copied a user's request instead of the assistant's reply. Small nonzero text
overlap scores are not evidence that the model has learned a useful procedure.
We therefore did not launch RL from that reward signal. A shorter, independent
conversation calibration is queued; a training-only demonstration program solves
all32 available training conversations, but that is teacher correctness, not a
trained-model result. Its actual tool interaction is being checked before SFT.

The new selection interface also needs a basic usability check. Of48 completed
episodes, only11 had a strict final answer and9 also agreed with the declared
finish action. The original exporter marks the changed prompts unavailable, so
these are raw-trace diagnostics, not a promoted accuracy comparison. A fresh
paired test asks whether one syntax-only example improves use of the interface.
Deeper recursion and a persistent working-state variant wait for usable evidence.

GPU training is active on the same first128 articles repeated for eight updates.
It tests whether additional training alone explains the broader-data gain. The
first update uses identical examples, sampled answers and losses, but not bitwise
identical gradient updates; this numerical limitation is recorded. Other admitted
jobs test fresh official news examples and whether the trained helper improves
whole-system answers under an unchanged controller. A new encyclopedia
classification panel is frozen for a different-domain/label-space check.

The sections below are dated history, not live job status.

## Current result — September 12, 15:10 UTC

The broader RL gain repeated. On the same 512 articles, the starting helper got
422 right, supervised training got 427, and two independently randomized RL
training runs got 437 and 436. The RL models agree on 511 predictions. All 16
second-run corrections and both regressions also occur in the first run.
This strengthens training repeatability, not generalization to different data.

The second run completed all eight real weight updates in 35.55 minutes and its
fixed final evaluation in 7.07 minutes. All required answers were available;
source, raw response, probability, replay and optimizer checks passed. See the
[full seed-replication readout](helper-agnews-seed-replication-findings-2026-09-12/FINDINGS.md).

The GPU is now testing the controller's Python procedure. Follow-ons test whether
the helper retains its earlier question-category skill, whether repeating 128
articles can match training on 1,024 different articles, and whether all four
fixed helper models improve on a separately frozen official-test news panel.
No controller improvement or new-data gain is established yet.

The earlier narrative below is retained as a dated research history, not the
current job status. In particular, the one-update failed replication and the
eight-update successful replication are different experiments.

## Earlier context (through 14:25 UTC)

We want a small model to learn how to inspect a problem, decide what to delegate,
and combine the resulting evidence correctly. We are testing helper learning
and controller learning separately so a failure in one does not get mistaken
for a failure of the entire idea.

## What the latest experiments say

- The broader-data comparison now has a promising RL result. On the same 512
  previously unqueried test articles, the starting model answered 422 correctly,
  supervised training answered 427 correctly, and RL answered 437 correctly.
  All three produced every required answer. RL corrected 17 starting-model
  errors and introduced two, a net gain of 15 answers (2.93 percentage points).
  Fourteen of those net answers came from the science-and-technology category.
  This is one fixed eight-update run, not yet a replicated improvement.
- Changing temperature, taking larger updates, changing the reward baseline,
  and serving one item at a time did not produce a useful RL gain on the earlier
  small training set. The updates really changed weights; completion of a
  training run is not evidence of better answers.
- Training on new news examples improved one of 256 test answers in the first
  run, but a new-seed replication reproduced the starting model's predictions
  exactly. The one-answer gain did not replicate. Both runs made real weight
  updates with valid reward variation; neither establishes useful learning.
- Clearer helper instructions improved several final answers, but repeated
  actions and incorrect calculations remain. One correct answer was produced
  by the wrong calculation. We must measure faithful computation as well as
  answer accuracy.
- The numerical Python experiment mostly exposed poor code and method choice.
  More room for code improved completion, not correctness. That particular
  free-form variant is retired rather than given another larger budget.
- Three conversation-search attempts failed before model calls: an obsolete
  container store, a task-setup ordering error, and an audit looking in an obsolete
  installation directory. These are operational failures, not model results.
  The new repair passed a real end-to-end CPU exercise of task setup, container,
  installed harness, context reading, causal prompts, and a fake final answer.
- The fourth attempt then exposed a separate request-recording error before
  forwarding any model request. We stopped it early after 473 seconds and
  released the GPU. Its repeated failed interception attempts are not model
  calls or model failures. The earlier CPU exercise missed that wrapper;
  the next repair must test the actual complete collector path.
- Splitting the four-item count reward into four item rewards and adding them
  back together gives the same update signal. The two pilot collections contain
  no hidden item-level variation that this change would recover.

## What happens next

Repeat the same eight-update RL experiment with different sampling and training
seeds before changing its recipe. Keep the same articles, model, update count,
and fixed final test. That tests training repeatability, not transfer to another
dataset. Broader transfer and helper-input-size tests follow only if the signal
holds. The conditional diagnostic for nearly unchanged predictions is not
needed: RL changed 21 labels, exceeding its predeclared five-label trigger.

That replication is active from 14:21 UTC, with the first generation block
completed and the first weight update underway. Its checkpoint and final-test
receipts will determine completion; no new accuracy result is available yet.

Supervised training is an important comparison, not a straw baseline. It used
the same 1,024 training articles and eight updates, but different losses and
fewer output samples. RL required about 35 minutes of owned training workflow;
SFT required about four minutes. The observed accuracy advantage is not a
compute-matched claim that RL is better than supervised learning.

The new-seed replication retires the one-answer positive signal.
The eight-step supervised-learning run completed on 1,024 new
articles, with a separate 512-article final test. Their article exposure and
update opportunities will match, but their losses and token budgets will not.
This comparison asks whether the material is learnable and whether the reward
procedure can exploit it.

This broader comparison was frozen before the replication result. It is a new
data-and-dose question, not an escalation based on a positive result. The RL
launch's nested Python import failure has been repaired and tested on its actual
CPU entry path. RL completed all eight updates in2,094.99 owned seconds, about
35 minutes. All1,024 sampled maps passed replay checks;43 of256 question groups
had differing rewards. The starting model, final RL model, and final SFT model
completed the same fresh512-article test. Only complete eight-step models
were eligible; no choosing
the best intermediate checkpoint after seeing test answers. SFT made
eight committed updates in 224.440 training seconds (236.254 owned seconds).
Its final test improved by five net answers; successful training alone would
not have established that improvement.

The separate conversation-search calibration asks whether a controller can
inspect external data and produce useful reward variation before we train its
weights. Eight questions about one conversation are not eight independent
conversations. A later transfer test must use different underlying material.
Five short conversations are now frozen for a small three-train/two-test study;
their exact dialogue pairs do not overlap. That is an exploratory transfer test,
not evidence of broad generalization or semantic independence.

The conversation-search repair is back in CPU preparation. A conditional root-only
RL update remains unlaunched. The new evidence-selection screen also stopped
before model calls: its real collector rejected the frozen task identity.
Both failures are being repaired in their actual production entry paths. The
GPU was idle for about nine minutes while those repairs and the RL replication
were prepared. The replication now owns it. The idle interval is lost research
opportunity, not useful experimental compute.
The latter lets the controller
choose which record IDs to ask about, accumulate authentic saved helper replies,
and explicitly finish. Its first screen separates evidence-selection behavior
from helper sampling and cannot establish a real child-compute saving.

A separate OpenAI conversation-search dataset now has 32 training and 16 test
conversations frozen without looking at model outcomes. Their exact conversation
pairs do not overlap within the selected short-context pool, although the shared
demonstration remains and prior model exposure is unknown. The source question,
requested occurrence, and answer links were checked. This is data readiness,
not a completed learning or transfer result.

## Evidence and resumption

- [Current decision and measured costs](2026-09-12-midday-learning-decision.md).
- [New-data RL audit](helper-agnews-native-hf-outcomes-2026-09-12/REPORT.md).
- [Replication audit](helper-agnews-native-hf-seed2-outcomes-2026-09-12/REPORT.md).
- [Reward and supervised-signal diagnosis](agnews-credit-and-sft-signal-2026-09-12/REPORT.md).
- [Broader RL checkpoint audit](helper-agnews-eightstep-live-audit-2026-09-12/HANDOFF.md).
- [Fixed final comparisons](helper-agnews-eightstep-live-audit-2026-09-12/outcomes/READOUT-003.md).
- [New conversation-data freeze and limitations](openai-mrcr-source-inventory-2026-09-12/FROZEN_SHORT_DATA.md).
- [Evidence-selection proposal](../ideas/2026-09-12-budgeted-evidence-stop-interface.md).
- [Small conversation-transfer design](mrcr-independent-context-data-2026-09-12/DESIGN.md).
- [Helper-interface interpretation](root-recursion-interface-qualifier-independent-2026-09-12/INTERPRETATION_ADDENDUM.md).
- [Correction to the initial-prompt diagnostic](root-recursion-interface-qualifier-independent-2026-09-12/PREFIX_ADDENDUM.md).
- [Numerical diagnosis](anomalyxl-budget-shape-v2-mechanism-2026-09-12/REPORT.md).
- [Corrected conversation-data inventory](post-mechanics-next-learning-2026-09-12/REVIEW_AMENDMENT.md).
- [Live queue and exact resume pointers](../RESEARCH_QUEUE.md).
- [Longer history and earlier conclusions](CURRENT_SUMMARY.md).

Earlier strongest publication leads remain the multi-model keyed-handoff study
and the learned use of supplied operators. The broader-data RL result is a new
lead worth replicating, not yet a reliable RL claim or autonomous decomposition
learning. Its success concerns a classifier used as an RLM helper, not the whole
controller or a learned recursive tree.
Source/report snapshots are pushed periodically; GitHub is not a backup of
external model checkpoints and raw run artifacts.
