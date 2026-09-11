---
status: ready_for_main_review
date: 2026-09-10
---

# Completion v2 handoff

The retained completion-v1 log proves the CUDA repair worked: the model loaded all 398 weight
shards. It then failed before evaluating the NLL gate or constructing Adam because the original
new-corpus package omitted `inputs/GATE_PLAN.json`.

V2 freezes the missing six rows as an exact subset of the immutable 72 captures. The rule mirrors
the original gate structure without consulting outcomes: T1/M1/J1/P1/P2/P3 from new training
contexts 00..05. The actual TRAIN interpreter executed `train_v2.py verify-inputs` and returned
`{"corpus":72,"gate":6,"gate_ids_in_corpus":true}`. Three focused tests passed. The actual NATIVE
owner dependency chain and both training/collector argv paths were also exercised.

No science, optimizer, seed, teacher, role mask, loss, gate calculation, checkpoint rule, readout,
or budget changed. Both failed attempts remain immutable; neither performed an Adam update or
readout. The original 72 capture calls and both short failed training stages remain separately
charged. V2 performs no recapture.

READY SHA: `704d6f8481c26fea6e067e99759300ecb3e657f001a52779dd8b24b0c49478d9`.
Identity: `074728a07ee4e3a581e3bd20018c21ff1024f0faa04a7e89b380d5263a1d0c6f`.
Gate receipt SHA: `d7a90941d0a771f6d9d33648484f15fb3b07c19105b6d9b7ce0752de074892ca`.
