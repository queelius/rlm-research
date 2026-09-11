---
schema: rlm-living-claim-card-v1
id: "claim:operator-composition-transfer-limit"
question_id: "rq:controller"
updated_utc: "2026-09-10T06:12:00Z"
status: exploratory_transfer_limit_with_diagnostic_followups
publication_readiness: not_publication_ready
novelty_claim: none_established
statement: Learning to acquire labels and perform a local routine did not establish reliable execution of new query compositions.
intervention:
  checkpoints: [24, 6]
  child_policy: fixed_c32
  interface_changed: false
  training_during_readout: false
evaluation:
  planned_per_policy: 48
  context_clusters: 8
  primitive_questions: 24
  composed_questions: 24
  nonzero_questions: 41
  strict_correct: {sft24: 9, sft6: 6}
  native_available: {sft24: 28, sft6: 31}
  native_null: {sft24: 20, sft6: 17}
  primitive_strict_correct: {sft24: 5, sft6: 3}
  composition_strict_correct: {sft24: 4, sft6: 3}
  nonzero_strict_correct: {sft24: 6, sft6: 1}
  verified_task_faithful_correct: {sft24: 2, sft6: 0}
  verified_task_faithful_composition_correct: {sft24: 0, sft6: 0}
  faithful_success_context_clusters: 1
  conservative_correct_bounds: {sft24: [9, 29], sft6: [6, 23]}
  source_exposure: New root-input contexts under the named inventory; all child-training and catalog exposure disclosed.
cost:
  physical_attempts: 1083
  native_returns: 1072
  unknown_usage_attempts: 11
  known_input_tokens: 3353659
  known_output_tokens: 139250
  known_cached_input_tokens: 3216608
  owner_wall_seconds: 1460.9429307
  billing_and_gpu_kernel_time: unmeasured
evidence:
  report: ../analyses/root-operator-composition-transfer-live-2026-09-10/REPORT.md
  report_sha256: 80a955add6e0964ba1ef1ccd4308bad1a37ab267458e693b1fa466dbc64bdb90
  final_seal_sha256: 4c27e028b5c247d5f00614d8fabe3135cb46896d54c6eb4f134881321eac5824
  main_verification: ../operations/2026-09-09-allocation-5780/MAIN_VERIFICATION_0612.json
audit_timing:
  method_and_parser: Sealed before launch.
  manual_operator_review: After outcomes; all59 available endpoint programs and all37 available composed traces reviewed.
next_comparisons:
  - ../ideas/2026-09-10-operator-task-spec-interface72.md
  - ../ideas/2026-09-10-sft24-terminal-rlvr-warmstart-design.md
  - ../ideas/2026-09-10-operator-scale-state24.md
---

# Acquiring evidence is not the same as choosing the right calculation

The stronger checkpoint often obtained a complete set of child predictions,
but then substituted a simpler calculation for the requested one. For example,
it sometimes added every target record's weight when asked for the largest
user-level total. Those numbers can coincide when only one user contributes.
All four correct composed answers from the stronger checkpoint used the wrong
operator. They count as correct answers, but not as correct decompositions.

Only two successes, a count and a weight sum in one context, were verified as
the requested computations. Another correctly executed count gave the wrong
answer because a child label was wrong. These distinguish errors in evidence
acquisition from errors in choosing and executing the task.

This study does not show a reliable overall advantage on the new panel:
17 early and20 later finals are unavailable, and conservative bounds overlap.
There are eight context groups, not48 independent examples. It does not prove
that extra training caused the transfer failure or that a different interface
will fix it.

The next tests ask whether explicit task parameters help and whether learning
from actual rewarded attempts improves the stronger starting routine. Both
must report real operator/scope/state use separately from answer correctness.
The exposed panel may guide exploration; it cannot certify a selected final
method without another independently chosen test panel.
