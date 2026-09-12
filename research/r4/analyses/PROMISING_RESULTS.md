# The findings most worth pursuing

## Decision update — September 12, 09:57 UTC

The exploration-only explanation is weaker. T2 produced 40 mixed training groups
versus 16, but all 256 evaluation predictions matched the reference four-step
model. Do not keep increasing sampling temperature without a new reason. The
queued larger-update and paired reward-baseline controls are now more informative;
broader training and root decision-making should be prepared in parallel.

This is a useful negative mechanism result, not the main publication claim. The
stronger leads remain reliable intermediate-answer interfaces, task-dependent
effects of helper input size, and the supervised helper's same-task improvement.
The fresh adaptive comparison will test whether observable disagreement supports
selective smaller requests beyond majority voting, with full token accounting.
Any claim about learned recursive depth requires an actual multi-level task and
decision experiment; category batching alone does not establish it.

Evidence: `helper-hf-fixed256-perturbations-2026-09-12/arms/t2_lr1e5_4step.json`
and the fixed-panel reference comparison in the same analysis directory.

## Post-meeting update — September 12, 09:15 UTC

**Decomposition stability is a concrete harness question.** With fixed16-record
requests, rearranging the same256records changes22TREC and29news labels across
four arrangements. Original/reverse/A/B accuracies117/118/118/113TREC and
115/111/113/109news show gains and regressions, not a uniformly useful trick.
Same-slot regrouping changes companions and absolute tokenoffset together.
Independent all64raw-call audit9bc764d7... supports presentation sensitivity.
Next: can observable disagreement identify worthwhile smaller requests, after
counting the extra groupings? First inspect offline replay, then fresh live data.
Agreement alone is not correctness; news alreadywarns that singletonrepaircanhurt.

**A faster RL update is now technically plausible, not yet demonstrated.** Fresh
batchinvariant48actions pass unchangedimportancegates(ESS45.45/48), and scoring
recovery took22.67seconds withoutrecollection oroptimization. Exact rawratios are
notall1; retain correction andactualgradientpathcheck. This is an enabling result,
not a publishable qualityclaim. One-update implementation isapproved separately.

**The T2 exploration control creates more relative feedback in its first batch.**
Mixedgroups11/32versus4/32reference, butfinalcheckpointqualitypending. A second
controlled baseline experiment will compare two updates onthe samefresh128actions:
within-questionRLOO versus rewardsfromthe other31questions. Standardunbiased
baseline conditions areanalyzed; more gradients may add noise/cost, notlearning.

## Post-meeting update — September 12, 08:35 UTC

**The strongest new decomposition lead is a task-dependent tradeoff, not a universal
gain from splitting.** On256SFT-disjoint but now research-exposed records, fixedc32
size16/4/1 scored117/119/120 of128TREC and115/112/109 of128AGNews. Every response
was valid. Combined reportedtokens29302/64959/207621 mean individual requests
cost7.09times as manytokens. The AG reversal motivates companion/position controls
and a later learned task-sensitive choice, with independent confirmation needed.
Source: `helper-unseen-size-transfer-2026-09-12/REPORT.json` (792f7d39...).

**RL now has four verified updates, but no added evaluation benefit.** The new
four-update model exactlymatches the one-step pilot's256category predictions,
120TREC/112AGNews. Freshseed/freshsamples mean this is not an isolated dose effect.
Only4/5/4/3traininggroups of32 had mixedrewards; consistentlywrong groups canhave
zero relative-reward signal. Prioritize informative feedback/broadertraining over
more identical easyupdates. Source: `helper-hf-fourstep-generalization-2026-09-12/REPORT.json`.

The existing multi-model keyed-handoff result and supervised92to119TREC transfer
remain stronger quality findings than these small RL changes. A concrete new
harness ablation is active: ask fullcategories versus just targetcategory/other
for80category-count tasks. It has no completed result at this cutoff. Do not
turn its planned benefit into a claim or hide its reuse-aware cost comparison.

## Post-meeting update — September 12, 07:42 UTC

These are ranked follow-ups, not four publication claims. The earlier multi-model
input–answer matching result below remains important; the new experiments should
connect those interface choices to useful whole-task behavior rather than replace
that research story with a training run log.

