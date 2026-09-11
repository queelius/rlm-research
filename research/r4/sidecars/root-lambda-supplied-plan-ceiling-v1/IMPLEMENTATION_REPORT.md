---
id: root-lambda-supplied-plan-ceiling-v1-implementation
status: cpu_qualified_no_gpu_launch
date: 2026-09-10
---

# Supplied-plan ceiling CPU handoff

The package freezes all four prior scale clusters at sizes 64 and 256: eight
episodes, forty complete 32-record child batches, and one fresh fixed seed per
episode. The largest prompt is 1,850 tokens, leaving the frozen 2,048-token
output allowance inside 8,192 tokens.

The collector reuses the qualified four-worker native c32 path. It accepts only
whole strict ID maps, retains native request/response/result checkpoints and
costs, and invokes the deterministic public J1 reducer only when every batch in
an episode is complete. Private host labels are used only for post-response
diagnostics. There are no root-model calls, retries, repairs, or gold-fed
requests.

Focused CPU qualification covers exact inventory/record boundaries, gold
isolation, incomplete-map rejection, the public reducer, a genuine nonempty
native transport, and registered service-wrapper/config-to-launch composition.
MAIN alone owns any GPU launch.
