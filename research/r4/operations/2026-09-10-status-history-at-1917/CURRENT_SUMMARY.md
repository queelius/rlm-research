# What we know so far

Updated on September 10, 2026, at 19:12 UTC. These are exploratory results, not a
claim that we have solved general problem decomposition. This page includes newer
evidence than the fixed-cutoff cross-experiment review.

## Latest results at 19:12 UTC

The full execution review supports the trained controller's transfer across
changed user names, weights and thresholds. Correct answers backed by the
requested calculation rose **12→50 out of72**; for composed questions, **0→32
out of48**. All available paths were reviewed. The same source records were
used, so this is metadata transfer, not new-task generalization. Twelve trained
wrong answers used the right calculation on wrong subtask labels, making the
child model a concrete next target. [Report](../../analyses/root-question-sensitive-readout-followups-2026-09-10/metadata-semantics/REPORT.md).

The fresh-context field-order test supports the earlier direction: writing
the answer before its identifier reduced misleading-reference errors. Its
selective effect was **9.77 percentage points**, positive in14/16 contexts.
All96 calls were valid, but the effect narrowly missed our predeclared10-point
threshold. We report directional support without moving that threshold.
[Report and complete comparison](../../analyses/leaf-mnli-field-order-replication-live-2026-09-10/REPORT.md).

The GPU is now testing whether the trained controller scales to16/64/128/256
records and whether a cumulative subtask-return interface helps. The row-number
experiment completed96 calls and awaits its audit. RLVR still has no new update:
its latest attempt exposed a stale startup alarm that interrupted real rollouts
early. A timer-only recovery preserves the original tasks and seeds. Failed
attempts and their time costs remain visible; they are not negative RL results.

## Historical result at18:50 UTC

The child-model transfer test is now audited: fine-tuning improved official-test
label accuracy from64.0% to84.5% with100-record batches and from71.7% to88.5%
with16-record batches. All148 calls were verified, with no missing answers.
None of the500 normalized questions appears in the actual optimizer corpus,
although489 were previously evaluated in this research project. MAIN replayed
all148 calls and checked481 evidence pins without mismatch.
[Result, limits and next question](../../claims/child-adaptation-transfers-to-official-test.md).

The newRLVR and two interface/scale evaluations encountered integration failures
before scientific calls. No training update occurred in the failedRLVR attempt.
Those attempts remain preserved and are not evidence against the methods.
The corrected new-context field-order replication is now making requests on the
GPU; correctedRLVR, scale and positional-anchor jobs are being prepared.

## Historical update at 18:35 UTC

