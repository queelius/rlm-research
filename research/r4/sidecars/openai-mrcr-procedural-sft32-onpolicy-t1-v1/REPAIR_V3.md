---
schema: openai-mrcr-procedural-sft32-onpolicy-t1-repair-v3
failed_attempts: [outputs/attempt-001, outputs/attempt-002]
new_attempt: outputs/attempt-003
scientific_change: none
---

# T1 role-audit repair

Attempt-002 falsified the V2 transport-constructor hypothesis: a fresh process using
the same repaired context successfully reached the live engine, while the scientific
collector still recorded only `ProviderError("Connection error.")` and zero provider
returns. Inspection of the exact executable hook found the pre-network cause:
`root-only-credit-v1/native_routing.py` asserts physical sampling temperature 0.5 in
its HTTP request event hook. Every legitimate T1 request raised there before the
engine POST. The outer TrainClient error boundary hid that hook exception as a generic
connection error.

V3 loads the pinned role hook and changes exactly that audit expectation from 0.5 to
1.0. It keeps the V2 proven context constructor, all 32 inputs, checkpoint32, seeds,
prompts, terminal-strip-disabled condition, turn/token limits, child binding, and
metrics unchanged. The CPU fixture installs both the actual role hook and native
capture around a real frozen-task `env.run_slot`, and observes a returned authenticated
`/inference/v1/generate` request at temperature 1.0. It uses no GPU or model weights.

