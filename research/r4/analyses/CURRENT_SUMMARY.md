# What we know so far

## Current update — September 12, 19:35 UTC

The latest overview is [NOW.md](NOW.md). A fixed32-update supervised controller
learned to retrieve the requested reply from a Python-accessible conversation.
On16separate conversations with two trials each, it returned17exact answers
versus2for the starting model (29baseoutcomes available;32trainedoutcomes).
Paired29 gives15corrections andno regressions. Correcttextwas printed30/32times.

Eight more generatedexactanswers were changed by runtime whitespace trimming;
the originalscore is unchanged. We are testing a narrow separate-process fix
before using those outcomes for further exact-reward RL. CurrentcontrollerRL
has onlyone exactgaininitsfirstseedblock, afterawholeconversationdump; thesecond
blockretainsallfixedmodels. Focusedhelperrequestsanswered1/12MuSiQuequestions,
the same as broadrequestsandstopping;fullsourceanswered3/12. No learnedrecursion
benefit is established. Frozennewlongerconversationsare readiedfortransfer.

The new source-repository plain-language report is
`docs/research-checkpoints/2026-09-12-procedure-transfer-and-exact-rewards.md`.
Older entries are history, not the current interpretation or active queue.

## Current update — September 12, 12:24 UTC

Giving the numerical task a longer Python response let six of ten trials reach
an answer, versus two when the same token allowance was divided into shorter
attempts. But all of those Python answers scored zero, and neither condition
met the planned minimum for a quality comparison. We are inspecting the actual
calculations before spending more GPU time on this direction.

The GPU is now learning from a new set of news examples, after completing its
separate starting-model evaluation. All 128 sampled training responses were
saved; the optimizer and heldout result are still pending. A larger, disjoint
training inventory and a fresh 512-item test set are ready if the initial run
supports a more substantial dose of learning.

Two other accepted jobs will test explicit helper instructions and whether an
untrained controller can search an external conversation to recover a requested
answer. The latter uses one underlying conversation, not eight independent
ones, and will not yet train weights. This separates the ability to obtain
useful training feedback from a later claim that the model learned to decompose.
Source/report checkpoints are pushed as RLM `604ac4e` and notebook `0e400f3`.

## Current update — September 12, 12:09 UTC

The single-item comparison is complete: the supervised helper scored 120/128
question categories and 109/128 news, while the four-update RL helper scored
120 and 108. All 512 calls produced available predictions. There was one
regression and no improvement. The starting helper reproduced all 256 earlier
singleton completions exactly. This does not support serving input-size mismatch
as the reason RL added little. See
`helper-hf-singleton-policy-comparison-2026-09-12/REPORT.json`.

Together with the paired reward-baseline null, this makes broader training data,
a meaningful fixed training dose, and root-procedure learning higher priorities.
The GPU is running the numerical inspection-budget comparison; new AG training
and root-interface checks remain queued. The latest plain-language RLM report
is pushed in commit604ac4e. Full external runs and weights are not Git backups.

## Current update — September 12, 12:02 UTC

Changing the RL reward baseline did not improve evaluated answers. Two models
trained on exactly the same128 attempts made identical predictions on all256
evaluation records, even though the alternative provided nonzero signal for
32training questions instead of5. Their parameter updates really differed.
This narrows our next moves toward broader training material and root procedures,
not more small reward tweaks on the same familiar questions. The full result
and corrected shared-sample costs are in
`paired-feedback-recovery-2026-09-12/REPORT.md`.

The GPU is now evaluating the trained model on single-item requests. Its fresh
starting-model control already completed256 requests. Numerical-budget, new
AGtraining/readout and explicit-root-interface experiments remain accepted
successors under the shared lock. MRCR root calibration is CPU preparation;
it uses one underlying long context and is not a generalization test.

## Current update — September 12, 11:44 UTC

The delegation experiment mostly exposed an interface problem. The model kept
trying to import a helper that was already available, or repeating invalid
Python, until some conversations exceeded the context limit. The same root
model behaved much better under its earlier, explicit interface instructions.
Only half the planned comparison ran; the raw first48 episodes are auditable,
but they do not provide a clean estimate of whether delegation helps. A small
shared-instruction check is being prepared before any larger followup.

