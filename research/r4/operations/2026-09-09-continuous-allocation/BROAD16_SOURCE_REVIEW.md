# BROAD16 bounded independent source review

Reviewed 2026-09-09 UTC, CPU-only, by `storage_audit`. Verdict: **no material implementation or experiment-validity blocker found in the inspected scope**. Parent owns acceptance and execution; this report does not authorize a launch. Review began before launch and completed after the parent's launch notification, without opening live campaign outcomes or changing any source/input.

## Scope and authenticated identity

Read the implementation brief, broader-curriculum idea, candidate-data README, all new common/campaign/native/train/prepare/qualification/seal code, tests and design/runbook/report; inspected the relevant inherited state-loop, native task/export and exact-overflow paths. Reused the earlier numerical-training/recovery review rather than repeating a global audit.

- READY: `94f416ebe6a613f4109a3648a177407f5567df574047cbb8a0e60a10ceec10a1`.
- CAMPAIGN: `c2f52b6765ed63bea50c7b3da6a9be2ac9988ac2486a1f22aa38c9cafd765369`.
- Campaign ID: `475600bacdcc07ec48edae3c0d58b723a1622b70d9bf79bcbcbe215c40d1012f`.
- Authenticated READY's 206 source/input paths once, with no mismatch. Independently recomputed all seven recorded private source transformations, including occurrence counts and executed-source hashes; all matched.

## Material checks

**Start, credit and update chain.** The policy starts from original converted step0 adapter `857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6`, with no inherited optimizer/update/RNG state. Child `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3` stays fixed. Private module registration propagates the new namespace to coordinator, trainer, native collector and lifecycle instead of reopening the earlier campaign. Generation bounds, loop, validation schedule, final step and transfer selection consistently extend through 16, including 8→9. Persistent Adam/checkpoint authentication, exact FP32 adapter loading, root-only causal masks and numerical TIS update are inherited unchanged. Admission is exactly 24 recorded training trajectories, three task groups of eight with exact planned IDs/seeds; only genuine mixed groups train. The narrow prior exact-overflow exclusion remains narrow. Missing signal can stop the run; 16 successful updates are not guaranteed.

**Data and selection.** The actual runtime registry contains 80 tasks over 47 contexts, not every optional candidate-data stratum. All 16 rounds have 24 unique episode IDs and the prescribed 16/32/64-context mixture. There are 48 training task groups: each of the 24 training contexts appears twice with different targets. Validation has eight tasks and transfer has 24 tasks, each with two paired seeds. Original/final transfer task-seed lists match exactly. Primary selection is fixed final16, not the validation maximum; earliest-best validation is descriptive only. No evaluation row enters training.

The selected contexts contain 2,784 distinct source question-group IDs: training 896, validation 384, composition transfer 384, size transfer 1,024 and leaf-test-exposed transfer 96. All pairwise partition intersections are zero; context lengths and within-context uniqueness match declarations. Public runtime contexts contain only ID/text; gold stays host-side. Registered train/evaluation prompts use the same qualified task path. Source-group disjointness is a local split claim, not freedom from old/public-model pretraining or every historical experiment. Child-train-supported and child-test-exposed transfer remain distinct; the optional SST and child-validation strata are not silently included.

**Qualification and lifecycle.** The metadata-only qualification wrapper records absent PEFT in the serving environment and separately inventories the training environment; it neither installs packages nor changes runtime/training code. Published evidence records nine focused native tests, one actual tiny-PEFT 16-step/root-mask test, and a rootless fake-provider proof with three physical calls (two root credited, one child uncredited). I inspected this evidence, not reran its tests. The inherited narrowly scoped `/proc`-absence fix is installed on the actual coordinator module and remains visible to lifecycle observers. Exclusive empty-device/shared-lock authority remains the parent's responsibility.

## Interpretation limits retained

This changes curriculum breadth, update count and attempted rollout volume together; it is not a breadth-only causal comparison. Reserved target categories are not unseen semantic labels. The 256-record context can exceed the request context limit as a whole and is intentionally file-backed; qualification does not promise the policy will inspect it successfully. Transfer phases are serial original→final, so service/order effects remain. The small fake-provider/tiny-model checks do not establish real-model learning or 16-round completion. TREC licensing/provenance and named-history exclusions retain the candidate data's explicit caveats. No additional hardening or source changes are requested by this review.
