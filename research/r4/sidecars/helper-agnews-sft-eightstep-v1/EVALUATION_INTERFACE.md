# Conditional fixed checkpoint8 interface

Call `sft_study.endpoint()` only after the training owner exits. It requires all
eight `checkpoint-NNNN/state.json` and `STEP_COMMIT.json` links, persistent Adam
counters `[N]`, exact c32 provenance, unchanged root, `RESULT.status` equal to
`UPDATED_STEP8`, and a complete error-free owner terminal.

The returned binding names `outputs/attempt-001/checkpoint-0008`, authenticates
adapter/config/state/commit/RESULT/READY hashes, and declares no checkpoint
selection. The shared evaluator must use the frozen broader-data heldout schedule:
128 B4 calls, 512 records, temperature zero, seeds 202609126000–202609126127.
It must retain c32, RL8, and SFT8 as distinct arms and must not substitute a
partial SFT checkpoint.