The GPU is still working on the comparison of two ways to calculate RL feedback
from identical sampled answers. One branch is finished and the second is
replaying its training samples. Automatic successors will evaluate both, test
whether single-item versus four-item inputs hide an improvement, and revisit
the numerical Python task with usable inspection budgets. The next proposed
training step changes the training material to new news examples, with a
separate heldout panel. No meaningful new RL gain is claimed from a checkpoint
alone. See `../RESEARCH_QUEUE.md` and
`root-recursion-headroom-partial-2026-09-12/PARTIAL.md`.

## Current update — September 12, 11:24 UTC

The fast48 update is now independently qualified, not merely a checkpoint file:
all48 differentiable likelihood checks passed exactly, only helper tokens were
trained, and Adam advanced once. Its256 evaluation labels exactly match the
reference four-update model. This is a useful faster collection/training route
to investigate, not an additional quality gain; total acquisition, qualification,
and evaluation time must be counted separately from36.309s optimizer work.
See `fresh48-fast-one-update-2026-09-12/REPORT.md`.

The GPU is collecting the actual optional-helper/no-helper comparison. A six-stage
successor chain is accepted and waiting, covering reward-baseline recovery and
readouts, singleton inference-shape controls, and numerical inspection-budget
allocation. CPU analysis will use each outcome to select the next comparison.
No additional temperature-only or larger-step repeat is planned.

## Current update — September 12, 11:13 UTC

The matched three-update comparison is available: reference120/128 question
categories and112/128 news, versus larger-learning-rate117/128 and111/128.
All256answers were available in both. Larger updates did not help this model
and small familiar training set. The larger arm stopped before update4 because
the whole batch had zero relative-reward contrast; no fourth checkpoint exists.
The retained fast48 update path is next on the GPU, and the independent
optional-helper experiment has an accepted import-isolated recovery owner.

The numerical pilot reached no Python final answers: eight code truncations and
two timeouts. A followup will first make the inspection budget functional, not
train on an apparent zero-score architectural result. The fresh classification
checking result also needs its cheapest comparator: selective checking tied
the original total across datasets at2.66times the observed token cost, despite
passing its narrower comparison against three-answer voting.

## Current update — September 12, 11:08 UTC

On 128 fresh examples, selective checking was cheaper than voting over three
answers and at least as accurate on both datasets. However, the original single
pass was much cheaper still. Selective checking lost one correct question-category
answer (61 versus 62 of 64) and gained one news-category answer (56 versus 55).
This is a useful cost/quality observation, not a demonstrated general advantage
over the simplest RLM helper policy. All 152 raw responses were decoded by an
independent analyzer; all policies had complete output and the service released.
See `helper-adaptive-fresh-independent-2026-09-12/REPORT.md`.

The larger-learning-rate model has three saved updates and awaits its matched
three-update evaluation. Its fourth batch had no reward contrast, despite some
different wrong answers: answer diversity and useful reward diversity are not
the same thing. The paired reward-baseline experiment collected 128 answers but
failed on an RNG-restoration import before updating either branch; that is a
software failure, not a negative RL result. A repair will reuse authenticated
answers when exact-policy replay permits it. The optional-delegation experiment
also failed during dependency loading before making model calls.

The GPU is currently running the new numerical-data/Python pilot. Four accepted
readout/update jobs are waiting under the same lock (PTY 75691), while CPU work
repairs the observed seams and evaluates the next research decisions. Exact
receipts and limitations are in `../RESEARCH_QUEUE.md`. No meaningful new RL
improvement is claimed yet.

## Current update — 2026-09-12 10:54:58 UTC

The larger-learning-rate run applied three updates, then stopped because its
fourth batch had no reward contrast. Thirty questions received four correct
answers each; two received four wrong answers each. That gives 120/128 correct
training answers but zero relative-reward advantage for every sample. There is
no fourth checkpoint and no evaluated quality claim yet. A separate, explicitly
adaptive readout of checkpoint 3 is prepared, with a matching reference step-3
control being added. Do not treat the rejected step-4 evaluation as poor accuracy.

The independent training audit also confirms that both earlier T1 and T2 updates
changed training likelihoods. Their identical evaluation outputs do not mean the
optimizer did nothing. T2 exposed more right/wrong contrasts without improving
the fixed evaluation labels. This narrows the next tests to useful reward signal,
update scale, training coverage, and which part of the RLM should learn.

The GPU is now running the shared-action comparison of two reward baselines.
A faster 48-action path failed before loading the model because its NumPy seed
was out of range; a minimal additive repair is ready for review. That setup error
produced no optimizer update and is not a negative scientific result.
Fresh-input selective checking, optional-delegation headroom, and a 20-episode
numerical-data/Python pilot remain accepted successors. The numerical pilot is
neither RL nor recursive-depth learning; it deliberately changes information access.

