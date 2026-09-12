---
schema_version: "rlm-question-card-v1"
id: "rq:rl-effective-feedback"
title: "Can an RLM learn from its own attempts, and which errors obscure that signal?"
status: "fixed_baseline_gain_did_not_replicate_fresh_contrast_readout_pending"
updated_utc: "2026-09-12T22:16:00Z"
evidence_cutoff: "2026-09-12T22:16:00Z"
source_catalog:
  path: "/project/alex_phd/runs/rlm-research-r4/analyses/research-factory-2026-09-09/CATALOG.json"
  sha256: "e0fa23412505eee178d27041816e84f7931d6da01b02e13f664393a6586ff39c"
catalog_boundary: "New post-meeting question; the old catalog does not contain the new experiments."
related_questions: ["rq:controller", "rq:authenticated-calculation-reward", "rq:counterfactual-credit", "rq:adaptive-decomposition"]
claim_ids: []
reports:
  - "../analyses/openai-mrcr-fixed-rl-decode-replica-2026-09-12/REPORT.md"
  - "../analyses/openai-mrcr-fixed-baseline-rl-paired-2026-09-12/readout-002.md"
  - "../analyses/openai-mrcr-cp32-fixed-baseline-rl-update-audit-2026-09-12/REPORT.md"
  - "../analyses/root-qs6-ag-live-helper-transfer-mechanism-2026-09-12/REPORT.md"
  - "../analyses/helper-agnews-official-test-transfer-findings-2026-09-12/FINDINGS.md"
  - "../analyses/openai-mrcr-short32-outcomes-2026-09-12/PROGRAM_VS_TERMINAL_ADDENDUM.md"
  - "../analyses/qs6-onebatch-learning-2026-09-12/REPORT.md"
  - "../analyses/qs6-onebatch-learning-2026-09-12/discordance-audit/SFT_REPORT.md"
  - "../analyses/qs6-onebatch-learning-2026-09-12/TRAINING_STAGE.md"
  - "../analyses/root-authenticated-map-reward-pair-live-2026-09-11/final-pair-2026-09-11T0840Z/REPORT.md"
publication_readiness: "not_publication_ready"
---

# Can we turn the model's own attempts into useful learning?

## Decision update — September 12, 22:16 UTC

The fixed-baseline gain did not replicate: the new paired decoding block
scored25/32 atcp32 and22/32 afterRL,0wins3losses,allavailable. Earlier23→25
remains a real but inconsistent result, not a checkpoint-selection opportunity.
All three new losses add finalLF after unchanged correct programs and stdout.
Five full token paths changed;27 were identical. Two affected context units
account for the three losses. No generalized RL success claim is justified.

The fresh8 screen yielded7/32 exact,24 clean retrievals,17 copying errors,
8 literal-selector failures and3 mixed groups. One final-only RLOO update
completed fromcp32, using12 nonzero finals and20 exactzero rows retained in
the32 denominator. The update took33.24s and deltaL2 .04046. Its preclip
gradient norm24.309 is not directly comparable to saved postclip gradients.
Short32/long16/fourneedle16 evaluation is fixed and accepted regardlessscore.
Both source batch and reward baseline differ from the previous recipe.

Prioritize informative, verifiable choices rather than merely increasing
update size. The all-zero email groups cannot teach literal selection through
group-relative terminal reward. A generic input-inspection instruction is
currently being tested; a separate compositional-task pilot is in CPU design.

## Decision update — September 12, 21:37 UTC

After procedural SFT, a fixed-baseline final-token reward update improved short
exact answers23→25/32 and left long answers10/16 unchanged, all48 available.
Two short wins occur on different contexts: one missing-space correction, one
substantial content correction. Parsed programs and observations are unchanged.
Only final tokens enter the loss, but shared weights can affect every stage.
This is a one-step exploratory result on exposed panels; all16 short contexts
will receive a paired two-new-seed replication with both checkpoints.

The familiar8-context group-relative batch had28/32 exact but zero mixed groups,
so every advantage was zero. Higher temperature produced27/32 and only one
mixed group, a procedural failure rather than clean final-answer alternatives.
The earlier SFT checkpoint restored variation at the cost of accuracy6/31,
with one unavailable attempt. A fresh8-context cp32 screen is now running.

