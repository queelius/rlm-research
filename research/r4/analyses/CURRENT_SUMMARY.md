# What we know so far

Updated on September 11, 2026, at 00:18 UTC. These are exploratory results, not a
claim that we have solved general problem decomposition. This page includes newer
evidence than the fixed-cutoff cross-experiment review.

## Current conclusions — September 11, 00:18 UTC

The two main positive findings now have additional checks.

- Training with another separately prepared set of demonstrations again gave a
  large gain: 55 verified correct-and-performed answers out of72, versus50 with
  the first training set and12 at the shared already-trained starting model.
  Two new-run questions were attempted but timed out, so55 could become at most57.
  This is two training corpora on one shared eight-input evaluation, not evidence
  that the second corpus is better or that unfamiliar tasks are solved.
  [Report](root-question-sensitive-sft-new-corpus-live-2026-09-10/REPORT_RECOVERY_V2.md)
  and required [starting-model correction](root-question-sensitive-sft-new-corpus-live-2026-09-10/ERRATUM_START_AND_CLAIM.md).
- Matching tags also helped Qwen3-8B: later-label accuracy was31.5% without tags,
  85.5% with row numbers, and81.1% with arbitrary tags. Both improvements appeared
  in all16 inputs, with no missing responses. These are the same inputs previously
  used with the4B model, and both models are from one family.
  [Audited second-model result](leaf-mnli-stable-anchor-qwen8b-live-2026-09-10/REPORT.md).

The13-slide advisor PDF and teaching guide now include both checks (cutoff00:15).
The smaller-update reward-training run is active; the whole-task matching-tag
comparison is queued. A balanced tag-matching control and genuinely new-input
SFT evaluation are in CPU preparation. Historical live labels below are archival,
not current GPU status; consult RESEARCH_QUEUE.md.

## Latest result —23:34 UTC

Arbitrary matching tags preserved the large improvement seen with row numbers.
On sixteen more batches, later-record accuracy was 34.2% without matching keys,
85.4% with sequential numbers, 86.1% with shuffled numbers, and 84.9% with
arbitrary tags. Both non-sequential methods improved all sixteen batches.
The output rules supplied tags and order, not the labels; this does not prove
that the model learned to manage tags itself. It does show that ordinary
counting order is unnecessary in this setup. The next useful test is whether
the improvement survives a whole task.
[Audited result](leaf-mnli-stable-anchor-vs-sequence-counting-live-2026-09-10/REPORT.md).

The meeting package now has thirteen slides and a matching teaching guide,
with a 23:25 evidence cutoff. New-corpus SFT is running with checkpoints saved;
the smaller-update reward-training comparison is queued. Their earlier launch
failures produced no weight updates and are retained as infrastructure failures.

## Previous results —23:14 UTC

The advisor meeting package now has a reviewable 12-slide PDF, worked examples,
a slide-indexed teaching guide, fuller evidence, and two publication options:
repos/rlm/slides/2026-09-11-advisor-meeting/. Its numerical cutoff is 23:00 UTC.
The pending training repetition and matching-key studies are not findings yet.

Six actual reward-training updates did not improve final answers on the fixed
panel: 47/72 were correct, versus 55/72 at the start. Missing-outcome bounds
leave a decline of five to nine successes. Of 45 available combined-operation
paths, 42 acquired complete helper labels, 32 performed the requested calculation,
and 26 did so and answered correctly. Four other correct zeros came from wrong
calculations. Whether the reward caused those shortcuts is untested.
[Final continuation report](root-composed-rl-continuation-live-2026-09-10/REPORT.md).

The separately trained helper produced slightly better labels, but not reliably
better final counts: 1,148/1,280 versus 1,129 true six-class labels, and 1/8 versus
0/8 exact answers. Total absolute error rose from 117 to 130. The downstream
screen therefore failed. Direct per-user summaries had valid formats but much
worse numbers: 0/8 exact answers and total absolute error 1,805 versus 117.
Incorrect weighted sums dominated. These results favor testing a checkable
record-level representation instead of repeating the same short-summary method.
[Mixedchild report](root-lambda-supplied-plan-mixed-child-live-2026-09-10/REPORT.md);
[Statistics report](root-j1-sufficient-statistics-live-2026-09-10/REPORT.md).

