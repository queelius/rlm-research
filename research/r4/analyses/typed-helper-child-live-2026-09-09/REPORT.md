# Typed child maps worked when used; end-to-end improvement remains unresolved

Independent terminal audit, September9,2026. The study author was the padding agent; this auditor reviewed related sources but did not author this scientific driver. The main agent wrote [METHOD.md](METHOD.md) after launch and before inspecting outcomes—not a prelaunch registration. No model code was executed, no jobs were rerun, and no experiment sources or raw outputs changed.

## Bottom line

The typed child treatment produced complete valid maps in **15/15 eligible child invocations**, versus16/29 eligible raw invocations. But only **three typed root episodes actually used an eligible contract**, and only one of those answered correctly. Two other typed successes never received the grammar treatment. The primary paired end-to-end result is therefore promising only in a very limited sense: two wins, one loss and five ties among eight observable pairs; four unknown pairs leave the full12-pair net difference bounded by **−2 to+4** successes.

The unchanged-prompt calibration is a strong negative control: it already achieved six successes. Even crediting every unknown typed or raw coordinate as successful would give either taught-interface arm at most five. This fixed exposed schedule therefore does **not** support improving the existing root simply by adding the taught ID-map interface. It does not establish a population-level effect or rule out learning that interface.

## What actually completed

| Arm | Planned | Raw records | Scored/observable | Correct | Completed empty failures | Recorded null | Unrun |
|---|---:|---:|---:|---:|---:|---:|---:|
| Unchanged U |12|10|9|6|0|1|2|
| Restored raw R |12|10|8|1|1|2|2|
| Typed T |12|11|10|3|2|1|1|

All remaining observable failures are well-formed but wrong counts: U3,R6,T5. There are no nonempty malformed final replies. All three scored-empty replies nevertheless contain sampled output (537,537,594 tokens, all stop), not zero model output. Primary endpoint reconstruction uses the inherited last-nonblank-line syntax, permitted wrappers and numeric grammar; all31 raw records agree with their stored strict reward. Empty scored completions are0. Infrastructure/cancellation records remain null.

STATUS reported28 records and one censored record. The immutable raw directory contains31 records and four censored records: three additional cancellation records were committed approximately8,15 and39ms after STATUS. All three are null—not hidden successes or added policy failures. The collector's cancellation handler writes each record before re-raising; its summary snapshot can precede siblings finishing cancellation. [SUPPLEMENT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SUPPLEMENT.json") preserves exact times and IDs. Five coordinates never produced a record. The sixth context has no observable endpoint.

The operation exited1 without an outer timeout after1841.670s; scientific collection elapsed1792.290s, scientific owned elapsed1838.906s. The native collector returned3 at its wall-time cap. Service release records verify all captured owned process identities exited and ports were free; the operation recorded no GPU processes afterward. No automatic retry occurred.

## Every paired coordinate

`C` means recorded cancellation/null; `—` means unrun. Values are strict rewards. Each context contains64 source questions and two count queries; all are exposed, child-training-supported contexts.

| Context/query | Seed suffix* | U | R | T |
|---|---:|---:|---:|---:|
|1200/0|601|1|0|0|
|1200/1|602|1|0|1|
|1201/0|603|0|0|0|
|1201/1|604|1|0|0|
|1202/0|605|1|0|0|
|1202/1|606|1|0|0|
|1203/0|607|1|C|1|
|1203/1|608|0|1|0|
|1204/0|609|0|C|0|
|1204/1|610|C|0|1|
|1205/0|611|—|—|C|
|1205/1|612|—|—|—|

*Full seeds981291601–981291612. The12 triples are nested in six contexts, only five contributing observed endpoints. No binomial claim using hundreds of child calls as independent samples is appropriate. All-planned success counts are U6,R1,T3; unknown-completion bounds are U[6,9],R[1,5],T[3,5].

## Treatment delivery and where the root still fails

| Eligible-contract readout | Raw R | Typed T |
|---|---:|---:|
| Root episodes with eligibility |4|3|
| Eligible child invocations |29|15|
| Child responses across those invocations |70|15|
| Valid final maps |16|15|
| Empty final helper outputs |13|0|
| Valid label occurrences |142|192|
| Correct label occurrences |123|180|

Raw eligible invocations generated41 tool-call responses,25 stop responses and4 length responses. Typed eligible invocations each generated one stop response. This is an output-action-space intervention: grammar suppresses child tools; it is not merely wording. Label-accuracy denominators reflect different adaptive batches and repeated records and must not be presented as paired semantic gains. The remaining627 child invocations were ineligible; custom/binary contracts were deliberately left alone.

