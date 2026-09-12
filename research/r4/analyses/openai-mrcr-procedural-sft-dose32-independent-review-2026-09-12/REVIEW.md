---
date: 2026-09-12
status: independent_CPU_review_pass_material_interpretation_clarifications
scope: fixed_SFT32_held_panel_original_returned_score_and_inert_decoder_diagnostic
source_report_sha256: 32b72266cf8d2484f4c21db55650d38274990afc88f60dfe2ccfeb2a16bc3a51
decoder_V2_sha256: ba15522db4bf25620a4fae2061d25336eae651eeeeec3d6e1302bb2e95f14dee
review_json_sha256: dd68a56efddc5034dd12755942a6de5c9bd676a18fa016ae77ccc3de4560571c
GPU_calls: 0
generated_programs_executed: false
---

# Procedure transfer is supported, with a separate output-fidelity loss

The reported paired gain survives this bounded independent review: **17 exact returned answers / 32 available cp32 episodes**, versus **2 / 29 available base episodes**, out of 32 planned per arm. The 29 available matched pairs have **15 cp32 wins and zero losses**, spanning nine distinct contexts. Both base successes remain successes. This is meaningful exploratory evidence of transfer of the trained retrieval procedure to this fixed same-family panel—not just lower teacher loss or train memorization.

The unit is **16 contexts with two stochastic repeats**, not 32 independent examples or 15 independent discoveries. Contexts share benchmark conventions/common demonstrations, the campaign is adaptive, and this held panel has research exposure. “Held” means separate from the procedure-training corpus, not a pristine confirmatory benchmark; base pretraining is unknown. This does not establish semantic multihop ability, learned delegation or useful recursion: actual child calls are zero.

## The eight trimmed exact answers are individually verified

“Raw exact” in the original table actually means **exact original harness-returned text**, not untouched model-token content. Keep the primary 17 unchanged and use “returned exact” in plain-language summaries.

All 61 saved native final responses were independently replayed through the installed Qwen3 parser and tied to the corresponding model/session and completion-token hash. Before the first configured stop, cp32 has 30 bare semantic final spans, **25 of which exactly equal gold** without normalization. Seventeen remain exact after parsing. Each of the other eight is individually gold-exact in the tokens and loses precisely gold's trailing two spaces at parsing; these eight observations concern four contexts, both repeats each. Thus the eight are demonstrated by exact per-case comparisons, not inferred merely from 25−17. The ACP boundary also strips text, but the saved native content already lost these spaces: these particular traces do not identify an additional second loss there.

The other seven returned failures are distinct: four already omit the spaces in the generated tokens (two contexts twice), one changes a digit, and two fail to retrieve the same email-about-stores target. Token-level 25 is an **inert diagnostic**, not the outcome of a new lossless rollout or permission to replace the frozen primary score. Reasoning/tool-protocol-bearing wire is excluded from semantic-answer credit. The prospective two-boundary intervention is the appropriate test of whether preserved content reaches the scored final without changing other behavior.

## Execution evidence and missingness

Recomputed clean stdout equals the target in **30/32 cp32 episodes across 15/16 contexts**, versus 0/32 base. The reported cp32 role/ordinal/successor pattern occurs in all 32; these flags alone are not a correctness proof, but clean target stdout plus final fidelity is stronger execution evidence. The two retrieval failures use `write a message about stores` instead of the actual email request; zero literal matches remain through attempted repairs. No cp32 broad-dump or schema-error flags were reported. Held `teacher_ast_exact=0` is not applicable because no held teachers exist—it must not be interpreted as failed procedure learning.

There are **no unrecorded coordinates**. Three base episodes are recorded but unavailable: the provider rejects actual prompt lengths **10826, 8722 and 8250**, above its 8192 limit. These are trajectory/context-growth-associated failures, not random missing files or unexplained timeouts. Preserve the original unavailable taxonomy rather than zero-filling or retrospectively recoding them. The comparison has 29 usable pairs. None of cp32's 17 returned-exact answers falls in these three excluded pairs.

## Costs and evidence scope

| Held arm | Physical starts / returned | Observed input / output tokens | Owner elapsed |
| --- | ---: | ---: | ---: |
| Base | 95 / 92 | 180067 / 25754 | 404.30 s |
| cp32 | 66 / 66 | 73557 / 23424 | 423.79 s |

Token counts were recomputed from every saved returned token sequence and checked against usage and collector totals. Base's three rejected requests have no usage: these are observed returned-token subtotals, not complete cost for every attempted request. Collector `usage_unknown_calls=0` does not mean those rejected requests supplied usage. Fewer calls/input tokens did **not** translate into a lower measured owner wall time here. Do not claim latency improvement or a matched monetary-cost reduction.

The review verified all **600 unique declared source hashes** from the report and decoder closures, rechecked 64 exported episode finals and exact clean target stdout, replayed all 61 available native terminal parsers, and recomputed paired/context counts and returned-token totals. `review.py` and `REVIEW.json` preserve reproducible inputs, per-case hashes and results without republishing answers. Full model/Adam/backprop qualification and general causal mapping are the already reviewed evaluator's evidence, not independently replicated training here. Original files and metrics are unchanged.

Decision: retain the exploratory same-family procedure-transfer finding. Keep output fidelity as a separately measured bottleneck, then assess the already approved prospective strip-disabled arm; no additional training or retrospective score rewrite is justified by this review alone.
