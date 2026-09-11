# Additive CPU qualification history

All attempts use authored fixture tokens, never model-generated science or measured behavior logprobs. No model service/GPU launch occurred. Historical source seals were untouched.

- qualification-001: stopped before environment creation/provider calls because SingleAgentEnv requires a registered seed taskset. Directory retained; the exception was observed in the tool transcript.
- qualification-002: stopped before provider calls because the old Oolong plugin registration was not importable without the prior task's dependency bootstrap. Replaced that dependency with the new sidecar's minimal join_taskset registration; no Oolong data/helper is loaded. Directory retained.
- qualification-003: three native setup attestations retained, but zero provider requests; ACP bridge lost its subprocess because PYTHONPATH incorrectly applied the RLM bootstrap to the bridge's separate UV interpreter. Raw failed episodes and empty PROVIDER_REQUESTS.json retained.
- qualification-004: actual present/absent/unadvertised-tool fixture passed in20.087s with4 authored provider calls, one IPython observation, no disabled execution and paired messages/files equal.
- qualification-005: expanded actual fixture passed in34.613s with5 authored provider calls, including root→child→root. Strict full-branch native final verification passed for present/absent; the unadvertised tool action had no native final and operational0. Explicit policy-failure accounting was then tested against this retained authentic record.
- qualification-006: final source-matching native fixture, separately recorded in RESULT.json. Its own pass/failure and hashes, not this history note, are authoritative.
- First readiness round-trip rejected READY.json because insertion-order identity hashing disagreed with sorted-key storage. That draft is preserved unchanged and is not accepted. Canonical metadata identity hashing and an exact write/read regression were added; actual request/text serialization and protocol inputs are unchanged. Owner and verifier exclusively use additive READY_V2.json.
- qualification-007: repeated current-source native fixture passed in40.841s with5 authored calls; CPU_TESTS_FINAL_V2.json records18 passing focused tests after the identity correction.

Focused tests were written before their protocol/native/owner/scoring implementations. Early missing-component failures were observed. The collector-composition test initially used a function in place of httpx.AsyncClient, which broke an upstream runtime annotation during lazy imports; the test double was corrected to a real AsyncClient subclass. A service-entry test initially shadowed its importlib name; that test-only error was corrected before the expected missing-wrapper failure was demonstrated. These are CPU preparation defects, not model findings.

Final CPU_TESTS.json records the fresh complete focused-test invocation and exact source hashes. Temporary test directories are managed by tempfile.TemporaryDirectory and contain only authored fixtures; no scientific attempt output was created.
