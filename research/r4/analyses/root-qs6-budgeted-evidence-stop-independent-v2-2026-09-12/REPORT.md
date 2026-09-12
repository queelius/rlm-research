---
title: Independent budgeted-evidence / stop screen outcome
date: 2026-09-12
status: completed_cpu_analysis
---

# Independent budgeted-evidence / stop screen outcome

Observed 48/48 endpoints and 24/24 complete pairs. Budgeted versus eager had 1 wins, 0 losses, 2 ties, and 21 unknown pairs on host-gold exactness.

The report keeps three notions separate: exactness against host gold, agreement with the actual saved helper map, and consistency between `finish()` state and the causal final answer. Map agreement is not proof that the saved labels caused the program's answer.

Evidence savings are counted only when API state is present and the static action audit is eligible. Missing finalize state is unknown, never zero. A flagged direct backing-map or module/introspection access retains raw accuracy but is ineligible for evidence-savings and faithfulness claims; an eligible audit is still not a sandbox guarantee.

## Conditions

- `eager_all16`: 4/6 observed finals gold-exact; 4 supplied-map-exact; 5 finish-consistent; 1 audited zero-request direct paths; 0 flagged bypasses; 0 unknown evidence states; 24 unavailable endpoints; known acquired-ID range 0–16; known physical cost `{"cached": 180560, "input": 196835, "output": 38824, "uncached": 16275}`; unknown-cost ledger `{"cached": 0, "input": 0, "output": 0, "uncached": 0}` with 0 coordinates lacking a cost object.
- `budgeted_as_needed`: 3/5 observed finals gold-exact; 3 supplied-map-exact; 4 finish-consistent; 4 audited zero-request direct paths; 0 flagged bypasses; 2 unknown evidence states; 24 unavailable endpoints; known acquired-ID range 0–12; known physical cost `{"cached": 262448, "input": 285006, "output": 46839, "uncached": 22558}`; unknown-cost ledger `{"cached": 2, "input": 2, "output": 2, "uncached": 2}` with 0 coordinates lacking a cost object.

## Six frozen task families

- `J1`: eager_all16 0/4 gold-exact; budgeted_as_needed 0/4 gold-exact.
- `J2`: eager_all16 0/4 gold-exact; budgeted_as_needed 0/4 gold-exact.
- `M1`: eager_all16 1/4 gold-exact; budgeted_as_needed 0/4 gold-exact.
- `M2`: eager_all16 1/4 gold-exact; budgeted_as_needed 1/4 gold-exact.
- `T1`: eager_all16 1/4 gold-exact; budgeted_as_needed 2/4 gold-exact.
- `T2`: eager_all16 1/4 gold-exact; budgeted_as_needed 0/4 gold-exact.

## Simplified examples

These omit task text, record IDs, labels, and raw generated code. They describe only frozen family/arm and accounting outcomes.

- Successful/eligible example: `{"access_audit_status": "eligible", "access_flags": [], "acquired_id_count": 16, "arm": "eager_all16", "classify_call_count": 1, "endpoint_reason": "ValueError: first prompt/model mismatch", "family": "M1", "final_status": "observed", "finish_consistent": true, "gold_exact": true, "supplied_map_exact": true}`
- Failure/unknown example: `{"access_audit_status": "eligible", "access_flags": [], "acquired_id_count": 0, "arm": "budgeted_as_needed", "classify_call_count": 0, "endpoint_reason": "ValueError: first prompt/model mismatch", "family": "J1", "final_status": "unavailable", "finish_consistent": false, "gold_exact": null, "supplied_map_exact": null}`

## Interpretation boundary

Both arms still choose direct versus delegated solving and when to finish; their supported classification action sets differ. These are two research-exposed contexts with replayed, sometimes wrong helper labels and zero actual child model calls. No child speedup, fresh generalization, causal information-use, or learned routing claim follows from this screen.

The promotion threshold was frozen in the launch manifest and was not adjusted after outcomes.
