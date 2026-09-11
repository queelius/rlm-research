# Receipt lifecycle delta: narrow independent review

2026-09-09 06:39–06:41 UTC. Read the complete operation-local wrapper, two tests and amendment, the reused observer helper, and the relevant frozen lifecycle install/observe path. Freshly checked six direct source/READY hashes below. No tests rerun, service/model/GPU call, process observation/signaling, source edit, acceptance or continuation-outcome inspection. This does not repeat or supersede the primary receipt review.

Verdict: **no material blocker in the inspected delta**. `receipt_driver.install_observer` wraps the actual imported receipt coordinator's `process_identity`. The reused helper catches only FileNotFoundError and ProcessLookupError and returns absence; successful identities are unchanged, and PermissionError/other failures propagate. The pinned helper module has no top-level stack loading or run invocation, so importing it does not enter the independent-seed campaign or read its outcomes.

The real frozen receipt lifecycle has `v1` equal to that coordinator module. Its `observe` performs a dynamic `v1.process_identity` lookup, and `install` replaces only claim/stop plus native binding/spec preparation, **not process_identity**. Consequently the subsequent unchanged receipt `run` call retains the intended observer patch. Stable UID/PID/start/group ownership checks and scoped cleanup are not relaxed. The second test exercises precisely this shared-module seam after `lifecycle.install`; the first covers both disappearance classes, unchanged live identity and a non-absence exception. This is source review of those tests, not an independent passing-test claim.

Scientific code, original driver/READY/SPEC, 72 coordinates, weights, rendering, prompts, score and budgets remain unchanged. The wrapper invokes original `verify_ready`, acquires the same sidecar lock and calls unchanged `driver.run`; it adds no retry, repair, model call or acceptance path. It has no analysis tail before releasing the lock.

Provenance linkage is adequate **when the parent operation binds this exact wrapper/test/amendment and pinned helper in its accepted source closure and records the wrapper argv in COMMAND**. The operation's stated isolated loader retains the qualified shared-lock/empty-GPU/accepted-argv checks. At review time final PLAN/accepted closure were not yet published, so this is not a claim they were authenticated or a launch approval. The receipt RUN still identifies its original scientific SPEC/READY; downstream audits must also cite the accepted parent operation for the actually executed lifecycle amendment, not describe RUN alone as the entire source identity.

The prior helper-log/catalog mutability, absent per-helper native-source corroboration, no semantic validation, optional uptake, inherited retry/partial-trace caveats and secondary cost/AST projection limits remain unchanged.

## Directly verified identities

| Artifact | SHA256 |
|---|---|
| `operations/2026-09-09-after-identity-receipt/receipt_driver.py` | `e2789bf5c4df114f8005f83dcfb68a909888995e2677c395a5d6de969b7a1c83` |
| same directory: `test_receipt_driver.py` | `ce6e334bc48e9e5b82183a0dec857f720c841c3973fa859a7c18e49a24100d61` |
| same directory: `LIFECYCLE_AMENDMENT.md` | `4e0b683777cc1d54afdf56c7333c9af0656d99910fe88efb7fe71208dbc10889` |
| `sidecars/root-seed-lifecycle-continuation-v1/driver.py` | `bdf75065eec803bb9a2952aa7ac5debcbaa4db1f35d69c48958dc1eaa964cbdd` |
| `sidecars/root-receipt-ablation-v1/driver.py` | `e3b936b3d2a5358fe4682cad0a875a28673bb7aae7fe06de4606567fee5ff32e` |
| `sidecars/root-receipt-ablation-v1/READY.json` | `1eba49031384deda22bbfdd9d234cc7ff1b43e63c0b72081af2c7c270a5b74f2` |

All paths are relative to `/project/alex_phd/runs/rlm-research-r4`. The amendment describes an approximate decision time; the actual review/source hashes above, not that prose timestamp, delimit this review.
