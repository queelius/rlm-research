---
schema: helper-agnews-fresh512-endpoint-design-v1
status: CPU-only-preparation
arms: [c32, rl_step8, sft_step8]
records: 512
physical_calls_per_arm: 128
request_size: 4
temperature: 0
owner_seconds: 900
external_seconds: 1000
model_queries_during_preparation: false
---

# Shared fixed fresh512 endpoint

Use the broader frozen heldout512 and its exact128 B4 native request bodies, ID order, definitions, four-label schemas and seeds202609126000–202609126127. Restore schema property order from `schema_ordered_json`. All arms use the same batch-invariant service configuration and fixed child alias, changing only the authenticated child checkpoint. Root/base weights remain fixed.

Each trained arm requires its exact final step8, complete source/state/optimizer/commit eligibility and no checkpoint selection. MAIN must fix compared trained endpoints before any heldout model queries; a write-once `ENDPOINTS_FIXED.json` pins the qualified endpoint checkpoint hashes. The c32 baseline may then be collected once and reused only if its complete128/512 coverage, exact schedule, service configuration, kernel marker, clean release and c32 binding match the other arm. Older AG256/old-panel baselines are not reusable.

The RL source is the sealed native/HF eight-step trainer plus its additive V2 admission-only repair (READY SHA256 `e9dcccfdcb45a092d5ad85d4a161266f85c3f8f3cbe2f3a494aaec46edeaabb5`). The SFT source was subsequently sealed and its actual `sft_study_v2.endpoint()` interface reviewed before binding: READY_V2 SHA256 `088f4b7e366582365f62d226fac9e3677957e0f32c54e534f5d000ea3bce9753`. Each trained arm has a separate conditional READY, full eight-link eligibility, actual optimizer-counter checks and exact child/root binding verification.

Save exact request body bytes before every send; save full response bytes (including HTTP errors), status code, decoded response, token IDs, ordered prediction, finish reason, usage and hashes for every returned call. Preserve failures and the unattempted tail. No retries, fallback answers or subset-selected completion. Calls are serial, bounded by900 owner/1000 external seconds, with cleanup reserve and the actual EngineCore batch-invariant marker required after release.

Primary accuracy exists only with complete512 predictions; missingness is never silently wrong. Always report correct/available, unavailable IDs, invalid/request-error/unattempted counts, per-class planned128/available/correct/confusion, and observed token subtotals with unknown-usage counts. Classification differences are paired on record IDs; the128 shared four-record requests are the uncertainty clusters. Descriptive paired cluster bootstrap uses2000 replicates and fixed seed202609127999. Do not use a512-independent-item significance claim or pick a best checkpoint/arm. Report all predeclared comparisons and training/evaluation costs separately.

One focused fixture uses the actual frozen512 inventory, exact schema/token decoding and literal synthetic full/per-class/missing accounting; it also checks paired one-loss behavior. No GPU service or heldout inference is used for this fixture.
