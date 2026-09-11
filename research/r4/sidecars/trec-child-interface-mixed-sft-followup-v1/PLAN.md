# Execution plan

1. Materialize and seal one mixed TRAIN stream plus the 192-call fixed readout.
2. Train exact c32 for 24 updates with fresh Adam/RNG and save 6/12/18/24.
3. Serve fixed update 24 beside unchanged c32 using the qualified dual-LoRA lifecycle; issue only
   the 192 mixed-policy calls with no retry.
4. Release service and retain complete physical, cost, selection, state, and terminal inventories.
5. Post-terminal audit all raw native responses and compare against frozen old-policy receipts.
