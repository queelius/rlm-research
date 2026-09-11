# Sparse anchor144: independent completed-run audit

Every-record matching anchors strongly outperform constant anchors. With anchors every 4 or 16 positions, that advantage shrinks sharply, and every context–seed pair loses accuracy relative to dense matching. All 144 outputs satisfy the complete strict schema: this result is semantic degradation, not a malformed-output or infrastructure denominator effect.

This audit is independent of the sparse study's author, scorer, and collector implementation. The auditor has authored other studies using parts of the shared research harness; this is not an independently implemented inference system. METHOD was sealed after terminal status but before opening this run's outcomes (SHA256 `5b4fa6fcc21aae0c650a35c579392fe5cd736e2f04002826dd47f38d14ac051f`). It is an exploratory audit of an already frozen schedule, not a prospectively registered new experiment.

## Population and primary endpoints

There were 144 distinct planned/recorded/observed calls, 144 fully valid arrays, 9,216 aligned labels, zero infrastructure/unrun NULLs, zero schema-invalid responses, and zero length stops. All HTTP responses were 200 with captured first responses and no returned tool calls. No whole 64-label array was entirely correct (0/144). No record salvage, answer repair, reroll, or alternative alignment was applied. Matching/constant refer to the exact requested source-ID tag versus literal `p0000`, not alternative source labels.

Each table cell is eight calls (four context clusters × two paired sampling seeds), hence 512 planned and observed labels. Differences below are matching minus constant; all 72 arm pairs are jointly observed and jointly valid.

| Task | Cadence | Matching correct /512 | Constant correct /512 | Difference | Pair wins / ties / losses |
|---|---:|---:|---:|---:|---:|
| TREC | 1 | 488 | 230 | +258 | 8 / 0 / 0 |
| TREC | 4 | 318 | 190 | +128 | 8 / 0 / 0 |
| TREC | 16 | 231 | 217 | +14 | 5 / 2 / 1 |
| SST-2 | 1 | 482 | 313 | +169 | 8 / 0 / 0 |
| SST-2 | 4 | 414 | 301 | +113 | 8 / 0 / 0 |
| SST-2 | 16 | 342 | 320 | +22 | 5 / 1 / 2 |
| AG News | 1 | 411 | 192 | +219 | 8 / 0 / 0 |
| AG News | 4 | 235 | 192 | +43 | 8 / 0 / 0 |
| AG News | 16 | 200 | 175 | +25 | 6 / 1 / 1 |

Pooled matching accuracy is 1,381/1,536 (89.9%) at cadence1, 967/1,536 (63.0%) at cadence4, and 773/1,536 (50.3%) at cadence16. Constant totals are 735, 683, and 712 respectively. Pooling tasks is descriptive, not a reweighted primary endpoint. Sparse matching versus dense matching loses 414 labels at cadence4 and 608 at cadence16: each comparison loses in all 24 context–seed pairs, with no ties or gains.

## Context and seed consistency

Per-context matching-minus-constant differences below pool the two seeds, each arm having 128 labels per entry. Four contexts per task—not hundreds of independent records—are the main source clusters.

| Task / audit context | Cadence1 | Cadence4 | Cadence16 |
|---|---:|---:|---:|
| TREC 0 | +56 | +23 | +4 |
| TREC 1 | +72 | +43 | −5 |
| TREC 2 | +63 | +25 | +4 |
| TREC 3 | +67 | +37 | +11 |
| SST-2 4 | +49 | +25 | +9 |
| SST-2 5 | +29 | +14 | −5 |
| SST-2 6 | +40 | +37 | +9 |
| SST-2 7 | +51 | +37 | +9 |
| AG News 8 | +52 | +8 | +5 |
| AG News 9 | +53 | +18 | +4 |
| AG News 10 | +55 | +10 | +2 |
| AG News 11 | +59 | +7 | +14 |

