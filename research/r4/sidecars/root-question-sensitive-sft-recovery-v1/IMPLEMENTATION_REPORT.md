# Question-sensitive SFT72 recovery V2 handoff

Status: CPU-ready; no GPU/model/service launched. MAIN owns acceptance and execution.

- Entry: `recovery_owner_v2.py`; exact unused output: `outputs/attempt-001`.
- READY V2 identity: `d7c78056e3919b576badbd40aa0c80fdbe1774fe854269d35c01651de46ffcc3`.
- V1 is preserved as a preacceptance source snapshot and was never launched. V2 only repairs the recovered-checkpoint binding validator used by the lazily imported free collector.
- Frozen source boundary: original indices 0–64 are reused; 65 is an explicit retry after an evidenced pre-request deadline failure; 66–71 are first attempts after original unstarted slots. No generated response is resampled.
- Index 65 evidence includes zero coordinate-local physical, role-audit, and typed-audit records. Its retained failure occurred during deadline cancellation/cleanup. The 65 complete predecessors each have `TEACHER.json`, `EPISODE.json`, and four physical transport records; their corpus authentication is repeated before training.
- Recovery capture remains serial and hard-coded to `[65:72]`. Combined corpus admission requires all 72 exact coordinates, unique actual c32 child receipts, prefix verification, and the three authored current-action turns.
- Training is unchanged fixed24/c32, fresh Adam0, six full72 passes, original masks/weights/gate/seed, fixed checkpoint6. Readout is recovered fixed6 only on the original dev8/protected72; original unchanged80 is terminal-gated, pinned, and never rerun.
- Recovery budget is 5400 outer / 5370 owned / 5220 work seconds. It refuses execution unless the original actual owner elapsed plus 5400 is at most 10800 seconds.
- The cost ledger unions original partial capture, original baseline, recovery capture, and recovery readout separately. It preserves physical attempts, HTTP responses, choice-bearing completions, usage unknowns, and the fact that billing is not measured.
- Focused qualification: `python -m pytest -q -p no:cacheprovider test_recovery.py test_recovery_v2.py` → 6 passed; `python recovery_owner_v2.py verify` → exact READY identity.

The original attempt was still running its baseline phase at the V2 seal time, so no original baseline outcomes or terminal-dependent recovery binding were consulted during implementation.
