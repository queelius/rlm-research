# Root interface SFT: equal-row weighting control

Status: design proposal only. No implementation, model call, acceptance or launch. MAIN owns approval and GPU scheduling. This is a bounded addition around the existing qualified SFT/readout flow, not a new runtime.

## Recommended single experiment

Train one new fixed-final4 root with equal-row current-action CE. Compare it with the authenticated existing global-target-token final4 on 48 new paired native readouts. Preserve the exact32 tokenized rows, historical473210 starting adapter, four update batches/order, training RNG, LR, precision, masks and checkpoints. Do not add demonstrations, semantic trajectories, grammar, terminal cues or prompt edits.

This is the smallest useful test of whether the original loss weighting contributes to the final-format regression. It does not test a complete solution curriculum. Reweighting can also reduce learning of the helper example, so a change in copying alone does not identify a distinct mechanism.

Evidence: the sealed independent [SFT report](../../analyses/root-interface-sft-live-2026-09-09/REPORT.md), SHA959ac7ce7ed3ee82b134d0acc5a1963e8077519358e82ac40e01682dad3b991d, found actual helper uptake24/24, strict correct1→2/24, valid format19→9/24, and22/24 final-policy first actions matching the taught four-record example. Its original-vs-final labels are weight conditions: the copied actions are from the final SFT policy, not its starting policy. The reports/weights were exposed before this proposal; no active RL outcomes are consulted.

## Exact arms and weighting

- Control T: existing original SFT fixed-final4, adapter efab2913e7fe9f5f9b381ae6eb67bb56071070f86b237e6145f98654816aad64, config d665754d496ad234fd441cfb340d2f597a8f13e7763a3f0592bf28720ef85a57, in root-interface-sft-local-runtime-v1/outputs/attempt-001/training/checkpoint-0004. Authenticate RESULT/SELECTION/state and all members once. Reuse its frozen training outcome; do not retrain it or pool its earlier readout into the new comparison.
- Treatment R: new equal-row final4 from exact historical473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd, not from efab2913 and not from any live RL checkpoint. Its output identity is new and explicitly names the loss amendment. Fixed checkpoint4 regardless of new readout.

Let L_i be summed causal CE over row i's n_i unmasked action tokens, including the same single EOS. For each effective batch of16: T uses sum_i L_i / sum_i n_i; R uses sum_i L_i/(16*n_i). Compute n_i from shifted labels, never from unshifted sequence length. Reject zero-target rows. Every prefix, tool observation and child token remains masked. No row duplication, oversampling, LR compensation or extra optimizer step.

The literal inventory is1520 helper-target plus83 terminal-target tokens per epoch. That5.18% fraction is not a measured gradient share. Exact per-batch objective mass for terminal rows is:

| Update | Target tokens | T terminal mass | R terminal mass |
|---|---:|---:|---:|
| 1 | 713 | 0.06732117812061711 | 0.5625 |
| 2 | 890 | 0.03932584269662921 | 0.4375 |
| 3 | 801 | 0.05118601747815231 | 0.5 |
| 4 | 802 | 0.05236907730673317 | 0.5 |

