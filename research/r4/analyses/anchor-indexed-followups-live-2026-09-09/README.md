# Anchor control and indexed training: completed follow-up audit

**Final: both jobs completed and the independent audit passed.** All600 anchor calls and624 matched HF readouts are accounted for; no component was censored. The lead finding is the control: **B already scores373/384 with free indexed output, versus374/384 after explicit indexed-target training.** This does not establish a useful additional indexed-training benefit. Both still fail anonymous64. No experiment, queue, GPU process, or frozen input was changed by the audit.

Start with the [final report](REPORT.md). Machine-readable results are in [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json"); exact source inventories are in [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json"), with detailed [SFT checks and raw hashes](../../../../ARTIFACTS.md#unpublished-files "Not published: SFT_METRICS.json") and [operation/load evidence](../../../../ARTIFACTS.md#unpublished-files "Not published: SFT_SUPPLEMENT.json").

Completed finding: [explicit output IDs recover large-batch correspondence across two tasks](ANCHOR_REPORT.md), with [structured metrics and raw hashes](../../../../ARTIFACTS.md#unpublished-files "Not published: ANCHOR_METRICS.json") and the [independent audit program](../../../../ARTIFACTS.md#unpublished-files "Not published: audit_anchor.py").

## Fixed-final checkpoint and the earlier partial snapshot

The immutable [new-model RESULT](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-indexed-sft-v1/outputs/attempt-001/RESULT.json") has SHA256 `d59a21872fdf2c3dc3766f3ee8400cb4f279f2c8766e71e3678d09ff2cc8b400`; [SELECTION](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-indexed-sft-v1/outputs/attempt-001/SELECTION.json") has SHA256 `cb74d933d58212ad3405514398c21a185254df0bb6ff6aa4bd7e67a00848cf2c`. The fixed epoch2/step204 checkpoint state hashes to `1713048928326db62d50dd930a101e06600fdf78c2c12e73d78f7ca5b05b63c5`; its model hashes to `7a18736df45431856ac998658f2bbd89a9081d273a10253202babb221f3764db`. All state-listed adapter/config/optimizer/RNG file hashes were checked. The [binding record](../../../../ARTIFACTS.md#unpublished-files "Not published: FINAL_CHECKPOINT_BINDING.json") deliberately preserves its earlier pending-comparison timestamp/state; it is a historical snapshot, not the current status. The completed [COMPARISON](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-indexed-sft-v1/outputs/attempt-001/COMPARISON.json") hashes to `06cd867dff796260ddf08fffb9b03329fdfb50e9a75a15709e71dc840322f763`.

The formerly provisional new-model counts now match independent raw recomputation. The complete control comparison, failure types, paired gains/losses, actual Adam204 state and5.034778 LoRA delta are in the final report. Six long contexts contain384 previously exposed TREC questions. No general reasoning, RLM orchestration, or meaningful indexed-SFT-over-B gain is claimed.

## Scope

Read-only monitoring followed the accepted anchor → indexed-SFT handoff through completion. The marker watcher has exited. Completed-stage audits ran once; large inputs/checkpoints were not rehashed on each polling interval.

- Operation: [accepted plan](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../operations/2026-09-09-queued-successors/PLAN.json"), [parent acceptance](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../operations/2026-09-09-queued-successors/ACCEPTANCE.json"), [live events](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../operations/2026-09-09-queued-successors/attempt-001/events.jsonl").
- Anchor control: [frozen design](../../sidecars/leaf-correspondence-anchor-transfer-v1/DESIGN.md), [specification](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-correspondence-anchor-transfer-v1/SPEC.json"). Planned 600 old-child calls; paired output representations on identical indexed inputs, TREC permutations and public SST-2 validation.
- Indexed SFT: [frozen design](../../sidecars/leaf-indexed-sft-v1/DESIGN.md), [readiness](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-indexed-sft-v1/READY.json"). Planned exact B record allocation, two epochs from the original adapter, fixed final checkpoint, and matched old/B/new HF readouts.

## Audit questions

1. Did the serial handoff preserve ownership, accepted sources, bounded work, and distinct wait clocks?
2. For the anchor control, do raw calls reproduce the published paired accuracy and coverage, and do captured HTTP bodies/provider prompt IDs match the frozen physical-input qualification?
3. For indexed training, were 204 actual updates and epoch/checkpoint saves completed, with the specified original start and fixed-final decision? Were actual target-token exposure, optimizer/RNG state, precision, and wall/optimization clocks preserved?
4. Do old/B/new readouts share exact prepared prompt IDs and scoring rules within representation? Are any improvements format/coverage recovery, semantic accuracy, or both?
5. What does each result change about the next experiment? These are component-level classification controls, not an end-to-end RLM gain demonstration.

All final artifacts are present. The [next-experiment proposal](NEXT_EXPERIMENT_PROPOSAL.md) is advisory, not an executable schedule; the parent's accepted studies remain authoritative.
