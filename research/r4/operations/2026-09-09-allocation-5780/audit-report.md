# Independent three-root bridge outcome audit — complete CPU follow-through

The stronger fixed roots do not lift the strict checksum endpoint off its floor: array0/8 and map0/8 for low SFT8, RL4 and higher-rate SFT8. Count shows an RL4 map advantage of2/8, but higher-rate SFT8 ties at3/8 with one win and one loss. The full audit now supersedes the explicitly preliminary endpoint screens. All96 frozen panel slots are retained; the original32 results are reused from their sealed audit, and64 new actual-native finals were independently scored. All64 are available, with zero NULLs, zero decimal repairs, and no endpoint disagreement between preliminary and full passes.

| Fixed root | Checksum array / map | Checksum map−array W/L/T | Count array / map | Count map−array W/L/T | Checksum both-arm uptake |
|---|---:|---:|---:|---:|---:|
| Low SFT8 |0/8 /0/8|0/0/8|1/8 /1/8|0/0/8|3/8|
| RL4 |0/8 /0/8|0/0/8|0/8 /2/8|2/0/6|4/8|
| Higher-rate SFT8 |0/8 /0/8|0/0/8|3/8 /3/8|1/1/6|8/8|

All bounds are point identified: checksum net[0,0] for each root; count[0,0], [2,2], [0,0]. All roots have count uptake8/8 in both arms. Thus higher-rate SFT8's checksum failure is not explained by absent child engagement alone. Relative to low SFT8, the descriptive format interaction is+2/8 for RL4 count and0/8 for higher-rate count; all checksum interactions are0. These are four exposed context clusters with two seeds nested within context/task, not96 independent observations or randomized training comparisons. Root training histories, objectives and budgets differ, and runs are sequential.

Count successes by context, array/map, are RL4: query_transfer-00 0/2/0/2; query_transfer-01 0/2/1/2; length_transfer-00 0/2/0/2; length_transfer-01 0/2/1/2. Higher-rate SFT8: 0/2/0/2;2/2/1/2;0/2/0/2;1/2/2/2 respectively. Equivalently, RL4 count is array0/map1 in both the32- and128-record strata; higher-rate is array2/map1 at32 and array1/map2 at128, each out of4. Every context/length checksum cell remains zero. Exact context, stratum, pair and same-format cross-root comparisons are in PANEL_METRICS.json. Compared with low SFT8, RL4 count array loses one matched success and map gains one; higher-rate array gains two, while map gains three and loses one. No historical benchmark scores are pooled.

## Representation evidence and its limits

| Root / task | Array label agreement | Map label agreement | Array target FP/FN | Map target FP/FN |
|---|---:|---:|---:|---:|
| RL4 checksum |336/448|304/320|2/26|1/1|
| RL4 count |373/640|602/640|13/51|1/2|
| Higher-rate checksum |429/628|552/596|18/39|0/3|
| Higher-rate count |551/680|639/688|6/19|2/2|

These are physical label occurrences, including repeated IDs, and agreement with frozen dataset labels, not independent semantic adjudication. Adaptive requested-record sequences match in only7/8 RL4 count pairs and3/8 higher-rate count pairs; checksum sequences match5/8 and2/8, including empty/empty sequences. Consequently these aggregate improvements are useful diagnostics but not an isolated paired label treatment effect. Map generation changes instructions, grammar and action space together.

RL4 widths are predominantly4, with actual128-wide calls: checksum array80×4 and1×128; map76×4 and2×8. Count array16×4,16×8,6×32,2×128; map16×4,17×8,12×10,6×32,1×128. Higher-rate checksum array45×4 and14×32; map21×4,1×8,12×10,8×32,1×128. Higher-rate count array50×4,6×8,24×10,2×32,1×128; map20×4,4×8,2×32,4×128. Width is an adaptive outcome, not a randomized factor here.

Three trace-linked cases explain why component improvements do not imply endpoint improvements:

1. Higher-rate checksum/map, length_transfer-01, seed981326021: complete, unconflicted delivered labels imply gold1611. At root code node13, `strict_map` has already returned a dictionary, but the root applies `dict(zip([row["id"] for row in batch], labels))`. Dictionary iteration supplies ID keys as the new values; comparing those keys to `human being` selects nothing. Actual tool node16 displays0 and the native final is `Answer: 0`. This is dictionary misuse before reduction, followed by faithful scalar copying. The complete map is delivered to the REPL; only repeated initial four-ID maps are literally displayed. Raw episode SHA21c0bafba5719c2058d89ab03a312fe86b02e9e2e22bf4928af213c5ee0d7c87.
2. Higher-rate count/map, query_transfer-01, seed981326011: the full corroborated32-ID map is visibly printed and implies7, but the root emits `Answer: 13`. There is no displayed computed scalar. The paired array arm computes/displays7 and answers correctly. This is a visible-map reduction failure, not evidence that a correct displayed scalar was copied incorrectly. Raw map episode SHA940f60130ac5aa4ad87119610b431595f6b83fcab0d4c882ecde0b3341039937.
3. RL4 count's two map gains have different meanings. On query_transfer-01 seed981326011, the array response contains a correct7 embedded in prose and therefore fails the frozen whole-response syntax rule; the map computes7 and returns strict `Answer: 7`. No lenient repair is applied. On length_transfer-01 seed981326021, array classifies one128-wide batch and displays6; map switches to batches of10, accumulates `all_labels`, computes28 and returns28. Both format and the ensuing root plan differ, so that gain cannot isolate representation from batch width/state handling.

Verbatim captured code, observation nodes, raw paths/hashes and endpoint evidence for these cases are in PANEL_FOCUSED.json. None of the generated code was executed by the auditor. RL4 has two correct last displayed scalars; higher-rate has six, all count successes. There is no correct-last-scalar/wrong-final case. A host scalar derived from a complete label union is never substituted for an executed computation or answer.

## Full physical, projection and visibility reconciliation

RL4 has528 typed requests/results and528 role requests/results:277 root and251 child calls. Higher-rate has397 of each:182 root and215 child calls. All925 attempts returned; no request-only, provider-failed or missing-usage attempts occur. Every native prompt/completion token sequence and completion logprob list matches the corresponding physical wire capture, and all925 graph prefixes match. All466 child semantic-call edges point to actual root call nodes; semantic edges are explicitly distinct from physical message ancestry.

All466 children qualify at ordinary depth1 under source-bound exact public ID/text requests. Every actual transformed prompt, requested order, schema/cardinality and grammar matches independent reconstruction. Roots have no grammar. All466 raw arrays/maps are valid and remain raw in the native graph. All466 root-writable delivered claims have exactly one corroborating physical match to the independently projected serialization, with zero unmatched/multiple matches, zero ordering failures and zero duplicate deliveries. This corroboration is not cryptographic delivery proof or evidence of actual root consumption.

Complete unconflicted supplied/delivered coverage, checksum array/map then count array/map, is RL4 5/4 then5/7 and higher-rate3/4 then7/8. Complete corroborated literal-map visibility on the final root branch is RL4 5/4 then1/1 and higher-rate1/0 then1/1. Each run has two episodes with conflicting delivered values, preserved as conflicts. Scalar display may be a valid efficient workflow; no full-map visibility requirement gates endpoint scoring.

Initial root prompt, sampling and sampled output match in all16 pairs for each new root, and all16 actual start orders match frozen pair order. These facts do not make later trajectories identical. RL4 captured root cells parse221/245;24 remain unparsed. All150 higher-rate cells parse. No captured code explicitly names the four screened configuration/event/overlay markers; this literal screen does not prove blindness or absence of dynamic access. Root-readable/writable configuration and overlay remain a design limitation.

## Costs and binding

RL4 uses973280 logical input tokens,44042 output,914832 cached input and58448 uncached input. Higher-rate uses680532 input,42611 output,629712 cached and50820 uncached. All usage fields are known for all925 calls. Output tokens by checksum array/map and count array/map are RL4 12706/13995 and6638/10703; higher-rate13437/10529 and9232/9413. Full per-context/task/arm/length cost tables, including cached and uncached usage, are in PANEL_METRICS.json. Different adaptive plans/exposure preclude treating these totals as equal-work throughput comparisons.