Both seed aggregates favor matching in all nine task/cadence cells. Seed981296011 / seed981296021 differences are TREC 128/130, 63/65, 8/6; SST-2 84/85, 59/54, 12/10; AG News 111/108, 25/18, 20/5 for cadences1/4/16. At cadences1 and4 the sign also persists in both dispatch-order strata. At cadence16 TREC's matching-first stratum is −2 versus +16 when constant runs first; other task/order aggregates remain positive. Small strata, repeated records, and shared service/cache state preclude a strong order-interaction conclusion. Same sampling seeds are a pairing intent, not guaranteed deterministic counterfactuals.

## Distance since anchor and class-count errors

At cadence4, each distance has 128 labels per task/arm, all observed and valid. The table gives matching / constant correct at distances0–3; distance0 is the actual tag-bearing position.

| Task | Distance0 | Distance1 | Distance2 | Distance3 |
|---|---:|---:|---:|---:|
| TREC | 120 / 42 | 92 / 51 | 59 / 54 | 47 / 43 |
| SST-2 | 121 / 74 | 117 / 68 | 95 / 82 | 81 / 77 |
| AG News | 102 / 41 | 51 / 64 | 44 / 48 | 38 / 39 |

This is a strong descriptive local-correspondence pattern. In AG News, cadence4's +43 aggregate consists of +61 at anchors and −18 across nonanchors: the aggregate gain does not establish useful propagation between anchors. TREC's nonanchor gain is +50 and SST-2's +66. At cadence16, matching's distance0 accuracy remains 28/32 TREC, 32/32 SST-2, and 28/32 AG News; distance15 is 8/32, 20/32, and 5/32. Intermediate distances are noisy, not universally monotonic. Exact per-distance arm denominators are in METRICS; context × seed × distance contrasts are in SUPPLEMENT and individual positions in POSITION_LEDGER. Different distances contain different records, and slot0 is a different output representation: this is not isolated evidence about internal attention or a causal decay constant.

Mean per-array class-count L1 errors (matching / constant) are:

| Task | Cadence1 | Cadence4 | Cadence16 |
|---|---:|---:|---:|
| TREC | 4.50 / 50.50 | 22.75 / 64.00 | 44.00 / 54.50 |
| SST-2 | 2.00 / 30.75 | 6.50 / 31.25 | 16.00 / 14.50 |
| AG News | 15.00 / 46.75 | 37.25 / 59.25 | 51.00 / 64.00 |

Counts can conceal assignment mistakes because labels repeat. SST-2 cadence16 illustrates this: matching has more aligned labels correct yet worse count L1. Neither a near-right histogram nor a legal tag proves semantic correspondence. Task/arm/cadence confusion matrices and gold/prediction counts are in SUPPLEMENT.

## Physical cost and tradeoff

All 144 raw response bodies supplied known prompt, cached, and output counts. Totals are 460,476 prompt tokens = 287,792 cached + 172,684 uncached, and 82,821 output tokens. No cost fields are missing. Native prompt ID lengths and output ID lengths agree with usage on all 144 calls; every full prompt-ID vector hashes to its frozen typed-renderer reference. Returned output ID vectors are preserved in raw calls; this audit does not claim a separately re-tokenized proof of output text equality.

The matching arm's pooled cost is:

| Cadence (24 calls) | Correct /1,536 | Prompt | Cached | Uncached | Output |
|---|---:|---:|---:|---:|---:|
| 1 | 1,381 | 80,102 | 50,832 | 29,270 | 25,117 |
| 4 | 967 | 75,638 | 47,168 | 28,470 | 10,224 |
| 16 | 773 | 74,534 | 45,904 | 28,630 | 6,333 |

Cadence4 saves 59.3% output tokens relative to dense matching, but loses 414 correct labels; cadence16 saves 74.8% but loses 608. Uncached input savings are just 2.73% and 2.19%. These are observed-work comparisons with complete equal denominators, not equal-accuracy or successful-whole-array efficiency claims (there are no whole-array successes). Constant-arm totals, all task cells, and paired cost deltas are supplied in METRICS/SUPPLEMENT. Within each cadence/task matching's total prompt overhead is eight tokens (one per call); output costs differ with canonical labels and cache costs depend on ordering/state. Equal standalone tag-token length is not equal realized compute, and token counters are not FLOPs.