Public checkpoints: RLM `54372e5` and research notebook `fb690be`. The latter
archives selected scripts and findings, not weights or raw external traces.
Main-account quota was 90% remaining at 10:50 UTC. See `../RESEARCH_QUEUE.md`
for exact owners, caps and the independent CPU analysis waiters.

Sources: `helper-hf-fourstep-signal-audit-2026-09-12/REPORT.md` and the immutable
LR arm `RESULT.json`, three checkpoint commits, and update-4 collection/replay
records under `../sidecars/helper-hf-onpolicy-fourstep-temperature-lr-v1/`.

## Current update — September 12, 10:08 UTC

The complete yes/no comparison is also negative. Full-category outputs produced
31/48 exact counts versus 20/48 from targeted yes/no, with total absolute count
error 18 versus 182. All 56 calls were valid. MAIN independently decoded every
raw response and reproduced the counts and the 3 wins / 14 losses. Retain the
full-category contract for c32; further simple binary rewrites are low priority.
Source: `helper-trec-yesno-local-review-2026-09-12/REPORT.json` (09144b71...).

Combined plain-language report is in the RLM repository at
`docs/research-checkpoints/2026-09-12-exploration-and-helper-contracts.md`.
It was pushed in commit `54372e5`. The current GPU is training the LR 10x arm;
fast48, paired reward baselines and fresh adaptive input sizing remain accepted
successors. New decomposition and broader-data jobs are CPU preparation, not
completed experiments. The supported main-account quota was 93% remaining at
10:09:24 UTC, following the observed reset.

## Current update — September 12, 09:57 UTC

Higher exploration increased the number of mixed right/wrong training groups
from 16 to 40 across four updates, but did not change any of the 256 final
evaluation predictions compared with the reference run. Both scored 120/128
question categories and 112/128 news categories. T2 training took 51.05 minutes
versus 42.04 minutes for the reference. This weakens the explanation that more
answer variety alone will fix the weak RL result under this learning rate and
small, repeatedly used training set. It does not show that the policy distribution
was unchanged or that exploration cannot help at another dose or on other tasks.

MAIN independently recomputed all 256 prediction comparisons and the four
collection totals. Analysis:
`helper-hf-fixed256-perturbations-2026-09-12/arms/t2_lr1e5_4step.json`, SHA256
`54d66b8e6df95eccc09c24d03a76f243a466df09979e5be22ea5f2478b3162f9`.

The GPU is running the fresh yes/no output experiment. Higher learning rate,
qualified fast-sample training, and the paired reward-baseline experiment are
accepted successors. CPU preparation is moving beyond the current batch:
fresh-data adaptive request sizing, a genuine recurse/no-recurse comparison,
and a broader training-data proposal. The user's latest instruction explicitly
authorizes continuing beyond the queue, adapting to results, and preserving a
plain-language handoff before allocation or account-budget exhaustion.

## Current update — September 12, 09:15 UTC

The fixed-size grouping control is complete and independently audited. Original,
reversed, neighbor-A and neighbor-B groups of sixteen scored117/118/118/113 on128
TREC records and115/111/113/109 on128news records. Across the four arrangements,
22TREC and29news records changed predicted label. All64calls/1024relatedslots
were valid. Neighboring-record changes preserve numberedslot, not absolute
tokenoffset. This strengthens presentation-sensitivity evidence, not a claim that
regrouping improves performance or identifies an attention mechanism. Audit:
`helper-companion-position-local-review-2026-09-12/REPORT.json` (9bc764d7...).

Fresh48 batch-invariant native samples passed the original HF probability gates:
ESS45.44856/48, maxnormalizedweight0.0278127, rawratios0.190389..1.301337.
The recovered scoring stage used the exact saved samples and precomputed masks,
took22.67seconds and madezerooptimizerupdates. Its independent audit4b8e6f19...
is adopted. An actual one-step importance-weighted update is now approved for
CPUimplementation, separately from the32-question onpolicyHFexperiment.

T2 fourstep training is active and checkpoint1 is saved. Its first collection had
11mixedgroups, versus4in the T1 reference; lower collectionreward109/128versus114
is not an evaluation result. Four bounded successors are accepted in an automatic
chain: T2evaluation, yes/no56, LR10xtraining, LR10xevaluation. A paired other31
reward-baseline single-step comparison is CPUimplementation, not GPUlaunched.

