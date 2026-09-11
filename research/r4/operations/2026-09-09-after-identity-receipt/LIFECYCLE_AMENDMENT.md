# Pre-launch operational amendment

September9,2026, approximately06:39UTC. Preserve the frozen receipt sidecar,
SPEC90000411… and READY1eba4903… unchanged. Launch through `receipt_driver.py` in
this operation. This is not a scientific condition or an outcome-dependent change.

The independent-root run stopped when a descendant exited between reading `/proc`
and calling `os.getpgid`. The receipt runner inherits that same observer. Reuse the
already tested `observe_or_absent` helper from the pinned continuation driver,
wrapping only the inherited campaign's `process_identity`. FileNotFoundError and
ProcessLookupError mean absent; PermissionError and all other errors propagate.
Existing UID/PID/start/group checks and owned-only cleanup remain unchanged.

The wrapper verifies the frozen original receipt driver, READY and continuation
driver hashes before import. All source files are additionally bound by the
operation's main acceptance manifest. Original receipt verification still runs.
The original run output links its original READY/SPEC; the parent operation's
COMMAND, START, PLAN and acceptance link this exact operational amendment.
No old artifact is overwritten, and no source under a live process is edited.

Two narrow tests first failed because the new wrapper did not exist. They exercise
both exception propagation and the actual frozen receipt lifecycle module after
its install function, proving that the intended shared observer is patched.
The unchanged seven receipt tests and wrapper verification are run separately.
No additional model call, retry, grammar, prompt, reward, seed or budget is added.
