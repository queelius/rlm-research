# Observed pre-seal fixture repair

The expanded first seal fixture completed the six-response depth-2 traversal, the blocked seventh attempt and question-only request, then failed because its overlong-input assertion expected the explicit cap name. The request hook had refused at10032 prompt-plus-output tokens before transport, but the SDK translated its exception into `ProviderError: Connection error.` The preserved `CPU_TESTS.json` and `cpu-fixture/` show that failure, not a passing qualification.

The narrow fix restores only an already-recorded, source-owned `status=refused` reason at the outer native-client boundary with status400, while retaining the original error in the raw audit. Ordinary provider/transport errors are unchanged; no request is retried, no input is truncated, and the budget is not loosened. `CPU_TESTS_V2.json` is the fresh final two-fixture qualification. No model weights or GPU were used.
