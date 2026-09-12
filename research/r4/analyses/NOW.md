---
schema: research-current-brief-v1
updated_utc: 2026-09-12T23:37:00Z
status: active_exploratory_research
claim_level: exploratory_procedure_transfer_and_exact_return_contract_mismatch
---

# Research in plain language

## Current interpretation — September 12, 23:37 UTC

Increasing the reward-update size taught the model to deliver answers it had
already retrieved: training exact answers rose7→17→24/32 for noRL, smallerRL
and largerRL. The two consistently wrong search strategies remained wrong.
On an already examined evaluation panel, the larger update scored28/32 versus
25/32 before training: five gains but two losses. All gains followed unchanged
retrieval; one loss failed to produce a usable action. Output cost increased.
We are testing unused conversations before claiming a transferable improvement.

Asking helpers for just record IDs modestly improved selected sets, but did
not produce correct complete solutions. Six apparent interface failures were
only unsorted ID lists. Even ignoring order did not rescue the overall task.
A fixed one/two/four-helper comparison on fresh local records is running to
test whether smaller inputs help. This is not yet learned recursion depth.

The first financial-calculation pilot needs diagnosis: supplied targets and
generated program validity both have problems. It is not evidence that code
execution is inherently unhelpful. See the
[decision update](2026-09-12-evening-decision-update.md) for counts, limitations
and the next discriminating experiments. Earlier entries below are historical.

## Current interpretation — September 12, 22:55 UTC

The new reward update did not improve the main tests: short answers stayed
at25/32 and longer-input answers at10/16. Its one additional success on the
third/fourth-occurrence test restored two spaces, not a new retrieval ability.
All64 outcomes were available. We are checking the original training attempts
to determine whether the update learned locally without transferring, or
barely changed sampled behavior. A possible larger single-step comparison
would isolate update size; it is not yet a completed experiment.

Merely telling the model to inspect the actual request wording did not make
it do so. Correct answers fell7→4/32 and correct retrieval24→18/32. The
instruction used29% more generated tokens. We retire this prompt condition,
not the idea of learning a useful inspection action.

The decomposition pilot is diagnostic, not a capability result. Its grader
expected an output status that the prompt failed to name, and an execution
receipt was absent despite44 physical responses. Those failures are preserved
and being addressed before another comparison. The question remains useful:
what must a helper report for the final stage to solve the task, and when can
the final stage compensate using the original source?

The strongest positive evidence remains supervised procedure transfer within
the repeated-request task family. Neither new reward recipe establishes a
replicated RL gain. Publication candidates should target a measured decision
or information bottleneck, not an isolated favorable score.

## Current interpretation — September 12, 22:16 UTC

The small RL gain did not replicate. The first short-answer comparison was
23 to 25 correct; two new decoding seeds per conversation gave 25 to 22, with
three losses and no gains. Both models were run again on every conversation.
The new losses added a line break after correctly retrieving the answer. We
therefore have an actual weight update, but no reliable accuracy improvement.

Supervised training remains more promising. The learned Python search routine
answered 10 of 16 new third/fourth-occurrence questions, versus none for the
base model. This complements its separate 0-to-10 result on longer inputs.
These are different panels in the same task family, not general recursion.

New training questions supplied the reward variation missing from familiar
questions. A group-relative update has completed, and its fixed 64-output
readout is queued across short, longer and higher-occurrence panels. We will
not infer success from its gradient size. The GPU currently tests whether
asking the model to inspect actual request wording repairs literal searches.

An extra quoted-relation helper and a cheaper concise-answer instruction each
raised exact answers from 3 to 5 out of 12, but corrected different questions.
Their gains changed wording, not missing facts. To study decomposition itself,
we are preparing a small task with verifiable intermediate answers and joins.
The next useful question is what information a helper must retain for another
stage to succeed, rather than simply whether adding a helper raises a score.

These are post-meeting findings. Earlier entries below preserve the evolving
interpretation; they do not supersede this update.

## Current interpretation — September 12, 21:31 UTC

