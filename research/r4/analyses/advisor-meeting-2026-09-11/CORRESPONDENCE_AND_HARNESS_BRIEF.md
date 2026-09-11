---
title: Correspondence and harness brief for advisor meeting
meeting_date: 2026-09-11
prepared_date: 2026-09-10
status: evidence_synthesis
audience: PhD advisor
---

# The discussion in one sentence

Small language models can classify records reasonably well yet lose the association between a
record and its output when many items share one prompt; explicit input/output correspondence nearly
eliminates that late-batch failure, but current same-child verification and compressed-statistic
interfaces do not reliably turn local predictions into exact composed answers.

# What is strongest enough to lead with

## 1. The model follows identifiers semantically, even when that is wrong

When an output slot was constrained to carry the ID of a different visible record, displayed-record
accuracy fell from 81.0% to 36.5%. On positions where the two records had different gold labels, the
model emitted the label of the record named by the wrong ID 71.5% of the time, versus the displayed
record's label 15.3%. A fresh 16-context panel reproduced the contrast: unrelated aliases scored
80.47%, shifted visible-record aliases 38.80%, a +41.67-point paired difference, positive in all
16 context units. This is strong behavioral evidence for semantic redirection by the supplied
identifier.

It does not prove an attention mechanism or spontaneous ID retrieval. The decoder forced the output
IDs, and the new contexts are excluded from named research inventories rather than guaranteed unseen
in pretraining.

## 2. Matched input/output row numbers repair the late-batch correspondence failure

Across another 16 inventory-excluded contexts and three reference conditions, adding row numbers to
both inputs and keyed outputs produced a prospectively primary late-position interaction of
657/1,536, or +42.77 percentage points, positive in 16/16 context units. The benefit was similar with
wrong, unrelated, and aligned reference IDs (+45.90, +47.27, and +46.29 points for the matched-row
late gain). Output row numbers without matching input rows added only +3.71 points. The corrected
denominator is 512 late labels per cell; the result and gate were always calculated with that value.

The prospectively frozen stable-key follow-up resolves that ambiguity under the same forced-output
contract. Late accuracy was 34.18% for labels only, 85.42% for sequential row numbers, 86.13% for
permuted numeric keys, and 84.90% for opaque keys, pooled across the three reference conditions.
Opaque and permuted keys each improved all 16 paired contexts and passed their independent gates;
the pooled stable conditions were +0.10 point relative to sequential numbering. Stable one-to-one
anchors therefore preserve the repair, and ordinary sequence counting is not necessary. Structured
decoding still forces the keys and output order, so this remains an encoding-package result rather
than proof of a binding mechanism.

## 3. Root behavior can improve while exact composition remains child-error limited

Question-sensitive root training substantially improved correct-and-performed outcomes on three
related readouts of one checkpoint, including nonzero answers and composed tasks. These are not
independent training or context replications. The clearest nonzero planned-denominator gains were
10→32/46, 9→27/46, and 7→25/44 across the original, fresh-seed, and metadata readouts; nonzero
composed gains were 1→20/29, 2→16/29, and 0→14/27.

Yet when the experimenter supplied the complete acquisition plan and a deterministic reducer, the
child classified 88.20% of 1,280 records but produced 0/8 exact final answers; oracle labels under
the same reducer gave 8/8. Confidence-based rechecking repaired a net 40–41 labels but only one or
two exact answers, and independent A/B agreement retained many shared mistakes. The latest direct
sufficient-statistics interface was fully available and schema-valid but also 0/8 exact: total
absolute answer error was 1,805 versus 117 for the full-label control. The present bottleneck is not
simply “the root needs a plan” or “sample the same child again.”

# A concrete example for a non-specialist

Imagine a spreadsheet row saying:

> **Row 7:** “A dog is running.” / “An animal is moving.” → entailment

Suppose its output box is accidentally stamped with the ID of another row whose correct label is
contradiction. The model often writes *contradiction* in Row 7's box—not because Row 7 became harder,
but because the stamp points it toward the other record. Replacing that misleading stamp with an
unrelated code restores the right label. Giving every row the same visible number on input and
output makes this mistake much rarer late in a long batch.

Recommended slide wording:

> “The label can be locally correct for the record the identifier points to, yet globally wrong for
> the row where it is placed. Explicit correspondence fields repair much of that routing error.”

# Prior art and the defensible novelty boundary

Indexed batch prompting, order sensitivity, and permutation controls already exist in Batch
Prompting and BatchPrompt. Grammar-constrained decoding is also known to alter generation
distributions, and semantic-operator systems already separate logical queries from physical
execution. Returning typed maps, fixed task menus, and deterministic reducers are therefore useful
controls, not standalone novelty claims.