The new RL objective uses fixed baseline.5,32 frozen final actions and one
LR1e-5 AdamW step. Its negative gradient is dominated by whitespace. Neither
raising a learning rate on zero advantages nor rewarding correct retrieval
guarantees better delivered answers. Next decisions use the fresh-context
contrast and paired rollout replication, not training likelihood alone.

## Decision update — September 12, 17:43 UTC

Eight updates alone do not explain the broader-data helper result. Repeating
the first 128 articles for all eight updates scored 417/512 on the shared exposed
panel, versus 422 for c32 and 437 for the broader eight-block RL checkpoint. The
repeat arm had 2 paired wins and 7 losses against c32, and 3 wins and 23 losses
against broader RL; all 512 answers were available. This supports a data-breadth
hypothesis, but one run and an already examined endpoint panel do not establish
it causally. A fixed checkpoint 8 readout on the already frozen official-test 512
panel is the next transfer check; it adds no checkpoint selection.

## Decision update — September 12, 17:35 UTC

The fixed RL8 helper's component signal did not survive its first fresh whole-RLM
screen. Deduplicated helper correctness improved103/128→108/128, but the same
QS6 root scored3/16 with both c32 and RL8 and all16 endpoint pairs tied. The one
new exact map aggregate was an error-cancellation case in which a correct c32
World label became an incorrect RL Sci/Tech label. This is a sharper example of
why a larger local reward signal is not automatically useful learning.

Trace evidence separates three failure sources. Helper errors keep most aggregates
wrong; generated reducers sometimes change scope; and four reducers silently
assign values so the next model turn receives no scalar. All20 recognized reducers
with visible scalar output were copied correctly into the endpoint, while all144
authored Python actions in the actual QS6 SFT corpus printed. A next root-learning
test should therefore use matched correctly scoped demonstrations and compare
print-then-final against the already-supported atomic `FINAL_TEXT` path on fresh
contexts. Repeating print targets alone would not isolate the demonstrated scope
failure. [Static audit](../analyses/root-qs6-ag-live-helper-transfer-mechanism-2026-09-12/REPORT.md).

Separately, the corrected syntax screen is retired: endpoint correctness fell
5/24→2/24, strict usable completions5/24→0/24, and strict correct usable
completions3/24→0/24. The original all-U export was an audit defect, not a model
result, but correcting it does not make the intervention promising.

## Decision update — September 12, 17:00 UTC

The frozen new-example readout is complete and materially weaker than the
research-exposed result. On official-test AG News examples, c32 / RL seed one /
SFT / RL seed two scored422/427/426/429 of512. Both RL seeds improve over c32 and
agree on508 labels, but exceed the supervised endpoint by only one and three
answers; both descriptive request-cluster intervals span zero. The earlier
422/437/427/436 panel remains separate and cannot be pooled with this one.

This supports a modest task-specific category-boundary adjustment, not a claim
that RL meaningfully beats SFT or improves general reasoning. RL gained mainly
on Sci/Tech and lost some World and Business answers; SFT changed only five
labels and gained four correct answers without a correct-to-wrong flip. A next
RL-versus-SFT claim needs a prospectively frozen matched replication and a
predeclared margin that does not hide compensating class losses. See the
[complete four-arm synthesis](../analyses/helper-agnews-official-test-transfer-findings-2026-09-12/FINDINGS.md)
(machine-readable SHA256 `391acb5fde4ab58b8157c55ba9792d60acf285066538152a6a604b2b6c452b02`).

The controller's partial MRCR reward also needs a stricter learning target. All
four outputs above0.90 similarity followed broad context dumps; their Python
selected the wrong item or failed, and the final model recovered by reading the
dump. Rewarding terminal overlap alone can therefore reinforce a shortcut rather
than programmatic retrieval. Preserve the frozen reward experiment, but audit
program selection and observation size before calling any gain learned
decomposition. [Program-versus-terminal audit](../analyses/openai-mrcr-short32-outcomes-2026-09-12/PROGRAM_VS_TERMINAL_ADDENDUM.md).

## Decision update — September 12, 15:10 UTC

The second eight-update RL run completed and scored 436/512, versus starting
422, first-seed RL 437 and supervised 427. It corrects 16 errors and introduces
the same two regressions as the first RL run; the two trained models agree on
511 labels. Every answer is available and all eight training/source/raw audits
pass. This establishes a repeated same-panel learning signal, not new-data
generalization. The [full readout](../analyses/helper-agnews-seed-replication-findings-2026-09-12/FINDINGS.md)
retains both seeds, per-class tradeoffs, request-cluster uncertainty and costs.

