# Fresh-composition96: acquisition transfers more than query-sensitive reduction

Independent audit of the original completed/released attempt. **SFT24 scores9/48 planned versus SFT6 6/48, but only2 versus0 are conservatively task-faithful correct observed reductions. Neither policy demonstrates a faithful composed success.** SFT24's four correct composed answers arise from wrong-operator coincidences. Substantial NULLs prevent a broad efficacy claim.

Auditor did not author this study; prior common native/runtime/operator plumbing contributions are disclosed. Prelaunch METHOD/PARSER were frozen before science; MAIN authorized outcomes only after terminal. CPU source/oracle review independently enumerated128 records/48 truths. Source novelty is only under the named refreshed root inventory, not child-training, catalog or pretraining novelty. Fixed SFT24 first, then SFT6; same48 tasks/seeds, eight contexts, six families. No checkpoint selection, output repair, rerun, gold map replacement or sampled-code reexecution occurred.

## Primary outcomes

Entries are correct / planned; available and NULL are distinct. Bounds permit any missing endpoint outcome, not an imputed accuracy.

| Panel | SFT6 correct; available; NULL; bounds | SFT24 correct; available; NULL; bounds |
| --- | --- | --- |
| All | 6/48;31;17;[6,23]/48 | 9/48;28;20;[9,29]/48 |
| Primitive | 3/24;10;14;[3,17]/24 | 5/24;12;12;[5,17]/24 |
| Composition | 3/24;21;3;[3,6]/24 | 4/24;16;8;[4,12]/24 |
| Nonzero | 1/41;25;16;[1,17]/41 | 6/41;25;16;[6,22]/41 |
| Zero | 5/7;6;1;[5,6]/7 | 3/7;3;4;[3,7]/7 |

Available-only accuracy19.35% versus32.14% is selection-conditional. Operational lower bounds12.50% versus18.75% are not no-NULL accuracy. Planned SFT24−SFT6 difference bounds: all[−14,+23]/48; primitive[−12,+14]/24; composition[−2,+9]/24. Of21 jointly available task pairs,4 favor24,1 favors6,3 both correct and13 both incorrect. Remaining pairs:2 (NULL6,correct24),2 (correct6,NULL24),5 (NULL6,wrong24),8 (wrong6,NULL24),10 both NULL. Do not treat48 tasks as independent replicates.

| Family, planned8/policy | SFT6 correct / NULL | SFT24 correct / NULL |
| --- | --- | --- |
| Count | 1 /5 | 2 /3 |
| Distinct users | 2 /2 | 2 /3 |
| Weight sum | 0 /7 | 1 /6 |
| Users above threshold | 2 /0 | 1 /1 |
| Maximum user weight | 1 /3 | 2 /3 |
| Conditional weight | 0 /0 | 1 /4 |

