---
schema: openai-mrcr-procedural-sft32-onpolicy-t1-repair-v2
failed_attempt: outputs/attempt-001
new_attempt: outputs/attempt-002
scientific_change: none
---

# T1 native transport repair

Attempt 001 is an infrastructure failure, not a temperature result. Its service was
healthy and exposed `/inference/v1/generate`, but 238 recorded interception attempts
ended in `ProviderError("Connection error.")`; the engine saw zero generate POSTs and
no episode had a verified initial prefix. MAIN stopped the collector after 630.94 s and
the owner released the service. The preserved provider wrapper did not retain the
underlying `OpenAIError`, so the precise socket-level cause is unavailable.

The V1 hand-written `ModelContext` serialized to the same client settings as the proven
T0.5 constructor. Therefore this repair does not claim that a differing field caused the
failure. It removes that independently reconstructed boundary anyway: V2 calls the exact
proven T0.5 `model_context`, then immutably changes only `sampling.temperature` to 1.0.
The schedule, records, seeds, checkpoint32, terminal-strip-disabled hooks, prompts, turn
and token caps, child binding, and metrics remain fixed.

The focused CPU fixture runs one authentic frozen task through `env.run_slot`, the
interception server, renderer, and `TrainClient` to a local native provider. It requires
an authenticated POST to the root-mounted `/inference/v1/generate`, temperature 1.0,
the expected checkpoint32 alias, and the exact frozen initial token prefix. This is a
transport-boundary fixture; it makes no model-quality claim.