1. **When is further splitting worth its cost?** On two familiar contexts, saved
   helper replies generated in groups of16/4/1 produced12/18/17correct final answers
   out of24. For4vs16, seven observed wins followed the changed helper-map formulas;
   two losses instead involved later root aggregation mistakes despite better maps.
   This motivates a live, new-record size comparison and eventually a learned
   selector. It does not establish an adaptive policy, unseen root generalization,
   or end-to-end savings. Reports: `qs6-batchsize-downstream-2026-09-12/RESULT.json`
   and `qs6-batchsize-downstream-mechanism-2026-09-12/REPORT_V2.md`.
2. **Supervised helper training transfers within the category task.** On128newTREC
   questions absent from verified helper training, original4B scored92 and the
   supervised-trained helper119, with28paired wins and1loss. News113to112 shows that
   this is not a general cross-domain improvement. The serving conditions differ,
   so no speed or perfectly isolated numerical-path claim is made. Report:
   `helper-unseen-baselines-base-repair-2026-09-12/REPORT.md`.
3. **The new RL pipeline works; its learning benefit is unresolved.** One qualified
   helper update changed newTREC119to120, news112to112, familiar245to244/256answers.
   Only4of32training questions provided mixed rewards. A four-update run is active;
   checkpoint1 is saved and checkpoint2 is being trained. Treat this as testing
   update mechanics and signal, not as the publication result. Move toward learned
   decomposition/checking decisions if repeated category updates stay uninformative.
   Report: `helper-hf-update-generalization-2026-09-12/REPORT.md`.
4. **An existing serving option resolves one observed numerical instability.**
   A candidate token's probability varied about140fold at an identical inspected
   prefix; with batch-invariant mode it was identical in all24helper requests.
   Runtime increased. This is a useful control for future RL and harness studies,
   not a novel algorithm, general invariance guarantee, or validation of old samples.
   Report: `qs6-fixed-helper-batch-invariant-attempt003-2026-09-12/REPORT_V2.md`.

The next decision should use the new fixed-size transfer comparison, not simply
extend the same small training recipe. If the best size varies meaningfully across
inputs, compare a learned choice against fixed-size and simple heuristic baselines,
including the selector's own cost. Keep train/test contexts separate. A prospective
fresh fast-rollout qualification is an independent efficiency question and cannot
relax the old acceptance gate retroactively.

The delivered September11deck keeps its meeting cutoff. These results are recorded
as post-meeting reports and ideas; no silent slide-history rewrite is warranted.
Earlier dated priorities below are preserved historical snapshots.

September 11, 2026. This is a short research-priority note. It distinguishes strong
local observations from a publication claim; the latter requires replication,
discriminating controls and a careful comparison with prior work.

## Current priorities — September11, approximately13:00UTC

Lead with a **record-level handoff study with measured whole-task utility**, not
with the invention of identifiers. The same-panel second-model result and three
output-order conditions strengthen the behavioral finding. E1's equal-work cost
comparison forces a sharper question: can a managed handoff beat simply making
smaller calls at a useful budget? Compact replies are a practical follow-up,
not an end-to-end contribution by themselves.

The **training execution-transfer** result also strengthened: new explicitly
described combinations improved2/72→29/72faithful-and-correct, missing bounds
2–13→29–30. The larger claim remains limited by supplied plans, reused contexts,
and no second real task. The completed longer reward pair did not improve its
secondary final-answer count; do not keep waiting for a result that is already
available, or call this a failure of reward learning generally.

The [current summary](CURRENT_SUMMARY.md) and [new decision question](../../../ARTIFACTS.md)
give current evidence and links. Historical current/queued statements below are
preserved snapshots, not active ownership or the latest slide deck.

## Previous priorities — September 11, 04:03 UTC

Two completed studies strengthen the two main directions without closing their central gaps.

- **Root SFT transferred to newly selected inputs.** Faithful-and-correct execution on one fresh
  72-task panel was12–19 for fixed24,55 for original-corpus SFT6, and53–55 for new-corpus SFT6.
  Both trained policies improved all eight contexts and recovered34–35/48 composed tasks versus
  zero for fixed24. This is now two training corpora plus one newly selected evaluation panel, but
  still the same task families, fixed child, and metadata transformation. Next prioritize a genuinely
  new operation combination or second task, not another readout of these same families.
