# Implementation plan

1. Bind and authenticate exact QS checkpoint-0006 and the fixed TRAIN/protected inputs.
2. Freeze 192 train attempts as eight 24-attempt windows and 144 paired readout intents.
3. Reuse qualified collector/export/native/trainer kernels with narrow QS aliases.
4. Add fixed-cursor owner, window-local checkpoints, lifecycle cleanup, inventory, and cost split.
5. Run focused CPU tests and source verification; emit READY only after MAIN review.

No GPU or service process is launched during preparation.
