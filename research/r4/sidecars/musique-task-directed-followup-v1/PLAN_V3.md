# Attempt003: exact engine-command ownership repair

Goal: run the unchanged 132-call report experiment with the actual V2 engine entrypoint authenticated during both initial ownership and release. Attempt002 failed before any scientific request because the inherited lifecycle still expected `bin/inference @ config`; its same check then prevented release. MAIN independently authenticated and terminated the owned group, preserving all failed receipts.

1. Add `lifecycle_v3.py`, `owner_v3.py`, `study_v3.py` and one focused actual-start/claim/release CPU fixture. Bind exactly `python engine_entry_v2.py @ config`; retain all launcher hashes, GPU, binding, PID/start/UID/PGID and final real-dispatch checks. Exercise rejection of a wrong engine command and safe exception details. Add a seal and CPU receipt.
2. MAIN reviews READY_V3 and owns any later launch. Attempt003 is unused; no agent GPU authority. Caps remain science1320/owner1700/external1800; V1/V2 sources, inputs and outputs remain immutable. No retries, template/math/kernel changes, answer selection or lifecycle framework refactor.

Only inherited process observation, launch and network readiness are replaced by bounded fixture doubles; real claim/release functions and on-disk ownership/stop receipts are exercised. This is not a GPU cleanup test. Sanitized tracebacks omit locals and redact credential-valued environment variables.
