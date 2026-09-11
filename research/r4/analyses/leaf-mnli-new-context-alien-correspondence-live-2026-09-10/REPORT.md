# Independent new-context MNLI matching/shift/alien48 audit

Completed 2026-09-10 after MAIN's 04:08:55 terminal relay. The unchanged prospective method and parser were frozen while attempt-001 was absent (03:27:29 and 03:32:56 UTC), before the 04:03:20.325 launch. The auditor did not implement this study. Every outcome file was pinned before independent response scoring; no model code was executed, no science source changed, and no scorer correction was needed.

## Result

The shifted visible-record alias penalty reproduces across all 16 new context clusters. Unrelated aliases retain substantially higher displayed-record accuracy despite identical token counts and equally successful output constraints.

| Arm | Strict displayed labels / 768 | Accuracy | Native / planned | Whole contract | Perfect arrays |
|---|---:|---:|---:|---:|---:|
| Matching | 611 | 79.56% | 16/16 | 16/16 | 0/16 |
| Shift17 | 298 | 38.80% | 16/16 | 16/16 | 0/16 |
| Alien | 618 | 80.47% | 16/16 | 16/16 | 0/16 |

All 48 responses are authenticated native content branches, with complete 48-row arrays and exact requested tags/field order. There are no missing, duplicate, extra or misplaced tags. All finishes are `stop`; no grammar-failure rescue, partial-array extraction, reordering or gold repair occurred. Shape-conditional and native-available accuracies equal the primary because every endpoint passes. NULL count is zero, so planned operational scores and native-final lower/upper bounds coincide.

| Paired contrast | Mean difference | Genre-stratified context bootstrap 95% | Context signs (+ / = / −) |
|---|---:|---:|---:|
| Alien − shift17 (primary) | +41.67 pp | +38.54 to +45.18 pp | 16 / 0 / 0 |
| Matching − shift17 | +40.76 pp | +37.50 to +44.27 pp | 16 / 0 / 0 |
| Alien − matching | +0.91 pp | −0.39 to +2.08 pp | 10 / 2 / 4 |

Exact two-sided paired sign-flip sensitivities are 0.00003052, 0.00003052, and 0.30969 respectively. These are exploratory 16-cluster summaries, not 768 independent trials; intervals use the predeclared 10,000 stratified resamples and seed981623001. No equivalence margin was declared, and alien≈matching does not establish equivalence.

## Named-record diagnostic, not a repaired primary

All shifted endpoints pass the predeclared contract gate. On the 530 positions where displayed and requested-tag-named records have different gold labels, outputs follow the named record in 361/530 (68.11%), the displayed record in 110/530 (20.75%), and neither in 59/530 (11.13%). Named exceeds displayed in every context. The other 238 equal-gold positions are excluded from this diagnostic; 188 are correct but cannot distinguish referents. This is behavioral evidence consistent with wrong-record semantic interference, not proof of an internal attention mechanism or uniform record lookup. Alien aliases have no named-record oracle. Perfect forced tag fidelity is a decoder property, not learned copying.

## Paired context results

Counts are displayed-label correct /48. G=government, S=slate, T=telephone, R=travel; each context has 16 premise groups and 48 pairs. The last column is named/displayed/third on unequal-gold shifted positions.

| Context | Genre | Matching | Shift17 | Alien | Shift diagnostic |
|---|---|---:|---:|---:|---|
| 0 | G | 37 | 20 | 38 | 22/8/1 |
| 1 | G | 38 | 17 | 37 | 21/6/4 |
| 2 | G | 36 | 23 | 39 | 20/9/3 |
| 3 | G | 44 | 17 | 45 | 29/8/0 |
| 4 | S | 35 | 17 | 36 | 24/6/5 |
| 5 | S | 39 | 18 | 38 | 23/8/4 |
| 6 | S | 40 | 20 | 42 | 24/4/2 |
| 7 | S | 35 | 17 | 35 | 24/8/4 |
| 8 | T | 32 | 12 | 33 | 20/6/10 |
| 9 | T | 37 | 17 | 38 | 21/4/5 |
| 10 | T | 41 | 14 | 40 | 25/3/5 |
| 11 | T | 40 | 21 | 37 | 22/7/4 |
| 12 | R | 37 | 22 | 38 | 19/10/5 |
| 13 | R | 38 | 21 | 38 | 21/7/4 |
| 14 | R | 41 | 22 | 42 | 23/8/1 |
| 15 | R | 41 | 20 | 42 | 23/8/2 |