Proceed with the already admitted repeated-first128 training comparison. Test
all four fixed completed models on an independently frozen official-test panel;
selection preceded the second-seed score. The TREC comparison is retention,
not a wholly unseen dataset. Keep controller experiments separate: better helper
categories do not demonstrate a better decomposition policy or final answer.

## Decision update — September 12, 14:47 UTC

The exact training-seed repeat is active; five of eight updates have been saved
and independently checked. Its final evaluation has not run. The first run's
422-to-437 improvement remains a single-run result until that readout completes.

The next mechanism comparison is prepared and MAIN-admitted, but not yet launched:
repeat the first frozen 128-article block eight times versus the completed run's
eight distinct blocks. Keep eight updates and the original run's randomization
paired. There are only 128 unique articles in the repeated arm, despite 1,024
article memberships across update batches and 4,096 sampled label decisions.
If repetition stops early because all rewards agree, that is not a completed
eight-update comparison. See the [training-breadth question](../ideas/2026-09-12-training-breadth-versus-dose.md).

A review of all 21 changed predictions suggests improved agreement with news
category conventions, especially commercial technology stories. It does not
establish general reasoning or decomposition. Both corrections and new mistakes
are retained in the [qualitative interpretation](../analyses/helper-agnews-fresh512-interpretation-2026-09-12/QUALITATIVE_LIMITS.md).

The new TREC panel can check retention of earlier skills, not unseen transfer.
All available TREC source groups were previously used in local training or
evaluation. Older entries below that call TREC records "new" mean absent from
the particular verified fine-tuning inputs or current comparison, not absent
from every historical local evaluation. This distinction must accompany future
reports. A genuinely different source partition remains a separate next test.

The controller repairs are accepted and queued independently. They investigate
the component that chooses evidence and uses Python; they cannot be inferred
from improvements to the helper's category answers.

## Decision update — September 12, 14:05 UTC

The fixed broader comparison now shows 422/512 correct for the starting
model, 437/512 for eight RL updates, and 427/512 for eight supervised updates.
RL corrected 17 errors and introduced two; all endpoints have complete
answers. This is a promising single-run helper result on the same task,
not yet a replicated gain or evidence about learning controller decisions.

Next, repeat the fixed RL dose with fresh training/sampling seeds and no
intermediate evaluation. Keep the already examined 512-article panel explicit:
this replication tests randomness, not transfer. Do not yet attribute success
to more data alone, because data exposure and update dose changed together
relative to the earlier unsuccessful pilots. The supervised comparator has
matched articles and update opportunities, not matched compute or actions.
Root-procedure learning and the independent evidence-selection screen remain
parallel directions.

## Decision update — September 12, 12:02 UTC

The same-action paired reward comparison is complete. Other-question feedback
gave nonzero signal to32/32 question groups instead of5/32, but the two updated
models made exactly the same256 evaluated predictions:120/128TREC,112/128AG.
All answers were available. Both checkpoints are genuinely different; their
parameter-update cosine is0.8389. This is not a no-op optimizer, but also not
evidence that their output distributions are identical.

Retire another identical reward-baseline repeat as a near-term priority. The
broader-data AG128 one-update package and paired fresh AG256 readout are now
accepted and queued. Its package changes data/domain, input shape and reward
granularity together; any signal requires replication and later separation of
causes. A root-only MRCR procedure calibration is being prepared because the
wrong trained component and task-verifier quality remain open explanations.
Its small data slice has one underlying context, so calibration is not transfer.

The singleton readout is active. The completed c32 control gives120/128TREC and
109/128AG, matching its prior singleton headline counts; trained-model result
is pending. It will test whether the four-item serving shape hid an RL gain.

See [paired result and corrected reuse costs](../analyses/paired-feedback-recovery-2026-09-12/REPORT.md).
The legacy analyzer's `fresh_actions` field means retained action rows here:
the repair sampled zero new actions, and both branches share the same128.

## Decision update — September 12, 11:19 UTC

The matched three-update readout is negative for larger steps: reference120/128
TREC and112/128AG, versus LR10x117/128 and111/128. All256 were available;
the larger arm had one win and five losses. This makes a simple learning-rate
increase low priority. Combined with the T2 result, neither more varied answers
nor larger parameter changes has yielded meaningful improvement on this small
repeated training set. Both models really changed; this is not a no-op optimizer.