[WEIGHTING_AND_SEED_AUDIT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: WEIGHTING_AND_SEED_AUDIT.json") contains every row's actual floating CE-sum multiplier, row mass and batch sum (=1). These are scalar loss coefficients; actual gradients, clipping and Adam responses need measurement. At runtime save FP32 coefficient values, per-row CE/count/weighted contribution, objective sum, token-mean diagnostic NLL and gradient norm; do not call row-mean NLL comparable to the old token-mean NLL.

## Constants, inputs and splits

Reuse TRAINING_ROWS_FINAL.json SHA3a8be3b78d9507aeec4dc8e9094789c466f558f901f13f2fd98208f07c369fe0 without retokenization or altered metadata. Exactly16 helper and16 final-answer microtask rows, two epochs, effective batch16/microbatch1, four updates,64 row exposures/3206 action-token exposures. Same training seed981284002 and shuffle Random(981284002+epoch), intentionally common training randomness, not a newly independent training seed. BF16 frozen base, exact FP32 rank8 LoRA/dropout0, fresh AdamW1e-4/weight-decay0, clip1, same SDPA implementation. Save adapter/config/Adam/RNG/cursor after every step; no historical optimizer restored.

Public allocation remains896 normalized source groups:384 train (8 contexts,32/64 records),192 validation (4),64 query transfer (2),256 length transfer (2×128). Training and readout question groups stay disjoint, but all are leaf-training-supported; the eight readout context clusters are exposed development evidence, not new task/source/pretraining-held-out evidence. No label-based reselection or changes to the skewed gold distribution. Keep host gold outside model payloads and the same fixed child c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3.

## Fresh paired readout and cap

Reuse the exact24 SFT task coordinates/prompts/context/environment/renderer/tools, with only fresh sampling seeds: validation981300101–108, query981300201–208, length981300301–308 in original EVAL_PLAN_FINAL order within stratum. Both roots share each fresh coordinate. Master981300001 fixes phase order by SHA256 of master:arm, yielding equal_row then global_target_token. The bounded133-file named metadata audit found no fresh-seed collision; the reused training seed is deliberately exempt. Freeze all48 coordinate IDs, source-coordinate crosswalk, exact native first-prompt IDs, task hashes and binding expectations before inference.

Two qualified sequential owned services, each current root plus the same child. Preserve local-runtime77df23b8/image8cfe, four workers, native Train/Qwen3 enable_thinking=True, T0.5/top_p1/top_k−1/min_p0, max2048, context8192, depth1, setup/rollout/finalize/scoring45/300/15/15s. The weight phases are not interleaved; fixed phase/service/time order and backend scheduling are nuisance factors. Matched seeds do not imply deterministic potential outcomes. Do not broaden serving to three aliases.

Keep original training600s, trainer-process900s, per-readout collection900s, service-ready180s, one shared work3180s plus120s owned cleanup=3300s inclusive/3330s parent envelope. Expected one-A100 wall12–16min based on the original752s inclusive run; this is an estimate, not a promised completion time. No new service until parent accepts and obtains its exact predecessor/shared-lock/empty-GPU conditions. Do not hold GPU scheduling authority for independent analysis.

## Falsifiable contrasts and missingness

Primary: R−T paired strict whole-reply Answer: N correctness over24 task coordinates, report gains/losses/ties and planned denominator; aggregate within each of eight context groups, then report validation/query/length separately. Four validation and two query/two length clusters are too few for confirmatory generalization. No independent-48 or pooled historical-denominator claim.

Prespecified diagnostics: paired format validity; first structured code present/AST-parsable; exact HELPER byte match among extractable first code (missing/invalid is null, not false); actual physical child use; relevant-record coverage and continuation beyond the example four, where source-bound maps are observable; final number vs observable map-implied count; semantic-label errors; root/child actual calls and logical/cached/uncached/completion token costs. Missing evidence stays null. Do not execute sampled code on host, infer coverage from prose, repair answers or turn a shape metric into success.

Apply the same original readout endpoint rule: completed available wrong/malformed/empty output=0; incomplete or provider-unavailable=null. Preserve raw episode.ok, finalize/setup errors, complete observable endpoint and native graph verification as separate fields; no new RL-admission gate or erasure of a completed score after a later cap. Record operational invalid/unrun status and both-phase censored pairs explicitly.

Interpretation:
- Better syntax with persistently shallow copying/poor coverage supports a terminal-weighting contribution while leaving task-solution insufficiency unresolved.
- Better strict answers with observable correct coverage supports useful downstream transfer of the weighting change, not proof of an attention/copying mechanism.
- Less copying/helper use without task gains may be loss of interface competence, not improved planning.
- Flat/negative results refute sufficiency of this four-step weighting intervention; they do not establish that example copying is the unique cause.
- A future complete-trajectory data intervention would test a different hypothesis and is explicitly deferred.

Alternative ranked second: replace the illustrative helper targets with verified full task trajectories. It could improve competence but changes scope, content, target length and credit, so it cannot cleanly attribute the current regression. Terminal-only oversampling ranks third because it also changes example exposures/order or step allocation. Neither is included here.
