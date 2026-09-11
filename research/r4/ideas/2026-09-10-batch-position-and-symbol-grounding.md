---
schema: literature-to-experiment-v1
id: idea:batch-position-and-symbol-grounding
created_utc: "2026-09-10T18:20:00Z"
status: primary_literature_linked_to_cpu_preparation
question_id: rq:correspondence
novelty_status: not_established_numbering_and_task_separation_are_prior_art
local_evidence: ../analyses/leaf-mnli-host-identifier-join-live-2026-09-10/POSITION_DIAGNOSTIC.json
next_design: 2026-09-10-mnli-positional-anchor-binding-design.md
---

# Keeping one's place is separate from emitting the right number of answers

Our post-hoc profile uses all 48 completed calls from the host-identifier study.
In the three labels-only conditions, first-16 accuracy is 77–84%, but remaining-32
accuracy is 34–37%. Each condition declines in every context. Aligned tag-first
answers remain 83% in both ranges. The 16-position division was chosen after
looking at this profile; it is not a previously registered threshold. All arrays
already have exactly 48 valid labels. The observation is therefore not simply an
output-count or JSON-validity failure.

## Nearby primary work and what it changes

**Cascaded Batch Prompting (August 27, 2026).** The method generates class names
first and then maps them to symbols. Its implementation uses N/b batched first-stage
calls plus N individual second-stage calls. Benefits vary: conventional batching
beats the cascade on GPT-4.1 MNLI, while other comparisons favor the cascade.
The paper discusses missing-output misalignment and a count-check/rerun control;
that control gives only a small nonsignificant gain in its reported example.
Our inference is that exact count does not settle semantic correspondence: our
arrays are complete but later labels deteriorate. Avoid claiming that a second
model-call stage, or separating content from formatting, is novel here.
Read scope: introduction, method, experimental setup/results, limitations and
Appendix A text; prompt figures were not inspected. No official source repository
was identified or executed. [Primary paper](https://arxiv.org/html/2608.27038v1).

**Sequential Enumeration in Large Language Models (v2).** The experiments compare
explicit markers/numbers, spontaneous counting, mental counting and forbidden
counting on sequence naming and production. The authors report advantages for
explicit counting, especially production, with weaker naming performance. That
provides prior art for generated position markers, not a direct demonstration of
our batched-classification mechanism. We should test markers against an input-only
control rather than attribute any gain to internal attention. Read scope: abstract,
introduction, §3.1–3.4, §4.1 and selected discussion; no claim of reproducing their
activation analysis. [Primary paper](https://arxiv.org/html/2512.04727v2).

**Exploring Limitations of LLM Capabilities with Multi-Problem Evaluation (2025).**
This study compares batched classification with selecting indices by class.
Its simplified control replaces input text with gold labels and improves selection,
suggesting the combined task can be harder than either component. This is directly
relevant to our distinction between subtask semantics and subsequent calculation.
We do not adopt the paper's broader interpretation about understanding as an
established explanation of our model. Read scope: authoritative abstract and PDF
§5.1–5.3, not the complete 20-page appendix.
[Primary publication](https://aclanthology.org/2025.insights-1.12/).

**Numbering is established practice.** A January 2026 name/address parsing paper
already describes numbered 16-record batches for alignment. We inspected its
method paragraph only; it does not establish an isolated causal benefit of numbers.
[Primary method](https://arxiv.org/html/2601.18014v1).

## Falsifiable next comparison

Cross explicit input row numbers with output row-first anchors versus labels-only,
under misleading, unrelated and aligned visible identifiers. Use fresh calls on
all eight exposed contexts, 96 endpoints total. Hold late positions 17–48 as the
prospective primary region. Compare total accuracy, prefix accuracy, availability
and token cost too. Fixed schema tokens and instruction wording form a harness
package; do not call a positive result an isolated attention mechanism.

The primary practical screen is at least a ten-point late-position gain from
output anchors without input numbers, averaged across references, with positive
context effects in at least six of eight and no availability loss. A larger gain
with input numbers helps interpret the mechanism but is not required to advance
a useful output-only intervention. Input-only benefits also justify a follow-up.

GPU shape: one existing 4B base on one A100, four concurrent calls, 1,800-second
inclusive cap; likely minutes based on the qualified 48-call studies. Keep all
raw/native results and missing outcomes; do not repair or reroll arrays. Replicate
any useful effect on new contexts before promotion.

If positional anchors help, test smaller batches and short generated counters
as accuracy/cost alternatives, then a weights-by-interface training factorial on
separate source groups. If none helps, retire the proposed position-cue remedy
and examine class bias, semantic difficulty and output-history conditioning.
