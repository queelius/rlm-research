# Query failures are concentrated, not a demonstrated final-copying bug

**Fifteen of the 32 query trajectories contain the same relevant dataset-label disagreement:** q0009, “What's the highest possible bid in Contract Bridge?”, is ENTY in the frozen TREC labels but “numeric value” in the fixed c32 child's returned map. Fourteen programs correctly count those returned labels, display 2 or 3, and faithfully submit that number. The other case displays the wrong-label map and answers with prose. This is disagreement with the frozen dataset—not independent adjudication that the child's semantic interpretation is wrong. Do not train on or remove this evaluation item based on this finding.

All eight query coordinates from each arm were examined: high-LR low/high and bounded-RL before/after. They reuse only **two 32-record contexts, four context-query definitions and three distinct root weights**; the low-SFT66c baseline appears in both studies with different seeds. Four correct trajectories and 28 frozen-primary failures are therefore not 32 independent tasks or a broad estimate of query generalization. Local fine-tuning split independence, exposed research/helper data and unknown base-pretraining exposure remain distinct.

## Complete 32-case taxonomy

| Recorded failure or success path | Cases |
|---|---:|
| Correctly reduced scoped child labels, with the q0009 dataset disagreement | 14 |
| Same disagreement plus a nonconforming prose final | 1 |
| Dictionary-key/value corruption in the reduction program | 1 |
| Correct complete scoped map, but no executed count; root manually answers 7/8 instead of 6 | 6 |
| Unfiltered full map returned; required metadata join not executed | 1 |
| Query work remains incomplete, followed by an observed prose final | 4 |
| Broker failure: no sampled final answer | 1 |
| Correct computed scalar and correct final answer | 4 |
| **Total** | **32** |

**All 19 displayed integer scalars are copied faithfully into the final answer. There are zero demonstrated correct-scalar/wrong-restatement cases.** Twenty-seven trajectories obtain complete relevant child-map coverage; the others stop with insufficient query evidence or the broker error. Requesting extra records is sometimes wasteful but does not itself imply wrong query scope. Sixteen recoverable Python error observations occur, commonly using the nonexistent key `"synthetic user metadata"` before inspecting a record and switching to `"user"`.

## Concrete boundaries

In high-LR seed981314201, the actual eight-record user subset contains q0009. The child's map gives two numeric labels; the code computes that count, tool node14 displays `2`, and final node15 says `Answer: 2`. Gold is1. The root's scope, reduction and copying are correct relative to the returned labels. [Raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-sft-lr-v1/outputs/attempt-001/high/rollout/episodes/e5f96bbaea4f57b99118c58fa0ea721e3dab1aba360ad66c43ea636f61086295.json"), SHA `6fc88678…`.

In high-LR seed981314207, code filters the correct two users, calls the child and ends with `print(labels)`. Tool node6 displays the complete supported 16-ID map containing six human labels. It does **not** display a computed count. Final node7 says `Answer: 8`. The same structural failure occurs in the other high-LR repeat and four bounded-RL before/after trajectories, which say7. This is missing executable reduction/manual map counting, not a proven restatement failure after correct computation. [Raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-sft-lr-v1/outputs/attempt-001/high/rollout/episodes/2dd7219477e6a950f850923cb24e508909260a81fec54d0994df8bedd15d8920.json"), SHA `7f652ce9…`.

Low-LR seed981314205 obtains usable labels but builds `dict(zip(ids, labels))`: iterating a dict supplies its keys, not category values. Its subsequent comparison with `'human being'` yields0; tool node15 displays0 and the root copies0. This is a program/data-structure mistake. [Raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-sft-lr-v1/outputs/attempt-001/low/rollout/episodes/362e36aa0413997666a51622e6a9ca7f953079d50a1bbf04ae371421da0207a9.json"), SHA `d6562376…`.

Bounded-RL-after seed981316513 returns all32 labels, then claims user metadata is unavailable instead of executing the remaining file-backed user join. The map alone does not display each ID's user, although that metadata remains accessible in records.json. Do not claim the root visibly saw and ignored the complete joined answer. [Raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/outputs/attempt-001/readout-after/rollout/episodes/377c4f50f5e91611b0838a5b54c8b35f5d1c5f7a6b224b9bb2b2ebbe35a2fb43.json"), SHA `300c71d4…`.

All32 final physical branches match captured native prompt-plus-completion IDs. Child availability, REPL data access and model-visible tool observations are nevertheless different evidential boundaries. No transport defect explains the six map-only counting cases. No sampled code was executed during this analysis.

## Additive availability correction

High-LR-low seed981314206 has trace `ok=false`, `stop_condition=error`, with IPython `set_broker_scope → _execute_silent → get_shell_msg(timeout=30) → _queue.Empty`. Its last native root response requests a tool; the empty root reply is not a sampled final. Preserve the old sealed primary0, but treat this case as unavailable in an explicitly separate sensitivity. The historical high-LR report's blanket “no fatal episode failure” statement does not hold for this raw case. Its matched high endpoint is correct; the query contrast's availability-safe net bounds are [-1,0], rather than treating the observed 2/8→2/8 totals as complete behavioral parity. [Raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-sft-lr-v1/outputs/attempt-001/low/rollout/episodes/43630b2c3981ca89e91b1a3848c9f45fecc39811175528a4208fa572186d45b1.json"), SHA `6b361e8a…`. No original report, score or admission was edited.

## Ranked smallest followups — proposals only

1. **New query-context readout first.** Prospectively hash-select four new 32-record context groups, freeze one single-user and one two-user-union query per group and two fresh seeds:16 coordinates, paired low66c versus fixed high0ba roots, c32 child unchanged,32 episodes. Select groups without inspecting model labels/answers and without excluding q0009 because of this result. Authenticate remaining normalized-group headroom first; if only new compositions are available, disclose source reuse rather than claim unseen questions. Report context-cluster strict outcomes, actual scoped-map target FP/FN and coverage alongside costs. This tests whether the apparent query bottleneck persists beyond the two repeatedly exposed groups; it is not independent training replication. A bounded 15–20-minute single-A100 envelope is a prospective cap, not measured throughput.

2. **Executed reduction support, not computed-finalization, if still needed after the already-running plan-SFT study.** On the same prospectively frozen new coordinates, hold high0ba/c32 weights fixed and compare current map API against an additive pure-REPL reducer such as `count_labels(map, requested_ids, target)`. Validate exact keys/category values, compute only from the actual supplied map and publicly selected IDs, return the scalar, and leave strict final submission to the model. No gold access, repaired labels, automatic submission or forced recursion. Two conditions×16 coordinates=32 live episodes; paired seeds are not full-state replay. This is an API-plus-instruction package, not pure arithmetic ability. It should address missing reduction/key-value misuse but cannot correct q0009-like child-label disagreement. Use all planned outcomes and physical costs; do not condition the primary on correct maps after generation.

Neither proposal targets an evaluation item for memorization. Changing only a training seed in a deterministic full-corpus/dropout-zero loop would not meaningfully replicate these learned policies; new independently frozen data/compositions are the more informative first check.

TAXONOMY.json provides every coordinate, category, native request/node, final availability, scalar/map evidence and raw hash. PROJECTION_ORDERED authenticates raw branch evidence and code text; its earlier unordered child-list projection is retained, with ordering corrected before assigning the taxonomy. METHOD declares this posthoc scope. Prior reports/manifests remain linked and unchanged; no active plan-SFT outcomes, GPU, service, network or queue changes were used.
