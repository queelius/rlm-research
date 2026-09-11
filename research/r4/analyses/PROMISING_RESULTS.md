# The findings most worth pursuing

September 11, 2026. This is a short research-priority note. It distinguishes strong
local observations from a publication claim; the latter requires replication,
discriminating controls and a careful comparison with prior work.

## Current priorities — September 11, 00:18 UTC

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
[Adopted checkpoint2 evidence](../../../ARTIFACTS.md#unpublished-files "Not published: root-composed-rl-checkpoint2-readout-live-2026-09-10/MAIN_ADOPTION.json").

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