The repaired fast48 method completed one importance-corrected update in36.309s
of recorded training time (43.101s wrapper), then scored120/128 and112/128.
The old128-action true-HF and fast48 full-map paths are different workloads;
do not turn the optimizer timing into an end-to-end or like-for-like speedup.
Prior collection/qualification cost remains attributable to the fast method.
Raw output equivalence and all gradient qualifications are being independently
audited. This is an enabling execution result, not a larger RL quality gain.

Next discriminate a previously untested mismatch: singleton training versus
four-record evaluation. Evaluate the trained reference and unchanged c32 on
the exact same singleton inputs; keep the already examined panel explicit.
The paired reward-baseline comparison is being recovered from its saved fresh
actions, with no resampling and no prior branch update. Broader AG News training
remains conditional after the mechanics readouts; a faster grouped-request
training package is also under CPU feasibility review, not yet admitted.

Independent matched-dose audit:
`../analyses/helper-hf-lr10x-stopped-vs-reference-step3-2026-09-12/REPORT.json`
(SHA256 b146bc729d8f01e353db907ae5d56fb666ba2795d71ae458cd85a666ef940e1e).

## Decision update — September 12, 10:50 UTC

The LR 10x arm stopped at three applied updates: its fourth 128-action batch
contained 30 all-correct and two all-wrong question groups, with no mixed rewards.
The weights had changed, but the within-question comparison supplied zero
advantage to every fourth-batch action. Different wrong answer strings can still
have the same zero reward; answer diversity and reward diversity are distinct.

Evaluate the actual stopped checkpoint and a matching reference checkpoint at
three updates. Keep the original four-step primary marked unavailable. The active
shared-action baseline experiment tests whether feedback from other questions
helps when a question's own attempts all receive the same reward. A potential
later recovery experiment could reuse the authenticated fourth-batch actions,
but would need to separate changed reward feedback from Adam momentum alone.
No recovery optimizer step is currently authorized or claimed.

If these mechanics comparisons remain weak, move to the frozen broader AG News
training split and the accepted harness decisions; do not indefinitely vary
temperature or repeat the same familiar 32 questions. The source paths and
corrected likelihood audit are recorded in `../analyses/CURRENT_SUMMARY.md`.

## Decision update — September 12, 09:57 UTC

The higher-temperature run is now evaluated. It created 40 mixed training groups
instead of 16, but its final predictions were identical to the reference on all
256 evaluation records. More varied answers alone did not help at this update
size and training scope. Keep the higher-learning-rate and reward-baseline
comparisons; prepare broader training material and root decision experiments
instead of adding more temperature-only runs. The fixed-panel T2 audit is linked
from `../analyses/CURRENT_SUMMARY.md`.

## Current interpretation — September 12, 09:53 UTC

Our reference helper RL run completed four updates but produced exactly the same
256 evaluation predictions as the earlier one-update pilot: 120/128 question
categories and 112/128 news categories. This is still only one additional correct
question over the supervised helper. We have working updates, but not a convincing
RL quality gain. Different seeds prevent treating this as an isolated dose comparison.

The current experiments separate three plausible problems rather than assuming
that more training will solve them:

- **Too little exploration:** higher sampling temperature produced more mixed
  right/wrong training groups. All four updates finished in 51.05 minutes; its
  fixed final checkpoint is now being evaluated. Training diversity is not test accuracy.
- **Too small an update:** a ten-times-higher learning rate is queued with the
  original temperature, common seed schedule, and fixed fourth-checkpoint evaluation.
- **Feedback is discarded:** the usual within-question comparison gives no signal
  when all four attempts are wrong. A queued paired trial compares that rule with
  an action-independent baseline from the other 31 questions. Both branches use
  identical starting weights and the same sampled answers. It supplies no teacher
  answer, and may increase gradient variance or cost; both outcomes are informative.

A separate faster collection path passed its original probability-weight checks
on 48 newly collected, never-updated actions: effective sample size 45.45/48 and
largest normalized weight 0.0278. This qualifies those samples, not policy identity
or model improvement. Its single update and evaluation are queued. The earlier
parsing/environment failures and older statistical HOLD remain preserved separately.