The defensible contribution is narrower and more interesting: a measured account of when semantic
predictions lose source correspondence in long batched/recursive computation; interventions that
separate source-ID redirection, output shape, input/output position matching, root acquisition, and
reduction; and evidence that leaf repair does not automatically survive exact downstream
composition. This is an empirical systems-and-learning contribution if it generalizes across a
second model or task family and demonstrates downstream utility.

No fresh human semantic review was performed for these results. The evidence comes from frozen task
oracles, native-response authentication, exact contracts, and independent arithmetic/replay audits.

# Most decision-relevant completed experiment before the meeting

The stable-key discriminator completed all 192 calls on 16 newly selected clustered contexts. All
responses were native-authenticated, available, and contract-valid. It compares labels only,
sequential numbers, a fixed permutation of numbers, and opaque non-record keys across wrong,
unrelated, and aligned references using one released 4B model and no training.

Why this result matters for the meeting:

- The positive opaque-key result turns “numbering helps” into evidence for a reusable stable-anchor
  interface under the tested decoder.
- Permuted numeric and opaque keys both match sequential performance within one point, so the effect
  is not specific to ordinal progression.
- The whole-root bridge remains the more publication-important next stage because local interface
  repair still needs compositional validation.

Opaque promotion was intentionally strict and independent of the numeric arm: opaque alone had to gain
at least 25 points over labels-only, remain within 10 points of sequential numbering, be positive in
at least 12/16 contexts, keep at least 15/16 calls available in every cell, and show no contract or
availability disadvantage. It passed every condition, as did permuted numeric. Structured decoding
forces key tokens, so key fidelity is only a contract check, not proof of copying.

# Publication path after that result

1. **Mechanism boundary:** complete the stable-versus-ordinal test. Retire generic-key language if
   opaque keys fail; retain only the observed positional encoding claim.
2. **Downstream use:** hold the root API fixed and compare a labels-only child return with an exact
   source-ID→label map on record-specific and aggregate questions. Report acquisition, map quality,
   consumption, and final correctness separately. A leaf gain without root gain redirects effort to
   aggregation and state visibility.
3. **Generalization:** replicate the winning interface on a second model or non-MNLI task with new
   clustered inputs. This matters more for publication than adding more seeds to the same exposed
   panel.
4. **Training question:** only after the interface works, test whether root/harness co-adaptation
   learns when to request and consume the map. Compare against an experimenter-supplied plan without
   describing the supplied reducer as learned planning.

# Likely advisor questions

**Is this just better formatting?**  The intervention is an encoding package, and formatting is part
of the system. The shifted-ID controls show a specifically semantic error: the model preferentially
answers for the record named by the wrong ID. The stable-key test asks whether reusable identity is
needed or ordered formatting alone suffices.

**Are 768 labels independent samples?**  No. Context is the clustered unit: 16 paired contexts in
the fresh studies. Labels, records, and arms inside a context are dependent.

**Does the decoder hand the model the answer?**  It forces syntax and key tokens, not the free label
choice. It may make correspondence easier, so claims are explicitly conditional on that decoding
contract.

**Why not simply use a larger child?**  That is a valuable later cross-model control. First isolate
whether the interface itself is reusable; then test whether more capable classification closes the
exact-composition gap.

**Why did direct statistics fail if they are sufficient?**  They are sufficient when correct, but
the same 4B child had to classify and add many weights inside each chunk without an independently
checkable record map. Its Boolean existence flags were mostly right, while its sums were badly wrong.

# Evidence anchors

- Fresh shifted-ID audit: `analyses/leaf-mnli-new-context-alien-correspondence-live-2026-09-10/REPORT.md`.
- Fresh positional audit and denominator correction:
  `analyses/leaf-mnli-positional-anchor-new-context-live-2026-09-10/{REPORT.md,ERRATUM.md}`.
- Stable-anchor audit and meeting figure data:
  `analyses/leaf-mnli-stable-anchor-vs-sequence-counting-live-2026-09-10/{REPORT.md,FIGURE_DATA.json}`.
- Nonzero root strata: `analyses/controller-zero-support-strata-2026-09-10/{REPORT.md,ERRATUM.md}`;
  these are related readouts of one checkpoint, not independent replications.
- Supplied-plan ceiling and rechecks:
  `analyses/root-lambda-supplied-plan-ceiling-live-2026-09-10/REPORT.md`,
  `analyses/root-supplied-plan-selective-recheck-live-2026-09-10/REPORT.md`, and
  `analyses/root-task-aware-selective-recheck-live-2026-09-10/REPORT.md`.
- Direct-statistics audit: `analyses/root-j1-sufficient-statistics-live-2026-09-10/REPORT.md`.
- Prior-art boundaries: `ideas/2026-09-08-batch-prompting-mechanism-controls.md`,
  `ideas/2026-09-09-correspondence-to-rlm-next-options.md`, and
  `ideas/2026-09-09-official-runtime-comparison.md`.
