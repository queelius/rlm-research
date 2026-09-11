# Authored plan-SFT: no filter-first advantage; more classification, worse strict outcomes

The prespecified primary comparison is **1/16 canonical versus1/16 filter-first**, with the same sole correct coordinate:0 paired wins,0 losses and16 ties. Both trained arms classify every visible record in every episode; the filter-first training does not produce the intended query-specific input selection in this readout. The unchanged low8 root has four known successes. Each trained-versus-unchanged comparison has1 win,4 losses,10 ties and1 unavailable control endpoint, giving a tight net difference of **[-4,-3] successes per16 planned coordinates**.

These are four exposed context clusters, with two query families and two seeds nested within each—not48 independent tasks. The two trained arms share a deterministic full-corpus recipe, start and orders; they are not independent training replications. All original source, failures, collector scores and frozen analysis files remain unchanged.

## Strict outcomes and availability

| Context (four coordinates each) | Canonical | Filter-first | Unchanged |
|---|---:|---:|---:|
| query_transfer-00 |0 correct,0 NULL|0 correct,0 NULL|0 correct,0 NULL|
| query_transfer-01 |0 correct,0 NULL|0 correct,0 NULL|1 correct,0 NULL|
| length_transfer-00 |0 correct,0 NULL|0 correct,0 NULL|2 correct,1 NULL|
| length_transfer-01 |1 correct,0 NULL|1 correct,0 NULL|1 correct,0 NULL|
| **All16 planned** |**1 correct,0 NULL**|**1 correct,0 NULL**|**4 correct,1 NULL**|

Query totals are0/8,0/8 and1/8. Length totals are1/8,1/8 and3 known successes plus1 NULL. Both trained roots lose one query success and have a length net bound of[-3,-2] versus unchanged. The primary comparison between trained arms has no missing outcomes.

