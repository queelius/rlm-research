# Fewer ID reminders save output, but lose correspondence accuracy

MAIN independently reconstructed all144 raw responses without importing the study's scorer or the other auditor's code. Every primary accuracy cell, per-distance cell and raw token/cache total agrees with the [sealed independent audit](../leaf-sparse-anchor-live-2026-09-09/REPORT.md). Eight narrow parser tests pass. This check was written after the results were known; it adds confidence in the analysis, not another experiment.

![Accuracy between source-ID reminders](../../../../ARTIFACTS.md#unpublished-files "Not published: accuracy-between-reminders.png")

[Vector figure](../../../../ARTIFACTS.md#unpublished-files "Not published: accuracy-between-reminders.svg") · [Checked data](../../../../ARTIFACTS.md#unpublished-files "Not published: MAIN_PRIMARY.json") · [Raw-source hashes](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") · [Figure provenance](../../../../ARTIFACTS.md#unpublished-files "Not published: FIGURE_PROVENANCE.json").

## The useful finding

A tag matching the source record is most effective when it accompanies every answer. Returning one every four answers still helps overall, but not enough to retain dense-output accuracy. Returning one every16 gives only a small, inconsistent advantage over the constant placeholder. All144 responses were fully valid, with no missing outcomes or truncated outputs.

| Task | Every answer: matching / constant | Every fourth: matching / constant | Every sixteenth: matching / constant |
|---|---:|---:|---:|
| Question type |488/512 /230/512|318/512 /190/512|231/512 /217/512|
| Sentiment |482/512 /313/512|414/512 /301/512|342/512 /320/512|
| News topic |411/512 /192/512|235/512 /192/512|200/512 /175/512|

The every-fourth condition also reveals where the benefit occurs. For news, the matching tag adds61 correct labels at the tag-bearing positions but loses18 across the other positions, relative to the placeholder. The overall43-label gain therefore does not show useful carryover between reminders on that task. Questions and sentiment retain some benefit at later positions, which diminishes across the block.

## What this changes

This result makes the existing output-ID lead more specific than “adding labels or more text helps.” The frequency and location of the identifying information matter. It suggests a focused question: if the ID comes after its label, does the relative advantage move toward the next item? The [new96-call design](../../ideas/2026-09-09-sparse-cue-order-design.md) freezes that comparison before new inference. Its field-order pairs share identical readable prompts; the requested schema order changes.

There is a real cost tradeoff, not a free optimization. Pooled matching outputs use25,117 tokens at every item,10,224 at every fourth, and6,333 at every sixteenth. Corresponding correct labels are1,381/1,536,967/1,536 and773/1,536. The sparse forms save59.3%/74.8% output tokens while losing414/608 correct labels. Uncached input falls only about2–3%; token savings are not FLOPs. No arm labels an entire64-item array perfectly, so an all-correct-array efficiency ratio is undefined.

## Limits and verification

These are four previously exposed source groups per task with two nested sampling seeds, not512 independent source groups per cell. Different distances contain different records, and tag-bearing positions use objects while intervening positions use bare strings. Matching versus constant also changes the requested tag and instruction. Dense/sparse formats change structure and output length. The graph is a descriptive behavioral pattern, not a causal attention decay curve, general decomposition result or established benefit to complete RLM answers.

The main parser independently requires exact array length, ordered anchor keys, exact source/constant tag, canonical label strings and bare nonanchor strings; any malformed array is wholly invalid with strict0. It checks all raw response objects against the captured response text and all request objects against frozen SPEC; native token-vector lengths match physical usage. It does not redo the other auditor's full prompt rendering/source crosswalk checks or reinterpret missingness. There are no missing responses here.

Both formats and every distance were retained. No source-ID realignment, repaired label, best seed, selected context, resampled model call or generated host-code execution was used. SVG and PNG were generated from the same checked data; the PNG was visually inspected for labels, axes and overlap. The vector is code-native, not an AI-drawn data illustration. Existing frozen sources and earlier report seals are unchanged.