Genre totals (matching/shift/alien, each /192): government155/77/159, slate149/72/151, telephone150/64/148, travel157/85/160. Four clusters per genre are diagnostic, not precise population estimates.

## Actual source, request and model closure

Independent checks re-read all selected rows and the parquet's actual label metadata: entailment0, neutral1, contradiction2. All 768 pairs/256 premise groups match the fixed label-blind selection and complete premise/hypothesis texts. Gold distribution is 282 entailment,234 neutral,252 contradiction; best constant label baseline36.72%. Public IDs derive from normalized text hashes; original dataset identifiers, gold and genre are not in actual requests. All 768 alien aliases are unique, collision-free under the named inventory and token-length matched; input token counts also match exactly within every three-arm block. All 48 outgoing bodies, frozen prefixes, full grammar, sampling and response prompt/output token IDs were verified. Label grammar leaves all three alternatives free. No tools or adapters were used.

Dataset: `nyu-mll/multi_nli`, revision`da70db2af9d09693783c3320c4249840212ee221`, validation_matched; raw9,815 rows. The source receipt preserves mixed OANC/CC-BY3/CC-BY-SA3/public-domain terms, not blanket MIT. Named prior exclusions cover1,536 normalized text hashes. These are new selected inputs under that explicit inventory, not globally research-unseen or pretraining-unseen. This replication was adaptively selected after prior exposed-panel results; offset17, model, generator and task family were familiar. Old results were not reused as new controls. The inherited aggregate phrase “8 repeated MNLI contexts” is stale: actual plan/data/runtime inventory has16 clusters and one paired seed each, as prospectively documented. Dispatch first-arm counts6/5/5 are not perfectly balanced.

Actual service descriptor, config and live model card agree on released Qwen3-4B-Instruct-2507 revision`cdbee75f17c01a7cc42f958dc650907174af0554`, BF16, no LoRA, context8192, no prefix cache, four workers; temperature0.5/top_p1/output3072, thinking disabled. Zero producer-score disagreements after independent scoring.

## Physical cost and lifecycle

| Arm | Physical / HTTP / authenticated | Input tokens | Output tokens |
|---|---:|---:|---:|
| Matching | 16 / 16 / 16 | 62,221 | 15,256 |
| Shift17 | 16 / 16 / 16 | 62,221 | 15,317 |
| Alien | 16 / 16 / 16 | 62,221 | 15,262 |
| Total | 48 / 48 / 48 | 186,663 | 45,835 |

All HTTP statuses200; all48 usage records known; cached tokens0 with cache information known for48. No extra call directories, retries or pretransport failures. Provider billing is unknown/not measured. Collector273.8874s, owner310.9278s, accepted command313.4925s; startup-to-collector35.2177s, collector-end-to-owner-terminal≈1.8227s. Parent exit0/no timeout; captured owned processes exited, ports free, and parent records empty GPU PID list. The1200s outer reservation was not consumed in full. Parent timing/exit receipts are separately pinned in CLOSURE.json; science includes every attempted request and response, not just successful scores.

## Decision and boundaries

This supports proceeding with the already designed fixed-output visible-reference48: hold requested tags/output grammar fixed, change displayed IDs only, and retain all16 now-exposed contexts without outcome filtering. It better separates alias-to-visible-record association from the current simultaneous change to prompt aliases and constrained output strings. Repetition remains a caveat for the unrelated-source arm. This audit supports neither a general schema-novelty claim nor transfer to native whole-RLM acquisition/reduction, different models, free decoding, or training gains. All outcome/source/method/parser hashes and exact per-endpoint scores are retained in AUDIT.json, OUTCOME_PINS.json and FINAL.json.
