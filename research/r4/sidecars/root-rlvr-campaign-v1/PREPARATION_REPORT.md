# CPU preparation evidence

Implementation follows the approved independent8-round decision and the parent's later explicit
8-worker collection choice. No old pilot/replay/source/weight files or active service were edited.
No GPU/model calls or server operations occurred during preparation.

The frozen plans contain256 unique new training seeds,8 new validation seeds reused at five
checkpoints, and24 transfer seeds paired across original/selected conditions. All campaign coordinate
seeds are collision-free against the pilot and each other except intentional paired/repeated uses.
Transfer has384 unique normalized official source-training question groups, six64-record contexts,
zero overlap with the pilot384, prior composition384, or leaf validation/test. All24 original/transfer
task prompt/context hashes are recorded; the original12 exactly match the qualified pilot.

Retained qualification: qualification-attempt-001/RESULT.json,
SHA256fc7adc41b6bdfc523d6e347b3f6b665c502a740bd85f4c43ed950bb8afca973e.
Ten focused CPU tests passed. The tiny real PEFT proof retains optimizer checkpoints1 and2, with
exact saved tensor/dtype and Adam/RNG reload, frozen base and child, action-only masks, rejection of
stale optimizer/generation, and a simulated crash after checkpoint state but before RESULT. Recovering
that step does not update again. Synthetic fixture probabilities are not research measurements.

Independent bounded review found a recovery provenance gap, reproduced by a failing regression:
same-generation recovery did not compare the current exported-group binding or reauthenticate the
correction capture. The fix checks saved INPUTS/correction hashes, saved input/group/export identity,
the current freshly authenticated group on trainer recovery, and exact round/group/campaign paths
on coordinator commit discovery. Those regressions and the two-step proof now pass.

Four native CPU tests additionally check original task identity, frozen paired transfer coordinates,
the previously qualified real root-child-root native fixture (two credited roots/one uncredited
child), parametric depth routing to a new actual root alias, and refusal to signal a reused PID.
Ruff E9/F checks passed. No broad repository suite, new environment installation, or framework
refactor was performed. Existing source guards remain intact and are included in the campaign seal.

Remaining launch qualification is deliberately exploratory: no newly assigned live endpoint has
been called in preparation. The coordinator authenticates actual base/adapter/config, /models,
native wire role/seed/sampling and runtime image before or during each fresh collection. Long-tail
budget failures, an empty mixed group, or numerical guards can stop the campaign with fewer than8
updates. The inherited two-row queue means validation8 has at most4 active episodes despite8 workers.