- **Matching keys prevented large-batch degradation on fresh inputs.** Labels-only accuracy fell
  from82.8% at8 records to43.8% at64, while sequential and opaque keys stayed83–87%; both keyed
  arms beat labels only in all16 contexts at32,48, and64 records. The next publication-relevant
  question remains downstream value in a complete task. Do not turn the observed32-record onset
  into a universal limit or the encoding package into an internal-mechanism claim.

The authenticated-map reward V1 and V2 attempts remain visible as zero-update integration failures.
V1 lacked a required serving-model manifest binding; V2's24 first-window task identities failed
before transport. Additive V3 has now crossed into real control-arm native rollout with the same
scientific inputs, but no optimizer update or arm comparison exists at this cutoff. Rollout activity
is operational progress, not reward-training evidence.

## Previous priorities — September 11, 03:12 UTC

Keep input–answer matching as the strongest near-term direction, while separating
three outcomes: well-formed output, accurate helper judgments, and useful final
answers. The new grammar control mostly improves the first, whereas H6 already
showed an accuracy gain with all outputs well formed. The partial bridge gives a
small posthoc fixed-calculation signal (2/16 to5/16 exact with opaque tags), but
not a successful full-RLM result:88/96 main-model finals remain NULL.

The next accepted test varies batch size on fresh selected inputs. A renewed
whole-task comparison should first address the trained-model/new-helper API
mismatch, not assume that increasing the context limit repairs it. These are
promising experiments, not yet publication-ready evidence.

The observed-map reward diagnostic is MAIN-adopted, with its mandatory grouping
erratum. It suggests different credit, not a dramatic increase in reward density.
Two24-window reward arms are CPU-prepared. Independent review found ordinary
missing helper maps wrongly invalidated training windows; MAIN also found a
lost startup-to-collection timer reset. Both are being corrected before launch.
No reward-training benefit is claimed from this CPU analysis.

The meeting keeps these later controls in a separate plain-language Q&A note,
not additional main slides. Its14-slide numerical cutoff remains02:15UTC.

## Previous priorities — September 11, 02:18 UTC

The balanced literal-reuse control passed cleanly. With arbitrary strings present on both sides,
matching input/output tag dictionaries scored 78.8% on later labels versus 32.6% for disjoint
dictionaries, a +46.2-point paired effect positive in all 16 exposed contexts; all 192 responses
were valid. This is stronger evidence that shared literal handles are useful in this structured
interface, not proof of an internal binding mechanism or whole-system value. The queued 96-call
grammar-on/off comparison tests how much the constrained output interface contributes.

The stable-identifier effect now has directional evidence in another model family. Mistral-7B
improved from 31.9% late-label accuracy with labels only to 55.8% with sequential identifiers and
52.5% with opaque identifiers; both frozen behavioral gates passed and all 144 calls were valid.
The lower absolute level than Qwen makes this useful breadth evidence, not a model-size result.
The intervention still bundles identifiers, requested output, and grammar; H6 isolates literal
reuse within that package but does not isolate a mechanism.

The LR-only terminal-reward ablation does not promote the RL direction: six updates at 1e-5 tied
the start on the 48 composed questions (36/48 each) and on grounded faithful execution (33/48
each). Missing outcomes leave the all-72 final between 52 and 56 versus 55 at start. The useful
next RL question is whether a denser calculation-aware diagnostic exposes meaningful within-task
credit, not another learning-rate-only repeat. Any such rescore is diagnostic until frozen as a
new intervention.

The highest-value short comparisons are now the queued grammar control, fresh-input replication,
and a successful whole-task bridge. H6 establishes neither whole-system benefit nor new-input
generalization.

An offline observed-helper-map reward diagnostic has been produced as a CPU-only derived result and
is pending MAIN review. It is not a training effect and does not authorize a new reward run.

## Previous priorities — September 11, 00:18 UTC

The input–answer matching direction remains the clearest near-term candidate.
The large gain appeared in another released model: Qwen3-8B31.5% untagged,
85.5% numbered,81.1% arbitrary. This strengthens the observed interface effect,
not a claim about internal mechanisms or model size. Whole-task benefit is still
unproven; that comparison is now serialized after the active reward-training job.

