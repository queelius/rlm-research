---
schema: rlm-living-claim-card-v1
id: "claim:acquisition-is-not-retention"
question_id: "rq:sufficient-interface"
updated_utc: "2026-09-10T08:28:00Z"
status: exploratory_mechanism_lead
publication_readiness: not_publication_ready
novelty_claim: none_established
statement: Obtaining every evidence batch did not ensure that the controller retained and combined those batches.
evaluation:
  fixed_root: operator_sft24
  fixed_child: c32
  parent_clusters: 4
  planned_per_size: 8
  sizes: [16, 128, 256]
  strict_correct: {size16: 4, size128: 0, size256: 0}
  native_available: {size16: 8, size128: 4, size256: 0}
  all24_attempted: true
  nonzero_gold: 24
  verified_requested_complete_map_reductions: 8
  correct_requested_complete_map_reductions: 4
  wrong_requested_complete_map_reductions_with_child_error: 4
  endpoints_with_returned_child: 22
  endpoints_with_at_least_two_child_requests: 7
  verified_executed_multi_acquisition_accumulations: 0
  size256_full_disjoint_acquisition_but_overwritten_paths: 2
  source_exposure: Root-new under the named inventory; child-training and catalog exposed.
cost:
  physical_attempts: 255
  returned_native_completions: 250
  child_attempts: 74
  child_returns: 72
  unknown_usage_attempts: 5
  known_input_tokens: 797176
  known_output_tokens: 44452
  known_cached_input_tokens: 656896
  outer_wall_seconds: 575.6623673066497
evidence:
  report: ../analyses/root-operator-scale-state-live-2026-09-10/REPORT.md
  report_sha256: f3b581b651d485b91055f82cb08f095f1020db66d37d0f59210eafa4a35251d4
  final_sha256: fa6b759578f314b08f33ed0d0ec302a3e53dd2176caaa22df954b65871fa8ce5
  main_verified_unique_pins: 6695
  main_pin_errors: 0
---

# Gathering every batch is not enough

In two256-record tasks the controller obtained labels covering every record,
using16 batches of16 and8 batches of32. But each new result replaced the previous
map. Neither task produced an executed calculation combining the batches.
The evidence existed in the recorded interaction without existing as usable
combined state in the controller's calculation.

This is a concrete failure mechanism, not a claim that it explains every large
task failure. Other failures involved incorrect child labels, wrong user scopes
or operations, invalid code/tool output, and context-limit rejections. Four
correct computations over complete child maps still gave wrong dataset answers
because those child predictions were wrong.

The next proposed harness test retains previously decoded evidence when a new
batch arrives. It must supply no unacquired labels, reduction algorithm or answer,
and must distinguish genuine child evidence from model-written substitutes.
It may increase the amount of text printed into the context; that cost belongs
in the result. A successful harness-assisted calculation would not by itself
show that the model learned general decomposition.

The experiment has only four parent contexts and fixed model/interface/token
budgets. Changing size also changes records and difficulty. Missing finals at
large sizes are retained, not repaired or treated as random missing data.
