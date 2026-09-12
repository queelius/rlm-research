# READY supersession

`CPU_READY.json` is an unlaunched failed CPU draft: its focused actual-input test incorrectly
required at least one child turn, while the frozen six complete groups contain zero child turns.
No training or model call used it. `CPU_READY_V2.json` is authoritative; it records the actual
zero-child inventory while continuing to require zero child loss.