The first reward-based update from the competent procedural checkpoint produced
a small held-result increase:23 to25 exact answers on32 short attempts, and no
change (10/16) on longer inputs. All attempts are accounted for. This is one
update and exposed panels, not a replicated general improvement. The gradient
mainly changed erroneous whitespace. We are checking the two actual gains
before deciding whether to expand this training recipe.

Adding a helper to extract quoted relationships also raised exact answers from
3 to5 out of12, but both gains merely changed answer wording. The same answer
content was already present. More calls did not establish better decomposition.
The next comparison tests clearer answer instructions without another helper.

Higher temperature did not resolve the old batch's lack of useful reward
variation. The GPU is now evaluating eight previously unused problems, while
CPU preparation builds a harder test requiring the third or fourth matching
request rather than the first or second. This asks whether the learned routine
extends to new task structure, not only longer text.

The historical updates below preserve how our interpretation changed.

## Current interpretation — September 12, 21:06 UTC

The earlier checkpoint restored some reward variation but lost useful accuracy:
6/31 available exact answers, versus 28/32 at the later checkpoint. It is not
the clean way to preserve retrieval while teaching answer delivery. A new
one-step RL job is now running from the later checkpoint with a fixed reward
baseline and loss only on the final answer. Its saved gradients and subsequent
rollout evaluation will distinguish an actual useful update from preparation.

The temperature comparison failed because an inherited request audit rejected
temperature 1.0 before it reached the model. Both failed attempts remain
operational failures, not temperature results. A repair targeting that exact
guard has passed the actual role-hook fixture and is queued after training.

Flexible passage choice raised complete annotated-source coverage from 3/12
to 6/12, but exact answers remained 3/12. The tie includes one genuinely
recovered source chain and loss of one previously unsupported exact answer.
The next harness test keeps all source sets fixed and adds quoted relationships
before final answering. This tests evidence use, with the extra call counted.

## Current interpretation — September 12, 20:51 UTC

The trained retrieval routine works on new, longer conversations: exact
answers increased from 0/16 to 10/16, and the correct text was retrieved in
15/16. Five remaining errors dropped two required spaces while copying;
one searched for the wrong kind of request. This is useful transfer within
one task family, not evidence of general recursive problem solving.

Four samples per familiar training question still produced identical rewards.
That batch cannot teach our group-relative RL method, even though it contains
a repeatable mistake. We are testing an earlier training checkpoint and
preparing a fixed-baseline reward objective that does not require variation
within each question. Higher-temperature testing hit a connection defect and
has no model result yet; its lost time and repair are recorded separately.

A separate experiment tests whether a planner should allocate four evidence
passages freely across two helpers, rather than always taking two from each.
This targets missing evidence, which the earlier summary-versus-source test
did not resolve. We will count the planner's extra call rather than claiming
that both policies have equal cost.

## Current interpretation — September 12, 20:23 UTC

The fresh supervised-controller batch answered28/32 attempts exactly, yet
provides no group-relative RL signal. Four attempts at each of eight questions
always gave the same answer: seven questions always correct, one always the
same copying mistake. All32 attempts first printed the correct target text.
Within every question the reward is constant, so every relative advantage is
zero. This rules out taking a useful step from this particular batch, whatever
learning rate or action mask we choose. It does not mean all RL is impossible.

We are testing whether increased sampling variation or a predetermined earlier
supervised checkpoint restores useful alternatives without losing the learned
routine. The GPU meanwhile compares the fixed trained model and starting model
on16 new longer conversations. No extra checkpoint is selected by its score.

The helper evidence screen gave4/12 summary answers versus3/12 original-text
answers. The separated exact scores are mostly answer formatting or unsupported
use, not evidence-preservation gains. Missing selected relations affect more
cases. A next comparison gives the final answer four passages either split
evenly between helpers or selected flexibly across them. This tests where
evidence capacity is allocated, while recording the extra planner cost.

## Current interpretation — September 12, 20:09 UTC