The trained controller's improvement survived changed user names, weights and
thresholds: correct answers rose **17→53 out of72**, with verified final answers
on55→72 tasks. Even allowing every missing comparison answer to be correct,
the trained model retains at least19 additional successes. Composed-question
correctness rose5→35/48. This is task-parameter transfer on the same records,
not new-record generalization. The full code-path audit is still pending.
[Native paired audit](../../../../ARTIFACTS.md#unpublished-files "Not published: root-question-sensitive-readout-followups-2026-09-10/root-question-sensitive-metadata-transfer-v1-AUDIT.json").

The fresh-seed code-path review is closed: correct answers backed by an actually
performed requested calculation rose **15→49/72**, supporting the original
15→52 result. A correction distinguishes three baseline expressions that were
written from calculations that actually completed; use19→60 for the latter,
not22→60. These are repeated samples on eight contexts, not new training runs.
[Finding and audit links](../../claims/question-sensitive-executed-composition.md).

The official500-record TREC test comparison finished all148 model requests;
its native audit is pending. A new terminal-reward training run now starts from
the successful SFT checkpoint and trains on composed questions, with primitive
questions reserved to check retention. Every update is checkpointed.

Two new evaluations hit integration failures before task calls. Their failures
are retained, fixes are being prepared, and they are not scientific evidence
against the tested methods. The three earlier component reports have passed
MAIN's evidence-pin checks and numerical review.

## Historical update at 18:08 UTC

The strongest new result is now fully audited. After varied-question SFT,
correct answers backed by the requested calculation rose from **15/72 to 52/72**.
For composed questions, they rose from **1/48 to 33/48**. Strict answer accuracy
rose 28→57/72, but five trained correct answers still used an unfaithful path;
we keep those measures separate. All 149 available original readouts received
manual program-and-observation review, and all 9,130 final source/artifact pins
verified without error. Ten faithful but wrong trained answers are completely
explained by wrong subtask labels.
[Plain-language finding, example and limits](../../claims/question-sensitive-executed-composition.md).

A fresh-seed readout supports the effect: 25→51 correct out of 72 planned tasks,
with 62→70 available answers and conservative gain bounds of +16 to +28. These
are the same eight contexts, not a new-context or training replication. Its
complete semantic report is being finalized. The GPU is testing changed user
names, weights and thresholds next; no transfer outcome has been read yet.

The output-field-order, host-side identifier attachment and base-versus-trained
child studies have separate audited reports. MAIN's final adoption is pending.
Their important caution is already clear: an interface may help misleading-ID
cases while harming aligned cases. That is not a universally better harness.
A new-context field-order replication and the complete official TREC-test child
comparison are both accepted behind the current run. Composed-task reward
training is being prepared from the stronger question-sensitive checkpoint.

## Historical update at 17:32 UTC

Training on varied questions produced a substantial local improvement:
correct protected answers rose from28/72 to57/72. On questions requiring
combined operations, they rose from13/48 to38/48. All eight contexts improved,
and conservative bounds for missing answers still show a positive gain.
Development questions remained3/8, so this is not a universal improvement.

The program review is encouraging but not yet fully closed. Among the trained
model's72protected attempts, MAIN found62actual task-faithful calculations,
52ofwhich also gave the correct answer. Five correct answers still arose from
incorrect or unsupported calculations. Ten faithful-but-wrong paths need
their remaining child-label error diagnosis. The complete baseline/development
semantic review is in progress; do not present these as independently replicated
or new-task generalization. These contexts were excluded from this root training
process but were exposed to child training. A fresh-seed paired readout is running.

Three further GPU studies have finished: output field order, host-side identifier
attachment, and trained-child versus base-model accuracy at two batch sizes.
Their terminal native audits are in progress. Full source results remain in
separate immutable run directories, including every failure.

## Historical update at 17:04 UTC

Question-sensitive SFT has now completed all six fixed updates on all72
demonstrations. The actual training/checkpoint timer was738.8seconds, and
the training phase took776.7seconds. Earlier capture and launch failures
are preserved separately; they were not successful training. Held-out
evaluation is running, so improved task performance is not yet established.

The identifier wording control has finished. Misleading identifiers reduced
accuracy to38.0–39.6%, versus80.2–82.8% in unrelated/aligned conditions.
Explicit same-record instructions left the large penalty in every context.
[Full finding and limits](../../analyses/leaf-mnli-visible-reference-disambiguation-live-2026-09-10/REPORT_MAIN.md).

Smaller child batches improved label accuracy by2.44percentage points, mostly
in one of two exposed contexts. They reduced all four host-computed target
errors, but none became exact. This keeps child semantics—not just Python
bookkeeping—as a useful next research target.
[Diagnostic report](../../analyses/leaf-c32-batch-granularity-live-2026-09-10/REPORT_MAIN.md).

Two GPU successors are accepted and waiting: answer-before-identifier and
label-only outputs with code attaching identifiers. Both compare fresh
responses under fixed prospective designs. Recent related work is summarized
in [the literature-to-experiment note](../../ideas/2026-09-10-output-addressing-and-reward.md).

## Historical update at 11:51 UTC

We now have two examples of the model genuinely combining child answers across
all 256 records and finishing the requested calculation. A shorter printed
view let it use data retained in Python without putting the full growing map
back into every model request. Both answers were wrong because of child-label
errors, not arithmetic. Every condition still scored zero strict task successes.
This is a useful harness mechanism to investigate, not an accuracy breakthrough.
[Finding and concrete examples](../../claims/shorter-view-enables-retained-computation.md).

The larger guide follow-up did not establish a practical gain. Guided versus
unguided accuracy was 5/24 versus 5/24 on original questions and 2/24 versus 1/24
on changed questions, with worse guided availability. It failed its complete
continuation criterion. [Evidence and limitations](../../claims/procedural-card-headroom.md).

The A100 is now testing whether clearer wording reduces the misleading-identifier
effect, using a full six-condition comparison on eight newly selected contexts.
The question-sensitive SFT attempt captured 65 of 72 demonstrations before its
time cap and performed no training. Its baseline evaluation is complete; a
bounded recovery will collect only the seven missing demonstrations, reuse the
baseline once and preserve the same six-update training plan. A separate fresh
small-versus-wide child-batch test is being prepared.

## Historical update at10:57 UTC

The RL audit is sealed. Seven weight updates made the routine cheaper, but
not more accurate:15→13 correct answers out of48, and408→229 physical model
requests. None of the correct composed answers in either condition performed
the full requested calculation. More reliable completion is useful, but it is
not the task-sensitive computation we are trying to teach.
[Finding, example and limits](../../claims/warm-primitive-rl-transfer-limit.md).

The96-question changed-parameter guide test has finished; its outcome audit
is beginning. The32-run shortened-Python-output test started automatically
3.24 seconds later and is using the GPU now. It changes the displayed view,
not the actual data retained in Python. Targeted SFT is CPU-qualified behind
it:72 demonstrations of varied operations and parameters, six fixed updates,
and144 protected plus16 development evaluation slots. No training gain is
assumed. A separate40-call misleading-identifier control is being prepared
on CPU as another decision-relevant successor.

## Historical update at10:36 UTC

The RL continuation and its evaluation have finished. It made seven actual
updates; its eighth batch had no reward variation, so correctly made no update.
MAIN reproduced the saved-checkpoint and action-loss checks. This verifies that
training occurred as intended, not that it improved the model's reasoning.

The initial final comparison is not an accuracy gain: 15/48 strict correct
before RL and 13/48 afterward, with more native final answers afterward.
The full trace audit is still being completed. Its initial review finds that
the correct composed answers in both conditions use a wrong calculation or
scope that happens to yield the correct number. These counts are preliminary,
not a sealed transfer finding. Empty returned outputs are being reported
separately from infrastructure failures and ordinary wrong answers.

The next experiment started automatically about five seconds later. It tests
the instruction card on both original and changed-parameter questions. The
shortened-output experiment is also accepted and queued. Meanwhile, a new SFT
curriculum is being prepared to teach the composed calculations directly,
with changed scopes, categories and thresholds and a separate withheld split.
It will be tested without the card. Its inputs are allocated, but training
has not started. [Current owners and restart record](../../RESEARCH_QUEUE.md).

## Historical update at10:08 UTC

The instruction-card audit is complete. A shared short guide elicited six
executions of the requested calculation, versus none without it. Four guided
answers were both faithfully calculated and correct; two were faithful but
wrong because the child predictions were wrong. This is useful instructional
headroom, not a learned skill. The full improvement criterion failed: the guide
raised strict scores from 3/24 to 7/24 but reduced available finals from 18 to 16.
[Finding, examples and limits](../../claims/procedural-card-headroom.md).

The next card test is now being implemented. It retains both original and
changed tasks, with and without the guide. All 24 changed cases separate the
requested answer from four specified shortcut calculations under the dataset
labels. This is a deliberately selected challenge, not an unbiased benchmark;
actual child predictions and executed programs must still be checked.

The A100 is continuing terminal-reward training. Six checkpoint state files
now exist; the first update's saved payloads were independently checked, and
later optimizer continuity is under CPU review. Final evaluation is still ahead.
The other CPU-prepared successor tests a shorter printed view of Python output
without reducing the underlying state or injecting a calculation procedure.

## Historical update at09:40 UTC

Keeping earlier subtask answers worked mechanically, but did not yet let the
model finish a calculation across batches. In six cases across all four context
groups, the memory helper returned growing collections of actual child answers.
None reached a completed calculation over that accumulated evidence. The
unchanged and cumulative versions scored1/16 and0/16, with only5 and4 final
answers. This is a useful diagnosis, not an accuracy improvement.
[Verified finding and next test](../../claims/retention-is-not-completed-computation.md).

Printing the growing maps is one concrete obstacle. Thirteen missing-result
paths hit the context limit: ten in root requests and three in child requests.
We are preparing a controlled test that keeps the Python state intact while
shortening its printed view. It cannot fix oversized child requests or wrong
child predictions, and it will supply no summary, algorithm or correct answer.

The reward-training continuation is now actually updating weights. Its first
saved update reused the original training batch, with13 admitted mixed-group
episodes and5173 root-action target tokens; the optimizer took87.66 seconds.
A second checkpoint exists. Final matched evaluation remains ahead, so these
are training-progress facts, not evidence of a performance gain. Checkpoints
include the adapter, optimizer and random state.

The instruction-card experiment has also finished. Its author-disclosed initial
review finds examples of all three requested procedures being executed only
with the card, including both correct answers and correct calculations of wrong
child predictions. Its final source audit is pending. This could identify useful
instructional headroom, but would not show that the model learned decomposition.

The separate task-file audit now covers all48 available finals, not just its
ten successes: none performs the requested operation and scope. The added
files were never read in the65 retained graphs. An additive wording correction
clarifies that the card experiment keeps the original questions and records
unchanged; only the shared instruction text is added to the prompt.
[Updated task-file claim](../../claims/task-description-access-not-exercised.md).

The last two automatic GPU handoffs took0.91 and2.20 seconds. Earlier recorded
idle gaps remain costs, not useful GPU work. Current owners, next experiments
and restart details are in the [queue](../../RESEARCH_QUEUE.md) and
[session checkpoint](../../../../ARTIFACTS.md#unpublished-files "Not published: ../operations/2026-09-09-allocation-5780/SESSION_0940.md").

## Historical update at09:14 UTC

The task-description audit is complete. Separate prose and JSON files were not
read in any of the 65 retained episode graphs. The unchanged/prose/JSON arms
scored 2/4/4 correct answers out of 24 each, but none of these ten successes
faithfully executed the requested calculation and scope. This is evidence that
the intended feature was not used, not evidence that task parameters are
useless. Missing answers and the small dependent panel limit accuracy claims.
[Claim and verified evidence](../../claims/task-description-access-not-exercised.md).

The GPU is testing automatic retention of earlier decoded batches. An accepted
successor will put the three general calculation procedures directly in the
model's input. These distinguish losing retrieved evidence from failing to
choose or execute the requested calculation; neither supplies correct labels.

The reward-training pilot collected a complete first batch but encountered a
shutdown error before any weight update. The saved batch passed authenticated
replay and a training preflight check. An additive continuation will use those
same examples, not replace them with another sample. Its costs include the
failed attempt. A separate accounting defect is also documented: the original
summary searched the wrong file layout and said zero calls, while the retained
wire records establish 286 calls and 283 returned completions. Original artifacts
are preserved. No RL efficacy result can be claimed from this failed attempt.

See the [live queue](../../RESEARCH_QUEUE.md) for execution details and the
[session checkpoint](../../../../ARTIFACTS.md#unpublished-files "Not published: ../operations/2026-09-09-allocation-5780/SESSION_0905.md")
for the recovery decision. Earlier status paragraphs below are historical.

## Historical update at08:53 UTC

The stronger SFT checkpoint is now generating training attempts for a bounded
terminal-reward pilot. The question is whether rewarding correct final answers
helps a model that already knows how to obtain and use subtask results select
the right calculation on changing questions. The comparison uses the unchanged
SFT model and the last actually committed RL update, not the best-looking saved
checkpoint. Every successful update retains weights, optimizer and random state.
No result from this training run is available yet.

The task-description experiment has finished. Preliminary counts are2/24 correct
with the original description and4/24 with either additional prose fields or a
JSON task file. Only16/17/15 final answers respectively are available. The trace
audit is checking whether any successes actually perform the requested composed
calculation; these small raw differences are not yet evidence of a reasoning gain.
The queued memory experiment instead tests a concrete observed failure: earlier
subtask predictions can be lost when a later batch overwrites the same variable.

Current process identities and handoffs are in the [live queue](../../RESEARCH_QUEUE.md).
The new14.14-minute evaluation-to-training gap is recorded as idle allocation,
separately from the earlier117.72-minute gap. Neither is counted as GPU research.

## Historical update at08:28 UTC

The four-checkpoint comparison reinforces a local training result. The saved
6/12/18/24-update models give4/1/3/15 correct answers out of16 repeated basic
tasks. Twelve of the15 later-model successes execute the requested calculation;
the other three are coincidences. The middle checkpoints often loop or produce
invalid tool calls, so this is not a smooth learning curve or evidence of an
abrupt learning threshold. These are exposed diagnostic tasks, not new transfer.
[Checkpoint audit](../../analyses/root-operator-dose-intermediate-live-2026-09-10/REPORT.md).

The larger-input test gives4/8 correct answers at16 records,0/8 at128, and0/8
at256. Four, zero and zero answers respectively are both correct and faithfully
computed. Only8/4/0 native finals are available. In two256-record cases the
model obtained all label batches but overwrote earlier batches instead of
combining them. Other failures involve child-label errors, wrong calculations
and context limits. This motivates a precise harness test of retained acquired
state, not simply more child calls.
[Scale audit](../../analyses/root-operator-scale-state-live-2026-09-10/REPORT.md).

The GPU is now running the three-arm task-description comparison. The terminal-
reward pilot is being corrected before launch after CPU review exposed three
integration defects; no scientific training attempt was made with that version.
The gap after the scale run was117.72 minutes without a GPU successor and is
recorded as idle allocation, not research compute. The next accepted successor
will advance automatically. Current execution details belong in the
[live queue](../../RESEARCH_QUEUE.md), not in historical status paragraphs below.

## Historical update at06:12 UTC

The local training gain remains verified:5/48 to29/48 correct answers, with
actual child acquisition increasing from1/48 to48/48 tasks. Exact review verifies
the requested computation in26 of the29 successes. Two others accidentally
give the right number despite using the wrong user scope; one recovers using
a literal record ID after losing the combined label map. Thus the gain is real,
but our earlier description of all29 as correct computations was too broad.
[Additive semantic audit](../../analyses/root-operator-dose-semantic-retrospective-2026-09-10/REPORT.md).

The new-context test is complete: the longer-trained model gives9/48 correct
answers, compared with6/48 for the earlier model. Only two successes, both basic
operations in one context, follow the requested computation. None of the
successful composed answers does. For example, adding everyone's weights can
accidentally match a request for the largest user's total. Many finals are
missing, so the small overall difference does not establish a transfer gain.
[Complete transfer audit](../../analyses/root-operator-composition-transfer-live-2026-09-10/REPORT.md).

The emerging question is precise: how do we move from a learned evidence-gathering
routine to choosing the right calculation for a changing question? We are
preparing a matched prose/JSON task-description comparison and a bounded
reward-based training pilot. Both will distinguish correct answers from
demonstrated correct operations. They are experiments, not presumed fixes.

The published8B reference is independently audited: neither tested package
produced a strict correct answer on24 tasks. Many outputs fail the final-answer
or child-label interface. This is a bounded model/scaffold compatibility result,
not a general model-quality judgment. Another full rerun is retired for now.
[Complete reference audit](../../analyses/root-published-rlm8b-reference-live-2026-09-10/REPORT.md).

At this historical cutoff the GPU was comparing four saved checkpoints and the
scale successor was accepted. Both are now complete; see the latest update and
live queue. The fixed-output misleading-ID finding below is unchanged.

## Historical update at04:52 UTC — mechanism wording qualified above

The longer training now produces a substantial **executed-behavior** gain, not
just lower training error. On the same48 questions, correct answers rise from5
after six updates to29 after24 updates. The longer-trained model asks a child
model for labels in every attempted task. All29 correct answers then use actual
calculations on the returned labels. Of these successes,28 have nonzero answers,
so this is not another improvement caused by guessing zero.
[Complete independent audit](../../analyses/root-operator-dose-continuation-live-2026-09-10/REPORT.md)
and [fit-versus-behavior plot](../../../../ARTIFACTS.md#unpublished-files "Not published: root-operator-dose-continuation-live-2026-09-10/operator-dose-fit-vs-behavior.svg").

The limitation is important: there are only12 input-context groups, some already
used in earlier evaluations; even the root-new records were used to train the
child. Seventeen early-model and ten later-model finals are unavailable, with
missing-outcome bounds reported. The direction of the overall gain survives
those bounds. Most successful tasks fit in one child request; reliable combining
of multiple batches is not established. We are preparing new-context tests with
both familiar operations and new combinations, plus intermediate-checkpoint
readouts to locate the change in behavior.

The tighter identifier control is also complete. With the requested output tags
held fixed, aligned source IDs give610/768 correct labels, misleading IDs289/768,
and unrelated IDs620/768. Every output is valid. Both aligned and unrelated
conditions beat misleading references in all16 groups. This strengthens the
wrong-reference interference finding, while showing that matching IDs are not
required for high performance here. It does not establish an internal mechanism
or statistical equivalence between the two better conditions.
[Fixed-output audit](../../analyses/leaf-mnli-fixed-output-visible-reference-live-2026-09-10/REPORT.md).

The GPU is running the published RLM8B/base8B package comparison. Its results are
not available yet. These parallel research threads distinguish improving a
component from improving the whole system, and fitting examples from using
evidence successfully in a free task.

## Historical update at04:24 UTC

The misleading-identifier result now repeats on16 additional sentence-pair
batches. Matching identifiers give611/768 correct labels, misleading references
298/768, and unrelated identifiers618/768: approximately80%,39%, and80%.
Every output satisfies the required format. Matching and unrelated identifiers
both beat misleading references in every batch. This strengthens the evidence
that an identifier can steer a prediction toward the wrong record; it does not
identify an internal mechanism or establish an improvement to the full RLM.
The close matching/unrelated scores are not a claim of equivalence.
[Independent replication](../../analyses/leaf-mnli-new-context-alien-correspondence-live-2026-09-10/REPORT.md).

The longer training run completed all18 additional updates, reaching the fixed
24-update checkpoint. It fits the demonstrations much better, including the
first evidence-acquisition action. The independent audit verified all updates,
optimizer continuity and saved checkpoints. Training plus checkpointing took
about61minutes; the separate behavioral evaluation is now running. Lower training
error does not yet establish that the model chooses and executes the routine
correctly on its own.
[Training audit](../../analyses/root-operator-dose-continuation-live-2026-09-10/TRAINING_REPORT.md).

Two follow-ups are already accepted: a tighter identifier control that keeps the
requested output tags fixed, followed by the published RLM-trained8B model and its
base model in the same paper-derived scaffold. The latter is a root-and-child
package comparison on an exposed panel, not a clean model-size or root-only
effect. Both will retain failed and unfinished cases. Recent literature supports
separating evidence acquisition, faithful use of acquired evidence, and final
correctness; a learned critic is not automatically a trustworthy reward.

## Historical update at03:29 UTC

The matching-ID advantage also appears on16 additional sentence-pair context
groups:639/768 correct labels versus398/768 with a constant tag. Every response
met the full output contract, and every context group favored matching IDs.
This adds breadth within the same four genres; it is not new-domain confirmation
or a claim that the model never saw these sentences during pretraining.
[New-context audit](../../analyses/leaf-mnli-new-context-correspondence-live-2026-09-10/REPORT.md).

The optional data-loader experiment is finished. Correct answers were7/24 with
ordinary files and10/24 with the loader available, but the model used the helper
only once and never used it to reload state. All21 faithful calculations used
ordinary files. Therefore the difference does not show that the helper fixed
state recovery. Five missing finals remain explicit; four faithful calculations
still inherit wrong labels from the source model.
[Loader audit](../../analyses/root-canonical-source-loader-live-2026-09-10/REPORT.md) and
[context-count correction](../../analyses/root-canonical-source-loader-live-2026-09-10/REPORT_CORRECTION.md).

The GPU is now continuing the same training recipe to a fixed24 updates, with
checkpoints7–13 saved so far. Its paired evaluation will compare old and new
checkpoints on the same tasks and separately test whether the demonstrated first
action is learned. Another accepted experiment first repeats the misleading-ID
control on new contexts. A comparison with the published RLM8B model is being
prepared under its intended interface. These are ongoing experiments, not results.

## Historical update at02:42 UTC

The misleading-ID result now has a useful control. Matching IDs produced619/768
correct labels, IDs belonging to the wrong visible records produced284/768, and
unrelated IDs produced628/768. Every response satisfied the exact format. Both
matching and unrelated IDs beat misleading IDs in all eight context groups. This
points to interference from a wrong visible reference, not merely the effort of
producing varied identifiers. The unrelated and matching conditions are close;
we have not established statistical equivalence or an internal mechanism. These
are exposed contexts. [Independent control audit](../../analyses/leaf-mnli-alien-tag-correspondence-live-2026-09-10/REPORT.md).

The fresh factual-world test is also sealed. File-only evidence produced12/16
correct answers and16/16 available finals; inline evidence produced9/16 correct
and10/16 available. All six missing inline finals followed copying/repair failures.
Among the ten pairs with answers on both sides, inline won twice and the other
eight tied. Thus the practical availability gain is clearer than any intrinsic
accuracy gain. File-only loaded the real evidence16/16 times, but still sometimes
replaced it with invented records after an error. Reversing the records changed
correctness in two worlds in opposite directions. [Fresh-world audit](../../analyses/root-fresh-join-externalization-order-live-2026-09-10/REPORT.md).

The six-pass training recovery has finished. It made six genuine Adam updates,
trained137,082 target-token exposures in20.2 minutes, and lowered teacher loss.
But all15 authenticated test finals said `Answer: 0`; only one was correct, and
none of22 recorded episodes acquired labels from a child. Baseline was2/24 planned
versus trained1/24, with22 and15 available finals respectively. Nine trained
finals remain unavailable, not repaired or silently scored as observed mistakes.
This recipe has not taught free task decomposition. [Recovery audit](../../analyses/root-operator-diverse-sft-live-2026-09-10/RECOVERY_REPORT.md).

A new-context sentence-pair replication is now running, followed automatically by
a voluntary canonical-data loader comparison. A longer training comparison is
being designed to distinguish learning the demonstrated first action from choosing
it freely. No result from these follow-ups is claimed yet. MAIN has read the full
new reports and verified their sealed analysis/raw-artifact pins.

## Historical update at02:08 UTC

**The strongest component finding now extends to deciding whether one sentence
follows from another.** When each answer carries the correct source record's ID,
the model labels622/768 pairs correctly (81%). Requiring a different visible
record's ID lowers this to280/768 (36%), despite every output satisfying the same
strict format. Where the two records have different correct labels, the model
follows the named record373 times, the displayed record80 times, and neither69
times. This is evidence that the requested identifier can redirect a prediction,
not merely help formatting. All eight context groups favor the matching condition.
These are repeated, already exposed contexts, not independent new-source confirmation
or a measurement of internal attention. [Exact-tag audit](../../analyses/leaf-mnli-exact-tag-correspondence-live-2026-09-10/REPORT.md).

**External files change how the root works, but the benefit depends on what is in
the file.** An initial factual-record experiment found that file-only evidence led
to8/8 real loads; with those same facts in the prompt, the model loaded none and
copied them into its programs. File-only produced far fewer output tokens, but
the six pairs with answers on both sides were all correct ties. A32-endpoint test
on newly generated worlds has now completed and its independent execution audit
is being finalized; consult the queue for preliminary results, not a stronger
accuracy claim. [Initial factual-record audit](../../analyses/root-record-externalization-live-2026-09-10/REPORT.md).

The completed semantic-prediction comparison is more cautionary. Hiding the map
from the prompt increases actual file reads7/24→19/24, but faithful calculations
only9/24→11/24. Final correct answers are5/24→7/24, with more model requests in the
file-only condition. Nine of the20 faithful calculations are wrong against the
dataset because the acquired predictions themselves are wrong. One additional
correct answer is an accidental zero after broken parsing. Thus reading evidence,
using it correctly, and answering correctly are three distinct measurements. All
eight missing finals are model-generated malformed tool calls, not random network
loss. [Semantic-map audit](../../analyses/root-semantic-map-externalization-live-2026-09-10/REPORT.md).

**The larger operator demonstration set is now actually training.** The original
attempt captured72 complete demonstrations using180 real child-model responses, but
a launch defect hid the GPU from the trainer. Its original24 trained endpoints
remain unrun, not evidence of ineffective SFT. The additive recovery reuses the
same captured corpus and fixed six-pass recipe; checkpoints1 and2 are saved, with
verified parameter updates. Its fixed final checkpoint will be tested on the24
originally unrun questions. We do not yet know whether it improves task behavior.
[Original attempt audit](../../analyses/root-operator-diverse-sft-live-2026-09-10/REPORT.md),
[current queue and checkpoints](../../RESEARCH_QUEUE.md).

Next comparisons are being prepared while training runs: misleading visible IDs
versus unrelated aliases, replication on new sentence-pair contexts, and a narrow
harness change addressing observed state-loading/repair failures. These are designs,
not results or accepted GPU jobs. The frozen earlier evidence catalog is unchanged.

## Historical update at00:07 UTC

The query-sensitive reward-training run completed all12 windows and made10 real
Adam updates. That is solid execution evidence, but its paired final test does not
show persuasive learning. Unchanged scored2/48 planned with46 available; trained
scored4/48 with36 available. Every trained success had gold answer zero, and22/25
exact trained replies were `Answer: 0`. The three paired trained wins were zero-gold;
the one nonzero unchanged success was lost to a trained NULL. Neither final arm
called a child. [Independent audit](../2026-09-09-allocation-5780/query-sensitive-rl-audit-report.md).

The availability regression is concentrated in the ambiguous `all` scope: trained
returned5/16 versus15/16 unchanged, usually after long root-call loops. The frozen
phrase “records belonging to all four users” was repeatedly read as an intersection.
Those endpoints remain in the original denominator. Even across unaffected single/
union cells, where both arms returned31/32, the apparent1/32→4/32 gain consists only
of additional zero answers. The result does not support repeating this exact
terminal-only recipe unchanged; it does
not rule out controller training, direct correct solutions, or child assistance.

The smallest next training decision is a disambiguated, nonzero-balanced released/
ancestor calibration, followed only if warranted by a tiny execution-grounded warm
start. Terminal reward with balanced answer support is the practical control. A
process-reward arm would answer a different mechanism question and must reward actual
use of returned evidence, not ceremonial tool calls. [Decision note](../../ideas/2026-09-10-after-qsr-training-decision.md).

## Previous update at22:59 UTC

The combination test found a practical bottleneck: giving the model Python helped
on2 of8 direct-input questions, but six programs failed to parse the sentence
records correctly. All eight copied the real facts; none opened the evidence file
or asked a child model. We have queued a matched comparison offering the same facts
as explicit JSON records, then making those records visible from the start.
This is a small, previously used four-world probe, not proof of general planning.
[Native-Python report](../2026-09-09-allocation-5780/native-partition-join-audit-report.md).

The report-mediated part of that run could not be evaluated: its strict extraction
gate left32 planned root endpoints unrun. Several incomplete reports still held
enough facts to answer the question. We therefore distinguish failing a complete
report contract from losing the answer itself; neither lets us invent missing root
results. The [correction](../2026-09-09-allocation-5780/native-partition-join-audit-report-erratum.md)
and [question card](../../questions/sufficient-interface.md) explain that distinction.

At that time reward training was still running, with three updates through five
batches. The completed result and ambiguity analysis are now summarized above.
Transfer of the joint-training signal and the record-format test were accepted
automatic successors. Consult the [live queue](../../RESEARCH_QUEUE.md), not this
historical status text.

## Training update at22:32 UTC

The new training experiment produced a useful, qualified signal. Training the whole
acquisition-to-answer sequence solved8 of16 planned free questions, compared with6
for reduction-and-stopping training and2 for the unchanged model. Most improvement
was on questions combining two users. The execution audit shows that the model
often copied returned labels into a calculation or counted them manually; it did
not reliably learn to carry accumulated state through the intended program. Joint
training also made401 free model requests, versus281 and77. Both trained arms had
four actual updates, but joint training used about four times as many target tokens.
Four previously used contexts and unavailable endpoints make this exploratory, not
a generalization claim. [Audited report](../2026-09-09-allocation-5780/joint-state-reduction-sft-audit-report.md),
[checkpoint-wording correction](../2026-09-09-allocation-5780/joint-state-reduction-sft-audit-report-erratum.md).

We are checking that signal on new root input groups with all three fixed policies.
Separately, a reward-training run is now asking whether the model can learn counting,
counting distinct users and adding visible weights, then combine those operations
with user scopes not paired with them during training. It reserves time to compare
the starting and trained models and saves every actual update. These are active
research questions, not results. The [live queue](../../RESEARCH_QUEUE.md) tracks them.

## Historical update at21:54 UTC

The separating visibility experiment is now audited. Showing actual earlier child
observations increased genuine old-state use from3/32 to18/32 and faithful scoped
calculation from3/32 to16/32, but final correctness only changed14/32→15/32.
Quoting producer code without its observations mostly prompted new acquisitions.
This supports an effect on evidence use, not yet a useful accuracy gain. All64
coordinates remain in the denominator; two endpoints were unavailable. See the
[report](../2026-09-09-allocation-5780/state-content-factorial-audit-report.md)
and [one denominator correction](../2026-09-09-allocation-5780/state-content-factorial-audit-report-erratum.md).

Both live-state SFT arms have completed four updates and are entering evaluation.
A planned larger count-training successor was retired before GPU launch: exact
comparison showed it reused the already completed BROAD16 curriculum. That earlier
run improved13/48→16/48 overall but was flat5/24 on the main composition test.
New starting weights and interface alone would not make it a new breadth study.
The replacement design will target genuinely query-sensitive operations; the native
Python composition experiment is being implemented concurrently. These decisions
preserve GPU time for a new uncertainty, not a duplicate of a stale plan.

## Sealed findings at21:41 UTC

Two useful results now have independently checked traces. First, **making the
model's earlier observations directly visible helped it use work already done**.
With the genuine earlier conversation quoted, it correctly answered10/16 tasks
and faithfully calculated from the earlier predictions12/16 times. When merely
given names of files containing the same state, it answered3/16, never opened
those state files, and instead made42 new child requests. A third condition that
displayed metadata but left the labels in files answered6/16 planned tasks, with
two no-answer endpoints. These are only four previously used source contexts.
The quoted condition includes both code and observations, so it does not isolate
the helpful ingredient. The separating64-endpoint experiment has just completed
and its actual programs are being audited. [Restart report](../2026-09-09-allocation-5780/artifact-restart-audit-report.md).

Second, **source-linked output labels still help under a cleaner classification
interface**. With coding instructions and tools removed, constrained matching-ID
outputs correctly labeled218/256 records, versus129 with a constant placeholder
and123 with plain labels. Matching helped in every one of four contexts. Removing
either the coding-oriented role or tools also improved matching's freely generated
valid batches from0/4 to3/4. Its remaining failure used a forbidden sentiment label,
not a wrong or missing ID. This separates some instruction/format problems from
the remaining classification advantage; it does not prove a hidden attention
mechanism or general performance across models. [Role/tool report](../2026-09-09-allocation-5780/leaf-role-tool-audit-report.md).

The latest narrow corrective training **did not establish better performance from
scratch**. Its original free-task scores were unchanged10/32, first-action training
2/32, and corrective training7/32 planned, with only25 corrective final answers
available. Both four-update training arms completed, but the last evaluation stage
hit its time limit. A separate completion of16 previously unrun prepared-state
tests obtained5/16, with14 available; only one actually calculated the supplied-map
scalar, the same count as the unchanged root. Other successes classified relevant
records again. This is not evidence that the taught correction was reliably learned.
The new queued recipe therefore uses actual accumulated state instead of copied
map literals, and includes the complete acquisition-to-answer sequence. [Original
training report](../2026-09-09-allocation-5780/corrective-sft-audit-report.md),
[additive conditional completion](../../analyses/root-corrective-reduction-sft-live-2026-09-09/completion/REPORT.md).

In the partition-composition test, a valid answer format was necessary but not
sufficient. Exact decoding made all12 constrained answers well-formed, but all12
were wrong, including the direct-input cases. All12 free answers also failed the
strict contract. Complete extracted evidence remained sufficient to compute the
answer. We are preparing a native Python comparison to test whether executing the
combination changes this bottleneck; the old fixed-level test did not provide
Python. [Final-interface report](../2026-09-09-allocation-5780/partition-final-interface-audit-report.md).

The active work is joint live-state SFT; a broader16-window reward-based training
study and the native Python diagnostic are being prepared concurrently. The
[live queue](../../RESEARCH_QUEUE.md) owns current operational state. Lower training
loss, successful file reads, and correct-looking answer agreement remain separate
from actual executed task success. These living updates do not modify the earlier
fixed-cutoff evidence catalog or erase unsuccessful runs.

## Earlier sealed findings at20:27 UTC

The new A100 allocation is active; consult the [live queue](../../RESEARCH_QUEUE.md)
for processes and successors. The summaries below use sealed evidence available
through 20:27 UTC. Repeated endpoints are nested within small numbers of context
clusters, so endpoint counts are not independent-replication counts.

Clearer descriptions of the input fields removed all 18 observed field-name
errors in the newest wording comparison. However, telling the model more about
the supplied label map did not consistently make it use that map. Of 48 cases
that loaded the file, only 18 used its labels for the requested calculation or
filtered list; many replaced it with a new child response. A final answer that
agrees with the map is therefore not enough to establish that the model used it.
There were 58 correct answers among 95 available endpoints, with one genuine
runtime failure kept separate. These repeated trials cover only four contexts.
[Sealed wording and execution audit](../../analyses/root-map-contract-clarity-live-2026-09-09/REPORT.md).

The new free-output test exposed an instruction mismatch. Exact output constraints
yielded48/48 valid batches, while free generation yielded4/48. But35 free responses
tried to use Python, which the request explicitly advertised, and nine other arrays
ran past the requested number of items. The four valid free batches copied every ID
correctly. This does not show that the model cannot copy IDs unaided. We are first
testing an explicit leaf-classification role with irrelevant tools removed. The
source-ID accuracy advantage remains strong in the constrained outputs on this
already exposed panel. [Independent free-output audit](../2026-09-09-allocation-5780/free-id-audit-report.md).

Adding final-answer demonstrations did not improve our newest training recipe.
The unchanged model answered 8/16 cases correctly; action-only and action-plus-final
training each answered 1/16. All answers were available. The model already knew
how to repeat a computed number. Its harder problem was selecting the right
records and actually computing their answer. After training, it often displayed
all the labels but skipped that calculation. We are retiring this particular
recipe, not concluding that SFT generally fails. [Full sealed report](../2026-09-09-allocation-5780/complete-sft-audit-report.md).

Simply making a reducer or map available was not enough. In the 32-endpoint
supplied-map study, ordinary Python scored 5/8 with either sampled or privileged
maps; the advertised helper scored 3/8 and 2/8. Only one helper endpoint actually
called the helper successfully, and it reduced a fresh child map rather than the
supplied map. This is evidence about resource uptake and execution, not a clean
arithmetic comparison. [Reducer audit](../../analyses/root-supplied-map-reducer-live-2026-09-09/REPORT.md).

A follow-up crossed the optional API example with whether the same map bytes were
also printed inline. Dataset correctness was 6/8 in every cell (24/32 total), so
all eight paired block contrasts were zero across only four context clusters.
Actual traces show supplied-map state use in 26/32 endpoints: 25 programmatic
reductions and one manual prose reduction. The other six—all example-present,
file-only—made a new child request and overwrote the supplied map. Every inline
endpoint's executed code still opened `labels.json`; none parsed the inline copy,
so map consistency is not evidence that inline text was used. The common field/map
clarification also makes this a different baseline from the earlier reducer.
[Independent visibility audit](../2026-09-09-allocation-5780/visibility-audit-report.md).

The first partition pilot scored 0/40 strict finals, but that floor does not show
communication loss. Its instrument was too narrow: all 24 child extraction calls
returned exactly the requested 16 triples (384/384 triples correct), and complete
evidence theoretically implied the gold answer on 8/8 coordinates, yet all eight
full-evidence parents hit the 256-token cap before answering. Ordinary prose also
retained positive buyer facts sufficient for all four cross-partition answers
under a separately labeled manual reduction. The next comparison must first make
the final JSON interface work at a sufficient cap. [Partition audit](../../analyses/root-partition-report-live-2026-09-09/REPORT.md).

The broader bridge audit is also complete. Better child labels still do not
produce a reliable whole-task improvement across the three trained roots.
All three remain at zero on the eight checksum cases in either output format.
Concrete traces reveal incorrect use of returned dictionaries and missing
calculations, rather than alteration of a correct displayed answer.
[Three-root audit](../2026-09-09-allocation-5780/audit-report.md).

Together these results prioritize executed state use, scoped reduction, and a
sufficient final-answer interface. They do not establish general decomposition,
a communication bottleneck, or a blanket failure of supervised learning.

## Historical handoff at 17:50 UTC

The current GPU evaluations have finished. At the user's request, work is moving
to an already available 48-hour allocation. The next training study is prepared
but unstarted; it compares the same first-action demonstrations with and without
an authentic final-answer example. [Exact resume instructions](../2026-09-09-to-48h-allocation/HANDOFF.md).

The latest helper diagnostic supports the source-ID result: with the same supplied
history, a matching rather than constant current ID increases mean probability
assigned to the correct label by about0.50 on news and0.28 on sentiment examples.
These are conditional probabilities over a fixed set of labels, not sampled
accuracy or measurements of attention. [Sealed replay audit](../../analyses/leaf-local-cue-replay-live-2026-09-09/REPORT.md).

That component improvement has not yet become a whole-RLM gain in the original
bridge test. Both child formats solve1/8 count cases and0/8 checksum cases, despite
better labels in matched count calls. A concrete root program accumulates labels
but counts only its last batch. The same comparison with two other trained roots
has finished; outcome audits are still pending. [Original bridge audit](../../analyses/root-child-representation-bridge-live-2026-09-09/REPORT.md).

The [new evidence catalog](../../analyses/research-factory-2026-09-09/README.md) links nine recent
sealed reports to eight research questions, thirteen claims and six decisions.
It retains negative findings, unavailable results and publication gaps. Its
bounded cutoff precedes the new replay audit and is not a full-history synthesis.

## Historical findings and work at 16:59 UTC

Matching output IDs still substantially improve labels on new research records in
both released models. All 32 paired comparisons favor matching over a constant
placeholder, and every response is valid. This reduces two concerns: the effect
does not require our fine-tuning and is not confined to the earlier records.
"New" refers to the checked research catalogs, not unknown pretraining exposure.
[Completed fresh-data audit](../../analyses/leaf-fresh-correspondence-live-2026-09-09/REPORT.md).

The misleading-ID follow-up is also strong: when forced to emit another record's
ID, the helper usually labels that named record instead of the displayed position.
The independent report is being sealed. This is a behavioral cue-following result,
not a hidden-attention measurement. The active whole-RLM experiment tests whether
child representation changes improve final count/checksum answers; a fixed-history
conditional diagnostic is queued afterward.

The latest reward-training run has completed four updates. Its sealed independent audit
finds 7 to 11 correct answers out of 24 paired cases, with gains mainly
on longer inputs and none on the new question patterns. One empty earlier answer
was caused by a runtime error; an availability-sensitive analysis still gives a
positive but small net change. The optional extra
sampling was never needed, so these results do not test whether refill helps.
[Full audit, costs and concrete failures](../../analyses/root-bounded-refill-rl-live-2026-09-09/REPORT.md).

Training on authored first actions did not teach the intended filtering strategy.
Both new variants solve the same 1/16 cases versus 4/16 for the starting model,
and their final answer format worsens. The final audit will retain one unavailable
starting-model endpoint. We are reassessing demonstration completeness and new
context coverage before the next training run.

The query failures also need a narrower interpretation. Many arise from one
record's label disagreement with the dataset, while other runs show a correct
label map without ever computing its count. All 19 displayed integer counts in
the reviewed trajectories are copied faithfully. This is not evidence that the
model routinely changes a correct computed answer when speaking its final reply.
[Trace-linked taxonomy and availability correction](../../analyses/root-query-failure-taxonomy-2026-09-09/REPORT.md).

## Completed results at 15:44 UTC

Using larger training updates on the same 27 successful examples improved correct
answers from 8/24 to 14/24 in a paired comparison. Nine cases improved and three
regressed. All 24 final answers used the required format. Most gains were on
longer inputs; new question patterns did not improve. The initial four-record
example was still copied just as often, so this does not demonstrate a newly
learned general planning strategy. [Full audit and examples](../../analyses/root-success-sft-lr-live-2026-09-09/REPORT.md).

A small follow-up also supports the concern about showing partial totals too soon.
With the success-trained model, always showing a running count scored 2/8, waiting
to show it until the relevant returned-label map was complete scored 5/8, and the
ordinary interface scored 4/8. The coverage-first rule took more calls. This is
an exploratory presentation effect, not yet a generally better harness.
[Completed independent audit](../../analyses/root-coverage-first-live-2026-09-09/REPORT.md).

A failed service launch, its exact repair, subsequent completed runs and the
current accepted successors are preserved in the [live queue](../../RESEARCH_QUEUE.md).

## Earlier results at 15:05 UTC

Training on27 complete successful RLM examples improved exact final answers from
5/24 to9/24 in a fresh paired readout. A separately reward-trained checkpoint also
scored9/24, but solved partly different cases. Both models became better at finishing
the required answer format and examining the relevant records; this does not yet
demonstrate reliable general decomposition. These24 cases come from eight previously
exposed contexts. [Complete comparison and examples](../../analyses/root-success-trajectory-sft-live-2026-09-09/REPORT.md).

The output-ID finding is stronger now. It appears in two released models without
our fine-tuning, and moving sparse ID reminders across the **same records** moves
the accuracy benefit with them. Benefit is large just after a reminder and smaller
three records later; constant placeholders are much flatter. This rules against
simply having easier records at the reminder positions. It does not reveal the
model's hidden attention mechanism or ensure an exact whole-RLM answer.
[Released-model test](../../analyses/leaf-qwen35-identity-live-2026-09-09/REPORT.md) ·
[Same-record test](../../analyses/reminder-phase-live-2026-09-09/REPORT.md) ·
[Plain-language same-record plot](../../analyses/reminder-phase-visualization-2026-09-09/REPORT.md) ·
[Field-order result and plot](../../analyses/leaf-sparse-cue-order-main-review-2026-09-09/REPORT.md).

One harness change made results worse in a useful, interpretable way. Showing a
running count led all eight episodes receiving it to stop after four records,
even though the summary said many records were unexamined. Exact answers fell
from3/8 to0/8. The completed follow-up above tests whether withholding partial
counts avoids that mistake. [Evidence and concrete example](../../analyses/root-accumulation-ledger-live-2026-09-09/REPORT.md).

Both the larger-update and coverage comparisons have since completed. All choices,
checkpoints, failures and idle scheduling gaps are in the
[live queue](../../RESEARCH_QUEUE.md). The detailed history below remains important;
none of these experiments establishes broad planning or a new generic ID method.

## The big picture

We are studying whether a small language model can solve larger problems by
writing Python, asking another model to solve smaller parts, and combining the
answers. In our RLM setup, a good answer from the helper is not enough: the
coordinating model must ask useful questions and use the returned information
correctly.

Two recent comparisons are encouraging. They address different parts of that
process and should not be presented as the same result.

| Question | What we observed | What it does not establish |
|---|---|---|
| Can reward-based training improve the coordinating model while the helper stays fixed? | Two independently seeded training runs improved matched final answers: 5/24 to16/24, and9/24 to15/24. The second had11 gains and5 losses. | Both use the same six exposed context groups. Their questions were used in helper training. This is encouraging directional evidence, not a precise replication estimate or general decomposition result. |
| Can a simple output-format change help a helper keep many answers matched to the right inputs? | For batches of 64 items, explicit output IDs increased question-classification accuracy from 38.2% to 93.6%, and sentiment-classification accuracy from 60.1% to 96.3%. Both conditions already had IDs in the input. | These are item-labeling results, not final RLM answers. The output instruction and enforced format changed together, and the ID format generated more tokens. |

The first result comes from the [first root-training comparison](../../analyses/root-continuation-live-2026-09-09/REPORT.md)
and the [completed independent-seed comparison](../../analyses/root-independent-seed-continuation-live-2026-09-09/REPORT.md).
The predeclared validation rule selected update8 in the first run and update6 in
the second. The second run saved eight updates, but update8 was not its evaluated
policy. Four of its six context groups improved, one tied and one worsened.
The second comes from the [completed output-ID comparison](../../analyses/anchor-indexed-followups-live-2026-09-09/ANCHOR_REPORT.md).
The reports explain the matching, denominators, costs and remaining uncertainties.

## Why these findings matter

Earlier supervised training showed that the helper could learn the local
classification task. The newer experiments suggest that using this ability
reliably also depends on how information is represented and how the coordinating
model has been trained. That gives us concrete changes to test in the RLM itself,
rather than only trying larger models.

A [closer look at the root result](../../analyses/root-first-action-screen-2026-09-09/REPORT.md)
shows one concrete improvement: its first request was correctly formatted for
the Python tool in 13/24 cases before training and 22/24 afterward. The setup
supplied instructions and a worked example, but did not prefill a tool-call opener.
An [additive correction](../../analyses/root-first-action-screen-2026-09-09/PREFILL_CORRECTION.md)
verifies that both models sampled the opener in all24 cases; training improved
valid serialization, not the observed rate of attempting a tool call.
Better interface use is an important prerequisite;
general adaptive planning remains a future research question.

A [new prospective comparison](../../analyses/root-contract-factorial-live-2026-09-09/REPORT.md)
strengthens the evidence for the trained coordinator, while raising a new
question. On fresh sampled runs with the ordinary instructions, the original
model solved 6/24 cases and the trained model solved 20/24. A reminder about how
to read returned JSON text changed those scores to 9/24 and 14/24, respectively.
The instruction helped one model but hurt the other. This is another evaluation
of the same trained weights on the same six contexts, not an independent training
run or a new dataset. It shows why we need to test training and interface changes
together, rather than assume that a seemingly clearer instruction helps every model.

The output-ID comparison is especially clear about one distinction: every output
was valid in both conditions, but many anonymous labels were still wrong. Getting
the right format does not guarantee that answers remain attached to the right
items. Even the improved ID condition rarely labeled an entire 64-item batch
perfectly, so exact downstream answers can still be difficult.

A [completed follow-up control](../../analyses/grammar-training-padding-controls-2026-09-09/REPORT.md)
helps separate useful output cues from simply writing more text. With the same
structured output, meaningful tags produced 491/512 correct question labels,
versus 229/512 with constant placeholder tags. Sentiment scores were 481/512
versus 328/512. Output-token counts were similar, and all four context groups
per task favored meaningful tags. However, those meaningful IDs also counted
positions in order. Neither result proves an attention mechanism or a benefit
to complete RLM answers.

The [next control](../../analyses/identity-counter-live-2026-09-09/REPORT.md) randomized source IDs
and input order. Matching source tags still gave95.6% correct question labels
and93.8% correct sentiment labels. A changing counter gave28.0% and49.3%, despite
similar output-token costs. All96 outputs were structurally valid.

A [post-hoc diagnostic](../../analyses/identity-counter-live-2026-09-09/POSTHOC_NUMERIC_ID_REPORT.md)
then uncovered an important confound: counterp0001 and sourceq0001 share a number.
If the counter's labels are compared to the source with that number, agreement
becomes83.9% and93.1%. The original scores stay unchanged: the model answered for
the wrong records. The counter therefore was not a clean neutral bookkeeping
control. The [completed prospective control](../../analyses/identity-factorial-live-2026-09-09/REPORT.md)
removed that overlap and swapped the letter prefixes. Matching source IDs still
beat position counters by47–53 percentage points on question types and about35
points on sentiment. Removing overlap improved the counter, but did not eliminate
the ID advantage; all four contexts per task favored matching IDs. All384 outputs
were valid. These are the same exposed context sets, not new-data confirmation.

There is an important distinction for our larger research question: a model can
attach labels to the wrong items yet preserve the total number of each label.
Indeed, some counter conditions had poor item correspondence but fairly accurate
category totals. Better item labeling therefore does not automatically imply
better whole-context counts. Questions that combine labels with record-specific
information can test where correspondence actually matters.

A [new-task comparison](../../analyses/agnews-identity-live-2026-09-09/REPORT.md) now strengthens
the output-ID finding. Across four new groups of news articles, matching each
output to its source ID improved classification by about43–47 percentage points
over numbered outputs. Every output satisfied its required format. The advantage
appeared both before and after our helper fine-tuning; that training was not
necessary for it. This is evidence across a third task, not yet a benefit to a
complete RLM answer or proof of the model's internal mechanism.

A [single traced example](../../analyses/root-consumption-example-2026-09-09/REPORT.md) illustrates
another problem. The helper correctly identified all 14 people relevant to a
counting question, but the coordinating program treated the returned JSON text
as individual characters rather than decoding it into labels. Its computed count
was zero, which the model then reported. This motivates a clearer return-type
instruction; it does not tell us how common the mistake is or prove that the
recent training fixed it.

## What is being tested next

The full training comparison is complete and independently audited. On the six
long question-classification contexts, the earlier mixed-size-trained model
already scored 373/384 when asked to return IDs. The model specifically trained
on ID outputs scored 374/384: two improved labels and one regression. We have not
demonstrated an additional benefit from that specialized training. Both models
still failed the requested long plain-list format. The
[completed report](../../analyses/anchor-indexed-followups-live-2026-09-09/REPORT.md) explains
why we should test the interface before simply adding more training.

The format, training and placeholder controls are complete. They reinforce the
absence of a demonstrated benefit from extra ID-specific training. Unconstrained
tagged outputs were all invalid, so the useful-tag semantic comparison currently
depends on an enforced output format.

The independent reward-training repeat is complete and audited. Its original
attempt stopped after six updates on a process-inspection race; a continuation
from exactly saved weights, optimizer and random state completed the remaining
stages. All old artifacts and the original failure remain available. Summed run
envelopes were89.5minutes, while optimizer work across eight updates was6.7minutes;
training-episode generation, evaluation and model serving account for much of the
remaining time. The final gain above belongs to its selected sixth-update policy.

A [whole-RLM helper experiment](../../analyses/receipt-ablation-live-2026-09-09/REPORT.md)
completed and audited 72 episodes. The unchanged setup solved 21/24 cases; two
new helper-interface variants each solved 0/24. Crucially, neither variant actually
called the helper. The model often looked for answer labels that were not in the
input, instead of asking the helper to classify it. This is a practical failure
to use the unfamiliar interface, not evidence that checking returned answers is
harmful. The new prompts also removed a familiar worked procedure. A small
follow-up tested explicit API teaching and restoration of that procedure.
That [96-episode follow-up is complete](../../analyses/receipt-uptake-live-2026-09-09/REPORT.md).
It restored some helper use, but did not improve final answers. Of127 matching
helper invocations,61 returned complete maps and65 ended with empty parsed
replies despite generating text; one ended in a request error. Even correct
helper information was sometimes combined incorrectly. The child interface and
the coordinating program have separate weaknesses.

The [broader reward-training campaign](../../analyses/root-broad-equality-continuation-live-2026-09-09/REPORT.md)
is now complete and independently audited. After sixteen updates, the model
solved 16/48 final cases versus 13/48 before training: eight gains and five
regressions. The main comparison on new 64-record compositions was unchanged
at 5/24. The small overall gain came from shorter cases and one additional
128-record success; neither model solved any of the four 256-record cases.
This is not evidence that simply broadening the training recipe produces
general problem decomposition.

A [later diagnostic](../../analyses/root-broad-posthoc-examples-2026-09-09/REPORT.md) adds an
important qualification. On the24 cases where both models returned numeric
answers, average counting error fell from4.63 to0.88. This was a post-hoc,
response-selected subset, not the original success criterion. The model often
got closer without getting the exact answer; we should measure both in future
experiments while keeping unusable outputs visible.

All sixteen weight updates were verified. The best intermediate validation
score was 9/16 at update eight, but the prespecified final model remained
update sixteen, which scored 8/16 on validation. We did not substitute the
more favorable checkpoint. The original stopped attempt and six excluded
episodes remain documented rather than being silently discarded or rescored.

The whole campaign took about 135 minutes of combined scientific run time;
optimizer and checkpoint work accounted for about seven minutes. Generating
training episodes, evaluating models, repeated model startup and running
their Python environments made up much of the rest. The final model used
more helper calls, but fewer output tokens, so there is no single unqualified
claim that every measure of cost increased.

The [16-episode role-instruction pilot](../../analyses/child-role-suffix-live-2026-09-09/REPORT.md)
is also complete. It did not improve final answers:2/8 in each condition. The
expensive helper tool loops that motivated it did not occur in either condition,
so this test cannot show that the instruction suppressed them. We are not
adopting that wording change as an improvement.

The [planning pilot](../../analyses/adaptive-filter-live-2026-09-09/REPORT.md) changed the question
on the same input: sometimes everyone matters, sometimes only one user's records.
The freely acting coordinator solved none of16 cases and never called a helper.
It often used unreliable keyword rules. The programmed filtering procedure
answered three of eight user cases correctly, but helper-format failures stopped
the other five. Full-file procedures also failed to finish their answers. This
does not yet give a clean test of which successful plan is cheaper.

Those follow-ups are now complete. Enforcing the helper's requested reply format
made eligible replies reliably readable, but did not by itself establish better
whole-task answers. The [typed-helper audit](../../analyses/typed-helper-child-live-2026-09-09/REPORT.md)
retains nine unavailable or unrun cases from its time-limited experiment.

With our own fixed Python programs, the filtering opportunity is now measurable.
In six matched cases where both programs answered correctly, filtering first
reduced helper calls from48 to6 and generated helper tokens from6,931 to428.
The filter answered all eight cases; the all-file program had two setup failures
and answered its other six correctly. Those failures are not two extra accuracy
wins. This is a [hand-written baseline](../../analyses/typed-adaptive-operator-live-2026-09-09/PRIMARY_REVIEW.md),
not a learned planning result. It shows a useful behavior a future model could
learn to choose. The linked additive cache correction supersedes the original
implementer report's incorrect missing-cache statement.

The [supervised training audit](../../analyses/root-interface-sft-live-2026-09-09/REPORT.md)
separates learning an interface from solving a task. Before training, the model
called no helpers in24 tests. After four updates, it called helpers in all24,
and all50 helper replies had the required structure. Yet correct final answers
only changed from1/24 to2/24, and correctly formatted final answers fell from19/24
to9/24. In22 tests, the model began by copying the taught four-record example.
Only11 covered every relevant record. Two even returned a wrong final answer
after collecting maps that implied the correct count.

The examples taught actions, not complete semantic counting solutions. Their
long helper-call targets received about95% of the supervised token weight;
short final answers received about5%. These observations motivate separate
tests of reward-based learning, balanced example weighting and more complete
demonstrations. They do not yet establish which limitation caused the failures.

The [48-call output-order comparison](../../analyses/output-cue-order-live-2026-09-09/REPORT.md)
is now independently audited. Matching IDs still helped substantially when the
label came before its ID. The benefit therefore does not require writing the
current ID immediately before the current prediction. This does not show that
field order never matters, or explain the model's internal mechanism. We have
completed a follow-up asking whether fewer ID reminders retain useful accuracy
while producing less text.

The [reminder-frequency experiment](../../analyses/leaf-sparse-anchor-main-review-2026-09-09/REPORT.md)
is complete and independently checked against all144 raw responses. Fewer reminders
produced substantially less text, but every context-and-seed pair lost accuracy.
When every fourth answer carried an ID, accuracy often fell between reminders.
For news articles, matching IDs helped at the tagged positions but did not improve
the intervening positions overall. The linked plot shows this clearly. This is
an output-behavior finding, not proof of how attention works inside the model.

The [adaptive reward-training follow-up](../../analyses/root-adaptive-rlvr-live-2026-09-09/REPORT.md)
stopped after seven real updates. In its eighth batch, answers to one question
were all correct and answers to the other were all wrong, leaving no within-question
contrast for that learning rule. This is not evidence that the model had mastered
the tasks. Its original midpoint stayed2/8 correct, and the planned final-eight
evaluation never ran. The seven-update checkpoint is preserved and has now been
tested in the new, explicitly separate successful-example comparison above.

The [equal-example-weight comparison](../../analyses/root-interface-sft-row-mean-live-2026-09-09/REPORT.md)
is complete: both models solved the same two of24 cases. Giving short final-answer
examples much more weight did not help. Those examples already had almost zero
training loss. The model could reproduce their easy answers, yet still failed
after real helper observations. This makes richer complete examples a more useful
next test than further changes to weighting alone.

We screened completed training trajectories, without taking examples from evaluation.
The [screen](../../analyses/adaptive-success-trajectory-feasibility-2026-09-09/REPORT.md)
identified27 successful trajectories with supported evidence and a faithful computed
answer. The completed run learned all114 actual root-model turns, including recovery
from errors, and saved eight complete-pass checkpoints. Its paired evaluation gives
5/24 before versus9/24 after training; the last saved reward-trained model also
scored9/24. Their equal totals do not establish equivalence, and SFT did not improve
the query-transfer subset. It is a comparison of training packages, not equal-compute
proof that one objective is inherently better.

The released-model ID, reminder-order and running-tally comparisons are now fully
audited and linked above. Matching IDs help both released models; reminder order
and distance matter. The tally harmed final answers by making partial totals easy
to report too early. It revealed no gold labels and did not produce the final answer
automatically. That negative result motivates the accepted coverage-first test.

The [live queue](../../RESEARCH_QUEUE.md) records exact status and follow-on authority.
One A100 remains active, and new experiments are chosen from these results.

## How to read the rest

- [The most promising findings](PROMISING_RESULTS.md) explains the possible paper
  connecting the two leading results, and what is still missing.
- The [analysis index](../../README.md) separates completed reports, ongoing work and literature.
- The [cross-experiment overview](../../analyses/cross-experiment-synthesis-2026-09-09/OVERVIEW.md)
  reviews the earlier evidence through 01:35 UTC. Its uncertainty about root
  learning predates the new completed comparison above.
- The [findings](../../analyses/cross-experiment-synthesis-2026-09-09/FINDINGS.md) and
  [experiment catalog](../../analyses/cross-experiment-synthesis-2026-09-09/EXPERIMENTS.md)
  cover the wider history, including failures and changes in interpretation.
- The [limitations](../../analyses/cross-experiment-synthesis-2026-09-09/LIMITATIONS.md) and
  [research questions](../../analyses/cross-experiment-synthesis-2026-09-09/RESEARCH_QUESTIONS.md)
  explain what the earlier evidence can and cannot support.

Repeated seeds and question permutations are repeated measurements, not new
independent datasets. Optimization time is also not total experiment time:
generating training episodes, evaluating models, loading weights and coordinating
services take additional time. Reports keep these costs separate where measured.