The training direction also gained evidence: another demonstration corpus yielded
55/72 correct-and-performed answers (two missing), compared with50 for the first
corpus and12 at the already-trained common start. The decisive next question is
new evaluation inputs, not which of the two corpora wins by a few answers.

Both checks are integrated into the13-slide meeting package and guide, without
adding slides. Historical priority sections below record how the plan evolved.

## Latest priority update —23:34 UTC

The arbitrary-tag comparison strengthens the input–answer matching route.
Late-label accuracy was 84.9% with arbitrary tags versus 85.4% with sequential numbers
and 34.2% without matching keys, with improvement in all 16 paired batches. Ordinary
counting order is not needed under the tested forced-tag, fixed-order interface.
This is an interpretable additional control, not proof of an internal mechanism
or a new invention of numbered batching. The next publication-relevant step is
a final-task benefit, followed by a second model or task and length/order controls.

H3 is now in the 13-slide advisor deck and its guide, evidence, and publication
options. The revised new-corpus training is active, and the lower-update-size
reward comparison is queued; neither has a new scientific result yet.

## Previous priority update —23:14 UTC

Lead the advisor discussion with learned requested calculations and the
replicated input–answer matching effect. Keep novelty narrow: numbered batching
already exists; the prospective contribution is a measured failure, a
discriminating explanation, and useful downstream benefit.

The matching-key test is now on the GPU. Its result will help decide whether
arbitrary reusable keys work, or whether the benefit depends on ordinary sequence
numbering. The new training corpus is captured and training is queued. This
addresses an important weakness of the SFT claim: dependence on one training corpus.

The complete six-update RL result remains negative for this exact recipe, and
mixed helper training did not reliably improve final counts. Direct model-computed
statistics failed sharply. Do not present local gains as whole-system gains or
scale the same failed summary/rechecking recipe without new evidence.

The advisor package is reviewable. These qualifications are explained in the
guide and evidence documents, not in a crowded catalogue of debugging on slides.

## Previous priority update —22:14 UTC

**Early RL updates have not preserved the SFT gain.** The fixed two-update
readout gave47 correct versus55 at the SFT start. Even favorable missing-outcome
assignments leave a decline of at least3/72. The live continuation supplies a
larger, fixed dose; a fresh-start lower-LR comparison will probe update size.
Neither result justifies abandoning RL generally. A second SFT training corpus
will independently test whether the encouraging process-training result depends
heavily on the original examples. These follow-ups were chosen for information,
not as retries until a positive score appears.
[Adopted checkpoint2 evidence](../../../ARTIFACTS.md).

**Training exposure can repair an interface mismatch.** Compact-only SFT gained
90/768 compact labels but lost18/768 fuller-format projected labels, missing the
retention target. Balanced mixed exposure gained75/768 compact labels while
also gaining9/768 fuller-format labels, clearing both local gates. This is a
single-seed exposed-panel result, not an independent generalization claim. The
next test is the same supplied-plan counting task with only the child changed.
[Mixed-format evidence](trec-child-interface-mixed-sft-followup-live-2026-09-10/REPORT.md).

**Same-model agreement did not supply a reliable repair signal.** The subsequent
48-call factorial failed the task-aware/verification/exact-answer targets.
Confidence-single gave2/8 exact totals; confidence-agreement and task-aware-
agreement each gave1/8. Agreement preserved42 and48 wrong labels respectively.
This supports testing different weights or sufficient statistics, not scaling
the present consensus rule. It is a useful boundary condition, not a novel
general claim about verification.
[Selection-by-agreement audit](root-task-aware-selective-recheck-live-2026-09-10/REPORT.md).

**Selective checking improves the pieces more than the final answer.** With
the same25% review budget, confidence-based rechecking produced+40 net correct
labels, versus-9 for random checking. It captured107/151 initial errors versus
34/151, and won on net label corrections in7/8 paired episodes. Yet it repaired
only one final composed answer, versus none for random checking, failing the
declared+2 downstream gate. This gives a sharper research question: should the
harness consider a record's effect on the final calculation, and should it
require agreement before replacing an earlier answer? The next small factorial
test examined both and failed its downstream gate above. The eight observations share four exposed clusters; this
is a mechanism lead, not a generalization or publication claim.
[Audited result](root-supplied-plan-selective-recheck-live-2026-09-10/REPORT.md).

