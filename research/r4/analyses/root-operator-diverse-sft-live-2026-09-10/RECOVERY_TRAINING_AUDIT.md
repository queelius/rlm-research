# Recovery training audit (pre-readout checkpoint)

Read after training completed and before any SFT6 endpoint existed. The isolated command preserved
MAIN's exact single MIG assignment. `LOAD_AUDIT.json` authenticates the released-reference 857 start:
504 adapter tensors, all values/dtypes equal, zero missing/unexpected keys. The six-example gate
completed in 5.660 seconds, passed its predeclared spending threshold in 6/6 rows, projected 1,518.534
seconds, and explicitly performed zero gradients/optimizer steps.

Training then committed six fixed epoch checkpoints. Independent CPU inspection of every retained
`optimizer.pt` found one parameter group, 504 state entries, and a uniform Adam `step` equal to the
checkpoint ordinal: `[1]`, `[2]`, `[3]`, `[4]`, `[5]`, `[6]`. This is six actual optimizer increments,
not six files standing in for one update. All state receipts retain scientific identity
`a19086d2…224e2`, corpus SHA `207d3699…92ea9`, cursor zero at epoch boundaries, and monotonically
increasing delta-from-start (0.2967 to 1.8175). Final RESULT reports 432 example exposures, 1,944 root
turn exposures, 137,082 target-token exposures, fresh optimizer true, child loaded/updated false,
and 1,214.167 seconds training. Selection is fixed final checkpoint 6, not validation-selected or a
partial substitute; adapter SHA is `efe7efc1…518cb`.

The training phase ended complete at epoch `1789006765.711728`. SFT6 service startup followed. No
treatment readout was inspected for this checkpoint, so this file makes no performance claim.
