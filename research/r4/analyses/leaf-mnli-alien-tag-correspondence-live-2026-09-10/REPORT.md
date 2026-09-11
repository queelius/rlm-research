# Unrelated aliases remove the shifted-visible-ID deficit on this exposed MNLI panel

Independent audit of `leaf-mnli-alien-tag-correspondence-v1/outputs/attempt-001`, accepted READY_v2. All 48 actual responses authenticate, satisfy the complete exact-tag contract, and finish with `stop`. No NULL, length cap, tool branch, score disagreement, repair or reroll. Matching and unrelated-alias accuracy are similar; the shifted visible-record referent remains markedly worse in every context.

| Arm | Strict displayed-label correct / 768 | Accuracy | Native/contract valid | Input / output tokens |
|---|---:|---:|---:|---:|
| Matching | 619 | 80.60% | 16/16 | 60,644 / 15,336 |
| Shift17 | 284 | 36.98% | 16/16 | 60,644 / 15,328 |
| Alien | 628 | 81.77% | 16/16 | 60,644 / 15,314 |

Whole-contract and shape-only semantic counts coincide; positional tag fidelity is 768/768 in every arm. No endpoint gets all 48 semantic labels correct. With no unavailable endpoints, NULL bounds collapse to the reported counts; operational and native-available summaries coincide here, not by assuming future missing responses are zero.

## Paired context evidence and mechanism

Each row combines two paired seeds: denominator 96 labels per arm. Eight contexts, not 2,304 independent labels, are the comparison units. Three hypotheses are nested within each of 128 exposed premise groups; the two seeds do not create fresh data.

| Context / genre | Matching | Shift17 | Alien |
|---|---:|---:|---:|
| 0 government | 80 | 37 | 78 |
| 1 government | 81 | 40 | 78 |
| 2 slate | 74 | 37 | 80 |
| 3 slate | 70 | 34 | 76 |
| 4 telephone | 72 | 32 | 73 |
| 5 telephone | 70 | 39 | 73 |
| 6 travel | 92 | 40 | 92 |
| 7 travel | 80 | 25 | 78 |

Matching minus shift17 is +335/768, or +43.62 percentage points; alien minus shift17 is +344/768, or +44.79 points. Both contrasts favor the first arm in all eight context clusters. Alien minus matching is only +9/768 (+1.17 points), with four positive, three negative and one tied context. These are paired descriptive contrasts, not an equivalence test or confirmatory significance claim.

At the precomputed 522 seed-expanded shift positions where displayed and named gold disagree, predictions match the **named record 368/522 (70.50%)**, displayed record 87/522 (16.67%), and third label 67/522 (12.84%). All 16 shift endpoints are eligible. The remaining 246 positions have coincident displayed/named gold and cannot discriminate the referent. Alien aliases have no named gold; their semantic target is only the displayed premise/hypothesis. No artificial alien-gold diagnostic is constructed.

This result argues against arbitrary tag diversity or copying difficulty alone explaining the shift deficit: alien retains one-to-one diverse tags, exact per-position ID token lengths matched to shift17, full exact-tag decoding, and identical actual input-token totals, while achieving matching-like semantics. A plausible narrower mechanism is interference from a requested alias that is also another visible record's ID. It does not prove an internal attention mechanism, universal semantic neutrality of alien strings, or that binding errors explain every NLI miss. The visible-ID collision and alias identity differ together, and this is one adaptively selected, repeatedly exposed panel on one released model. No tool/decomposition competence is tested.

## Native, source, cost and closure checks

The independent source check rebuilt all 48 tokenizer prefixes from actual messages; validated displayed text/order, seeds, exact per-position tag consts and all three free canonical label choices; verified alien dictionaries, within-context uniqueness, absence from displayed IDs and shifted per-position tokenizer-length equality; and checked common paired request fields. Exact wire bytes/hash/native prefixes were checked against every physical REQUEST. Model alias, one assistant branch, complete token arrays, decoded final and token usage authenticated independently. Actual service descriptor/config/live preflight identify released cdbee Qwen3-4B, no LoRA, BF16, context8192, vLLM0.28.0, four sequences and prefix cache disabled. No sampled code was executed.

48 physical requests / 48 raw returns / 48 authenticated endpoints. Total known input181,932 + output45,978 tokens; cache0 explicitly reported for all48, no unknown-usage requests. Equal input counts here do not establish equal FLOPs or billing. No new acquisitions; old corpus/model work is provenance, not current request cost. Collector272.070s; owner310.811s. OWNER complete/released, no error; all seven captured owned parent/descendant identities exited and ports were free. OWNER SHA `38ef7040b0e50247e15fed37b5b1b66a0d159487b30ea7cfea395e53dc0b8728`; SERVICE_STOPPED SHA `43029d5d23b7b1e70ad55d18bbd38f8ed68f383dddd2eb3cfe8b3cf69f7dc35c`.

## Independence and timing

This auditor did not author alien48, but authored original MNLI data/runtime and the separate new-context32 successor and contributed common native/lifecycle plumbing. The method was frozen after alien launch, before any alien aggregate/raw outcome contents were read; only live file names were seen. METHOD_READY epoch1789007407.9963536 / SHA `d7d6aef5f2035b8c61a540622cc2ecafa2494af65ad9784dd89c82ec79230bdd`. Prior MNLI/exact32 findings were known; this is not outcome-blind research globally or a prelaunch registration.

Parser/source checks and three authored regressions were sealed before raw reading: PARSER_READY SHA `e042ba947cad454c14b002377a504de4393949225efb406b533f2173ac5bb271`. Reused independent exact32 semantic and shifted-study native primitives, never producer scorer. The new parser handles all planned missing/failed-return branches rather than inheriting the old all-success assumption. No post-outcome parser amendment was needed. Independent AUDIT SHA `bfc4963f155308dbbb1b903dbf6900c2390e1dcb516c76edb14abe01eae5e18a`; all raw artifacts pinned in OUTCOME_PINS SHA `bfe18513ca40032dd24ab8ddc848c771947f476c7017a414b6e9ef7152624b6e`.

## What this changes

1. Preserve wrong-visible-reference interference as the strongest mechanism candidate; the arbitrary-alias control substantially narrows the explanation beyond matching-versus-shift alone.
2. Use the already prepared new-context matching/constant replication to assess source breadth, while acknowledging it does not itself repeat the alien/shift contrast. A later disjoint-context matching/shift/alien replication is the smallest direct generalization check if that result warrants it.
3. Do not expand this into more exposed-panel identifier variants before evaluating breadth and the active root-training evidence. These final-only effects neither establish hierarchical reasoning nor solve root acquisition/reduction reachability.
