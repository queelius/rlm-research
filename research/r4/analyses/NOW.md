---
schema: research-current-brief-v1
updated_utc: 2026-09-12T13:01:00Z
status: active_exploratory_research
claim_level: no_meaningful_new_RL_gain_established
---

# Research in plain language

We want a small model to learn how to inspect a problem, decide what to delegate,
and combine the resulting evidence correctly. We are testing helper learning
and controller learning separately so a failure in one does not get mistaken
for a failure of the entire idea.

## What the latest experiments say

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
- Two conversation-search attempts failed before model calls: first an obsolete
  container store, then a task-setup ordering error that left the context file
  absent. These are operational failures, not model results. The next repair
  must exercise the actual task setup, not just a standalone file-write smoke.

## What happens next

The new-seed replication retires the one-answer positive signal.
The eight-step supervised-learning run completed on 1,024 new
articles, with a separate 512-article final test. Their article exposure and
update opportunities will match, but their losses and token budgets will not.
This comparison asks whether the material is learnable and whether the reward
procedure can exploit it.

This broader comparison was frozen before the replication result. It is a new
data-and-dose question, not an escalation based on a positive result. The RL
launch's nested Python import failure has been repaired and tested on its actual
CPU entry path. RL is queued after the now-running conversation pilot. SFT made
eight committed updates in 224.440 training seconds (236.254 owned seconds).
Its final test has not run; successful training is not yet improved accuracy.

The separate conversation-search calibration asks whether a controller can
inspect external data and produce useful reward variation before we train its
weights. Eight questions about one conversation are not eight independent
conversations. A later transfer test must use different underlying material.

## Evidence and resumption

- [Current decision and measured costs](2026-09-12-midday-learning-decision.md).
- [New-data RL audit](helper-agnews-native-hf-outcomes-2026-09-12/REPORT.md).
- [Replication audit](helper-agnews-native-hf-seed2-outcomes-2026-09-12/REPORT.md).
- [Helper-interface interpretation](root-recursion-interface-qualifier-independent-2026-09-12/INTERPRETATION_ADDENDUM.md).
- [Correction to the initial-prompt diagnostic](root-recursion-interface-qualifier-independent-2026-09-12/PREFIX_ADDENDUM.md).
- [Numerical diagnosis](anomalyxl-budget-shape-v2-mechanism-2026-09-12/REPORT.md).
- [Corrected conversation-data inventory](post-mechanics-next-learning-2026-09-12/REVIEW_AMENDMENT.md).
- [Live queue and exact resume pointers](../RESEARCH_QUEUE.md).
- [Longer history and earlier conclusions](CURRENT_SUMMARY.md).

Earlier strongest publication leads remain the multi-model keyed-handoff study
and the learned use of supplied operators. This latest batch has not yet
established autonomous decomposition learning or a reliable RL improvement.
Source/report snapshots are pushed periodically; GitHub is not a backup of
external model checkpoints and raw run artifacts.