The partial target/other experiment was adverse: completedTRECblocks full27/42
exactcounts versus20/42targeted, totalabsoluteerror16versus152. Entity-target
prompts markedall112recordspositive(21true). No negative-tail rerun is planned;
the fresh yes/no treatment checks whether outputwording changes this behavior.
See `helper-targeted-counts-local-review-2026-09-12/INTERPRETATION.md`.

## Current update — September 12, 08:33 UTC

The new request-size experiment reverses the simple “smaller is better” story.
At16/4/1 records per call, fixedc32 scored117/119/120 of128TREC and115/112/109
of128AGNews, all valid. Individual calls used7.09times the combined tokens of
16-record calls. This motivates task-sensitive grouping and a test of neighboring
record effects, not promotion of a universal splitting rule. See independently
verified `helper-unseen-size-transfer-2026-09-12/REPORT.json`.

Four exact-HF RL updates completed in42.04minutes with all checkpoints saved.
Final evaluation120/128TREC and112/128AGNews exactly matches the earlier
one-update pilot's256predictions. The four-step run starts anew fromc32 with
freshseeds, so this is not a seed-controlled dose experiment. Only4/5/4/3 of32
groups gave mixed rewards across its collections; a consistently wrong training
question supplied zero relative-reward contrast. More informative training
samples are more promising than simply more of the same small-dose run.

Task-targeted helper output is now running:96calls test full labels versus
target-category/other on80predeclared count tasks, with reuse-aware costs.
The independent faster-RL qualification failed on a native-response parsing bug,
not a statistical gate. An additive fix is being prepared while the GPU evaluates.
Live queue contains ownership/caps; mainaccount reset is now observed100%remaining.

## Current update — September 12, 08:00 UTC

Three real HF helper RL updates are saved and update4 is collecting. Each uses
128 fresh actions; the first three collections had4,5,4 mixed-reward groups out
of32. Final-checkpoint accuracy is still pending. The A100 is occupied by the
training owner; three independent bounded successors are already waiting under
the shared lock: final-checkpoint evaluation, a live16/4/1 request-size comparison
on the new256panel, and fresh fast-collection probability qualification. See the
live queue for exact PTYs, hashes and caps. No successor optimizer is authorized.

The serving-probability audit is adopted and pushed in RLMmain`f31e4b0`:
batch-invariant mode eliminated the observed variation at one inspected prefix
position across24helper calls. This enables a fresh test, not validation of old
data or a blanket determinism guarantee. The strongest completed quality lead
remains supervised same-task transfer92to119/128TREC, with no news-task improvement.

Two concrete harness questions now complement the training effort: when is a
smaller helper request worth its extra cost, and can a helper answer only the
category distinction required by the final task? A96-call target-versus-full-map
design is approved for CPU implementation, not yet GPU launch. Another queued
idea asks whether public error signals can guide recursive stopping; ADaPT's
self-assessment failure discussion supplies relevant prior art. Keep genuinely
learned decomposition separate from these preliminary fixed-policy comparisons.

## Current update — September 12, 07:25 UTC

The unadapted4B control clarifies prior supervised training's transfer: newTREC
92to119correct/128 (28wins1loss), but AGNews113to112/128 (3wins4loss).
Original/SFT/oneRL scores are92/119/120 onTREC and113/112/112 onnews. Allquestions
are disjoint fromverifiedhelperoptimizerinputs/new32, not necessarilybasepretraining.
MAIN rebuilt bothpairedanalyses. Read publicRLMcheckpoint
`docs/research-checkpoints/2026-09-12-helper-rl-first-readout.md`, pushedb3812cb.
Differentbase/adaptedservingpaths preclude a weights-onlytimecomparison.

Four-updateHFhelperRL isrunning underPTY83114, fixedstep4primary andfreshsamples
everyupdate, checkpointedthroughout. No newaccuracyresultyet. The prospective
batchinvariant32callprobecompleted; targetprobabilitywasidenticalinall24matched
helperprefixes andmatchedchosen-tokenprobabilitydifferenceswere0. Independent
auditpending. Thisdoesnotvalidatethehistoricalimportanceweightedcollection.

## Current update — September 12, 07:08 UTC

A real helper RL update now exists. The repaired same-HF run replayed all32groups
with zero selected-token/sequence probability error and made one finite AdamW
step. It reused128authenticated pre-update samples from the memory-failed first
attempt. Only4groups offered a correct-versus-wrong learning contrast. The saved
checkpoint/optimizer audit independently reconstructs its weight change.

