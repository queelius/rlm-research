---
schema: rlm-living-claim-card-v1
id: "claim:task-description-access-not-exercised"
question_id: "rq:sufficient-interface"
updated_utc: "2026-09-10T09:40:00Z"
status: exploratory_intervention_not_exercised
publication_readiness: not_publication_ready
novelty_claim: none_established
statement: Supplying a separate task-description file did not make this policy retrieve and use that description.
evaluation:
  fixed_root: operator_sft24
  fixed_child: c32
  context_clusters: 8
  planned_per_arm: 24
  arms: [unchanged, prose_file, JSON_file]
  strict_correct: [2, 4, 4]
  native_available: [16, 17, 15]
  primary_NULL: [8, 7, 9]
  retained_episode_graphs: 65
  observed_task_file_reads_in_retained_graphs: 0
  available_added_file_endpoints: 32
  strict_successes_manually_reviewed: 10
  faithful_requested_operation_and_scope_among_strict_successes: 0
  wrong_operation_nonzero_successes: 6
  zero_coincidence_successes: 4
  all_available_finals_manually_reviewed: 48
  faithful_requested_operation_and_scope_among_available: 0
  available_endpoints_with_actual_child_calls: 48
  child_calls_within_available_final_paths: 72
  all_available_fidelity_review_timing: additive_post_outcome
  source_exposure: All contexts previously evaluated; child-training and catalog exposure also disclosed.
cost:
  physical_attempts: 1019
  root_attempts: 753
  child_attempts: 266
  returned_completions: 1012
  known_input_tokens: 3059757
  known_output_tokens: 95782
  known_cached_input_tokens: 2903552
  unknown_usage_attempts: 7
  outer_wall_seconds: 1060.8100007101893
evidence:
  report: ../analyses/root-operator-task-spec-interface-live-2026-09-10/REPORT.md
  report_sha256: b9ebfa96deb5497b03441b3237379afe4763fa0cdaee7b78d3d94b90854e1c03
  final_sha256: d87ccb9dbc08a85761f495d66bf60d9bdd2e29108047ecc5adb6a623e231901f
  main_verified_unique_pins: 11128
  main_verified_bytes: 1634728297
  main_verification_epoch: 1789031522.5045755
  main_pin_errors: 0
  main_pin_conflicts: 0
  additive_report: ../analyses/root-operator-task-spec-interface-live-2026-09-10/ALL_AVAILABLE_SEMANTIC_RETROSPECTIVE.md
  additive_report_sha256: d9e51412dd379c9b7fb41d9720a715fd8b0e6002cf7a022c2f3fde2dd92025d4
  additive_seal_sha256: 98a2781712312697718f4a8c2cb03ae30e8ff36b5e8eb56bd6b1e5e1a9700ad6
  wording_correction: ../analyses/root-operator-task-spec-interface-live-2026-09-10/RECOMMENDATION_CORRECTION.md
  wording_correction_sha256: 8461b6bc18a10a4be38d1755373f847ade3a3182aa8d9c84b37665941d944d97
  additive_main_verification_epoch: 1789033203.7574017
  additive_main_pin_errors: 0
---

# Providing a task file did not make the model use it

We added a second description of the requested calculation, either in a prose
file or in a JSON file. The original question and record files stayed unchanged.
The extra descriptions supplied task parameters, not instructions for solving
the task. Neither added file was read in the 65 recorded episode graphs.

The raw scores were 2, 4 and 4 correct answers out of 24 planned tasks. Only
16, 17 and 15 final answers were available, respectively. All ten correct
answers used an incorrect operation or scope, or coincidentally returned zero.
These remain correct under the original answer-based metric, but they do not
demonstrate correct execution of the requested calculation. A separate
post-outcome review now covers all48 available finals: none executes the
requested operation and scope, although all48 made actual child calls.
The mechanism failure is therefore not confined to the coincidentally correct
answers, nor is it simply failure to obtain any subtask evidence.

The practical lesson is to check whether a new feature is actually used before
interpreting its effect on answers. This experiment does not show that task
parameters are unhelpful when the model actually sees and uses them. Seven
episodes also lack a retained graph, so their behavior is not reconstructed.

The completed procedural-card comparison puts general algorithms directly in the
model's input. That tests a different question: whether explicit instructions
enable correct execution. Its question and record bytes remain unchanged;
the added instruction text changes the prompt context, not the task itself.
A separate directly rendered parameter comparison
would be needed to isolate access to task parameters. Neither would by itself
demonstrate learned or previously unseen problem decomposition.

This is a small, adaptively selected, already-exposed panel. The overlapping
missing-answer bounds and dependent contexts do not establish a general
accuracy advantage for either added-file format.
