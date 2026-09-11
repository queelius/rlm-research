# Additive correction: dose24 success semantics

The original **29/48 strict successes remain unchanged**, but “all 29 faithfully reduced the requested scope” was too strong. Manual reading of every selected root program and actual execution observation supports this narrower accounting:

| Among the 29 strict successes | Endpoints |
|---|---:|
| Requested operator, scope and target applied to actual child-label state, with executed scalar linked to final | 26 |
| Wrong user scope, coincidentally unchanged answer | 2 |
| Literal-ID recovery after repeated map overwrite/errors | 1 |

The 26 genuine requested computations comprise 10 counts, 8 distinct-user counts and 8 weight sums; 25 have nonzero gold. No wrong-operator or wrong-target coincidence was found among these 29. This is still substantial evidence for these disclosed primitive tasks, but not evidence that every correct answer followed the requested algorithm, nor that multi-batch accumulation is robust.

## Exact exceptions

- **Weight-all, dose-new-03**, coordinate `4fdc473558c541297b840c1af29d47215a2bc68341a664a52feb087ae68ccdf2`: successful program at node 7 restricts users to `u1,u2,u3`, omitting actual user `u0`; node 8 displays 11, final `Answer: 11`. Both actual predicted labels and dataset labels happen to contain no qualifying numeric record for the omitted user. The scope is wrong even though the number is right.
- **Distinct-all, dose-new-03**, coordinate `69c9e873fbff9591a10c329346e1349e1ab1f8120b4f4e5ea50a9ad2bacbdc6e`: node 7 restricts to `u0,u1,u2`, omitting `u3`; node 8 displays 2, final `Answer: 2`. Again the omitted user has no qualifying numeric record. These two coincidences share one context.
- **Count-single, dose-new-02**, coordinate `9e78771ad2f31a2a3ddfb7ca74dc36eaedf6c37b9991dc4ebe255ec5493d992e`: four genuine four-record acquisitions repeatedly overwrite `child_answer`. Six later full-map lookups fail with `KeyError`. The successful node 41 counts literal ID `q163b38602a81` within user `u3`, producing 1 at node 42 and final `Answer: 1`. The literal is supported by earlier observations, but the actual successful computation does not accumulate or consume a complete live map. A host union of the four earlier child maps would hide this failure.

Two other all-scope programs include nonexistent extra user names, while covering every actual `u0`–`u3` record; these are extensionally correct for the declared record universe. One successful program validates child-map IDs against a literal expected-ID list before correctly reducing live labels: ID validation alone is not literal-label recovery.

## Five leaf-error diagnoses confirmed, with dependence

All five previously identified wrong endpoints actually execute the requested operator, target and scope against the observed child labels. Their wrong answers remain attributable to relevant child-label errors for those executed operations:

| Coordinate prefix | Task | Dataset → final | Relevant source error |
|---|---|---|---|
| `4eb9827e1d` | dose-new-01 weight, user u0, entity | 0 → 7 | `q486ae6d0386e`: description/abstract → entity |
| `a7906cfee9` | dose-new-01 distinct, user u0, entity | 0 → 1 | Same record/category error |
| `c916dfe204` | dose-new-01 count, all, entity | 2 → 3 | Same record/category error |
| `fd9979513d` | dose-new-01 count, users u0/u3, entity | 0 → 1 | Same record/category error |
| `2f7086a34a` | dose-new-00 distinct, all, human | 2 → 1 | `q11ae4a9dd132`: human → location |

Thus these are five affected endpoints, **two contexts and two relevant repeated source errors**, not five independent semantic failures. Their source-error explanation is a diagnostic counterfactual, not a repaired model score.

## Evidence and limits

[REVIEW.json](../../../../ARTIFACTS.md#unpublished-files "Not published: REVIEW.json") contains all 34 complete coordinate IDs, exact questions, sampled root programs, actual tool observations and parent links, actual child maps, label differences, classifications and absolute raw directories. [SOURCE_PINS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCE_PINS.json") pins every file in those 34 raw endpoint directories and the original analysis/input evidence. EPISODE/RESULT hashes match the prior sealed native audit. Every reported final scalar is tied to the actual successful program's observation, not merely a matching integer elsewhere in the trace. No sampled program was reexecuted.

This outcome-aware review corrects interpretation only: original scores, native availability, attempted-failure taxonomy and physical costs are untouched. It relies on the prior sealed native-final authentication rather than duplicating the entire training/transport audit. The reviewer authored the continuation/readout implementation but not the prior independent dataflow audit; independence here is from that analysis, not experiment authorship. Other endpoints are outside this bounded review.

The inferential correction is therefore **26 verified requested live-label computations, two scope coincidences, one literal recovery**, not retirement of the observed answer improvement. Future mechanism reports should classify actual operator/scope/target and state lineage before calling scalar agreement faithful computation.