The first native readouts are essentially unchanged: new TREC119to120correct/128,
new AGNews112to112/128, familiar material245to244/256answers (128questions twice).
All requests returned valid answers. Do not promote a training-mechanics success
to an accuracy claim. Independent paired audit is underway. A four-update pilot
with fresh actions at every step is being prepared; no evaluation data enters it.

The stronger harness lead connects actual helper replies to final answers:
size16/4/1 yielded12/18/17correct of24 on two prior-trained contexts. The seven
4vs16wins follow the changed helper-map formulas; the two losses are consistent
with later root aggregation mistakes despite better maps. All nine discordances
had identical initial root responses, but later sampling remains uncontrolled.
Read `qs6-batchsize-downstream-mechanism-2026-09-12/REPORT_V2.md` for two concrete
examples. No generated trace code was executed by the analysis.

The base4B new-panel comparison failed before inference because a stale driver
library path masked the actual driver; a bounded repair is being prepared.
GPU is currently released; see the live queue for launch ownership and idle cost.
The second batch-invariance startup failure was a false-negative environment
check after setproctitle: actual engine activation succeeded, but zero scientific
calls ran. It does not establish whether invariance resolves probability drift.

## Current update — September 12, 06:36 UTC

The fresh same-HF helper pilot saved128answers (116correct,4/32mixed groups) but
ran out of40GB memory on the first gradient-bearing replay group. Zero optimizer
steps; this is an execution failure, not a failed answer-quality comparison.
An additive memory repair is in preparation. The batch-invariance probe sent no
requests because its flag was stripped by the child-launch environment; that
startup integration is being repaired separately. The independent72episode
observed-helper-map downstream test is running now. Read the livequeue forowners.

An actually c32-SFT-disjoint panel is frozen before scoring:128TRECtest questions
and128AGNewstest examples. Its source-ID and normalized-text checks use the
actual5065question optimizer inputs andnew32RLprompts. No base-pretraining-unseen
or pristine-research-holdout claim is made. A base-versus-c32 comparison is being
prepared before qualifying any newly trained helper. The completed helper-size
and exact training-exposure report was pushed as RLMmain894c9f6.

## Current update — September 12, 06:27 UTC

The strongest lead remains the helper's information: original/replayed/correct
local labels gave26/27/44 correct final answers of48 on two training contexts.
This is a diagnostic intervention, not a learned improvement. Self-SFT's repeat
gave57correct versus55unchanged, with4observed wins/3losses and two unavailable
answers each. Its earlier apparent cost saving reversed. No stable efficiency
or broad learning claim is justified.

New fixed-weight helper-size comparisons completed:16/4/1records percall gave
54/61/58correct of64 on32questions repeatedtwice, then239/243/245 of256 on128
questions repeatedtwice. Gains are modest and heterogeneous; four/one-record
requests used2.58x/8.89x total tokens on the broader panel. MAIN checked raw
counts; independent reports pin every source call and changed label. See
`c32-helper-batchsize-2026-09-12/REPORT.md` and
`c32-helper-batchsize-protected-2026-09-12/REPORT.md`.

IMPORTANT EXPOSURE CORRECTION: all160questions were consumed in two priorc32
SFT epochs. The actual checkpoint's per-step group-ID history exactly matches
the preparedTRAIN batches. They are not unseen by that helper, even though the
128are disjoint from the32newRL inputs. Evidence:
`../sidecars/helper-hf-onpolicy-v1/PRIOR_SFT_EXPOSURE.json`.
These are familiar-material behavior comparisons; genuinely new inputs are next.

Fresh same-HF on-policy helper RL is running, not yet an improvement result.
Older importance-weighted helperRL stays on hold. Completed prospective probes
show substantially different logged category probabilities for identical token
prefixes; rawtop20probabilities normalize, so the mechanism is unresolved.
Batch-invariant serving and downstream real-map root comparisons are prepared.
See live queue for exact ownership; older active-status paragraphs are historical.

## Current update — September 12, 05:47 UTC

The strongest new lead is local helper quality. On 48 diagnostic attempts from two
training contexts, the original helper replies yielded 26 correct final answers;
replaying those same replies yielded 27; supplying correct local categories yielded
44. The last condition is an evaluator intervention, not a learned improvement or
a deployable method. Compared with replay, it won 18 attempts and lost one.
It does not eliminate root-side counting, weighting, or Python-repair errors.
See the authenticated three-arm result in
`qs6-real-oracle-replay-endpoints-2026-09-12/OUTPUT_V1.json`.

