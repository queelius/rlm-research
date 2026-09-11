---
schema: rlm-living-claim-card-v1
id: "claim:question-sensitive-executed-composition"
question_id: "rq:controller"
updated_utc: "2026-09-10T20:22:00Z"
status: strong_local_exploratory_result_sampling_and_metadata_transfer_audited
publication_readiness: promising_requires_transfer_and_training_replication
novelty_claim: none_established
statement: Training on varied questions taught the small controller to choose and execute composed calculations, not merely repeat one fixed routine.
training:
  starting_root: fixed_operator_sft24
  final_adapter_sha256: 4d8287537a9ff3d8e33bc0314f64315dee06e71b801257b389dab8b667e27aca
  fixed_child: c32
  demonstrations: 72
  authored_root_actions: 216
  actual_updates: 6
  selection: fixed_last_checkpoint_not_best
  training_checkpoint_seconds: 738.7828965
  training_phase_seconds: 776.7349396
evaluation:
  protected_context_clusters: 8
  planned_per_arm: 72
  strict_correct: [28, 57]
  available: [64, 71]
  requested_calculation_performed: [18, 62]
  correct_and_faithfully_calculated: [15, 52]
  strict_paired_missing_outcome_bounds: [21, 30]
  faithful_correct_paired_missing_outcome_bounds: [29, 38]
  composed_planned_per_arm: 48
  composed_correct: [13, 38]
  composed_calculation_performed: [1, 38]
  composed_correct_and_faithful: [1, 33]
  trained_faithful_wrong_explained_by_child_labels: 10
  all_available_paths_manually_reviewed_including_development: 149
  strict_and_faithful_correct_improve_in_all_contexts: true
sampling_replication:
  status: native_and_semantic_audits_complete_with_comparability_erratum
  same_tasks_new_sampling_seeds: true
  serial_order_reversed: true
  strict_correct: [25, 51]
  available: [62, 70]
  strict_paired_missing_outcome_bounds: [16, 28]
  composed_correct_per_48: [12, 33]
  primitive_correct_per_24: [13, 18]
  requested_calculation_actually_performed: [19, 60]
  performed_and_strict: [15, 49]
  performed_and_strict_difference_bounds: [24, 36]
  sampled_but_unsuccessfully_executed_baseline_paths_excluded: [90, 92, 124]
  not_independent_training_or_new_context_replication: true
metadata_transfer:
  status: native_and_all_path_semantic_audits_complete
  same_contexts_new_names_weights_thresholds: true
  planned_per_arm: 72
  available: [55, 72]
  strict_correct: [17, 53]
  strict_difference_bounds: [19, 36]
  requested_calculation_actually_performed: [17, 62]
  performed_and_strict: [12, 50]
  composed_performed_per48: [0, 38]
  composed_performed_and_strict_per48: [0, 32]
  trained_faithful_wrong_explained_by_child_labels: 12
  trained_unfaithful_correct_coincidences: 3
  unchanged_true_null: 17
  unchanged_authenticated_empty_observed_zero: 11
  independently_trained_or_new_contexts: false
nonzero_support_diagnostic:
  status: additive_frozen_semantics_main_replay_complete
  original_successes_per46: [10, 32]
  original_missing_outcome_difference_bounds: [15, 22]
  fresh_seed_successes_per46: [9, 27]
  fresh_seed_missing_outcome_difference_bounds: [11, 19]
  metadata_successes_per44: [7, 25]
  metadata_missing_outcome_difference_bounds: [8, 18]
  not_independent_training_replications: true
  report: ../analyses/controller-zero-support-strata-2026-09-10/REPORT.md
  main_adoption: ../analyses/controller-zero-support-strata-2026-09-10/MAIN_ADOPTION.json
