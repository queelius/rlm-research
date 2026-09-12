---
schema: agnews-eightstep-training-seed-replication-v1
authority: MAIN_CPU_preparation_only
seed_namespace: agnews-broader8-seed2-20260912
native_seed_base: 20260912900000
hf_seed: 20260912910000
---

# Same-dose training-seed replica

Question: does the qualified RL step8 gain recur when only training randomness
changes? Same original c32, 1024 fixed records, eight128-record blocks and ordering,
B4×G4 actions, T.5, count-scaled RLOO/128, LR1e-5, carried Adam/RNG and exact
importance/replay gates. Fixed step8 only on the SAME already research-exposed512;
this is training-seed replication, not new-data confirmation. No training selection
or outcome-driven checkpoint choice. No continuation from seed1 weights/RNG.

Task1: new thin source-pinned sidecar. Reuse original core/numerical/mask/training
functions without editing their closures; local ROOT/default output, native/HF seeds
and request receipt paths are the only execution differences. All request fields
except seeds must byte/structure match original requests. Keep full source and input
hashes, original data manifest, optimizer/parent and every-step raw/probability chain.
Explicit admission retains V2 scoped ag_study qualification and truthfully records
prior seed1 readout exposure. Preserve600s step/5000s owner/5200s outer caps.
Two bounded fixtures: actual four-key native/token/mask/parent binding plus seed-only
schedule assertions; actual tiny-HF two-step Adam/RNG/gradient save-reload equivalence
and gate-failure no-step. Run actual CPU admission qualifier from a fresh process.

Task2: MAIN reviews immutable READY/closure and supplies separate admission before
any GPU work. Conditional fixed-step8 evaluator reuses the exact512 request schedule
and qualified native decoder/runtime; c32 baseline reuse requires exact matching
runtime and raw qualification. Replica midpoint evaluation is prohibited. All
failures/no-update stop normally; no gate weakening or automatic recollection.

Files: reuse.py, core.py, train_step.py, train_ag.py, prepare_masks.py, owner.py,
prepare_inputs.py, two focused fixtures, seal.py, RUNTIME/INPUTS/CPU/READY receipts;
separate conditional evaluator binding prepared after training closure is sealed.
No shared source, live output, environment, data, or production branch mutation.
