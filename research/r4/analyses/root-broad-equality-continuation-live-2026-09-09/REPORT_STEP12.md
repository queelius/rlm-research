# BROAD equality continuation: independent checkpoint12 audit

September 9, 2026. Interim only. Fixed final16 remains the primary endpoint; no checkpoint13–16 or final/transfer outcomes were read. The checkpoint8 publication remains unchanged. This audit performed no GPU/model calls, lifecycle actions, source changes or generated-code execution.

## Salient result

Validation12 has **8/16 strict correct answers**, all16 terminal-observable and graph-verified;14/16 satisfy the final-answer schema. The repeated validation trajectory is original5/16 → checkpoint4 4/16 → checkpoint8 9/16 → checkpoint12 8/16. This remains above original but is not monotonic improvement and does not justify intermediate checkpoint selection.

On the same16 coordinates, checkpoint12 versus original has four gains, one loss and eleven ties. The admitted comparison retains15 complete pairs because the original graph exclusion remains unchanged: four gains, one loss, ten ties, one null pair. Versus checkpoint8, all16 pairs are admitted: two gains, three losses, eleven ties. These are eight repeated context groups with two nested seeds each, not independent new test tasks.

| Validation subset | Original | Checkpoint8 | Checkpoint12 |
|---|---:|---:|---:|
| All | 5/16 | 9/16 | 8/16 |
| 32 records | 1/8 | 5/8 | 4/8 |
| 64 records | 4/8 | 4/8 | 4/8 |
| HUM | 2/4 | 2/4 | 2/4 |
| NUM | 1/4 | 1/4 | 1/4 |
| ENTY | 1/4 | 2/4 | 2/4 |
| LOC | 1/4 | 4/4 | 3/4 |

Per-context successes in HUM/NUM/ENTY/LOC order are1/2,0/2,2/2,1/2 for32 records and1/2,1/2,0/2,2/2 for64 records. The two schema-invalid validation outputs are observed strict failures, not nulls: a NUM32 prose response about fixing code and an empty LOC32 response with one truncated call. No response repair or broader semantic diagnosis was performed.

## New training coverage and gradient support

| Round | Correct/planned | Observable; graph-valid | Schema-valid | Selected mixed rows | Homogeneous valid, unselected |
|---|---:|---:|---:|---:|---|
| 9 | 11/24 | 23;23 | 23 | 7 | 8 all-one;8 all-zero |
| 10 | 20/24 | 24;24 | 24 | 8 | 16 all-one |
| 11 | 19/24 | 24;24 | 24 | 16 | 8 all-one |
| 12 | 14/24 | 24;24 | 22 | 24 | 0 |

Across96 new attempts:64 correct answers,95 graph-valid/admitted rows,55 selected mixed-group episodes,40 valid homogeneous unselected episodes and one setup null. The40 homogeneous rows are32 all-one and8 all-zero; these are not trace failures. Round12's two schema-invalid but complete/graph-valid empty outputs are observed zero-reward rows under the unchanged contract.

Round9 uses only seven admitted LOC64 rows (3 correct); NUM16 is8/8 and ENTY32 is0/8, yielding no group-relative credit. Round10 uses only HUM64 (4/8); its two smaller groups are8/8. Support then broadens again: round11 selects LOC16 (6/8) and HUM32 (5/8), while NUM64 is8/8; round12 selects all three groups, HUM16 5/8, NUM32 6/8 and ENTY64 3/8. Task/target rotation means these round totals are not a fixed-task learning curve.

## The null is an installer failure, not a policy failure

Round9 episode `9657f9ca8f0c7f31495a2f99dbf1888605cacaa57f9e3ce942999948c71ebb38`, training-064-00:location, seed1492531148, failed during harness setup before any model call. Its retained HarnessError identifies a timeout fetching `lxml-6.1.3-cp311-cp311-manylinux_2_26_x86_64.manylinux_2_28_x86_64.whl.metadata` from files.pythonhosted.org. The error text reports126.1 seconds; episode wall time is137.699 seconds. No native calls, root reply, truncation or budget censoring were recorded. The row remains null/unselected; it is neither a sampled wrong answer nor a broadened overflow exclusion.

`STEP12_INSTALLER_NULL_EVIDENCE.json` preserves the exact traceback/URL, raw SHA `ea464f41bbc30f2e016db9be963efa62ccb5c609665fa543ca654bdcb5ae742e`, recorded nano version4ef3438, and the installer command reconstructed from the pinned executed harness. Harness SHA `7256f1efe1d0b44c8488e62edc93c41fa2da1fae95620bc6de4dea2e7d517bfc` matches the prior sealed source audit. The harness's install.lock is a concurrency lock, not a dependency lock. The exact failed-install uv version and resolved dependency lock are unrecorded/null; a source-derived command is not misrepresented as an independently captured shell request. No installation, retry or cache mutation was attempted.

## Actual updates and credit checks