The first matched root-weight comparison was unchanged 53, one-update RL 52, and
self-SFT 57 correct out of 72. SFT's four additional correct answers comprise two
observed wrong-to-correct changes and two recovered unavailable answers. The gain
was concentrated in two of eight contexts. A fresh-seed repeat is active: the new
unchanged baseline finished with 55 correct, 15 wrong and two unavailable; its
paired SFT arm is still running. Do not compare its result against the old 53.

Helper RL has not yet updated any weights. Its first qualification stopped at an
effective sample size of 36.6/48, below the planned 38.4 minimum. A proposed relaxed
continuation is paused because identical historical helper prompts and outputs
have materially different logged token probabilities. The raw chosen-token values
agree across transport/export, but their probability meaning remains unvalidated.
A short serial/concurrent/mixed-model serving probe is being prepared next.

The corrected baseline-72 confidence analysis uses **71 physical helper maps**,
not the 69 maps retained in exported role graphs. Two valid helper replies belonged
to root attempts with unavailable final answers. MAIN reproduced V3 exactly:
1,136 labels, 72 errors; 44 errors have the descriptive logged-score proxy at least
0.95. A low-score rule flags 28 errors and 73 correct labels. This is neither a
calibrated probability of correctness nor a validated stopping policy. Use
`qs6-helper-confidence-baseline72-2026-09-12/REPORT_V3.md`; earlier inventories are
preserved but superseded. A smaller-helper-request experiment is in CPU preparation.

The delivered September 11 slides retain their historical cutoff. New source
reports are pushed through RLM main `b8642bd`. The external run/model store is not
backed up by Git. Latest supported quota receipt: 05:41 UTC, 14% remaining; the
user's explicit reserve override applies, and a special reset is not yet verified.
Read the live queue for actual ownership before starting another GPU process.

## Current update — September 12, 05:08 UTC

The matched one-update comparison is complete: unchanged53correct/17wrong/2unavailable,
root-RL52/19/1, self-SFT57/15/0. No integrity failures. Self-SFT has two observed
baseline-to-correct flips, no observed losses, and two availability recoveries;
all four additions occur in two of eight context clusters. One long baseline
retry chain accounts for88.7% of the apparent18.4% prompt-token reduction.
Do not call it a general efficiency gain or a72-independent-document result.

[Full paired result](../../../ARTIFACTS.md) and
[context/program/cost audit](../../../ARTIFACTS.md).
MAIN reproduced the full three-arm analysis and SFT audit from saved physical
evidence. Perfect-helper48 is running; byte-identical original-helper replay48
follows automatically. The helper-only grammar-conditioned RL update is CPU-ready
but requires a GPU likelihood gate before any optimizer step. A new-seed
baseline/self-SFT evaluation is CPU preparation, not independent new training.
Read the queue for live owners. Earlier snapshots below are historical.

## Current update — September 12, 04:30 UTC

The post-meeting research now compares root-only RL with learning from the model's
own correct-answer attempts. A new 48-attempt diagnostic completed with 26 correct
and 22 wrong answers and no unavailable results or integrity failures. Five of the
twelve training tasks produced both successes and failures among four samples.
This establishes usable contrast for the current group-relative objective, not
an improvement in answer quality or independent-source generalization.

Both one-update training copies are saved. RL used 20 attempts and 9,495 root
action tokens; self-SFT used 26 attempts and 7,134 tokens. Loading, updating and
saving took 109.632 and 55.031 seconds respectively. The unchanged model's matched
72-question evaluation is active, followed automatically by both trained copies
and a 48-attempt perfect-helper diagnostic. The evaluation panel is already
research-exposed. No updated-model answer-quality result is complete at this cutoff.

Read the [training-stage report](../../../ARTIFACTS.md)
and [living question](../questions/rl-effective-feedback.md). The source/document
checkpoint is pushed as `44b5dba` in the RLM repository; external weights and
experiment scripts are not backed up by that push. See the live queue for current
owners and later results. The historical statuses below are preserved, not current.

## Current update — September11, approximately13:40UTC

The meeting deck is now eight main slides plus six optional backups, published
with pushed Git milestone`a343e1a` in the RLM repository and final source commit
pending. Its main numerical cutoff is12:55; later compact/pilot evidence is supporting material.
The historical snapshots below are preserved; their active/queued labels and
slide numbers are not current operations. Consult the live RESEARCH_QUEUE.md.