The return-path experiment recovered seven answers without changing what the
model generated. The system had removed trailing spaces that were part of the
required answer. With this disabled, the fixed trained model scored23/32 versus
17/32 before. Seven gains have identical complete generation paths; one other
answer changed from right to wrong on a different generation path. Thus the
net six-answer gain is not six pure causal recoveries: seven are directly
attributable to preserving output, and three of32 paths differ overall.
This improves the harness/reward contract; it is not an RL result.

The old controller RL recipe did not show a stable advantage on a second
decoding block. We will instead collect fresh attempts from the controller
that has learned the retrieval routine, using the corrected return path, and
check whether its remaining errors provide useful learning feedback.

The GPU is comparing original selected passages with summaries of exactly
those passages. This asks whether evidence is lost during summarization,
separately from choosing the wrong passages. It uses12 previously examined
questions, not a fresh confirmation. A short newer-model screen gave0/8 exact
for both models under a two-turn limit; that does not justify a model switch
or a general ranking. Longer-input transfer still awaits a startup repair;
its two failed launches made no model queries.

## Current interpretation — September 12, 19:35 UTC

More supervised training taught the retrieval routine. Keeping32 demonstrations,
learningrate/objectivefixed and continuingthe sameoptimizer/RNGto32updates yielded
all32correct trainingfirstprograms/targetprints. On16separateconversations×2seeds,
base2/29availablevsSFT17/32; paired29 gives15wins0losses. Threebaseoutcomesunknown,
notwrong. The16contexts werepreviouslyusedinotherexperiments, notSFTtraining;
thisisexploratorysame-tasktransfer, notconfirmatoryorgeneraldecomposition.

SFT retrievescorrecttext30/32times butonlyreturns17exactly. Savedtokensshow8more
exactanswers lostthroughruntimewhitespace trimming, raisingrawtokenexactdiagnostic
to25—notrewriting17. Fourmodeltokenoutputsomitspaces,onechangesadigit,twofail
theemail→message selector. ActualQwen3parserandACPfinalreturnbothstriptext.
Prospectivepaired32arm disablesonlythoseclampsinnewprocess; no goldrepair.
Thisisthenextreward-facingtestbeforefreshRLfromtheusablecheckpoint.

RLfirstseedstillweak:base0/15low0/15high1/15;sameunknown;solegainbroadprint/copy.
Secondseedall16×3completed,analysisnext,keepallarms. MuSiQue132actualcalls48availablefinals:
stop1/12,broad1/12,targeted1/12(samequestion),fullsource3/12. Focusedrequests
didnothelpthisfixedreportrecipe. Do not claim learnedrouting/decomposition.

Mostpromisingpublicationdirection: separate access,selection,evidencepreservation
andfinaldelivery, then showamatchableinterventionimprovescompleteanswersonnewdata.
SFTaloneisaprerequisite; meaningfulRLgainstillnotestablished. New16longerMRCR
contextsareoutcome-blindselectedanddisjointfrom48priorcore/targettexts;notyetqueried.
See mainreport `2026-09-12-procedure-transfer-and-exact-rewards.md` and
[independent heldreadout](openai-mrcr-procedural-sft-dose32-readout-2026-09-12/main-final-held-snapshot-001/REPORT.md).

Older sections below are dated history, not current claims.

## Current interpretation — September 12, 18:23 UTC

The apparent benefit of varied training examples shrank sharply on the next
test panel. Repeated128 RL scored 425/512 on the frozen official test, versus
422 before training, 426 after supervised training, and 427/429 for the two
varied-data RL seeds. All answers were available. The first varied-versus-repeat
gap is only two answers here, compared with twenty on the earlier panel. Category
balance was identical across training blocks; differences in example difficulty,
the repeated block, and category boundaries remain possible explanations. Do not
claim a large general breadth effect from the earlier panel.

The controller tests separate access from task understanding. A structural
preview reduced Python tracebacks from18 to0 but exact answers from1/16 to0/16.
The model often returned a user request instead of the following reply. Four
supervised updates on32 verified retrieval demonstrations did not yet teach the
routine:0 exact,28 available,32 recorded on the training panel. The four missing
outcomes are three context overflows and one broker timeout, not four wrong
answers. No held readout ran. A fixed total32-step continuation is being prepared
with the same examples, prompt, objective and learning rate.