RL4 elapsed phases are49.006s before collection,483.886s collection and2.661s collection-end to recorded release; accepted job elapsed536.035s. Higher-rate phases are49.143s,453.888s and2.765s; accepted job elapsed506.365s. Its orchestration total836.458s includes330.022s waiting for a predecessor and is not GPU work time. Both jobs exit0, with no timeout, all32 recorded, no unstarted coordinates, owned process identities exited, ports free and empty post-exit GPU PID records. Historical caps remain collection1500/work1650/owned1770/outer1800 seconds. Summed request latency is not reported as GPU wall time.

Actual root files and descriptor/capture crosswalks authenticate RL4 adapter2286be3f7c0c9cc0e22c8ef8e3473b7d8eb6ec4b7a789ca380a0af9d3b944c71 and higher-rate adapter0ba42364183a311a8f5b67e4bac4e9294924c1dfb73f152a209811df09b78773; both use the fixed c32 child. The two root and one child safetensors/config files were directly hashed, six files total, with exact matches. Base manifest19619b44… is authenticated by the accepted descriptor boundary. The alias still says low8, and BINDING.campaign_policy retains stale473210/round8 prose. Those fields are not training ancestry evidence; models[role_map.root], descriptor adapter, live-model directory, direct file hashes and per-call model hashes establish what was served. Higher-rate METADATA_CORRECTION.md remains preserved, as do all historical seals.

## Disposition, verification and strongest follow-up

The immediate falsifiable question is whether checksum failure persists when representation/API interpretation and reduction are calibrated separately from classification. Use a small new-context difficulty ladder (8,16,32 records; count versus checksum; paired seeds) with a fixed higher-rate root and c32 child. Include a clearly separate diagnostic condition that supplies an immutable correct label map to the root, plus the ordinary sampled-map condition; neither condition repairs final answers or changes gold after generation. Score strict actual-native endpoints, parsed container misuse, displayed scalar correctness and whole-context coverage. If the supplied-map condition still fails through dictionary misuse or reduction, prioritize root interface/reduction training on disjoint compositions; if it passes while sampled maps fail, prioritize child semantics/width. Retire another blind three-root extension if both stay at floor without a new discriminating manipulation. A64-episode diagnostic with a1500s collection cap is a reasonable upper exploratory envelope based on the observed397 calls in454s, not a timing guarantee. Freeze sources, seeds, model files, stopping rule and output location before launch; MAIN owns scheduling and launch authority.

Completed: independent64 endpoints/gold/binding; full925-call wire/graph/projection/usage audit;466 semantic parent checks; context/length/pair/cost tables; focused mechanism evidence; historical32 reuse. Pending: only new experiments and any confirmatory replication, not an unresolved audit stage. Six bounded parser/boundary checks passed; the64 endpoint results independently agree between preliminary and full passes. No model/GPU/service/queue action, generated-code execution, literature expansion or historical artifact edit occurred.

Artifact directory: `/project/alex_phd/runs/rlm-research-r4/analyses/root-child-representation-bridge-panel-live-2026-09-09`.

- rl4-AUDIT.json SHA9a71ead47a77dd49f07ba48388e11a598e097fe27ba6a3e393a908f18bda321d.
- highlr_sft8-AUDIT.json SHA9267a112e5ae73dd616fa5544f02e6805bcd15c8934865104ef760cf384b1f8f.
- PANEL_METRICS.json SHAd79203d72b2c02322aa14dbffaddf628dc4ea78ae791f6d6fef78a25b2d05ca9.
- PANEL_FOCUSED.json SHAdfc42758d6b562dbb6efc05c85b127ba24fd843fd5e0942ddd893d8cbedd5bed.
- rl4-PRELIMINARY.json and highlr_sft8-PRELIMINARY.json remain explicitly labeled partial historical publications; full results above supersede their pending-stage labels.
- panel_audit.py and summarize_panel.py implement only the new namespace adapter/aggregation. They reuse pinned original helper functions and never call the original hardcoded main.
- FINAL_MANIFEST.json seals new outputs and this report while leaving original METHOD_READY/PANEL/RESUME_CHECKPOINT and prior audit seals unchanged.
