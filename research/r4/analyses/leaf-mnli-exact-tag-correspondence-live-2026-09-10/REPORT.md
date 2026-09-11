# Exact-tag MNLI correspondence: independent audit

## Result

Forcing each output tag to the exact requested public ID makes the correspondence effect directly
observable. Matching requested tags scored 622/768 displayed labels (81.0%); fixed shift17 scored
280/768 (36.5%), a 44.5 percentage-point gap. All 32 endpoints returned, authenticated, and satisfied
the entire 48-item tag/order/label contract, so there are no infrastructure NULLs or malformed-output
zeros and the missing-data bounds collapse to the point estimates.

On the predeclared 522 shifted positions whose displayed record and requested-named record have
different gold labels, the output followed the requested-named record 373 times (71.5%), the displayed
record 80 times (15.3%), and the third label 69 times (13.2%). On the other 246 shifted positions,
where the two gold labels agree, 200 were correct (81.3%). This pattern is much more specific than a
generic degradation from awkward IDs: performance remains near matching when the two candidate
semantics agree, while unequal positions predominantly follow the named record.

## Paired/context structure

The matching-minus-shift strict correct-count differences, pooling two paired seeds (96 items/arm)
inside each repeated context, were 42, 40, 40, 38, 41, 31, 54, and 56. The mean is 42.75 items per
context, identical to 342/768 overall. The direction holds in all eight exposed contexts and all four
descriptive genres. These are eight context clusters with seed robustness, not 1,536 independent
items or fresh-source replication; no confirmatory p-value is warranted.

## What the comparison identifies

Both arms displayed the same premises, hypotheses, order, public IDs, requested-tag field, messages,
label freedom, generic label enums, model, sampling seed within pair, and exact output contract. Each
arm's schema fixed the appropriate requested tag at every position; the shift is a label-blind cyclic
permutation of the same tag multiset. The independent source recount reproduced 261 unique
differing-gold positions, doubled to 522 over the two paired seeds.

This supports a strong semantic-redirection/correspondence interpretation under an exact constrained
decoder: the model's label is often for the record named by `requested_tag`, not the record occupying
that output position. It does not establish spontaneous free emission, unconstrained remapping,
attention internals, or generalization to unseen sources. The panel and prompt family were already
research-exposed, and this exact-tag follow-up was adaptively motivated by the earlier shifted study.

## Native and operational audit

The independent parser authenticated all 32 dispatched ordered bodies, expected native prompt token
IDs, unique assistant choices, released-model alias, completion token IDs/text, integer usage, and
finish branch. It independently parsed JSON with duplicate-key/nonfinite rejection and required 48
ordered `tag`,`label` objects, exact per-position requested tags, and canonical labels. It found no
producer-score disagreements. No tools were advertised or executed; no answer was reordered,
repaired, or partially rescued.

The live service was released Qwen3-4B-Instruct-2507 (cdbee), no adapter, BF16, 8,192 context,
vLLM 0.28.0, prefix caching off, and four sequences. Collection used 32 physical requests and
reported 121,288 prompt plus 30,592 completion tokens. Provider billing was not measured. The owner
completed and released cleanly in 218.538 seconds; collection itself took 181.180 seconds.

## Audit timing and authorship

Runtime_port's existing method was genuinely frozen before generation. This separate parser was
written after outputs existed and after MAIN disclosed the aggregate totals listed above; it is
therefore aggregate-aware, though its metrics and denominators were unchanged. This auditor authored
the generic shifted predecessor and original MNLI data preparation, but not this exact-tag
implementation. `AUDITOR_TIMING.md`, `AUDIT.json`, and `OUTCOME_PINS.json` preserve those boundaries.

## Next discriminating comparison

The highest-value next step is fresh-context replication of matching versus label-blind shifted IDs
under the same exact contract. If the effect repeats across newly frozen contexts, then test a free
decoder with a non-coding, no-tools interface to separate semantic correspondence from emission and
route failures. Output-diversity controls are no longer the central uncertainty here: both present
arms emit the same diverse tag multiset exactly.
