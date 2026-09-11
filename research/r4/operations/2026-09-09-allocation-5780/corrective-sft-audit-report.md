# Independent corrective-SFT audit: original attempt001

The original run does not establish a free-root improvement. Corrective training yields7 correct native finals among25 available, with7 planned NULLs; its frozen planned-denominator accuracy bounds are7–14/32. Under the separately labeled bounded operational-success metric, nonreturn is unsuccessful: corrective7/32 versus unchanged10/32 and first-producer2/32. Corrective controlled readout did not run. Its16 NULLs cannot be interpreted as failures of conditional state use. A separately launched completion will be reported additively, never substituted into this original inventory.

## Endpoint results

Every count below is independently derived from actual native response/branch tokens and a whole-strip `Answer: ([0-9]+)` match. Available malformed finals score0; outstanding tools/nonreturns/unrun slots remain NULL. Format denominators are native-available, not a dropped planned denominator.

| Original arm / mode | Planned | Native available | Correct | Format | Correctness bounds / planned |
|---|---:|---:|---:|---:|---:|
| Unchanged free |32|32|10|25|10/32|
| First-producer free |32|32|2|32|2/32|
| Corrective free |32|25|7|20|7–14/32|
| Unchanged controlled |16|16|2|9|2/16|
| First-producer controlled |16|16|1|14|1/16|
| Corrective controlled |16|0|NULL|NULL|0–16/16|

Corrective native accuracy conditional on return is28%; operational success is21.875%, versus unchanged31.25%. The native primary bound includes improvement or deterioration relative to unchanged; conditioning away policy-related nonreturns is not a valid treatment comparison. Across all six cells,123 RESULT files contain121 authentic native finals out of144 planned, with23 NULLs. Aggregate accuracy across free and controlled is not the scientific comparison.

Free new compositions: unchanged7/16, first-producer1/16, corrective4 correct/14 available/16 planned. Regression queries:3/16,1/16, and3 correct/11 available/16 planned. In context order train-00, train-01, validation-00, validation-01, free correct counts are unchanged[3,1,4,2], first-producer[0,2,0,0], corrective[2,1,1,3], with corrective NULLs[1,1,1,4]. Only four shared context clusters exist. Repeats, queries and producer widths are not independent tasks.

Paired free comparison: first-producer loses all10 unchanged successes and gains2 formerly incorrect coordinates. Corrective has3 shared successes,4 gains,5 observed losses,2 unchanged successes now NULL, and5 unchanged failures now NULL. These are descriptive matched-coordinate outcomes, not an independence-based significance claim. Controlled strict actual-map consistency is unchanged1/16 and first-producer0/16; the additional dataset-correct answers are fortuitous relative to the supplied erroneous maps.

## Actual state use and causal failure taxonomy

Unchanged free executes four faithful actual-child-map, actual-user-scoped scalar reductions, plus two separate keyword heuristics and one map-key/value bug. Unchanged controlled executes one faithful sampled reduction from exactly the prior map. First-producer executes no such scalar reduction in either mode: free actions collect maps; all16 controlled continuations terminate without a sampled tool action. Corrective free also executes no faithful scalar reduction, but four sampled programs genuinely scope records, call the child and print a category-selected list. This narrower successful evidence use is retained, not mislabeled as no state use. Full program/observation rulings are in STATE_USE_*.md and ACTIONS_*.json; no generated code was executed by the auditor.

The teacher's fresh-name correction does not appear in free trajectories. Imports and producer history available in training are not guaranteed at the free root. Observed behavior supports a reachability/action-selection mismatch and acquisition repetition, not a fixed root capability ceiling or a proven single causal mechanism.

The seven corrective free NULLs are not interchangeable availability dropouts:

- Two repeat setup/acquisition actions until over-context physical requests are rejected (8,238 and8,222 input tokens), then time out. In the first,53 sampled root actions precede the54th rejected physical request. The rejected request is not an established generated or paid model completion; its billing and missing usage remain unknown.
- Two repeat acquisitions and end with length-truncated outstanding-tool messages, not authentic final answers.
- Three are canceled by the shared450-second free-stage cap. Two already repeat acquisition loops; the last has only13 physical requests with scoped child/keyword exploration and is budget-censored. Do not attribute every cancellation to intrinsic context exhaustion.

