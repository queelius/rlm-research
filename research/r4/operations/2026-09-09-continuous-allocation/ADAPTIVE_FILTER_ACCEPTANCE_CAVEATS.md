# Adaptive-filter factual acceptance caveats

2026-09-09, additive after CPU seal and independent source review. Main requested
this note outside the frozen sidecar. No source, SPEC, READY, scientific behavior,
qualification outcome, model weight, task allocation or deadline is changed.
Main should bind this note and the independent review in any acceptance.

This applies to `sidecars/adaptive-filter-pilot-v1` READY SHA256
`582f90b85e67e47ff3ca2398d30db9bff79d117763d6f95465d1caa631bcda86`, SPEC
`1d4ee02d1356998d7705faac4c52d81282d1c25aa7c0c3f2694f1d56e0a443c3`, driver
`b129d5133acd2358dd21e6fe1d3e08360a0e7c40ab353308fee191afe26e72c0`.

## Inherited transient retries remain possible

Statements in the sealed documents/spec such as “no API retry” are too broad.
The accurate contract is **no new study-level retries, replacement episodes,
answer repair or automatic resampling**. Agent/SDK retry settings do not disable
the pinned nano runtime's separate transient retry wrapper.

The pinned nano `_call_model` calls `call_with_retries` around its ordinary
completion function. The inspected client wrapper allows an initial attempt
plus up to five retries, with delays15/30/60/90/120 seconds, for its declared
connection/timeout/server/not-found/rate-limit/response-validation failures.
Retries reuse the idempotency/model-request identity and add the retry-count
header. These inherited attempts remain subordinate to the same300-second
rollout timeout and absolute collection/work/allocation caps; no timer reset or
extra allocation is authorized. Not every theoretical retry can necessarily
fit inside the parent timeout.

Exact source seams inspected:

- `/project/alex_phd/research-cache/2026-09-08-literature/leaf-contract.7HPUr5/nano__engine.py`,
  `_call_model` around line698; SHA256
  `2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed`.
- `/project/alex_phd/research-cache/2026-09-08-literature/recursive-example.6xBrmx/src__rlm__client.py`,
  `_RETRYABLE`, `_RETRY_DELAYS` and `call_with_retries` around line72; SHA256
  `883ed932ebc79770b17c986bf959e27c5bf786d4eeb5016ce8ce8f331a84cbee`.

The operator adapter does not modify this client behavior. No transient retry
was observed in the saved final CPU success/filter/map-failure qualification;
the cancellation fixture is separately recorded. Future audits must count
actual native/transport attempt evidence, including repeated model-request IDs,
errors and unknown/request-only records. A logical request ID is not necessarily
one physical attempt. Do not claim universal retry absence from the zero
Agent/SDK setting or infer missing attempts as zero cost.

## The projection filename is not independent validation

`results.analyze` writes `INDEPENDENT_PROJECTION.json`, but that filename does
not confer independence. It is an **implementer-provided CPU projection**, using
the implementer's null/scoring/cost and logical-reference code. It is useful
evidence and preserves raw/native references; it is not itself independent
validation, a preregistered external audit or a confirmation of semantic
correctness. Independently assigned audit work must inspect the raw/native
artifacts and frozen method before making an independent-validation claim.
The filename is retained unchanged so the sealed source remains intact.

The independent reviewer separately checked the bounded scientific seams;
that source review also does not substitute for a future outcome/raw-wire audit.
No model inference or launch is authorized by this factual note.
