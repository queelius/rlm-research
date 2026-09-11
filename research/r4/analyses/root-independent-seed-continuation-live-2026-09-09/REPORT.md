# Independent root-training seed: completed continuation audit

The selected root improved exact transfer answers from **9/24 to 15/24** (+25 percentage points): 11 paired gains, 5 regressions and 8 ties. All 48 transfer episodes were completed, observable and admitted; none was censored or excluded. This is a positive directional result under a second root-training seed on the same six exposed, leaf-training-supported contexts—not a precise replication estimate, new-task confirmation, or evidence about base-model pretraining contamination.

The selected policy is **step 6**, not the final step 8. Validation at steps 0/2/4/6/8 was 2/8, 2/8, 1/8, 3/8, 3/8; the frozen earliest-maximum rule correctly selects step 6. Thus the evaluated gain cannot be attributed to the two extra continuation updates.

## Pairing and heterogeneity

Both conditions used the frozen task/context/prompt bytes and matched seeds with fixed child `c32de…`. The selected condition followed original in a separate owned service: service/order effects and seed-insensitive trajectory variation remain limitations. Four context clusters improved, one tied and one worsened; repeated task/seed outcomes are nested within these six clusters, not 24 independent samples.

| Context window | Original | Selected step 6 | Paired change |
|---|---:|---:|---:|
| 1200 | 1/4 | 3/4 | +2 |
| 1201 | 2/4 | 2/4 | 0 |
| 1202 | 1/4 | 4/4 | +3 |
| 1203 | 2/4 | 3/4 | +1 |
| 1204 | 0/4 | 2/4 | +2 |
| 1205 | 3/4 | 1/4 | −2 |

This verifies final-count success, not complete semantic label maps, faithful use of every child answer, or a particular decomposition mechanism. No generated code was executed by this audit. A fresh-seed paired replay of original versus the fixed selected step 6 would be the smallest way to measure trajectory sensitivity; a source-context-disjoint readout is needed before a broader transfer claim.

## Lineage, updates and failures

The original attempt remains a **six-update STOP caused by a process-disappearance launcher race**, with its report unchanged. The continuation references exactly its six completed round directories and validation 0/2/4 through nine symlinks; all inherited policies agree with the sealed audit. It neither rerolled those episodes nor reapplied their updates. The original seed-981265001 start from exact step0/empty Adam is established by the linked prior audit, not inferred from the continuation directory name.

The two new updates preserve the exact loaded previous adapter, persistent 504-entry Adam ordering/cursors 6→7→8, RNG/checkpoint hashes, generation/input/group identities and correction-capture bindings. Actual CPU tensor differences agree with saved deltas; all 504 new adapter tensors are finite FP32. Child parameters are absent from the training model; preceding prompt/child/observation tokens are masked, and all loss targets are current root actions. All correction guards pass.

| New update | Fresh train exact | Mixed episodes used | Root turns / action targets | Gradient norm | Actual adapter ΔL2 |
|---|---:|---:|---:|---:|---:|
| 7 | 18/32 | 32 | 85 / 24,393 | 0.07431 | 0.08085 |
| 8 | 19/32 | 24 | 57 / 14,707 | 0.12528 | 0.07754 |

All 128 new episodes (64 training, 16 validation, 48 transfer) were completed and admitted; no execution, observability, overflow-reclassification or budget exclusions occurred. Eight homogeneous valid training episodes in round 8 were unused by the mixed-group objective, not failures. Across the linked eight updates: 208 selected training episodes, 484 root turns, 148,250 action targets, and 404.08 seconds of optimizer work. Those training outcomes do not substitute for transfer evaluation.

Continuation FINAL is complete and the accepted child exited **0, no timeout**, with empty GPU-process evidence afterward. Five owned service release records confirm their captured parent/descendant identities exited, not merely that ports closed. This does not rewrite the original child’s exit 1 or remove its STOP.

## Actual cost

The new run retained 1,548 physical calls (313 root, 1,235 child), all returned, with a corresponding request file for every result and no request-only attempt. Independent native checks matched wire prompt/completion IDs, exported/native action logprobs, role/model identity and full-support T .5 sampling. New totals: 1,619,544 logical prompt tokens, 1,475,648 cached, 143,896 uncached and 192,882 completion/action tokens. Combined with the sealed first attempt: 3,751 calls, 4,004,510 logical prompt tokens and 546,095 completion/action tokens.

| Transfer condition | Root / child calls | Logical prompt | Completion/action | Collection elapsed |
|---|---:|---:|---:|---:|
| Original | 61 / 163 | 283,068 | 58,958 | 365.12 s |
| Selected step 6 | 59 / 214 | 289,576 | 32,619 | 210.17 s |

Selected used 21.9% more total calls and 2.3% more logical prompt tokens, but 44.7% fewer completion tokens and 42.4% less collection time in this ordered run. More recursive calls alone are not a cost improvement; these measures should remain separate.

Original terminal envelope: 3,432.94 s. Additional continuation: 1,938.29 s within its separately authorized 3,000 s inclusive / 2,880 s work allowance; accepted process elapsed 1,938.81 s. Sum of run envelopes is 5,371.23 s (89.52 min), plus 594.55 s between them; first start to final spans 99.43 min. The continuation did not complete as part of the original uninterrupted attempt. New collection stages total 1,397.27 s, five start-to-ready intervals 211.41 s, and the two optimizer phases 115.88 s; different clock boundaries mean these are not a complete GPU-utilization decomposition. Last release to accepted exit was about **0.49 s**, with no long post-release analysis lock tail.

## Audit boundary and evidence

METHOD was frozen before opening continuation outcomes, with parent-disclosed val6=3/8/checkpoint7/round8 activity recorded as prior exposure. The single raw audit took 11.12 s, scored exactly 128 new episodes once, and passed 20,535 assertions. Its cache read each of 3,330 needed paths at most once and reused 197 inherited hashes without byte reads; no old raw episodes were rescored or global closure hashed inside episode loops. This relies on completed-artifact immutability and metadata checks, not adversarial tamper resistance. Saved causal replay proofs are linked and physical role/action suffixes independently checked; a second complete native-graph reconstruction was not performed.

Machine evidence: [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json"), [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json"), [SUMMARY.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SUMMARY.json"), [METHOD.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METHOD.json"). The prior [stopped-attempt report](../root-independent-seed-live-2026-09-09/REPORT.md) remains sealed. Terminal selected adapter: `53e822f25323040463ebf4e10f73ea69b4c68b00f612b8bc8de4b89c4b5cf3bb`; final step8 adapter: `f6c2ead4e65cee947326f655be81a3f67b7e3f1ac4c495ec9d2e71bb67c0e7d9`. FINAL SHA `cb76e714a1192c7bd113be5ec5a228039472c653bbe8c574d436f4373d03ff46`; SELECTION SHA `75ec09e588136116b111c2b4cde0a33276055069c351c533f96c7f28f8932b82`. Full operation/source/checkpoint/raw identities are retained in the machine manifests.

Only this new analysis namespace was written. No GPU/model calls, process signals, lifecycle locks, acceptance changes, reward changes, response repair or edits to frozen research artifacts were performed.