This is largely policy-induced repeated behavior/context pressure with transport manifestations, plus shared-budget interference—not ignorable exogenous missingness. The sixteen original controlled slots are upstream-unrun, not tested failures. POLICY_NONRETURN_V2.json supersedes only the loose paid-attempt wording of preserved v1.

## Capture, targets, gate and actual training

Outcome-blind METHOD_READY SHA256 `620d81904a855e1908c4017b88ff65377b09990746d359418ce04d488d6e18e2` predates gate/map/readout exposure; the auditor did not implement this study. Source and input pins, the common accurate-contract amendment, and actual128 selected training groups from384 eligible are independently reproduced. There is no overlap with64 held-out record groups, but these raw readout contexts were already research-exposed. New user compositions are prospective within this panel, not a fresh benchmark. Common accurate id/user/text and child-prediction wording is shared across arms, not a treatment factor.

All32 training captures authenticate232 native transports:80 genuine immutable-c32 calls and152 authored root turns, including8 observed metadata-error turns. Maps exactly equal actual child responses, printed history and correction payloads. Independent actual-record/user/map recount reproduces every scalar.21 semantic map-label errors across repeated512 labels are retained; one scalar is0 versus dataset1 (train-07, q0007 child error). No gold repair. All16 controlled source histories similarly pass;40 genuine child calls plus72 authored turns,16 repeated label errors and2 map-derived scalars different from dataset truth. These histories are eval-only.

Native prefix rendering, authored completion/EOS, contiguous current-action suffix masks and token projections pass. Only the selected producer or correction turn receives loss; other history, producer/error turns and terminal diagnostic have zero weight. Synthetic transport likelihood is not RL behavior evidence; no reward, advantage or old-logprob training fields are present. Corrective per-pass target partition:1,664 mechanism tokens,5,787 actual-map payload tokens,368 copied Python-string literal tokens,1,440 other/boundary tokens, total9,259. Mechanism-NLL spans exclude copied payload/literals. This partition is not a measured gradient-share decomposition.

The first-eight gate passes:8/8 mechanism means exceed0.1 nat/token (1.173211–2.082674), median complete corrective NLL0.499243. Terminal NLL is already about4.29e-7–1.83e-4 with weight0. Span-weighted means reconstruct full recorded NLL. Gate records zero gradients/updates; projected training78.689s corrective and84.554s producer each pass600s. Projection uses mean measured forward×32×4×3 and excludes startup/checkpoint overhead. Gate forward time5.069s, total19.910s. First eight span only two contexts. No independent model forward was run by this CPU audit.

Both arms actually start the same low66c adapter, independently initialize fresh AdamW (lr1e-4, weight decay0, betas.9/.999, eps1e-8), use seed981351002, and perform exactly four complete32-example updates, each selected example mass1/32 with per-token mean CE and clip1. CPU safe tensor/optimizer inspection verifies504 FP32 LoRA tensors, finite Adam state, actual step1–4, RNG state/cursor/epoch, unchanged start values, checkpoint ancestry and reported tensor deltas. Base weights are frozen BF16; only fixed checkpoint4 is selected.

First-producer loss by update:0.637470,0.479994,0.345013,0.240025;128 selected-turn exposures,13,336 target-token exposures,66.442s. Corrective:0.524112,0.394745,0.318164,0.272236;128 turns,37,036 target-token exposures,92.564s. Equal updates/examples are not token/FLOP matching. Retained GPU numerical losses are authenticated, not recomputed with new model inference.

## Native provenance and replay

Actual served bindings, descriptors, alias/model hashes and immutable model directories authenticate low66c unchanged (`66cce400…`), first-producer fixed4 (`58ffe2ed…`), corrective fixed4 (`e796dbb7…`) and childc32 (`c32de129…`), using Qwen3-4B-Instruct-2507 revisioncdbee75f. No stale campaign-policy field is substituted for training ancestry, and no live GPU-weight inspection is claimed. Full hashes are in BINDING_*.json/TRAINING_*.json and their pinned source manifests.

All retained episode calls join actual physical requests and actual provider response identity, including repeated identical request bodies. Preserved native ancestor/prompt/completion IDs and final branches match. Some sampled histories are noncanonical tokenizations of the same decoded message text; the audit preserves actual token IDs and records canonical-rerender differences diagnostically, rather than silently re-encoding them.