The strongest near-term direction remains reliable helper handoffs, but **cost
measurements changed the proposed experiment**. All four E1 policies processed
the same768records. Large unnamed / large named /16-record unnamed /singleton
accuracy was49/85/81/87%, in19/91/19/31seconds. More calls were not automatically
slower. Singletons repeated more input text; named calls generated more output.
The next whole-task test must include smaller calls as a serious baseline.
[Full cost evidence](../../../ARTIFACTS.md).

Matching also helped Mistral on the same growing-batch panel (64-record accuracy
35→52%, versus Qwen44→83%). Qwen output-order tests retained83/82/81% under
original/reverse/interleaved orders. These are component effects with exposed
contexts, not whole-RLM gains or formal equivalence. A compact-output Qwen test
preserved85% accuracy while cutting output tokens23% and local block time24%
relative to a freshly paired verbose control. Mistral replication also reduced
output work and local time, but its accuracy increase mostly reflects fewer invalid
replies (12→14/16 valid), not demonstrated semantic-reading improvement.

Training produced another useful result: on explicitly described new combinations,
faithful-and-correct answers rose2/72→29/72 (missing bounds2–13→29–30). This is
execution transfer, not independent discovery of a plan. The longer reward pair
did not improve final-answer counts:57before,55–57answerreward,54extracheck.
Those are secondary counts, and the full faithful-calculation review is unfinished.

[Current resource-aware handoff question](../../../ARTIFACTS.md)
connects these findings to the next decision. Its first attempt authenticated all
32 helper calls but failed at the helper-to-root software transition before any
root call. The first root-only recovery also produced no root model call: all32
episodes failed during task setup, and a secondary scorer error masked that first
failure. A second recovery using the same maps/plans/seeds started13:29:01UTC; it
makes zero new helper calls. It ended at its fixed deadline after393.61seconds and
released the GPU. Independent native audit, reproduced byte-identically by MAIN,
finds four admitted failures and28NULLs (20unstarted, eight attempted missing final).
Named48 has1/16 observed and unnamed16 has3/16; none is correct or faithful.
All four available paths were manually reviewed: repeated synchronous-map API
misuse and failed reductions dominate. Paired missing-data accuracy bounds are
−81.25 to+93.75pp, so no whole-task gain is established. See the
[terminal pilot audit](../../../ARTIFACTS.md).
No GPU job remains owned. All inference and training claims remain
exploratory; no broad recursive-planning or publication-ready result is asserted.

## Historical04:03 update

Updated on September 11, 2026, at 04:03 UTC. These are exploratory results, not a
claim that we have solved general problem decomposition. This page includes newer
evidence than the fixed-cutoff cross-experiment review.

## Newly adopted findings — 03:45 UTC

- On 72 tasks from eight newly selected root source groups, faithful-and-correct execution was
  12/72 for fixed24 (seven NULLs; bounds12–19),55/72 for original-corpus SFT6, and53/72 for
  new-corpus SFT6 (two NULLs; bounds53–55). Both trained policies exceeded fixed24 in all eight
  context clusters; composed successes were0/48,35/48, and34/48. This supports bounded transfer
  beyond the earlier source groups and across two training corpora. The task families, child, and
  metadata transform remain research-exposed, and “new” means absent from named root inventories,
  not unseen in pretraining. [Independent audit](../../../ARTIFACTS.md)
  and [MAIN adoption scope](../../../ARTIFACTS.md).
- On16 newly selected MultiNLI context clusters, labels-only accuracy declined as nested batches
  grew:82.8% at8 records,82.0% at16,56.4% at32,49.2% at48, and43.8% at64. Matching sequential
  and opaque keys remained83–87% throughout. The frozen onset was32; at32/48/64 both keyed formats
  improved all16 contexts. This is an encoding-package result with16 clustered units, not a
  universal32-record limit or an internal-mechanism claim. [Independent audit](../../../ARTIFACTS.md)
  and [MAIN adoption scope](../../../ARTIFACTS.md).
- The authenticated-map reward V1 and V2 attempts are retained zero-update integration failures.
  V1 omitted a required serving-model manifest binding; V2's24 first-window task identities failed
  before transport, so both made zero provider calls and the bonus arm never launched. Additive V3
  is now making real control-arm rollout requests under the same scientific design, but no optimizer
  update or reward outcome exists at this cutoff. [Living question and operation pointer](../../../ARTIFACTS.md).

