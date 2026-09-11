# Independent V3 closure

Read-only review after V1/V2 findings; no experiment source changes. Read all `id_owner_v3.py` and V2→V3 execution-test differences. Fresh `python -m pytest -q test_execute_v3.py` passed 5 tests in 0.26 s using the qualified native environment.

Verdict: ready within the declared exploratory execution/scoring scope, with explicit accounting limitations below. The cleanup deadline is now `min(owned, stage_end, now + 30)`. Probe orphan RESPONSE bodies contribute their actual known usage; REQUEST-only coordinates remain prepared/attempt-unknown. Returned choice payloads are separated from native-final endpoints; the ledger explicitly does not recompute native-call authentication. No score synthesis or availability promotion is introduced. V1/V2 remain preserved.

Residual descriptive limitations (not execution/scoring blockers): `probe.physical_requests` counts RESULT-declared attempts, not the union-total including orphan responses. `response_proven_attempts` separately retains those responses; these overlapping counters must not be added blindly. The free ledger's `slot_taxonomy` enumerates top-level record files and omits directories containing only physical records, although physical costs and the full planned owner inventory retain/classify them. A later outcome audit must independently union exact coordinate/request identities and use the complete planned inventory. `returned_completions` is an alias for nonempty choice payloads, not independently authenticated model completions; HTTP errors are not sampled completions. Billing remains unknown.

No further code change requested for acceptance. Independent outcome authentication remains necessary and is not supplied by these CPU tests.