Controlled replay matches entire retained request JSON objects (model, tokens, seed, caps, cache and all other fields) and complete actual response objects, with no exception fields. The first paid sampled-root prefix equals the genuine source correction prefix. This is whole-object fidelity, not a claim of original HTTP byte-order equality. Authored and replayed transports are not newly paid calls. All original initial free prompts match the frozen accurate prompt token bodies.

## Physical cost and clock

Only newly dispatched model routes are in this table; rejected requests remain attempts, not presumed generations. Tokens are actual attempted input IDs and returned output IDs.

| Stage | Attempts | Provider completions | Attempted input | Returned output | Known cached input |
|---|---:|---:|---:|---:|---:|
| Training capture |80|80|73,992|4,871|66,896|
| Shared controlled source |40|40|37,340|2,430|34,528|
| Unchanged free |181|181|241,218|13,902|224,768|
| Unchanged controlled, new |17|17|27,169|3,271|20,960|
| First-producer free |146|146|174,766|10,539|162,768|
| First-producer controlled, new |16|16|25,166|610|19,088|
| Corrective free |740|738|1,841,998|48,695|1,778,848|
| Original corrective controlled |0|0|0|0|0|
| Total |1,220|1,218|2,421,649|84,318|2,307,856|

Provider-confirmed prompt usage totals2,405,189, excluding16,460 attempted input IDs on the two rejected requests. Two usage/cache records remain unknown, not zero; provider billing is not measured. One physical completion arrives before role cancellation, so provider completion count is deliberately distinguished from role-returned native count. Cached-token usage is recoverable in raw physical responses despite the original collector's unknown-cache summaries; FINAL_ACCOUNTING.json supplies this additive recovery.

New free root/child attempts are unchanged128/53, first-producer89/57, corrective459/281; controlled new attempts are17/0 and16/0. Both rejected requests are corrective roots. Thus corrective has457 returned provider root completions and281 child completions, with the one role-cancellation distinction retained.

The training authored152 transports contain229,447 input/18,013 output IDs; controlled-source authored72 contain107,062/8,894. Each observed controlled arm additionally replays40 authored producer and40 previously acquired child transports (89,184/6,582). They are not new model costs. The generic non_new_transports ledger contains synthetic/replayed response objects; its response/usage fields must not be read as new provider completions or new billing.

Shared controlled acquisition costs40 physical calls once. Charging it fully to each of the two actually executed controlled pipelines gives80 hypothetical acquisition calls versus40 physical, a40-call saving; the original prospective three-policy ledger's120 hypothetical/80 saved was not realized in this attempt. A later third completion will add new physical continuation cost and elapsed time while reusing—not regenerating—these40 actual calls. Standalone controlled totals here are unchanged57 calls (64,509 input/5,701 output) and producer56 (62,506/3,040). Free costs above are already standalone post-training pipelines. Training gate/update compute is separate from inference-token costs.

Owner elapsed2,540.190s; parent scientific job2,543.993s, exit1, no outer timeout, GPU-after empty, release errors empty and active service none. Parent elapsed3,179.079s includes635.034s predecessor waiting and is not all GPU occupancy. The corrective free450-second substage—not the6,900-second owner work cap—expires and aborts downstream controlled readout. Overlapping clocks and token counts are not additive GPU-seconds. Repeated sampled actions and failure elapsed time consume real opportunity even when the final rejected request does not generate.

## Decision and seal scope

First finish the already authorized, separately accounted16 untouched controlled coordinates with fixed4, identical seeds/source histories/scorer. This answers the missing conditional-state question, not free reachability. If correction succeeds only from genuine producer histories, prioritize a mixed producer-plus-corrective curriculum or faithful compact state interface with explicit free-root reachability and controlled-state tests. If both conditional and free behavior disappoint, retire this short recipe; reassess target mass and trajectory diversity before spending on more epochs. Do not infer an inherent root inability from this short adaptive run.

Original OUTCOME_PINS SHA256 `6dae5bd820001a377e8b276310a489c63e847a483e609d689f919f6d10adb07d` freezes10,173 JSON files and all144 original slots. OWNER_TERMINAL SHA256 `3b749f6d014ce1ef5b9cbc0ce55b34e5edd64a0d0f042d43fb5fd59abe1d7610` records the incomplete terminal. Focused independent tests and all six native-parser reproductions are recorded in VERIFICATION.json. FINAL_MANIFEST.json seals this report and audit artifacts after source-pin verification. No scientific source, GPU, service, environment, lock, queue or historical seal was changed. Later completion evidence will be additive and separately exposed/accounted.
