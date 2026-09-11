# Additive completion v2

Completion v1 proved CUDA visibility was repaired: the model loaded. It then exposed a distinct
pre-existing input omission before any gate evaluation or Adam step: the qualified trainer requires
`inputs/GATE_PLAN.json`, but the new-corpus package never froze one.

V2 adds only that missing receipt. It mechanically mirrors the original six-family gate layout:
T1/M1/J1/P1/P2/P3 from new-corpus training contexts 00 through 05. Every row is already one of the
72 immutable captured episodes. There is no outcome, gold, length, or model-output selection. V2
again reuses all 72 teachers, starts fresh Adam0, requires six full72 updates, and performs the same
metadata72 readout. V1 and the original attempt remain immutable and charged.