evidence:
  report: ../analyses/root-question-sensitive-sft-live-2026-09-10/REPORT_MAIN.md
  report_sha256: 6245e9559d0038d6284433f2ecd9ccb2c17e72d0dabd4be5d3b358b65da8ad4c
  final_seal: ../analyses/root-question-sensitive-sft-live-2026-09-10/FINAL_MAIN.json
  verified_pins: 9130
  verified_bytes: 2023594919
  pin_errors: 0
  replication_native_audit: ../analyses/root-question-sensitive-readout-followups-2026-09-10/root-question-sensitive-seed-replication-v1-AUDIT.json
  replication_semantic_report: ../analyses/root-question-sensitive-readout-followups-2026-09-10/fresh-seed-semantics/REPORT.md
  replication_comparability_erratum: ../analyses/root-question-sensitive-readout-followups-2026-09-10/fresh-seed-semantics/TIMING_AND_COMPARABILITY_ERRATUM.md
  replication_main_adoption_pins: 1624
  replication_main_adoption_errors: 0
  metadata_semantic_report: ../analyses/root-question-sensitive-readout-followups-2026-09-10/metadata-semantics/REPORT.md
  metadata_report_sha256: cc77b86e0f0be15b848138cf62576ff5a6e41848c7cebb4292548fe6e54b786d
  metadata_main_adoption_pins: 1487
  metadata_main_adoption_errors: 0
limits:
  - One small model and one training realization; eight root-protected but child-training-exposed contexts.
  - The curriculum combines further training with varied questions and genuine child observations; no isolated ingredient claim.
  - No new operators, new context sizes, or general decomposition benchmark demonstrated.
  - Correct answers can follow wrong procedures; report execution fidelity separately.
  - Missing-outcome bounds are not statistical confidence intervals.
next_comparisons:
  - Metadata transfer passed locally; next distinguish which fields matter or use genuinely new records.
  - Train terminal rewards on composed training tasks starting from this checkpoint; preparation active.
  - Test longer inputs, new context groups, paraphrases and an independently trained seed.
---

# The model learned to use the question, not just run a familiar script

Our earlier training taught a useful routine: ask a subtask model to label
records, calculate from the labels in Python, and answer. But it often applied
the wrong calculation when a question combined conditions or asked about users
rather than individual records. Correct numbers sometimes hid those mistakes.

We then trained on 72 demonstrations covering different operations and
parameters, with real subtask responses kept intact. After six fixed updates,
correct answers backed by the requested calculation rose from 15/72 to 52/72.
On the composed questions specifically, that measure rose from 1/48 to 33/48.
Every available execution was reviewed, not just the successful answers.

One matched example makes the change concrete. A question asked for the weight
of description records belonging to users who also had an entity record. Both
policies obtained the same subtask labels. Before training, the controller summed
the entity records and returned 14. After training, it first identified the
qualifying users, then summed their description records and returned the correct
21. This is an illustrative case, not an extra independent observation.

A separate readout with new sampling seeds also improved strict correctness,
from 25/72 to 51/72, and performed-and-correct answers from 15/72 to 49/72.
Its exhaustive semantic report is sealed, with an additive clarification that
three failed expressions are not successfully performed calculations. MAIN
reviewed those actual paths and verified 1,624 pins without mismatch. This
supports sampling stability on the same questions, not broad generalization.

Changing names, weights, and thresholds preserved the improvement: correct
answers backed by the requested calculation rose from 12/72 to 50/72. Every
available path was reviewed, and MAIN checked all 144 native-to-review links
and 1,487 evidence pins. This supports transfer across changed metadata on the
same records, not generalization to unseen tasks. Twelve trained wrong answers
again resulted from correct calculations over incorrect subtask labels.

A separate audit removes every zero-answer task. The correct-and-performed
gain remains:10→32/46 originally,9→27/46 with fresh seeds, and7→25/44 after
changing metadata. Even assigning every unavailable endpoint its least favorable
outcome leaves positive differences in all three nonzero composed strata.
This strengthens the local execution finding; it is not independent replication
or proof of general algorithms. The original nonzero primitive subset remains
inconclusive under missing-outcome bounds.
[Strata and limitations](../analyses/controller-zero-support-strata-2026-09-10/REPORT.md).

The next issue is now more precise: can the learned procedure survive longer
contexts, and can composed-task reward training improve it further? Ten trained
calculations in the original panel were faithful
but wrong because the subtask labels were wrong. Better planning alone cannot
remove that error source.
