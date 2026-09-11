---
schema: rlm-living-claim-card-v1
id: "claim:warm-primitive-rl-transfer-limit"
question_id: "rq:controller"
updated_utc: "2026-09-10T10:57:00Z"
status: exploratory_negative_transfer_result
publication_readiness: not_publication_ready
novelty_claim: none_established
statement: Terminal-reward training made a practiced routine cheaper, but did not improve accuracy or teach the composed calculations in this pilot.
training:
  starting_root: fixed_operator_sft24
  fixed_child: c32
  tasks: primitive_count_distinct_users_weight_sum
  attempted_episodes: 192
  admitted_episodes: 184
  positive_episodes: 125
  selected_mixed_group_episodes: 84
  scheduled_windows: 8
  actual_optimizer_updates: 7
  final_window: no_update_all_three_groups_have_constant_positive_reward
  root_action_target_tokens: 21313
  optimizer_region_seconds: 219.2305
  checkpoint_selection: last_committed_7_not_best
evaluation:
  arms: [unchanged_sft24, last_committed_rl7]
  context_clusters: 8
  planned_per_arm: 48
  strict_correct: [15, 13]
  native_available: [38, 45]
  source_observable: [42, 47]
  primary_NULL: [10, 3]
  paired_difference_bounds_per_48: [-12, 1]
  primitive_correct_per_24: [10, 7]
  primitive_paired_difference_bounds_per_24: [-7, -2]
  composed_correct_per_24: [5, 6]
  composed_faithfully_computed_per_24: [0, 0]
  primitive_faithfully_computed_per_24: [7, 8]
  primitive_correct_and_faithful_per_24: [6, 5]
  primitive_faithful_but_wrong_child_labels_per_24: [1, 3]
  nonzero_correct_per_41: [11, 8]
  nonzero_paired_difference_bounds_per_41: [-11, -1]
  final_physical_calls: [408, 229]
  all_available_programs_reviewed: 83
  serial_order: unchanged_then_trained
  exposed_contexts: true
  author_recovery_analysis_overlap: true
cost:
  combined_physical_attempts: 1684
  returned_native_completions: 1673
  unknown_usage_attempts: 11
  known_input_tokens: 3519068
  known_output_tokens: 182754
  known_cached_input_tokens: 3306304
  actual_parent_execution_seconds_including_failed_original: 3889.1546
  calendar_seconds_first_launch_to_final_exit: 5924.6740
evidence:
  report: ../analyses/root-sft24-terminal-rlvr-live-2026-09-10/REPORT_V4.md
  report_sha256: b8e5821052693d9c86704fd6ba9e291e106aa7609521ff43bb876f40e2643dfd
  final_ready_sha256: cd086440f8264babf676f767a710ad76781fbfbec1f9fae42e082405295f5006
  main_final_pin_verification_epoch: 1789037620.9964862
  main_unique_pins: 11258
  main_verified_bytes: 2994909705
  main_pin_errors: 0
  main_review_scope: Full final report and native parser; reproduced all seven checkpoint checks. Runtime_port reviewed every available final program.
next_comparison: Teach varied composed operations and task parameters directly through genuine executed demonstrations, then evaluate fixed-step weights without a guide on separately reserved contexts.
---

# More training reward did not mean better task-sensitive computation

The starting model already knew a basic routine: ask the child model to label
records, calculate something from the returned labels, and answer. We gave it
terminal rewards on record counts, distinct-user counts and weight sums. Seven
updates actually changed its weights. The eighth scheduled batch produced no
reward differences within any question group, so it correctly made no update.

On the fixed 48-question comparison, correct answers fell from 15 to 13. The
trained model made 229 physical requests instead of 408 and more often returned
an answer. This is a cost/behavior change, not an accuracy improvement. Its basic
questions declined from 10/24 to 7/24; even the declared missing-outcome bounds
preserve a negative difference on that finite panel.

Most importantly, none of the eleven correct composed answers across both
models performed the complete requested operation. Some summed all weights
when asked for the largest user's total; others omitted a condition. The wrong
operation happened to give the right number. Several trained programs omitted
user u3 even when the question explicitly included all four users.

The audit separately identifies faithful calculations of mistaken child labels.
Those are not root arithmetic failures. It also preserves six authenticated
empty model replies at the old reader's None-versus-empty-string boundary:
they remain primary NULL under the frozen rule, with observed empty failures
reported as a separate diagnostic. They are not six infrastructure failures.

This is one exposed eight-context pilot, with unchanged evaluated first. It
does not show that RL cannot learn composition: composition was not included
in its reward-training tasks. It does argue against simply extending the same
primitive recipe. The next curriculum teaches those operations directly while
varying their parameters, and tests whether that helps without a guide.
