# Does a source ID help only when it appears before the prediction?

September 9, 2026. Main research proposal, not an implemented or accepted run.
The active GPU campaign and the two accepted automatic successors are unchanged.
This is a small candidate after the new-task comparison, not another large
same-context factorial and not a reason to delay the query-sensitive RLM pilot.

## Question and nearest evidence

The completed identity384 study forced each output object to emit its tag before
its label. With randomized, numerically disjoint source IDs, matching tags still
strongly outperformed ordinal and constant tags. A useful next question is whether
the model needs that record-specific cue immediately before predicting its label.
JSON objects can contain the same fields and values in either order, but a
left-to-right model sees different prefixes while generating them.

This is not a claim that field order affecting model behavior is new. A recent
48-example classification study moves definitions between prompts and schema
descriptions and tests an added reasoning field before the label. That study
changes generated reasoning as well as schema structure; it does not test our
specific supplied-identifier timing contrast. Read depth: abstract, methods,
results and main limitations, not an independent reproduction.
[Lin, August 2026, v1](https://arxiv.org/html/2608.08254v1).

Other related work compares answer-before-explanation with explanation-before-
answer, including a recent autoregressive/diffusion comparison. Read depth here:
abstracts only. Their reasoning-order results are precedent, not a demonstration
of our identifier mechanism.
[Xie, v4](https://arxiv.org/abs/2408.05093v4),
[Yu et al., January 2026, v1](https://arxiv.org/abs/2601.22035v1).
The Format Tax also distinguishes format-requesting prompts from decoder
constraints and studies separating reasoning from formatting; abstract only.
[Lee et al., April 2026, v1](https://arxiv.org/abs/2604.03616v1).

Our inference is narrower: a semantically equivalent serialization order could
change whether a forced source cue is available at the moment of prediction.
We should test this directly before interpreting the ID effect as a general
identity-binding ability or adding more ID-specific SFT.

## Small candidate comparison

Reuse four exposed64-record contexts, the first two TREC and first two SST contexts
by their existing fixed context index in identity384 DATA. Select them by that
rule, not by observed effect. Use their first frozen display permutation,
numerically disjoint q-prefix source IDs and historical c32de helper weights.
The old scores are not reused as controls. This is a within-context explanation
screen with new sampled calls, not new-data confirmation.

Four contexts × two new fixed seeds × three tag rules × two field orders =48calls.
The two orders are `{"tag": ID, "label": LABEL}` and
`{"label": LABEL, "tag": ID}`. Meaningful, ordinal and constant tag values retain
identity384's exact definition and canonical label set. Each output still has64
objects scored in displayed-record order. No reindexing, repair, label-dependent
constraint or second-pass answer revision.

Candidate namespace `leaf-output-cue-order-v1`, master981282001 and sampling
seeds981282011/981282021; these must pass a named-source collision check before
freeze. Repeat each seed across all six conditions for one source context.
Use rotated/reversed six-condition blocks, four workers and one shared fixed
service. Freeze the complete order, no favorable-cell pilot or automatic retry.

Make the user instruction identical across the two order conditions: replace
the historical phrase "the keys tag then label" with "the keys tag and label" in
both. Change only the insertion order of schema `properties` and `required`,
if and only if the pinned actual XGrammar compiler enforces that order. Prove
acceptance of the designated string order and rejection of the opposite order
with the actual CPU compiler/matcher before READY. JSON Schema alone does not
semantically require object key order; do not assume dict insertion order proves
the intervention. If the backend accepts both orders, stop this proposal's
implementation and explicitly design an exact-order grammar for both arms before
any live model observations. No silent one-arm grammar-backend change.

Bind actual typed native request bodies and full prompt token IDs. Within a tag
rule, prompt IDs must be byte-for-byte identical across field order; only the
decoder grammar changes. Retain order-preserving serialized-schema and wire-body
hashes. Canonical
sorted-key JSON hashes or ordinary Python dict equality can erase the very
property-order difference being tested; neither alone proves this intervention.
Do not deduplicate ordered grammars with an order-insensitive key.
Compare representative complete-output token lengths,
but report actual generated tokens rather than assert identical compute: label
choices and tokenizer boundaries may differ. Preserve all raw output and actual
field order. No named rationale or free extra text is introduced.

Use the established component serving/sampling path, temperature0.5, full support,
max3072 output,8192 context and120-second request timeout, no retries. Tentative
one-A100 allocation: collection600s, shared work780s, owned900s including120s
cleanup, outer930s. This is a roughly4–8-minute estimate, not measured throughput.
Use an external sidecar and existing lifecycle only after main implementation
approval; no new model or environment is needed.

## Outcomes and decisions

Primary: paired source-matching-minus-ordinal accuracy within each field order,
and the difference of those differences, separately for question types and
sentiment. Show all four source contexts, with only two clusters per task. Include
constant-tag contrasts, strict validity, whole64 correctness, class-count error,
nulls, and physical token/cache/wall cost. Do not call48 independent examples or
infer a whole-RLM count improvement.

One prespecified diagnostic is previous-record agreement for positions2–64:
under label-first, the immediately preceding emitted source tag belongs to the
previous item. Compare predictions with that previous displayed item's gold,
alongside unchanged primary accuracy and a label-multiset chance reference.
Repeated semantic labels make agreement non-identifying; do not rename it a
recovered answer or claim it proves an attention mechanism. The first item has
no previous source tag and is reported separately, not assigned a fabricated one.

If the source-matching advantage is large only when the ID comes first, prioritize
a source-cue-before-answer helper contract and validate it end to end. If it
persists in both orders, a simple immediately preceding-ID explanation is
insufficient; broaden model/task coverage before expensive activation work. If
both orders lose the historical advantage, treat prompt/subset/sampling changes
as unresolved and narrow the mechanism claim. A generic "JSON order matters"
finding alone is not an adequate publication novelty claim.
