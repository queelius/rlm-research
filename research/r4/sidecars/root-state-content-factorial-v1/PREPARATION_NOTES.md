# Preparation timing and prior failures

MAIN accidentally started initial native qualification before the CPU input freeze finished.
The original CPU_TESTS.json is retained: four tests passed and one failed because PLAN.json did
not yet exist. No model/GPU job was involved. Preparation then completed64 native prompts;
CPU_TESTS_FINAL.json is the subsequent complete-input qualification, with no source-data or
scientific selection change. READY requires this final qualification to pass.

The first pure-protocol red test initially contained an else-whitespace syntax typo. It was
fixed, the intended absent-protocol import failure was observed, and the implemented protocol
then passed all three focused tests. These are CPU implementation steps, not experimental runs.
