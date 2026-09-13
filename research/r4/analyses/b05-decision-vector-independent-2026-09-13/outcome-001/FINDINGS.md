# Decision vector: shorter output, lower complete-set accuracy

The [independent native/public audit](REPORT.json) passes with **zero issues**. All48 calls returned known, normally stopped responses from the frozen released4B model with no adapter; actual prefixes, sampling/seeds, canonical/raw response hashes, completion IDs/logprobs/decoding and grades match. All12 newly generated public cases and130 candidate records/order were checked. No output was executed, repaired, padded or regraded permissively.

Primary unordered exact is **list16/24 → vector10/24**: **3 wins,9 losses,7 both correct,5 both wrong**. All24 planned attempts per arm remain in the denominator. List has24 valid ID sets; vector has21 valid arrays and3 known-invalid arrays, with no missing/unknown calls. The wins occur in3 contexts and losses in5 contexts; there are12 independent stage contexts, not24 independent tasks.

**All nine exact losses occur on valid full-length vectors.** The three invalid arrays are cases where the paired list answer was already wrong. Even excluding invalid vectors from both arms, exact remains list16/21 versus vector10/21. Array-length repair alone would not explain away the primary reversal.

## Matched validity, not a misleading conditional comparison

| On the same21 valid pairs | List | Vector |
|---|---:|---:|
| TP / FP / FN / TN | 142 /9 /2 /47 | 132 /5 /12 /51 |
| Mean per-set BA (21 sets) | .89187 | .90185 |
| Micro precision | 142/151=.9404 | 132/137=.9635 |
| Micro recall | 142/144=.9861 | 132/144=.9167 |
| Unordered exact | 16/21 | 10/21 |

The vector is somewhat more conservative: fewer false positives, substantially more missed eligible candidates, and lower complete-set accuracy. Macro BA gains about.010 on the matched population because it weights positive/negative recall within each stage; it is not equivalent to minimizing total candidate errors. Comparing unmatched list BA.85156 (24 sets) against vector BA.90185 (21 sets) exaggerates the apparent benefit.

All list answers are unsorted (strict sorted validity0/24); vector strict literal validity is21/24 and strict exact10/24. These are different output contracts. The improvement in strict-format counts must not be called a semantic gain.

## Array shape and position errors

All3 invalid outputs are width20 arrays containing **19 literal booleans**, ending with a normal stop—not token-cap truncation. Two come from `root_0209b2184b6d5d`, one from `root_97d18be3bd06ec`. Their selected-ID set and per-candidate rewards remain None.

An explicitly label-informed, inert diagnostic asks whether deleting one position from the true20-bit sequence could explain each19-bit reply. Even the best such alignment leaves **3,3,6 mismatches** respectively. Thus a single omitted slot is insufficient to explain their contents. This diagnostic never inserts a bit, chooses a corrected mapping or changes a score.

For valid arrays, every error is evaluated at the mandated public position. Across the21 arrays there are12 false-negative and5 false-positive positions; all5 false-positive selections violate explicit latest-check requirements. One two-bit error is compatible with swapping adjacent true/false positions, but the response does not reveal whether the model confused order or misapplied policy. Do not infer hidden intent from a convenient alignment. The exact vectors at width12 and one width20 show the interface can work, but neither shape nor decision reliability is assured.

## All12 case outcomes

Full positions, public facts, raw hashes and two-seed contrasts are in [MECHANISM_REVIEW.json](../../../../../ARTIFACTS.md) and [SUMMARY.json](SUMMARY.json). Counts below are exact answers out of two seeds; positions are zero-based.

| Context suffix | History / width | List → vector | Observed vector mechanism |
|---|---:|---:|---|
| `076e66142e5aa6` | 1 /6 | 2→2 | Both arrays fully correct. |
| `39c786d6900b9c` | 1 /6 | 0→1 | Seed0 correct; seed1 selects failed-check position1 and omits eligible position2. |
| `028de76a4236cf` | 1 /12 | 2→2 | Both arrays fully correct. |
| `5fceb69e86a64c` | 1 /12 | 2→0 | Misses eligible position1 versus5; same aggregate reward, different local errors. |
| `0209b2184b6d5d` | 1 /20 | 0→0 | Both arrays19/20; invalid, no positional scoring/repair. |
| `97d18be3bd06ec` | 1 /20 | 0→1 | Seed0 correct20-bit array; seed1 invalid19-bit array. |
| `50f0503c7defa6` | 3 /6 | 2→2 | Both arrays fully correct. |
| `61b96937cee04f` | 3 /6 | 2→1 | Seed1 omits eligible position2. |
| `1ce4825b3d609c` | 3 /6 | 2→0 | Both seeds omit eligible position4. |
| `ea27d8014b1fa4` | 3 /12 | 2→0 | Both select failed-schema positions1/9 and omit eligible8; seed0 additionally omits10. |
| `d7692972a0cc5e` | 3 /12 | 0→1 | Seed0 correct; seed1 omits eligible position11. |
| `de0b8639ce91c6` | 3 /12 | 2→0 | Both seeds omit eligible position1. |

History subsets use different new instances; their differences are not a causal history effect. Earlier normalization scores are kept separate: the fresh list16 here is not a paired improvement over the prior panel's9.

## Costs and potential G2 signal

Natural cost is one call per answer for both arms,48 physical calls. Observed input tokens are list48,994 versus vector49,800; completion tokens **3,403 →505** (85.2% fewer), with per-call ranges73–316 versus11–70 under the same384 cap. Total tokens are **52,397 →50,305**, only4.0% fewer because input dominates. All usage fields are known; owner elapsed102.192s, qualified/released. These are different interfaces and actual output lengths, not token-cost-matched conditions.

For potential RL diagnostics, compare the two sampled answers within each arm/context, only when **both full outputs are valid**:

- List:12 qualified G2 contexts,130 candidate pairs; one context has2 changed candidate decisions, one has nonzero BA contrast, none has exact-reward contrast.
- Vector:10 qualified contexts,90 candidate pairs; five contexts have **7 changed candidate decisions**, four have nonzero BA contrast, three have exact-reward contrast. The7 changed positions would give14 signed local correctness contrasts across the two actions, out of180 candidate-action positions. Two wide contexts are excluded from local-credit diagnostics because at least one vector is invalid; their primary results remain retained.
- `5fceb69e86a64c` illustrates possible local signal hidden by aggregate reward: two different omissions produce opposite candidate correctness contrasts while BA and exact both tie. Several other errors repeat identically across both seeds and offer no G2 contrast.

This is sparse diagnostic signal, not training admission or proof of usable token credit. No boolean-token span mapping, loss, gradient, optimizer or training runner was implemented. The vector should **not be promoted as a better complete-answer interface** on this evidence. Any later RL proposal must explicitly trade its worse complete-set accuracy/shape reliability against compact actions and local credit, and qualify actual token spans independently. No new GPU code or experiment is prepared here.

Evidence SHA: REPORT `bfef2172748fa03da11ceda764f05f44ba9b40dba27ec746449c1c94ad1a6fe8`; SUMMARY `bb8d717d047d8fe4ef00129a26f8ab0676ef918d92a38e1a5e84afaf0c84ceb3`; mechanism `ea4fbfd6592ad2a4f4f18545b9b755e9359fac29bd4bd9cd0b0c0aa737a6bdbe`. All source/call bindings remain linked in these artifacts; original science metrics are unchanged.
