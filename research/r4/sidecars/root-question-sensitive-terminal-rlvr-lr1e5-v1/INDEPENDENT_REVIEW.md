---
date: 2026-09-10
reviewer: independent_cpu_review
status: ready_for_main_review_with_nonblocking_qualification_limits
approval: false
gpu_calls: 0
campaign_identity: 9b59a77098cc4c289237967f9154eb2a5423cbbda4e69889f4da1e47741c4961
campaign_sha256: c5fff6a7cc4512c4e8e55fcdf910b5e90f7e871e87cb03aec2d60489cb1fd597
---

# Independent material-qualification review

## Conclusion

I found no experiment-compromising defect in the prepared LR1e-5 package. It is ready for MAIN's
independent identity review and, only after MAIN approval and sealing, serialized launch. This is a
readiness recommendation, not approval: `MAIN_REVIEW.json` and `READY.json` remain absent, and this
review does not authorize GPU use.

The package preserves the intended scientific comparison: exact QS6 start, fresh AdamW state,
fixed c32 child, eight frozen windows of 24 attempts (192 total), and one new fixed-last protected
readout of 72 calls. The copied scientific inputs are byte-identical to recovery-v2; all 120 native
task hashes, and only those hashes, change under the new study namespace. The recipe changes only
schema, learning rate (`5e-5` to `1e-5`), and the per-optimizer wall cap (`240` to `1800` seconds).

## Material checks performed

- Rebuilt `lr_prepare_campaign.build()` in a fresh process and obtained byte-equality with
  `CAMPAIGN.json`, identity
  `9b59a77098cc4c289237967f9154eb2a5423cbbda4e69889f4da1e47741c4961`.
- Recounted 8 x 24 distinct training coordinates, 72 distinct readout coordinates, 48 training
  task names, and 120 total unique native tasks.
- Reconstructed every one of the 120 tasks through the actual `terminal_native.make_task` and
  renderer. Every regenerated hash matched `inputs/TASKS.json`, every frozen first-prefix matched,
  and all 120 hashes were unique.
- Compared the seven claimed fixed scientific JSON inputs byte-for-byte with recovery-v2. Each was
  equal at the pinned hash. Compared all old/new task rows: keys were identical and the only changed
  field in every row was `task_hash`.
- Inspected the owner transform against pinned `warm_owner.py`. The transformed execution schedules
  only `lr1e5_last`, writes 72 rather than 96 planned finals, uses the isolated attempt-001 output,
  invokes `lr_train.py`, and preserves stop/release and fixed-last selection behavior.
- Inspected the optimizer path. The underlying qualified restore snapshots the complete parameter
  group dictionary before loading and rejects any post-load difference, verifies complete moment
  inventory and cursor, checks parameter-name order, restores Python/Torch/CUDA RNG state, and
  authenticates the policy. The LR wrapper additionally asserts LR1e-5 and zero weight decay before
  and after restore and rejects checkpoints outside the new attempt namespace.
- Inspected the retained material receipts. The fake-provider qualification reached the actual
  `env.run_slot` transport once with an authenticated result and a 1,079-token frozen prefix. The
  Torch fixture loaded actual AdamW state at step 1, advanced to step 2, and rejected a saved
  LR5e-5 group through `lr_train.restore_optimizer`. Both report zero GPU/model calls.
- Re-ran the focused suite: `10 passed in 0.63s`. Re-ran the native owner CLI help and campaign
  rebuild. `READY.json`, `MAIN_REVIEW.json`, and `outputs/attempt-001` were absent at review time.
- Confirmed that the incomplete inherited convenience cost ledger is disclosed as non-authoritative;
  the required independent raw role-audit recount is explicit.

## Nonblocking limitations to retain in MAIN's review

1. The design asks for a positive two-step optimizer fixture across a separate trainer process.
   The retained fixture serializes and reloads real AdamW state but does so in one Python process;
   it also reaches the RNG restore statements without independently asserting the restored RNG
   values. This is weaker qualification wording than promised. It does not compromise the planned
   experiment because the actual restore implementation is pinned, performs the complete group and
   cursor checks, and is invoked in a fresh trainer subprocess for every real window after the
   first update. MAIN should describe the retained receipt as a real serialize/load two-step
   fixture, not as a separate-process RNG-continuity proof.

2. The one-slot fake-provider task ends after the root returns `Answer: 0`; it proves task identity,
   prompt rendering, `env.run_slot`, provider routing, and authenticated result capture, but not a
   child/tool turn. The child/tool machinery is unchanged and pinned from the completed recovery-v2
   producer. MAIN should avoid saying the new fixture independently requalified every multi-turn
   branch.

3. `CAMPAIGN_ID` is a distinct fixed namespace digest, while the separate campaign `identity`
   binds the complete source/input closure. Therefore the documentation's phrase that the campaign
   ID itself is derived from the complete recipe is imprecise. The binding used by review/sealing is
   the full campaign identity, so this is not an identity defect.

4. The sparse credited-position implementation is objective-matched but not bitwise identical to
   the high-LR campaign's first dense-logit update. The design and campaign already disclose this,
   so any result supports the stated lower-LR sparse continuation comparison, not a pure numerical
   one-factor claim.

## MAIN acceptance checks still required

MAIN should independently verify the campaign and source pins, write an identity-bound approval,
seal without source changes, and launch only through the serialized GPU owner. Outcome audit must
authenticate terminal release before reading results, label early-stop/zero-update cases honestly,
recount raw physical calls and usage, and keep observed invalid endpoints separate from NULLs.