Root RL now has two genuine independent one-step checkpoints. Restoring the same
initial weights and using the same saved gradient gives the intended10x update
size. The larger update increases likelihood of both rewarded training attempts
and lowers five of six penalized attempts. This is likelihood movement, not new
answer accuracy. A paired starting-model/low-dose/high-dose evaluation on16
separate conversations is active. Keep all three outcomes, including failures.

The MuSiQue depth screen never called a helper:112 physical root calls, zero
children. A follow-up fixed graph compares ordinary reports, broad additional
reports, targeted questions, and the full source. Its first launch failed before
science because the serving entrypoint overwrote the requested worker extension;
repair is CPU preparation while the RL evaluation runs. No recursion benefit or
new architecture claim is supported yet.

See the focused analyses linked below and the new source-repository report
`docs/research-checkpoints/2026-09-12-controller-learning-and-transfer.md`.
Older sections are retained as dated history, not the current conclusion.

## Training-breadth update — September 12, 17:43 UTC

Repeating the same 128 training articles for eight RL updates did not reproduce
the broader-data result on the shared research-exposed 512-answer panel. The
fixed repeat128 checkpoint scored 417/512, versus 422 for c32 and 437 for the
eight-block broader-data checkpoint; every answer was available. Paired against
c32 it made 2 corrections and 7 regressions, and against broader RL it made 3
corrections and 23 regressions. This is evidence that the earlier result was not
caused by update count alone, but it is still one training run on an already
examined panel—not an isolated causal estimate of data breadth.

The next fixed test changes no checkpoint, prompt, seed, batching, grammar, or
scorer: evaluate repeat128 checkpoint 8 on the already frozen official-test 512
panel and compare it with the saved c32 / RL seed1 / SFT / RL seed2 readouts.
No new-panel result was used to select this checkpoint.

## Whole-RLM mechanism update — September 12, 17:35 UTC

The broader helper's component improvement did not improve this whole RLM. On
eight prospectively frozen AG News context groups, c32 and the fixed RL8 helper
both gave the unchanged QS6 root3/16 correct endpoints; all16 paired outcomes
tied. Deduplicating helper maps reused by two questions gives103/128 correct
record labels for c32 and108/128 for RL8, rather than treating the repeated
180/224→188/224 workload counts as224 independent decisions. Map aggregates
improved from5/14 to6/14 exact, but the sole new exact aggregate was error
cancellation: one gold-World record changed from a correct World label to an
incorrect Sci/Tech label while the context's local label score fell11/16→10/16.

The root mechanism audit found a concrete result-visibility failure. In four
paired count episodes the generated reducer assigned its integer without
printing it, so all three Python observations were empty. Context01's trusted
map count was3 but both roots answered2; context04's code also introduced the
wrong `u0,u1` scope. This was not taught by the authenticated QS6 corpus: all
144 authored Python actions across its72 training episodes printed their
outputs, including all72 reducers. Conversely, all20 live episodes with a
recognized reducer and nonempty scalar observation produced the matching root
answer, so the evidence does not say the root always ignores helper results.
See the [static mechanism audit](root-qs6-ag-live-helper-transfer-mechanism-2026-09-12/REPORT.md).

The corrected syntax result retires that intervention. Plain versus syntax was
5/24→2/24 endpoint correct. Strict finish-consistent usability was5/24→0/24,
and strict correct usability was3/24→0/24. Syntax reduced rejected actions but
did not produce a usable completion; the original all-unavailable export remains
an instrumentation failure, not the scientific result.

## Completed transfer and interface update — September 12, 17:00 UTC