**Matched row numbers look like a useful low-cost interface change.** On eight
exposed 48-record contexts, the input/output numbering package improved total
accuracy from 590/1152 to 933/1152 (+29.77 points), and later-record accuracy from
292/768 to 620/768 (+42.71 points). Output numbering without input numbers gained
only 16/768 later labels (+2.08 points), failing the frozen output-only gate.
The late input-by-output interaction is +40.625 points. All three reference
conditions benefited, so this is not specifically a cure for misleading IDs.
The subsequent16-new-context replication passed: late interaction+42.77points,
positive16/16, all192native/valid. The matched package gained46.48points versus
3.71 fromoutput-only numbering. Next test whether a paired RLM benefits and
which part of the interface causes the effect; numbering itself is not novel.
[Claim and limitations](../claims/output-addresses-help-and-interfere.md).

**Controller training has now survived a substantive metadata change.** The
full code-path audit gives correct-and-performed12→50/72, including0→32/48
on composed questions. This is stronger than answer-only improvement but is
still the same eight contexts and one training realization. The next decisions
are scale transfer and actual composed-task RL, not declaring general planning.

**Field-order interference has fresh-context directional support.** The
selective effect is+9.77points, positive14/16, with all96 responses valid.
It misses the frozen10-point threshold, so do not label it formally confirmed.
The positional-anchor evaluation above supplies a separate follow-up mechanism
hypothesis; it does not retroactively change this field-order threshold.

**The root/child error split is actionable.** Twelve metadata-transfer errors
are explained by wrong child labels despite correct root computation. Alongside
the optimizer-disjoint child gain below, this motivates the queued comparison
of full classification versus a query-specific three-way child representation.
That comparison has now completed: compact A/B/other output reduced accuracy,
whereas full-six output plus host projection retained a7.03-point adapter gain.
This redirects immediate engineering toward the existing full-label contract,
and research toward whether contract-specific training repairs the interaction.
[Audited result and limitations](../claims/child-interface-compatibility.md).

**Scaling remains the important unresolved problem.** The64-case factorial
produced only one verified nonzero-answer success. Six of seven correct-and-
performed successes were zero-answer cases, including two reducers that would
fail on nonempty selected records. The next supplied-plan diagnostic asks
whether classification errors would still prevent success even with acquisition
and reduction provided. It now gives a clear local answer:0/8 exact totals despite
88.2% correct labels and complete maps; reference labels give8/8 with the same
reducer. Selective rechecking is an actionable follow-up, motivated by a separate
native-confidence diagnostic that concentrates66–68% of child errors within the
least-confident25% of labels. Neither diagnostic establishes successful repair.
Do not use small-context SFT gains to imply reliable
large-context decomposition. [Execution and zero-support qualification](root-qs-scale-harness-factorial-live-2026-09-10/ZERO_SUPPORT_AND_ACQUISITION_NOTE.md).

## Child adaptation: strong component transfer, not a whole-system claim

The complete official-test comparison improves64.0→84.5% at100-record width and71.7→88.5% at16-record width, all148 responses verified. All500 normalized source questions are optimizer-disjoint;489 remain prior-research-exposed. The prospective five-point component-transfer gate passes at both widths. [Claim card](../claims/child-adaptation-transfers-to-official-test.md).

## Publication discipline

A publishable story should explain a transferable failure or improvement, not just report more checkpoints. The leading controller story is task-sensitive program execution; the leading interface story is the tradeoff between correspondence help and wrong-record interference. Neither has an established novelty claim. Keep new-context tests, independent training realizations, practical cost, and strong prior-art baselines explicit.

[Complete priority history](../operations/2026-09-10-status-history-at-1917/PROMISING_RESULTS.md) retains the prior leads, counterevidence, and abandoned or revised directions. [Question cards](../questions/README.md) and the [analysis index](README.md) connect claims to evidence; the [live queue](../RESEARCH_QUEUE.md) governs current work.