The advisor package is now a reviewable14-slide PDF and matching teaching guide
in `/project/alex_phd/repos/rlm/slides/2026-09-11-advisor-meeting/`, with fixed
numerical cutoff02:15UTC. H6 has a concrete tag example and two-bar comparison;
the SFT slide states its reused-input limitation prominently. It compiled without
warnings and passed visual/independent clarity checks. Later live results below
are not silently included in that deck. No MAINpush has been performed.

Current research operations: the fresh-input three-policy216 and nested batch-size studies are
complete and adopted. The repaired V3 paired reward study has entered native control-arm rollout;
it has not yet produced a training or comparison result. See
RESEARCH_QUEUE.md for exact ownership and caps.

## Two later checks — 03:06 UTC

- Enforcing the output format made all48 outputs usable, versus37/48 without
  enforcement. Strict late-label scores were1305/1536 versus1002/1536. Among37
  pairs valid in both conditions, the net difference was only one correct label.
  This supports format reliability, not improved internal reasoning. The selected
  both-valid comparison is descriptive. It does not explain away H6's matching
  effect, where all192 outputs were valid. [Audited control](../../../ARTIFACTS.md).
- Saved helper labels gave a small encouraging fixed-calculation result: exact
  answers2/16 without tags,4/16 with row numbers,5/16 with arbitrary matching
  tags. This is a posthoc Python diagnostic over8shared inputs, NOT the main
  model's observed performance. The full-RLM test remains inconclusive:8finals
  observed and88NULL, with repeated new-helper API misuse and context overflow.
  [Partial audit and scope](../../../ARTIFACTS.md).

Both appear only in the meeting's later-findings.md supporting notes. The
14-slide deck retains its02:15cutoff. No new main-slide result is silently added.

## Current conclusions — September 11, 02:18 UTC

Three newly sealed comparisons sharpen the interface and reward-training conclusions.

- A balanced control now shows that literal tag reuse matters in the tested interface. With
  arbitrary tags on both input and output sides, Qwen3-4B late-label accuracy was 78.8% when the
  tag dictionaries matched and 32.6% when they were disjoint, a paired +46.2-point effect positive
  in all 16 exposed context clusters. All 192 calls were native-valid. This isolates a behavioral
  effect of literal reuse within the complete interface package; it does not establish copying,
  attention, an internal binding mechanism, or whole-task benefit. A 96-call grammar-on/off control
  is queued. [Independent audit](../../../ARTIFACTS.md).
- The stable-identifier behavioral effect transferred to a different model family. On the same
  exposed 16-input panel, Mistral-7B late-label accuracy was 31.9% with labels only, 55.8% with
  sequential identifiers, and 52.5% with opaque identifiers. Sequential and opaque identifiers
  improved 15/16 and 16/16 context clusters, respectively, with all 144 calls native-valid. This
  is a bundled interface/grammar comparison, not evidence for semantic-name, literal-matching,
  position-binding, or internal mechanisms. Absolute keyed performance remained much lower than
  the Qwen models. [Report](../../../ARTIFACTS.md) and
  [interpretation qualification](../../../ARTIFACTS.md).
- Lowering the composed terminal-RL learning rate to 1e-5 did not recover a gain at this small
  dose. Six genuine updates left the 48 composed protected questions tied at 36 correct in both
  arms (46 known pairs; planned missing-outcome effect range -4.17 to +4.17 points). The exhaustive
  agent-authored path review also tied at 33 grounded-faithful-and-strict results per arm. Across
  all 72 questions the last checkpoint scored 52 versus 55 at the start, but missing outcomes
  permit 52–56, so this does not establish a decline. It is a bounded recipe result, not a general
  failure of reward learning. [Independent audit](../../../ARTIFACTS.md).

Fresh-input replication, the grammar control, and a successful whole-task bridge remain decisive.
Historical live-job wording below is archival; use RESEARCH_QUEUE.md for current ownership.

## Previous conclusions — September 11, 00:18 UTC

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
[Mixed-training report and MAIN review](../../../ARTIFACTS.md).

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

[Complete prior status history](../operations/2026-09-10-status-history-at-1917/CURRENT_SUMMARY.md) is preserved byte-for-byte, including failed experiments, earlier RL/SFT results, and subsequent corrections. The historical active-job labels are not current. [Migration receipt](../../../ARTIFACTS.md).
