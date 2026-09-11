# Indexed SFT: CPU-ready handoff

The approved experiment is prepared without GPU/model requests. The source and input identity is `204bc845987825514afe0f5a395917d933871e78b097de39db6736b72b5d23ca`. The parent alone launches after the root campaign releases its GPU.

## What is reused and changed

`driver.py` privately imports the exact mixed-size driver SHA `1a063bedc6882354736e822595472d8269211007aa92ff3fa8f3d487b7c5b708`. Its training loop, full-batch token-normalized supervised step, original adapter audit, Adam/resume cursor and checkpoint mechanisms are reused unchanged. Only this private imported module receives owned input-binding and evaluator callbacks. No frozen source or live service was edited.

New rendering substitutes an ID→question / ID→label map with the qualified indexed instruction. Batch-local IDs reset to q0001, avoiding stable question identifiers. Anonymous rendering is checked against the original fixed5 token IDs. All representations use the same prior-SFT tool serialization. No grammar during training or HF readout. Strict maps reject duplicate/missing/extra IDs and noncanonical labels; values are scored by ID, never positional repair.

## Frozen actual input accounting

| Quantity | Epoch1 | Epoch2 |
|---|---:|---:|
| Source records |5,065|5,065|
| Arrays |1,621|1,620|
| Optimizer increments |102|102|
| Supervised suffix tokens |59,100|59,098|
| Prompt tokens |1,355,978|1,355,200|
| Unpadded causal tokens |1,415,078|1,414,298|
| Microbatch2 padded tokens |1,508,127|1,512,304|
| Maximum causal length |2,804|2,852|

Total10,130record exposures and118,198supervised tokens. Exact B record/bucket/order/residual allocation reproduces; training is not compute-matched to B because IDs add target and input tokens. Target-token normalization also includes the ID syntax. Frozen partitions remain5,065/300/489unique groups with no cross-partition overlap.

Final readout contains208responses per weight:196fixed5 responses (98anonymous+98indexed,489groups each) and12long responses (sixcontexts×two representations),624acrossold/B/new. Epoch validation monitors both representations of the same300groups; the pooled600record summary is not600independent groups, and `by_representation` is the appropriate score comparison. Maximum64prompt is1,832tokens; prompt+3,072cap is4,904, below8,192. Full final summaries include classwise precision/recall/F1, exact arrays, quartiles, truncation and raw prompt/output IDs.

New weights are always the fixed epoch2 checkpoint, even if epoch1 validation is better. Oldc32de and B59ad8542 bindings authenticate adapter bytes, checkpoint members, RESULT and SELECTION. Fresh old/B readout occurs after new training/readout; the shared prepared rows make prompt IDs identical across weights. `RESULT.json` marks the new training result; `COMPARISON.json` marks all three readouts complete. A partial baseline comparison must not be described as complete merely because RESULT exists.

## Focused CPU evidence

Test-first RED: four intended contract tests failed because the new driver was absent. The overall-deadline test separately failed because the launcher was absent. The first implementation exposed one real renderer error (`labels` belongs to the frozen design, not its nested contract); it was fixed before preparation.

GREEN: six focused checks cover strict ID coverage/correspondence, actual tokenizer prefix/terminator masks, exact B group allocation, a tiny actual PEFT update with frozen base/save/reload/Adam1→2/RNG restoration, owned evaluator prompt/cap binding and output-contract separation, and real `/bin/true` versus timed-out owned `/bin/sleep` cleanup. The tiny PEFT fixture emits its standard warning that no pretrained vocabulary config is present; no real model download or GPU operation occurs.

`QUALIFICATION.json` independently checks all3,241rendered training arrays, exactB order, source disjointness, suffix-only loss, terminators, target exactness and context bounds, and authenticates61source/model/input hashes. This is a CPU qualification, not a real4Btraining or generated-answer success claim.

## Launch and clocks

Use the command in READY.json. The outer launcher starts only its own new process group and enforces the original attempt's90-minute overall deadline, including model load/evaluation/checkpoint time, with30seconds cleanup grace. The reused loop separately enforces60minutes accumulated optimization. The outer RUN/FINISH records actual overall wall time; trainer RESULT records optimization seconds. Partial outputs and last committed checkpoints remain on timeout. Resume must be explicit and retains the initial overall deadline.

Expected shape is one A100 with4B BF16base and FP32rank8LoRA; no larger model. Estimated total30–50minutes, not measured; caps govern. Source/data freeze precedes readiness. This is representation-specific supervised co-adaptation, not evidence of a full-RLM or fresh-task learning gain. The independent fresh-permutation/SST anchor control is a separate experiment.