All eight context means are retained below. Each primitive/composition entry is `correct+NULL` out of3, so its mean interval is `[correct,correct+NULL]/3. Δ is the operational correct-count difference divided by3; AUDIT.json retains each exact interval.

| Context | Primitive6→24 | Primitive Δ bounds (counts/3) | Composition6→24 | Composition Δ bounds (counts/3) |
| --- | --- | --- | --- | --- |
| 00 | 0+2 →0+3 | [−2,3] | 0+1 →0+1 | [−1,1] |
| 01 | 0+3 →0+3 | [−3,3] | 0+0 →0+0 | [0,0] |
| 02 | 0+1 →0+1 | [−1,1] | 0+0 →0+2 | [0,2] |
| 03 | 1+2 →2+0 | [−1,1] | 0+0 →1+0 | [1,1] |
| 04 | 0+1 →1+1 | [0,2] | 0+1 →0+1 | [−1,1] |
| 05 | 0+3 →0+0 | [−3,0] | 1+1 →0+2 | [−2,1] |
| 06 | 2+1 →1+2 | [−2,1] | 2+0 →2+1 | [0,1] |
| 07 | 0+1 →1+2 | [0,3] | 0+0 →1+1 | [1,2] |

Primitive operational means improve in3/8 contexts, decline1, tie4—not the prospective6/8 heuristic. Composition improves2, declines1, ties5. Neither prospective promotion heuristic is met, and no faithful nonzero composed success exists.

## Actual mechanisms, separate from primary scores

Post-outcome manual annotations cover **all59 available endpoints**, including all15 successes and all37 available composed endpoints. `MECHANISMS.json` links exact episode hashes/nodes and raw child files. Automatic extraction did not assign execution from keywords. Nested child programs can appear in the same graph and are not automatically attributed to root. Conservative faithfulness requires the declared operator, target and all-scope, not a simpler operation that happens to agree on these records.

| Observed category | Primitive6 | Primitive24 | Composition6 | Composition24 |
| --- | --- | --- | --- | --- |
| Correct, faithful observed semantic reduction | 0 | 2 | 0 | 0 |
| Correct, wrong operator | 0 | 2 | 0 | 4 |
| Correct, wrong scope | 0 | 1 | 0 | 0 |
| Correct, invalid semantic proxy/fallback | 3 | 0 | 3 | 0 |
| Wrong, faithful reduction with child semantic error | 0 | 1 | 0 | 0 |
| Remaining available incorrect | 7 | 6 | 18 | 12 |
| Primary NULL, mechanism not promoted | 14 | 12 | 3 | 8 |

Faithful-correct planned bounds from unresolved NULLs are primitive6[0,14]/24, primitive24[2,14]/24; composition6[0,3]/24, composition24[0,8]/24. These bounds do not erase already observed wrong mechanisms. More permissive on-this-state interpretation could regard omitted users with no target matches as harmless; that is **not** the conservative table definition.

Concrete traces (indices refer to frozen AUDIT rows):

- SFT24 rows9/11, context03 count/weight: one authenticated16-ID child map → live map indexing over all actual users → observed2/10 → matching native final. These are the two nonzero faithful successes, both one context and one acquisition, not multi-call accumulation.
- SFT24 row32, context04 count: one actual map contains four semantic label errors; the faithful all-user count returns2 versus dataset3. The missed relevant label includes `q8c254c5250d0` (“Who is the Incredible Hulk in reality?”). This is an unambiguous child-error failure, not evidence-use failure.
- SFT24 row7, context03 maximum: `sum(weight)` over all target records prints10; the true per-user maximum also happens to be10. Rows21/22 repeat pooled sum for threshold/max and succeed only at zero. Row46 sums B weights without constructing A-users and happens to return2. **All four correct composed endpoints fail the intended operator test.** All16 available SFT24 composed endpoints show pooled/simple wrong reductions, Boolean threshold misuse or erroneous user-key repair; none faithfully computes the declared composition.
- SFT24 rows33/42 count matching records instead of distinct users; row42 also omitsu0. Row18's zero count omitsu0/inventsu4 despite all-scope. Do not promote those three primary successes to task-faithful competence.
- SFT6 row58, its only nonzero success, treats `weight==1` as numeric category and coincidentally finds one user. Other successes use category-word substring tests, compare record text with the aggregate query, or ultimately fallback0 after missing-column errors. No SFT6 success uses actual child semantic acquisition.
- Partial-state example row38: real1/15-ID calls assign the same variable twice, losing the first map; later scope exclusions avoid its missing key, then count records instead of distinct users. Row39 reacquires a selected subset twice, fixes a Boolean-key typo, but preserves wrong scope. These are not authenticated faithful accumulation or pure child-error cases.

Actual supplied-map diagnostics are available for26 SFT24 endpoints with exactly one complete, authenticated16-ID map also seen in the root observation. Only11 finals agree with the correctly evaluated query on that map: all9 primary successes plus rows32/37. Agreement still includes wrong-operator coincidences. Four of16 composed finals agree with observed-map truth, all four by wrong-operator coincidence. Multiple-call/overwritten or non-map episodes are not assigned a convenient union. Semantic child errors remain uncorrected.

## Native availability, failures and costs

All96 planned rows independently rescored, **zero producer-score/availability disagreements**. Existing RESULT count39/46 differs from native availability28/31. Missing RESULT9/2 remains primary NULL; all11 have episode-timeout FAILURE receipts (~181–182s). No missing-RESULT authentic-final diagnostic was found. Other source-unavailable endpoints: SFT24 five length-ended no-finals, five stop-ended no-finals, one unresolved tool/internal harness error; SFT6 fourteen length-ended no-finals, one stop-ended no-final. These are not turned into strict0. Two authenticated malformed finals—SFT24 `Answer: False`, SFT6 `Answer: numeric value`—remain strict0. All59 admitted finals finish_reason=stop.

Failure examples: SFT24 repeatedly decodes genuine child IDs against invented `record0..2` (16 actual calls; eventual kernel internal error); invents `user_16` and slices maps by nonexistent matches; overwrites maps then repeats KeyErrors; reads NDJSON context via `json.load` repeatedly. SFT6 repeatedly calls a child but iterates the returned string as a list of dictionaries. These distinguish acquisition, state decoding, wrong operator and finishing failures; no blanket hardware explanation is established.

| Policy | Physical root/child | Returned | Known input / output / cached tokens | Calls with unknown usage |
| --- | --- | --- | --- | --- |
| SFT24 | 631 /233 =864 | 855 | 2,741,070 /60,489 /2,639,312 | 9 |
| SFT6 | 184 /35 =219 | 217 | 612,589 /78,761 /577,296 | 2 |
| Total | 815 /268 =1083 | 1072 | 3,353,659 /139,250 /3,216,608 | 11 |

Every returned call's actual model/adapter and prompt/completion token correspondence independently agrees with its matching role record:1072 returns, zero integrity errors. All268 child calls returned;35 child calls under SFT6 are concentrated in failed/wrong routes, so “SFT6 never calls children” would be false. No extra/unplanned physical directory, unmatched role intent or orphan confirmed attempt was found. NULL endpoints consume735/864 SFT24 calls and119/219 SFT6 calls. Serialized native inputs across all attempts total3,444,884 tokens; this is distinct from known provider usage. Unknown usage/cache is not zero; provider billing/FLOPs are unknown. Historical training costs are not new evaluation inference.

OWNER_TERMINAL SHA `f417fef594991ea142a4ba6344362e4877fc91bcbf225b1901ca1a22627270b1`: complete/released, no active service/error,1460.942931s. Parent exact EXIT0,1461.430546s, not timed out, empty GPU process inventory. Both SERVICE_STOPPED receipts assert owned identities exited/ports free. Method sources,6501 scientific files, parent closure and final analyses are pinned by FINAL_SEAL.

## Queue implications

Do not promote9/48 as nine faithful solutions, composition transfer, or a reason for blind dose extension. The strongest supported change is increased real acquisition plus a narrow learned count/weight routine, with query/operator binding failures and costly loops. A small matched public task-spec versus prose-control experiment is now justified by observed operator substitutions; no authored algorithm/map/answer should be supplied. It must remain separate from any warm-start RL job. Scale-state remains a separately approved question about actual multi-acquisition retention; this panel's successful traces do not demonstrate that mechanism. Serial policy order, eight context clusters, reused child/catalog exposure and adaptive exploratory decisions limit causal/general claims.