These are exploratory helper experiments, not evidence that the root has learned
to plan or recurse. Any useful helper gain must later survive whole-RLM evaluation,
new task families, fresh evaluation inputs, and compute-matched baselines. The old
256-record evaluation panel is now research-exposed and cannot be called pristine.

Evidence: `../analyses/helper-hf-fourstep-generalization-2026-09-12/REPORT.json`,
`../analyses/fresh-batch-invariant-hf-recovery-2026-09-12/REPORT.json`,
`../analyses/qs6-other-question-baseline-2026-09-12/REPORT.md`, and the immutable
READY receipts and live owner pointers in `../RESEARCH_QUEUE.md`.

## Current interpretation — September 12, 08:33 UTC

Four fresh-sample updates fromc32 completed; their final256predictions exactly
match the earlier one-update pilot:120TREC/112AGNews versusc32119/112. All128
group replay checks passed across four steps. This demonstrates training mechanics,
not a useful added quality improvement, and the differentseeds prevent an isolated
training-dose causal interpretation. Fourcollections had only4/5/4/3mixedgroups
of32. One consistently wrong question had zero relative-reward gradient eachtime.
Next test should improve feedback diversity or training coverage using training-only
signals, with fixed evaluation and cost accounting. The held fast-collector approach
remains separate; its fresh qualification failed in parsing before probability audit
and is being repaired additively, not counted as a failed statistical gate.

Evidence: `../analyses/helper-hf-fourstep-generalization-2026-09-12/REPORT.json`;
public summary `docs/research-checkpoints/2026-09-12-decomposition-transfer-and-four-step-rl.md`
in the RLMrepository. The new size16/4/1 comparison also shows a cross-task boundary:
TREC117/119/120 butAGNews115/112/109. Adaptive decomposition cannot safely assume
that more splitting always improves labels, even before considering token cost.

## Current interpretation — September 12, 07:52 UTC

The supervised helper provides the stronger quality result so far: on128TREC
questions absent from its verified fine-tuning inputs, the original4B model
answered92correctly and the supervised helper119. On128news examples the result
was113versus112, so this is not evidence of broad cross-task improvement. These
are deployed model conditions; their serving configurations were not identical.
One additional qualified helper RL update then changed119to120TREC and left news
at112. The nearly unchanged readout does not establish useful RL learning.

The four-update run is now active, starting again from the original supervised
helper with fresh samples at every update. Two updates are saved. Only4and5of32
training questions respectively produced both successful and unsuccessful samples.
This limited relative-reward signal motivates a later training-only data-sampling
comparison, not changing the active run after observing its intermediate results.
Its fixed fourth-checkpoint evaluation is queued; no final accuracy is available.

Separately, enabling vLLM's existing batch-invariant serving mode removed all
observed next-token probability variation at one inspected answer position across
24matched-prefix calls. That is a local stability result, not proof of matching
serving/training probabilities. A fresh48-action qualification-only test is being
prepared with the original ESS and maximum-weight gates. It performs no optimizer
step even if those gates pass; the older held batch is not retroactively approved.

Evidence: `../analyses/helper-unseen-baselines-base-repair-2026-09-12/REPORT.json`,
`../analyses/helper-hf-update-generalization-2026-09-12/REPORT.json`,
`../analyses/qs6-fixed-helper-batch-invariant-attempt003-2026-09-12/REPORT_V2.md`.
The live queue records GPU ownership and immutable inputs for pending comparisons.

## Execution update — September 12, 07:08 UTC

One exact-policy helper update completed and passed all original replay gates.
The128samples provided only4mixed-reward groups. Native evaluation is nearly
unchanged:119to120/128newTREC,112to112/128AGNews,245to244/256familiar answers.
This establishes working update mechanics, not useful learning. The next bounded
question is whether four successive updates with newly sampled actions help.
The design keeps32training records, one carried AdamW,128action denominator,
strict replay gates and fixed step4 primary checkpoint. No evaluation inputs
enter training. Further evaluation-panel reuse is explicitly exploratory.

Evidence: `../analyses/helper-hf-v2-update-stage-local-review-2026-09-12/REPORT.md`,
`../sidecars/helper-hf-onpolicy-eval-v1/outputs/attempt-001/RESULT.json`,
`../sidecars/helper-unseen-generalization-hf-updated-v1/outputs/attempt-001/RESULT.json`.
The old importance-weighted helper-RL HOLD remains separate and unchanged.

## Execution update — September 12, 06:36 UTC

