---
id: leaf-mnli-positional-anchor-binding-v1-attempt002-recovery
status: cpu_qualified_not_launched
date: 2026-09-10
---

# Additive launcher-identity recovery

Attempt 001 failed before the collector and before any scientific request. The
outer wrapper loaded the qualified host-join wrapper but did not rebind that
module's `__file__`. The executed launcher therefore wrote the qualified
wrapper SHA `43e502…a73` into `SERVER_START.json`, while the allocation
lifecycle had registered this study's wrapper SHA `9cf9bf…eba`. Ownership
authentication and release correctly refused the mismatch.

Attempt 002 changes only the wrapper identity chain and output namespace. The
new outer wrapper rebinds the qualified module's `__file__` to the actual V2
launcher, and the owner registers that same path as both `SERVE` and
`ALLOCATION_SERVICE`. All 96 contexts, records, prompts, schemas, seeds,
sampling settings, scoring rules, model weights, workers and clocks are the
immutable attempt-001 inputs. There is no response reroll because attempt 001
made zero scientific requests.

The focused regression executes the complete wrapper entry through real
binding/config construction with only model process creation intercepted. It
then passes the resulting `SERVER_START`, `SERVICE_REQUEST`, inference command
and binding through the actual registered allocation `claim_service` logic.
It also checks the exact attempt-002 owner-to-collector argv and the retained
zero-request failure evidence. MAIN alone may accept or launch the recovery.