The sealed auditor initially reproduced the collector's1/16,1/16,4/16 projection, treating all48 as observed. A narrow additive implementation correction enforces the already-frozen method's **actual native final-response boundary**. Unchanged seed981320303 has `episode.ok=false`, `trace.ok=false`, `stop_condition=error` and a broker `set_broker_scope → get_shell_msg(timeout=30) → _queue.Empty`. Its last physical root response is a tool request, not a sampled empty final. [Raw case](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-plan-sft-v1/outputs/attempt-001/unchanged/rollout/episodes/9b40410cdefb70b8f6b07902d695f1feddd8b9036a0dae9360d5cf5fdbe8dd9e.json"); exact raw/request hashes are in NATIVE_ENDPOINTS.json. The old0 stays in AUDIT/EARLY and the collector; the availability-safe result is NULL. This does not affect the primary trained-arm contrast.

The other47 physical last-root responses have normal `stop`, no structured tool call, and content exactly equal to the recorded final reply. All48 final physical branches, including the interrupted branch, match native prompt-plus-completion IDs. A verifiable graph is not itself proof an answer exists. No later cleanup or budget state censors an already sampled answer.

## What behavior actually changed

Both trained arms obtain valid child maps covering all1280 visible record exposures, with **640 query-irrelevant exposures** and no repeated-ID classification. Unchanged uses636 label occurrences and53 unique-irrelevant-ID exposures across its trajectories, with complete relevant child-map coverage in11/16 rather than16/16. Full source coverage is not the same as correct scope, correct classification or correct reduction.

Every initial root action in all48 episodes is a parsed Python tool request. Canonical13/16 and filter-first14/16 still copy the old four-record helper example verbatim, as does unchanged14/16. No first action uses a literal `selected = ...` assignment; this lexical observation alone is not a strategy test. The decisive physical check is that both trained arms request all32 records in every query episode and all128 in every length episode. More supervised fitting did not manifest as filter-before-classify behavior here.

Canonical14/16 and filter-first15/16 finish after a displayed label map; only2/16 and1/16 finish after a displayed computed scalar. Root-visible literal-map coverage corroborated against child values is complete in14/16 and15/16, respectively; the scalar-only cases can have full child coverage without printing those maps. Corroboration means the observed values match physical child outputs, not that those values agree with the dataset or were used faithfully.

Each trained arm emits eleven short decimal-form answers, for example `Answer: 13.0`, invalid under the frozen integer-only contract. These must not be repaired into successes: canonical query seed981320203 says10.0 versus gold2, while filter-first length seed981320301 says24.0 versus gold1; both last observations are four-ID maps, not the claimed scalar. Across the three displayed trained-arm scalar observations, finals copy the scalars faithfully: canonical17 versus gold1, and the shared correct28 in each arm. Thus these examples do not establish a correct-computation/wrong-restatement bug.

Strict integer syntax holds in4/16 canonical,3/16 filter-first and10/15 available unchanged endpoints. The new training contains only initial actions, no terminal-answer examples; this experiment does not isolate why terminal formatting worsened. Nor does the failure of this short training dose show filtering cannot be learned.

## The supervised updates are real and correctly bound

Both four-step chains start at exact low8 adapter `66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5`, with fresh Adam, LR1e-4, shared training seed981320002 and the same four shuffled full-corpus passes. Fixed final4 is used, with no validation selection:

- Canonical adapter: `70353bb5324f31f87fc5943630b4e08b5098afa9fe13fefa0c1d98532610d8c4`.
- Filter-first adapter: `f675e5eb04568e2720cdc1427d949bdd9cb19e20d69d682ed9a6cd8609cef7ab`.

The independent audit checks all504 FP32 adapter tensors at each checkpoint against the exact start: finite changes, final L2 deltas1.34764649 and1.34483983. Saved Adam state has504 parameter states and actual counters1→4 with the declared LR/betas/epsilon/zero weight decay; optimizer/RNG/cursor and prior-state hashes are contiguous. No child model is loaded or updated during training.

Each arm has16 authored first actions,2472 targets per pass and9888 targets over64 example/root-turn exposures. Combined targets are19776. Prompt/observation/child tokens are masked, and the honest151645 terminator is included. There are no fabricated teacher successes or behavior likelihoods. The two arms have eight identical global examples and eight assignment-only single-user differences. Every recorded float32 row coefficient equals1/(16×its actual action-token count); each full-pass mass sums to0.9999999820720404. Weighted CE, separate token NLL and positive finite gradients reconcile. Pre-update token NLL falls across the four passes from0.8110→0.3714 and0.8035→0.3739; these are training fits, not readout gains.

## Provenance and all-call costs

The actual corrected READY_V2, corpus, source/input identity, fixed checkpoint/config, three phase descriptors and captured `/models` crosswalks reconcile. Root physical aliases bind the appropriate real checkpoint; depth1 always uses unchanged c32de. All1252 pretransport requests have results and verified physical token IDs/logprobs, with no request-only record. Typed output constraints apply only at depth1. All16 matched initial prompt-token sequences and sampling objects are equal across arms; model alias/weight is the intended difference. Fixed phase order canonical→filter-first→unchanged remains a service/time nuisance, not deterministic replay.

| Arm | Physical root / child calls | Logical input | Generated output | Cached input | Uncached input |
|---|---:|---:|---:|---:|---:|
| Canonical |243 /227|922440|34846|891600|30840|
| Filter-first |274 /258|1061705|37888|1031936|29769|
| Unchanged |138 /112|460109|22298|437120|22989|
| **Total** |**655 /597**|**2444254**|**95032**|**2360656**|**83598**|

All1252 calls have known usage in every displayed field; costs include the broker-failed trajectory's prior calls. Logical repeated prefixes are not unique tokens or GPU time. Collection times are358.917s,373.530s and261.196s. Training takes53.699s and53.752s, with11.187GB peak allocated per trainer. Accepted operation elapsed1258.628s, exit0/no timeout; all three owned-release records confirm identities exited/ports free, and the outer EXIT reports no GPU processes. Independent analysis is outside GPU ownership.

Only one coordinate is jointly correct between the trained arms; both use3 calls,5982 input and1279 output tokens there. Each trained-versus-control contrast has zero jointly correct coordinates. This selected-cost diagnostic cannot support a general efficiency claim. On all planned tasks the trained packages cost1.88× and2.128× the control's physical calls while scoring worse.

## Decision and limits

Do not promote either fixed4 adapter or infer a filter-first effect. At this dose, the authored-initial-action package increases exhaustive classification and leaves scope/terminal behavior weak. Before increasing the same dose, prioritize the already-motivated prospectively selected new query-context readout; two repeatedly reused32-record query contexts and four total clusters cannot establish broad transfer. A later executed-reduction API can target missing reduction/key/value handling, but cannot repair child-label disagreements and must not automatically submit or use gold. No evaluation-item-specific retraining is justified.

The384 training,320 evaluation and192 unused-validation normalized groups remain disjoint locally; evaluation compositions and helper/source data are exposed to this research, and base-model pretraining exposure is unknown. Reused source data, deterministic full-batch training, phase order and a single training dose limit interpretation. AUDIT retains the unchanged original projection; NATIVE_ENDPOINTS provides the availability-safe outcomes, tight bounds, final observation evidence and exact raw hashes. Three focused endpoint/bounds fixtures pass; no generated code, model, GPU, service, process signal or accepted source was executed or changed by this audit.
