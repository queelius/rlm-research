# V2 binding-validation amendment

V1 CPU qualification exposed the fixed capture boundary and owner flow but did not execute the lazy free-collector descriptor-validation import. The inherited collector imports `od_binding` inside `run`; recovered fixed6 is not present in the failed original attempt, so the original validator cannot resolve it. V2 adds an exact recovered-checkpoint validator and holds that module alias across both collector composition and execution. `recovery_owner_v2.py` routes only readout to V2. Capture, combined corpus, trainer, tasks, seeds, clocks, and output namespace are unchanged. V1 READY and sources remain preserved and were never GPU-launched.