The following examples are drawn from **all seven roots with at least one eligible invocation**, with three typed cases highlighted rather than selected by success. Full examples and native paths are in [SUPPLEMENT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SUPPLEMENT.json").

1. **Successful consumption after an import repair:** typed [416f062a…](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/typed-helper-child-v1/outputs/attempt-001/phase-step8/rollout/episodes/416f062a4bceb45b83d9ad2c5876b62942adb7843c2c5a09f2e59289c7b28cbc.json"), context1200/query1. Initial code omits the `rlm_records` import and gets a visible NameError; corrected code receives seven valid maps covering64 IDs,62 labels correct, computes15 numeric records and prints `Answer: 15`. The final15 equals gold15.
2. **A valid complete map can still give the wrong aggregate:** typed [9900e3e…](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/typed-helper-child-v1/outputs/attempt-001/phase-step8/rollout/episodes/9900e3e8ea062582205e063ce21929b4b2c9c8cebf4b847844b48df37502d6b6.json"), context1203/query1. One64-ID map is fully valid but58/64 labels are correct. The model map contains five numeric labels; the root observes5 and faithfully returns5, while gold is6. Grammar cannot repair semantic labels.
3. **A second root-output bottleneck remains after child delivery:** typed [b4b8f12d…](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/typed-helper-child-v1/outputs/attempt-001/phase-step8/rollout/episodes/b4b8f12d77eee7f343bd9d4f71729fe62b2a253734464e9d6f02fd3f32039359.json"), context1201/query1. After repairing the same import error, seven valid maps cover64 IDs,60 labels correct. The map implies three numeric records versus gold4. Root code ends with the annotation `Answer: {total_numeric_value_count}`, not a print; the tool observation is blank and final answer is0. Both child semantic error and root output handling matter here.

Conversely, raw [81535a73…](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/typed-helper-child-v1/outputs/attempt-001/phase-step8/rollout/episodes/81535a736f350f6d8dd7a0272c45e304f6685c5e23e2c6eb80b924a0a636c555.json") returns the correct6 after valid maps cover only20/64 IDs. Correct final equality is not proof of complete classification coverage. Two typed successes use64 custom, ineligible child invocations each; they are not evidence of successful grammar delivery.

## Native integrity, errors and cost

All847 native attempt role/weight bindings match root473210… and childc32de…. No independently checked treatment/schema/coordinate discrepancy was found. There are843 HTTP200 responses and four explicit child prompt-overlength HTTP400 rejections (9253,10844,10331,8318 input tokens versus8192). No request-only tail appears in the retained audit union. HTTP400 output/cache usage remains unknown, never zero-filled as known cost.

762 successful sampled calls in committed graphs pass exact graph/native/wire token, logprob, usage, role and observation-mask checks. Twenty-six episodes have complete error-free capture; one additional observable U failure retains three child400 errors and its scored reward0. The four cancellation records have no committed graph. Another82 physical attempts—including a fourth400—survive outside committed graphs and are included in cost, not manufactured into endpoint rewards or training rows.

All nine available R/T initial wire prefixes and sampling settings match. Only three of those pairs have identical sampled first root actions. Seed pairing therefore does not provide deterministic counterfactual trajectories, and later child invocations are not pairwise matched.

Exact source-contract membership and schemas were independently rebuilt from public IDs/text and the fixed six labels, with one immutable decision per invocation and no root schema. On-disk wire bodies are parsed/sorted JSON: the original HTTP property insertion order cannot be independently recovered from those files alone. Ordered schema strings plus the pinned live pre-transport assertion corroborate transport order. Contract matching authenticates content, not that Python called a particular helper. Root-written helper logs were not used alone to prove delivery or consumption.

| Physical work | Root | Child | Total |
|---|---:|---:|---:|
| Attempts |95|752|847|
| Known input tokens |250366|818800|1069166|
| Known output tokens |40209|72783|112992|
| Known cached input tokens |238464|689280|927744|
| Known uncached input tokens |11902|90774|102676|

Four child400 attempts have unknown output/cache/uncached usage; their38746 input tokens are included in total known input. Arm-level work is U215/R378/T254 attempts and9786/74838/28368 known output tokens. These are realized adaptive costs with unequal completed coverage, not paired efficiency estimates. Native call durations sum1434.322s and overlap; they are not allocation wall time.139 completed runtime-command timing records sum1210.116s, including79 `sh -c` records summing685.053s; those are not all exclusively startup, and canceled commands can be absent. The new image's startup/storage environment is not a randomized historical speed comparison. Inherited nano transient retries remain possible; the retained attempt union is counted once, but identical requests alone are not proof of retries or new inference.

## What this changes next

Keep typed child delivery as a controlled interface for the already prepared root-competence SFT comparison. This audit supports separately measuring imports, actual helper use, complete ID coverage, semantic aggregate error and final-output consistency. It does not justify assuming typed child maps solve the task or that interface teaching improves planning. The approved SFT's explicit import and real-observation final-answer supervision target concrete observed failures; its evaluation must still retain unchanged/root baseline and semantic/query/length controls.

A later terminal-reward RL comparison should use only fresh sampled root traces and preserve complete malformed/empty policy failures where graph-admissible; scripted operator traces supply no root likelihood. Do not enlarge training merely because this censored pilot is inconclusive. First ask whether a learned root reliably uses the common interface and returns the aggregate actually supported by its observations, without losing the unchanged harness's current competence.

## Artifacts and reproducibility

[SUMMARY.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SUMMARY.json") is the compact result; [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") contains per-coordinate endpoints, physical attempts, native proofs, invocation maps and visible code evidence; [SUPPLEMENT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SUPPLEMENT.json") contains cancellation reconciliation and all eligible-root examples. [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") and [SUPPLEMENT_SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SUPPLEMENT_SOURCES.json") pin examined artifacts. The exact immutable study/READY/acceptance and actual two adapters were authenticated once; previously accepted large base/source closure is explicitly inherited, not repeatedly rehashed per call.

[audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py") and [supplement.py](../../../../ARTIFACTS.md#unpublished-files "Not published: supplement.py") implement the calculations. Two focused fixtures passed for scored-empty versus null, inherited wrapper scoring, unknown bounds and duplicate-map rejection. An initial utility-cache wiring error was fixed before the successful native audit; numerical preliminary output was preserved and checked identical, not rerolled. No implementer projection was used as primary evidence. FINAL_MANIFEST.json binds this completed audit package.
