# Same-dataset self-SFT control

Prepared control: all six verified successful episodes from the same sealed 40-row fresh
4B rollout dataset used by RLVR. They contain 2,863 supervised action tokens across four
tasks; the longest exact causal sequence has 1,448 tokens. No heldout outcomes were read
to select training data or the recipe.

The frozen recipe is one epoch, six optimizer steps, rank8, AdamW LR2e-5, no weight decay,
gradient clipping1, and seed960260100. Loss is ordinary untempered action-token NLL, not
temperature-scaled RLVR. Earlier actions, observations, prompts, and scaffolding remain
context only. There is no truncation or fixed turn-count admission rule.

The original self-training question is whether a model can improve as an RLM by fitting
its own successful decisions with a fixed harness. This exploratory success-SFT/RLVR
comparison is not compute-matched and does not replace the original matched plain/RLM
self-training study. Success means verified terminal aggregate agreement, not independently
verified intermediate classification correctness. Weak successful heuristics may be reinforced.

## Exact starting policy

The immutable original Prime step0 adapter is unchanged. `inputs/step0-peft-key-conversion-v2`
is an additive key-only conversion. Its `CONVERSION.json` records all504 source/destination
names and tensor byte hashes. CPU loading with the real4B model shape verified every tensor's
values and dtype, with zero missing/unexpected keys and no warnings.

The base and lm_head stay BF16; LoRA tensors stay FP32, as in the original frozen checkpoint.
`autocast_adapter_dtype=True` is necessary here: disabling it rounds the FP32 checkpoint into
BF16 LoRA storage. The trainer audits every actual loaded tensor before its first forward.
`inputs/step0-peft-key-conversion-v1` is the retained, unsealed diagnostic copy from that failed
BF16 adapter-load validation; do not use it as a validated input.

## Launch and recovery

The parent exclusively owns GPU assignment. After inference has stopped:

```bash
env CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 \
  LD_LIBRARY_PATH=/project/alex_phd/.cache/nvidia-driver-580.126.09/runtime-lib-v1${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH} \
  /project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/single-gpu-self-sft-control-v1/source/self_sft_control.py \
  train --attempt /project/alex_phd/runs/rlm-research-r4/sidecars/single-gpu-self-sft-control-v1/outputs/attempt-001
```

Each complete step atomically publishes `training/checkpoint-0001` through `checkpoint-0006`,
including adapter, optimizer, RNG, hashes, and consumed episode cursor. Add `--resume` to the
same command after interruption; incomplete staging directories are retained and ignored.
The full-epoch result is `training/result.json`. Each invocation has a20-minute alarm cap.
Checkpointed elapsed time excludes abandoned partial work, so it is not a complete allocation
time measure; use the parent process logs for total compute accounting.

## CPU verification

Eleven tests passed using the pinned training Python and `CUDA_VISIBLE_DEVICES=''`, including
finite nonzero gradients with zero context-token targets, exact tensor conversion checks,
success-only admission, full positive-epoch coverage, and final-checkpoint result recovery.
Ruff passed. The prepared plan and all pinned inputs/sources authenticated successfully.
Preparation did not launch a GPU or execute generated code.