The frozen official-test comparison materially weakens the apparent RL advantage.
On512 new local AG News examples, the starting helper scored422, the two fixed RL
seeds scored427 and429, and supervised training scored426. The RL seeds agree on
508 labels, so this is not simply a best-seed artifact, but their gains over the
supervised endpoint are only one and three answers; both descriptive
request-cluster intervals span zero. On the distinct, research-exposed panel the
corresponding totals were422/437/427/436. Do not pool the panels or claim that RL
meaningfully beats supervised learning. The changed official-test answers look
like modest category-boundary shifts, not a broader capability. See the
[four-arm source-to-raw synthesis](helper-agnews-official-test-transfer-findings-2026-09-12/FINDINGS.md)
(JSON SHA256 `391acb5fde4ab58b8157c55ba9792d60acf285066538152a6a604b2b6c452b02`).

The controller evidence is also narrower than a terminal score suggests. The
four short-conversation outputs with at least0.90 similarity did contain the
target passage, but only after broadly printing the context. Their Python
selection chose the wrong value or failed; the final model then read the broad
observation. This is recovery from a context dump, not successful programmatic
retrieval. See the [program-versus-terminal audit](openai-mrcr-short32-outcomes-2026-09-12/PROGRAM_VS_TERMINAL_ADDENDUM.md)
(JSON SHA256 `858fb090ea54796da506b1a155461dd7291e0da8022b115238868bfddffbcebb`).

The paired syntax run exposed an instrumentation defect, then yielded a recoverable
result. The legacy exporter rejected all48 endpoints against stale first-prompt
IDs, although every actual wire prefix matches the frozen condition prefix. A
call-free audit of the same saved responses corrected only that lookup. Endpoint
C/W/U is5/17/2 plain versus2/19/3 syntax; paired, syntax has1 win,4 losses,15 ties
and4 unknowns. Under the stricter finish-consistent interface metric it is3/2/19
versus0/0/24, or0 syntax usability wins and5 losses. Rejected actions still fell
35→8, but lower syntax friction did not improve complete behavior. Five requests
exceeded the8192-token limit; there were zero physical child calls. See the
[standalone syntax finding](../../../ARTIFACTS.md)
and [corrected source-to-raw readout](root-qs6-budgeted-evidence-syntax-corrected-readout-2026-09-12/CORRECTED_REPORT.md).

## New interpretation — September 12, 16:30 UTC

The controller sometimes finds the right passage but copies it incorrectly. In
the shorter-conversation test, four attempts located the correct answer but wrote
the two characters `\n` instead of a line break; three also added stray closing
punctuation. None passed the unchanged exact-copy requirement. Two other attempts
copied the wrong passage and still received partial similarity credit. The full
test had32 attempts,30 available results and two context-length failures.

A closer procedure audit adds an important limit: all four near-successes printed
a large part of the conversation into the model's own view. The Python extraction
was wrong or failed; the final model reply found the passage in that broad output.
This is not yet a learned search program or decomposition. The reward-learning
test may reinforce this shortcut, so we will measure observation size and actual
code behavior as well as the final answer. See the
[procedure audit](openai-mrcr-short32-outcomes-2026-09-12/PROGRAM_VS_TERMINAL_ADDENDUM.md).

This distinction matters for training. We should reward finding the right content
without mistaking text overlap with a wrong passage for success. We are preparing
two small comparisons: learning a complete working routine from demonstrations,
and learning from a reward that gives partial credit for near-exact retrieval and
full credit for an exact answer. The training examples are separate from the final
evaluation conversations. We have not yet shown that either approach improves the
controller. See the [mechanism audit](openai-mrcr-short32-outcomes-2026-09-12/SIGNAL_ADDENDUM.md).

The GPU is now testing all four previously fixed helper models on fresh official
news-test examples. Other accepted comparisons test a different classification
dataset, the original model before specialization, and whether better helper
answers improve the whole system. The repeated-small-training-set experiment has
completed eight updates; its heldout result is still pending.

We are also preparing a more direct decomposition test: questions that require
connecting facts across several passages. The model will choose its own helper
questions under the same total call ceiling, with zero, one, or two permitted
levels of delegation. This is a planned feasibility experiment, not a result.

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