The same-HF pilot collected128valid answers with4mixed-reward groups, but OOM
prevented its first gradient-bearing replay. No optimizer step occurred. Preserve
those fresh actions for a same-policy, memory-repaired replay only after exact
checkpoint/probability qualification. Downstream observed-map72 is running;
actually c32-SFT-disjoint TREC/AGNews data is ready for baseline acquisition.
The first batch-invariant attempt had zero model requests because the launch
wrapper stripped the intervention flag. Neither failure establishes a model
quality result. The localmemory andenv repairs are independent CPU preparation.

## Latest adopted result — September 12, 06:27 UTC

Fixed-helper request sizes16/4/1 produced54/61/58correct of64 repeated training
predictions and239/243/245 of256 broader-panel predictions. Smaller requests
helped on aggregate but spoiled some previously correct answers and cost more
tokens. The actual saved SFT optimizer history proves all160questions appeared
twice in c32's earlier training. This is not unseen-helper generalization.

The next decisions are whether these actual better maps help final root answers,
whether fresh local-reward RL can improve helper behavior, and whether either
effect transfers to questions not used by priorc32SFT. The same-HF RL pilot is
running with fresh sampled actions, exact-prefix probability replay and one
prospective update. Older importance-weighted V2 remains held; prospective
serving probes exposed large same-prefix logged-probability changes, not proof
that old behavior probabilities are usable. Consult queue for current owners.

## Latest adopted result — September 12, 05:55 UTC

The new sampling repeat finished at unchanged55/15/2 and self-SFT57/13/2
(correct/wrong/unavailable). Four observed SFT wins and three losses among68
jointly observed pairs give a mixed signal. The extra two available correct answers
combine one net observed improvement and one net availability contribution.
This is the same saved update on the same eight exposed contexts, not independent
training or new-context generalization. Physical input work increased from557,729
to863,518 returned-call tokens, so the earlier apparent efficiency gain does not
replicate. MAIN's analysis is
`../analyses/qs6-selfsft-seed-repeat-2026-09-12/RESULT.json`.

Prioritize the stronger controlled helper-information lead (26real/27replay/44oracle
correct of48), followed by local helper training and request-size changes. Do not
launch the proposed relaxed-ESS helper-RL update yet: identical saved helper prompts
and completions have materially different logged token probabilities. Native wire
agreement does not establish their probability meaning. A repaired serial/concurrent/
mixed-LoRA probe is running after an import-only failed attempt. The live queue
records exact owners, scientific limits and the next84-call batch-size experiment.

## Later adopted result — September 12, 05:23 UTC

Originalhelper26/48, original-replycallback27/48, correct-labelcallback44/48;
zero unavailable inallthree. MAIN rebuilt exactscorerresultSHA
d91aea95bead75bd1cf2e7224e94cf58f4e5b0ca5c4f29ff69cd6054555e7cb1.
Oracle vsreplay18wins1loss. Read
[three-arm interpretation](../../../ARTIFACTS.md).
The muchlarger oraclecontrast supports prioritizing helperinformationquality in
this smallsetting; it is not a learnedhelpergain, formalbound or generalization.
LeafRLOOV1 performed numericalqualification only andstoppedbeforeweightschanged:
ESS36.574<38.4 despiteallsupport+finite/maxweightpassing. An explicit exploratory
amendment is underCPUreview; do not silentlyreclassifyV1 orcallittrained.
Freshseedbaseline/SFTrepeat is executing. Seequeueforowner/readiness.

## Latest result — September 12, 05:08 UTC

The unchanged/RL/self-SFT copies completed their matched72 readout with53/52/57
correct answers and2/1/0 unavailable. Self-SFT has two observed wins and no losses
versus baseline, plus two unavailable-to-correct attempts. Gains occur in only two
of eight source contexts. The apparent18.4% prompt reduction is88.7% explained by
one removed long retry chain; excluding that attempt gives2.52% saving and equal
returned root-call counts. Keep self-SFT as a promising baseline, not a confirmed
general improvement. New-seed evaluation is being prepared; an independent
training realization later requires a new rollout collection, not merely a new
seed on this deterministic fixed-batch update. The oracle/replay controls are
active/queued, and helper-only RL is CPU-ready with a prospective likelihood gate.
Earlier pending-result paragraphs below preserve their historical cutoff.

## Question

