# Fixed one-step readout implementation plan

Goal: evaluate the one fixed qualified RL endpoint on all original 32 short-held episodes and all 16 long episodes, comparing against already-qualified cp32 outputs. No score-dependent admission or filtering.

Architecture: study.py delegates exact original short/long schedules, payloads and environments; collect.py loads one original native scientific collector with explicit study/checkpoint bindings and unchanged terminal-strip-disabled hooks. checkpoint.py authenticates completed trainer state, actual initial/final/gradient/Adam/RNG artifacts and publishes its exact root binding. owner.py uses the accepted service lifecycle. prepare.py seals sources, payload/baseline inventories and two focused CPU fixtures.

Constraints: new external sidecar only; no GPU launch, installs, T1 runtime/hooks or sealed-source mutation. Same T.5/seeds, zero children, six total actions, 2048 tokens/action, original 8192 context cap and scorer. Separate fixed short/long stages; both run regardless of accuracy. Fixed endpoint checkpoint-0001 only. Short 600s science/900s owner/1000s external; long900/1100/1200. Missing/invalid distinct from wrong. Readiness is conditional on UPDATED plus full parent/source/optimizer qualification, never a manipulation score gate.

1. Implement and CPU-qualify exact payload/model-context and state/binding failure tests; preserve raw requests and responses through the inherited collector. Checkpoint admission must be exercised on the actual completed trainer when available, not fabricated candidate weights.
2. Seal READY and separate stage argv, then MAIN review/admission only. Save checkpoint and baseline source hashes in every run. No cp32 reruns, no checkpoint selection, no held/long fields in training.
