# TREC retention after broader AG training

This is an interference/retention readout on 128 TREC test records that were already
evaluated during the original c32 SFT study. It is not an unseen-source or independent
generalization panel. The comparison holds the exact established TREC B4 prompt,
schema, temperature-zero schedule, base model, and root binding fixed while changing
only the helper adapter among c32, completed AG RL step 8, and completed AG SFT step 8.

The panel manifest's optional seed-2 note referred to an obsolete one-step replica.
This evaluator amendment instead names the current broader eight-step RL replica.
That arm is deferred until it actually reaches and qualifies fixed step 8; these READYs
cover only the three already completed endpoints. Report per-record paired wins/losses,
per-label outcomes, exact-map availability, and physical request/token/wall costs
separately for every arm.