With the same starting root and collection budget, does reward-based learning
improve complete answers more than simply training on the correct attempts?
Which part of the remaining error comes from helper responses rather than the
root's plan, code or calculation?

## Why this changes our next decision

The earlier longer RL comparison did not improve the final-answer count. More
updates of that recipe alone are not the most informative next step. The current
small comparison checks whether the collected attempts contain useful contrasts,
whether each update actually changes weights, and whether those changes help.
The oracle-helper comparison separately asks where better information would help.

## Completed evidence

The new fixed-model diagnostic completed all 48 attempts on twelve existing
training tasks: 26 correct, 22 wrong, no unavailable answers or integrity failures.
Five tasks had both correct and incorrect attempts among four samples. Five always
succeeded, and two always failed. These are twelve tasks from two source contexts,
not 48 independent source documents or a held-out accuracy result.

Both one-update learning copies are saved. RL used all 20 attempts from the five
mixed groups; self-SFT used all 26 correct-answer attempts. They shared the same
starting checkpoint, collection pool, learning rate and optimizer setup, but
selected different tasks and token doses. Root actions alone receive loss.
Finite gradients and changed weights establish execution, not improved answers.

## Accepted comparisons, with results still pending

1. The unchanged model, RL copy and self-SFT copy each attempt the same 72 existing
   evaluation questions. The panel is separate from this training batch but already
   research-exposed. Scores, unavailable answers and resource costs remain separate.
2. The unchanged root repeats the original 48 attempts with exact answers to its
   legitimate local helper requests. Root prompts and seeds are unchanged. This is
   explicitly a nondeployable oracle, not a new learned helper. Unsupported requests
   are recorded, and no child model tokens or logprobs are invented.

Both automatic supervisors are active; consult their live records through
[the queue](../RESEARCH_QUEUE.md), not this fixed-cutoff paragraph. Each model
evaluation/diagnostic owner has a 1,800-second cap and persists individual attempts.

### Later diagnostic analysis — 04:36 UTC

The [native-evidence replay](../../../ARTIFACTS.md)
shows that 18 of 22 wrong final answers equal the declared calculation on their
incorrect helper maps. Four differ from that calculation. MAIN independently
reproduced these counts and the 102 wrong labels among 768 observed label decisions.
Agreement is consistent with error propagation, not proof that the root faithfully
executed the method or a prediction of the oracle score.

Three of the five mixed-reward groups have map-consistent answers on all four
attempts. Thus a mixed reward group alone does not show that the root discovered
a better plan; the helper's differing replies can explain the observed contrast.
The [next-decision note](../../../ARTIFACTS.md) connects
this observation to local helper rewards, controlled continuations and recent
primary literature. A byte-identical original-helper callback control is prepared
to accompany the oracle test; no result from it is claimed here.

## How we will use the outcomes

- If the oracle substantially improves answers, prioritize the helper's accuracy
  and how correct local information reaches the root. Better helper information is
  a candidate mechanism, not proof that joint RL would learn it.
- If wrong answers remain despite correct helper outputs, inspect scope selection,
  missing records, aggregation and termination. Train or modify the actual failing
  step rather than rewarding tool calls merely for occurring.
- If self-SFT is competitive with RL, retain it as the practical baseline. A more
  complex objective needs an advantage in quality, cost or transfer.
- If neither one-update copy improves, do not declare RL impossible. Check update
  size and selected-trajectory diversity, then choose a bounded multi-batch test or
  a targeted corrective-example experiment using the oracle evidence.
- A small difference on this 72-question panel is a lead, not confirmation. Any
  selected recipe needs new source/task data and an independent training realization.

## Important alternatives and limits

Final-answer selection can reward accidental correct answers or shortcuts. A
separate method review is required to claim learned decomposition. The oracle
intervention changes helper output and subsequent root states; matched seeds do
not make the later generated trajectories identical. Perfect helper labels cannot
rescue evidence that the root never requests or relationships it discards.

The exact callback also removes actual helper inference latency. Report its cost
separately; it cannot be advertised as a free accuracy improvement. Strong future
controls include replaying authentic helper answers through the same callback and
using exact replies with matched pacing if deadlines plausibly explain the result.
These controls are proposals, not prerequisites for this first exploratory test.

Generic recursive RL and counterfactual credit are already prior art. The intended
contribution must be a better-understood, effective learning or communication choice
that survives simple baselines and tests outside the development setting.