| Actual Adam step | Selected episodes | Root turns | Root action tokens | Consecutive adapter L2 delta |
|---|---:|---:|---:|---:|
| 9 | 7 | 14 | 2,886 | 0.07903387464822538 |
| 10 | 8 | 16 | 3,300 | 0.07273433621951274 |
| 11 | 16 | 32 | 6,930 | 0.07396878701482903 |
| 12 | 24 | 56 | 16,671 | 0.07809110883958706 |

The step8 adapter anchor was loaded once; only the four new optimizer/adapter states were loaded. All504 actual Adam parameter cursors equal their respective step, optimizer tensors are finite, and all504 adapter tensors change per update with independently measured deltas matching saved metrics. Parameter ordering, preceding-policy/optimizer/RNG links, exact adapter-load equality and COMMIT/state/INPUTS/export identities agree. Reported gradient norms are finite and positive. No optimizer restart, checkpoint recovery/reapplication or child model loading is indicated.

The55 selected episodes contribute118 root turns and29,787 root action tokens. Exact native action IDs/logprobs, root suffix labels/masks, equal-episode/equal-root-turn weighting and correction-capture bijections pass. Child and observation loss tokens remain zero; fixed childc32de is unchanged. These checks certify the declared credit/provenance contract, not semantic child correctness or faithful root computation.

All five correction guards were independently reconstructed and passed each update. Across steps9–12: mean absolute log ratio0.002932–0.005855; sampled k3 0.000301–0.000963; fraction outside[0.5,2]0–0.001010; removed IS mass0–0.00003993; token ESS fraction0.998122–0.999394. Exact values and bounds are in STEP12.json; these are sampled-action correction diagnostics, not entropy.

Checkpoint12 adapter SHA is `d3198db3af3bcd401d1ff25a309f002299ee0c60d4f546ad7c609c4e7d2d6a79`; optimizer SHA `1a8ec3bf60023b8d5f8750eab5e7e51c43ce42fb5d68eed7b49e2c4a19d82795`. Full policy/member identities are preserved in the machine audit.

## Cost of this delta

All1,208 retained physical requests returned:246 root and962 child. There are no request-only records, unassigned results, provider errors or missing token-usage fields in this delta. The setup null incurred wall time but no model tokens; it is not a zero-cost episode.

| Stage | Collection seconds | Requests root/child | Logical prompt | Cached | Completion |
|---|---:|---:|---:|---:|---:|
| Round9 | 203.416 | 54/185 | 242,593 | 232,736 | 16,147 |
| Round10 | 179.364 | 48/208 | 238,435 | 226,336 | 13,882 |
| Round11 | 183.477 | 49/204 | 236,668 | 223,216 | 14,426 |
| Round12 | 221.389 | 56/208 | 265,690 | 250,640 | 20,334 |
| Validation12 | 253.579 | 39/157 | 207,675 | 191,328 | 27,224 |
| Total | 1,041.226 | 246/962 | 1,191,061 | 1,124,256 | 92,013 |

Uncached prompts total66,805 tokens. Completion tokens split66,110 root and25,903 child. The four optimizer/checkpoint durations total90.924 seconds; collection plus update work totals1,132.150 seconds. These are stage work totals, not full campaign/allocation elapsed time, and omit service/interstage orchestration. Validation12 is slower than the sealed validation8 despite slightly fewer model calls; no uniform efficiency improvement is inferred. Cumulative campaign caps and the fixed final endpoint are unchanged.

## Verification and audit limitations

All five new stages had finalized STATUS/export files before scoring. The successful audit processed112 new episode records once, with2,612 cached immutable paths, five inherited hash reuses and five authenticated serving-log prefixes; maximum physical reads per immutable path within that invocation was one. No appended downstream log bytes were read and no old raw graphs were rescored. The audit passed83,174 assertions in14.266 seconds, exit0. Six focused pairing/null-projection tests pass; no broad tests or environment changes were made.

The initial audit invocation exited1 before publishing a stage or loading checkpoint tensors because its diagnostic projection indexed a missing root_reply field. The exact expression was reproduced in a regression (one failure, three passes), then an additive nullable wrapper was introduced; strict scoring/admission were not changed. That failed process's partial first-stage reads were necessarily repeated once. The single setup-null record was subsequently reopened for bounded error/installer evidence; other raw records and checkpoint tensors were not reopened. Original audit_step12.py, its pre-outcome method seal, the amendment and executed wrapper are all retained. This analysis failure is not an inference failure or rerun.

Artifacts: STEP12.json, STEP12_SOURCES.json, STEP12_SUMMARY.json, five STEP12_*_RAW.json projections, four STEP12_UPDATE_*.json snapshots, STEP12_INSTALLER_NULL_EVIDENCE.json, frozen method/amendment/test sources and STEP12_PUBLISHED.json. Integrated independently reconstructed guards are in STEP12.json; helper update snapshots preserve their earlier unaugmented fields.

Conclusion: training remains a genuine continuous root-only update chain, with mixed-group support broadening in rounds11–12. Development validation remains above original but below checkpoint8. Continue to the prespecified final16 comparison; the installer timeout motivates a separate bounded operational caching investigation, not live mutation or reward reclassification.