The GPU is testing ordinary row numbers against permuted numbers and arbitrary
matching keys on 16 new batches. Supervised training on a different corpus and
a smaller-update-size reward-training comparison are queued successors.
The new corpus's 72 captures completed, but its first training launch failed
because an inherited CPU-only launcher hid the GPU. That attempt produced no
weight updates; recovery reuses the captured corpus without collecting it again.

## Earlier results and context

The following notes preserve earlier comparisons. Their “next experiment”
statements are superseded by the latest result and queue sections above.

Training on both answer formats repaired much of the compact-format weakness
without the fuller-format loss seen with compact-only training. On the same
research-exposed panel, the mixed model scored665/768 compact labels versus
590/768 before this training, while the fuller format improved734/768 versus
725/768. Both local targets passed. The fuller-format metric projects six
classes to A/B/other; it is not six-class accuracy. The128 source questions are
reused across class pairs, so768 slots are not768 independent questions. The
next experiment tests whether the improved child helps a complete counting task.
[Mixed-training report and MAIN review](../../../ARTIFACTS.md#unpublished-files "Not published: trec-child-interface-mixed-sft-followup-live-2026-09-10/MAIN_ADOPTION.json").

Repeating a check is not yet a useful verifier. In the completed selection-by-
agreement comparison, requiring two same-model samples to agree preserved many
wrong labels. Confidence-selected single checks gave2/8 exact final answers;
requiring agreement gave1/8. Task-sensitive selection plus agreement also gave
1/8 and failed the predefined downstream targets. This redirects the next small
tests toward different child weights and a task-specific representation, not
more repeated samples. These are eight nested cases in four exposed clusters.
[Complete negative-gate result](root-task-aware-selective-recheck-live-2026-09-10/REPORT.md).

A simple correspondence aid produced a large local improvement. When the input
records and output answers both carried matching row numbers, accuracy rose from
**51.2% to 81.0%** across eight previously examined batches. For the later records
in each batch, it rose from **38.0% to 80.7%**. Numbering only the output barely
helped those later records, and failed our original improvement threshold. Thus
the promising result is the matched input/output package, not numbering alone.
All 96 responses were available and valid. The subsequent 16-new-context test
repeated the pattern: the input/output interaction was +42.77 percentage points
for later records, positive in all16 contexts. Matching numbers improved those
later labels by46.48 points; output-only numbering gained3.71 points. All192
responses were valid. This supports the interface package, not an established
mechanism or an end-to-end RLM benefit.
[Replication and corrected segment denominators](leaf-mnli-positional-anchor-new-context-live-2026-09-10/ERRATUM.md).
[Full factorial report](leaf-mnli-positional-anchor-binding-live-2026-09-10/REPORT.md).

The full execution review supports the trained controller's transfer across
changed user names, weights and thresholds. Correct answers backed by the
requested calculation rose **12→50 out of72**; for composed questions, **0→32
out of48**. All available paths were reviewed. The same source records were
used, so this is metadata transfer, not new-task generalization. Twelve trained
wrong answers used the right calculation on wrong subtask labels, making the
child model a concrete next target. [Report](root-question-sensitive-readout-followups-2026-09-10/metadata-semantics/REPORT.md).

The fresh-context field-order test supports the earlier direction: writing
the answer before its identifier reduced misleading-reference errors. Its
selective effect was **9.77 percentage points**, positive in14/16 contexts.
All96 calls were valid, but the effect narrowly missed our predeclared10-point
threshold. We report directional support without moving that threshold.
[Report and complete comparison](leaf-mnli-field-order-replication-live-2026-09-10/REPORT.md).

The query-conditioned child test is now audited. Requesting only A/B/other
labels performed worse than obtaining six labels and converting them in Python:
**94.5%→78.8%** for the trained child, **87.5%→78.8%** for the base child.
All192 responses were valid. A smaller interface is not automatically easier,
especially when it differs from the training format.
[Claim, class-wise tradeoff and next test](../claims/child-interface-compatibility.md).

The larger-input comparison exposes a real limitation. It produced9 verified
correct answers across64 planned cases,29 observed wrong or empty answers, and
26 timeouts. Seven correct answers were backed by the requested calculation,
but six of those had a correct answer of zero. Only one nonzero-answer case
was verified correct. We have not established scale transfer. A subsequent test
supplied the decomposition and calculation code. It got0/8 final totals exactly
right despite complete maps and88.2% correct child labels. Reference labels gave
8/8 correct totals with the same code. Child mistakes remain a concrete limit
even when the plan is supplied; this does not explain every free-root failure.
[Supplied-plan diagnostic](root-lambda-supplied-plan-ceiling-live-2026-09-10/REPORT.md).
[Failure report](root-qs-scale-harness-factorial-live-2026-09-10/REPORT.md) and
[important zero-answer qualifications](root-qs-scale-harness-factorial-live-2026-09-10/ZERO_SUPPORT_AND_ACQUISITION_NOTE.md).

The two-update RL evaluation shows deterioration on this fixed panel:47 correct
answers versus53 after one update and55 at the start. There are five missing
outcomes versus one for each comparator, but even favorable assignments to every
missing outcome cannot erase the decline. The two-update minus start difference
is bounded by−9 to−3 correct answers out of72. These are missing-outcome bounds,
not confidence intervals. Of43 observable composed executions,32 use the requested
calculation on the observed child labels;27 are also strictly correct. This is
a small-dose, specialized experiment, not a general conclusion about RL.
[MAIN review and bounds](root-composed-rl-checkpoint2-readout-live-2026-09-10/MAIN_MISSING_OUTCOME_NOTE.md).

The longer continuation started at21:47 UTC without selecting batches from that
evaluation. Five weight updates are committed as of22:13, with the eighth and
last planned training batch underway. Each update saves model, optimizer and
random-number state. A lower-learning-rate comparison and a new-training-corpus
SFT replication are being prepared on CPU. Earlier failed attempts and their
costs remain visible; infrastructure failures are not negative model results.

The earlier SFT gains are not just zero-answer successes. Removing all such tasks
leaves correct-and-performed improvements of10→32/46 in the original test,
9→27/46 with fresh sampling seeds, and7→25/44 after the metadata change.
The nonzero composed-task gains stay positive even under worst-case assignments
to missing outcomes. These are three related readouts of one checkpoint, not
three independent training replications.
[Detailed support audit](controller-zero-support-strata-2026-09-10/REPORT.md),
[relationship and annotation-retrieval clarification](controller-zero-support-strata-2026-09-10/ERRATUM.md).

The child's reported label probabilities contain a useful review signal. The
least-confident quarter covered about66–68% of its mistakes in the completed
official-test runs, versus25% expected from random selection. This is a ranking
diagnostic, not proof that rechecking repairs answers or that probabilities are
calibrated. The matched recheck has now completed: confidence-based checking
corrected71 mistakes while introducing31 new ones, for a net gain of40 labels.
Random checking corrected19 and introduced28, for a net loss of9. However, the
final composed calculation was exactly right in only1/8 versus0/8 cases,
missing our declared downstream target. Better local answers are not sufficient
for reliable final answers. The next comparison has now completed and likewise
failed its downstream gate, as described above.
[Recheck result and failed downstream gate](root-supplied-plan-selective-recheck-live-2026-09-10/REPORT.md).
[Diagnostic and limits](leaf-trec-confidence-ranking-live-2026-09-10/REPORT.md).

## Other leading evidence

Child-model fine-tuning improved official-test label accuracy from64.0% to84.5% with100-record batches and71.7% to88.5% with16-record batches. All148 calls were verified; all500 normalized questions were absent from the actual optimizer corpus, but489 were previously evaluated in this research project. This is a component result, not an end-to-end RLM gain. [Claim and provenance](../claims/child-adaptation-transfers-to-official-test.md).

The original varied-question SFT comparison improved correct-and-performed answers15→52/72; a fresh sampling-seed readout gave15→49/72. The metadata result above is a third diagnostic of the same trained checkpoint, not three independent training runs. [Full claim and limitations](../claims/question-sensitive-executed-composition.md).

Earlier root reward training also produced a local improvement5→16/24 with eight updates. Later training and transfer tests were uneven; the current composed-RL attempt addresses a different bottleneck and its first update is now being evaluated. [Earlier audited result](root-continuation-live-2026-09-09/REPORT.md).

## Read deeper

[Most promising directions](PROMISING_RESULTS.md) · [Question-centered research](../questions/README.md) · [All report links](README.md) · [Live execution queue](../RESEARCH_QUEUE.md).

[Complete prior status history](../operations/2026-09-10-status-history-at-1917/CURRENT_SUMMARY.md) is preserved byte-for-byte, including failed experiments, earlier RL/SFT results, and subsequent corrections. The historical active-job labels are not current. [Migration receipt](../../../ARTIFACTS.md#unpublished-files "Not published: ../operations/2026-09-10-status-history-at-1917/PATH_MAP.json").
