# Frozen execution plan

1. Verify the original READY, complete72 corpus receipt, and all pinned teacher files.
2. Launch the original six-update trainer with its original inputs and a new output directory,
   preserving the assigned CUDA device. Require the exact checkpoint-6 ancestry before serving.
3. Serve only the recovered checkpoint and collect all 72 frozen metadata endpoints once.
4. Preserve every invalid or missing endpoint as observed zero or NULL under the original rules;
   do not retry, substitute, or select a checkpoint by readout outcome.
5. Release the owned service and write native physical-cost and terminal inventories.
