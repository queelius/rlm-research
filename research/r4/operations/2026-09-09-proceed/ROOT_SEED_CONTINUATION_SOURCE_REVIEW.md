# Root seed lifecycle continuation: bounded independent review

2026-09-09,06:05–06:08 UTC. No material blocker found in the requested full PLAN.md, driver.py and test_driver.py review. This is source/integration review, not launch acceptance or a fresh GPU qualification. No tests, verifier/coordinator execution, signals, service/model calls or frozen edits were performed by this reviewer.

The new run references only completed rounds1–6 and validation0/2/4. Existing `committed_policies` resolves checkpoint/group paths through those references to their original targets; policy and COMMIT identities therefore remain the original six-update chain. Existing COMMIT files are compared rather than regenerated when equal. The new namespace imports neither the old STOP nor its services, and the guard rejects existing round7 collection or validation6. The unchanged state machine begins at policy6, validation6 and fresh round7; it does not apply the first six optimizer steps again. The step6 adapter is explicitly pinned to53e822f25323040463ebf4e10f73ea69b4c68b00f612b8bc8de4b89c4b5cf3bb.

The process-disappearance patch reaches `lifecycle.observe`: its `v1` is the campaign wrapper, whose attribute forwarding reads the patched `coordinator.impl.process_identity`. Only FileNotFoundError/ProcessLookupError from that original identity read become absence. Permission and other failures propagate; successful identities are returned unchanged. Exact PID/start/UID/PGID and owned-descendant release checks remain the V2 implementation. This does not justify arbitrary cleanup or stopping a predecessor.

`install_provenance` wraps the already authenticated independent-seed/lifecycle/overflow `prepare_spec`; it does not replace task construction, masks, rewards, sampler or role routing. The new note includes original STOP and baseline-spec hashes and pins the added source/READY. Collection and training subprocesses still use the original independent-seed ROOT and fixed plans, with exact current-policy/export authentication. Prior valid stages are read, not recollected; validation selection is unchanged.

The3000-second inclusive **exception** budget and2880-second work deadline are an explicit additional infrastructure envelope, not another independent seed or completion within the original budget. Keep the original3432.94 seconds separately visible and report ordinary cleanup grace/actual release; do not equate the signal deadline with instantaneous process exit. Parent owns the shared lock, actual empty-GPU check and launch. Dynamic remaining-stage checks remain necessary; no unseen outcome or post-step6 likelihood was fabricated for this review.

Reviewed SHA256:

- PLAN.md: `f6e12c24c3c5bd7827aa1d4be388c492e5c6eb51e8a631ab1af8682310a7e18d`
- driver.py: `bdf75065eec803bb9a2952aa7ac5debcbaa4db1f35d69c48958dc1eaa964cbdd`
- test_driver.py: `263b0a5ff8979326b696b669dd7df3106b8f2348a9dfbc308cf0ef1388213c0c`

Scope excludes broad source redesign and the already completed original-seed preparation review. The six focused tests were reported by main, not rerun here.