Collection lasted 270.499992s; summed concurrent call wall time was 1,070.901292s and must not be mistaken for elapsed wall time. Owned lifecycle elapsed321.662214s, outer process322.189108s, within the frozen caps. STATUS has no stop reason or unrun IDs. FINISH records owned release; SERVICE_STOPPED records all captured owned process identities exited and ports free. Operation EXIT is0, not timed out, with empty GPU PID list and completion-marker hashes matching the independently read STATUS/FINISH. No new GPU/process action was taken by this audit.

## Provenance and checks

Scientific READY SHA256 `25b80395b129dae68d559357281b67f5e34e9337ca99887440018f69d3b53847`; SPEC `1627f461a52811e68dfab15bd5a0ec1f173ef71accee493b50bc5fcb31c173c3`. The 152-path READY closure plus exact weight provenance were authenticated once, not per episode. The old validation-selected child is adapter `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`, with config `ec773bc3b9de58af98a7c4dce9a40af795a4d05cd47284dbbfb27eac99b74174`, on Qwen3-4B-Instruct-2507 revision `cdbee75f17c01a7cc42f958dc650907174af0554`. Owned BINDING and actual model preflight agree on alias and adapter path; preflight reports vLLM0.28.0. This is one child weight, not a training comparison.

The auditor independently checked all144 coordinate/request canonical hashes, actual ordered wire bytes/hashes, aliases, seeds, exact per-slot grammar, public input record order/text, gold-to-source crosswalk, and full native prompt vectors. Source context records match the frozen factorial/AG source specifications exactly. Each paired arm has identical input text/order, system prompt, tools, and sampling controls. Only the approved instructions/schema differ. Fixed source permutation0 is retained; this is not a new permutation replication. The actual route is the qualified component `/v1/chat/completions` first-response collector, not recursive RLM execution. No tools were executed and no model-generated code was executed on the audit host.

There are four previously exposed contexts per task, 64 records/context and 256 distinct source groups/task. These are reused developmental source records, not new holdouts. TREC/SST-2 and AG source provenance and unknown-license qualifications remain those in the bound upstream data manifests; no new acquisition or license assurance is implied. Fresh study sampling seeds are981296011 and981296021; repeated source clusters limit generalization.

Independent parsing rejects duplicate keys, nonfinite JSON, non-list/wrong cardinality, wrong object key order/extra keys, wrong anchor IDs, non-string/noncanonical labels, and objects at nonanchor positions. No stored score was used to compute primary results; all144 independent validity/correctness results subsequently agree with stored per-call scores. The source's `anchor_key_order_valid` can be true for an otherwise invalid prefix and was never treated as full validation; here independent whole-array validation passes all144. Nine focused parser tests pass, including a late bad anchor that invalidates the whole otherwise-correct prefix. No broad suite or inference rerun was performed.

## Interpretation

Dense source correspondence remains the clear accuracy choice on these exposed contexts. Sparse output reduces generation cost but does not retain dense accuracy; at cadence16 the matching advantage is small and context-inconsistent. Local improvements around tag-bearing slots motivate correspondence-sensitive hypotheses, but instructions, q-versus-p lexical identity, forced grammar, output representation, and amount of generated text all remain possible contributors. This experiment cannot establish an internal attention mechanism, general learned planning, new-task generalization, or an accuracy-preserving compute optimization.

Artifacts: audit.py (independent raw reconstruction), test_audit.py (nine focused tests), ROW_LEDGER.json (144 endpoints and costs), POSITION_LEDGER.json (9,216 positions), METRICS.json, SUPPLEMENT.json (paired/context/distance/confusion/cost detail), SOURCES.json and SUPPLEMENT_SOURCES.json (raw/source hashes), and SEAL.json. Scientific source and outputs remain unchanged.
