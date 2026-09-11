---
schema: rlm-living-claim-card-v1
id: "claim:procedural-card-headroom"
question_id: "rq:controller"
updated_utc: "2026-09-10T11:51:36Z"
status: exploratory_instructional_headroom
publication_readiness: not_publication_ready
novelty_claim: none_established
statement: A short calculation guide elicited some correct procedures, but did not satisfy the prespecified overall improvement criterion.
evaluation:
  fixed_root: operator_sft24
  fixed_child: c32
  context_clusters: 8
  composed_questions_per_context: 3
  planned_per_arm: 24
  arms: [unchanged, shared_procedural_card]
  strict_correct: [3, 7]
  native_available: [18, 16]
  primary_NULL: [6, 8]
  faithfully_requested_computations: [0, 6]
  faithful_and_correct: [0, 4]
  faithful_but_wrong_child_labels: [0, 2]
  correct_but_wrong_operation_or_scope: [3, 3]
  card_contexts_with_faithful_computation: 5
  card_contexts_with_faithful_correct_computation: 3
  nonzero_strict_correct: [2, 6]
  nonzero_planned_per_arm: 20
  zero_strict_correct: [1, 1]
  zero_planned_per_arm: 4
  strict_missing_outcome_bounds: [[3, 9], [7, 15]]
  paired_difference_bounds_per_24: [-2, 12]
  complete_practical_promotion_gate_met: false
  failed_gate_component: Card availability is lower, 16 versus 18.
  exposed_panel: true
  author_analysis_overlap: true
cost:
  physical_attempts: 611
  root_attempts: 503
  child_attempts: 108
  returned_native_completions: 605
  unknown_usage_attempts: 6
  known_input_tokens: 1983281
  known_output_tokens: 55727
  known_cached_input_tokens: 1884256
  outer_wall_seconds: 684.6731276903
evidence:
  report: ../analyses/root-procedural-card-headroom-live-2026-09-10/REPORT.md
  report_sha256: 2eed9bb2bf8bfe5314ea89d4bdef2ee45a5f4b8e1c6c2308909a28619aa0c6a4
  final_sha256: a476bf7468aecff29bf94f9496496c10938219a374f0fa5b09561c7d0d56b5b8
  promotion_disposition: ../analyses/root-procedural-card-headroom-live-2026-09-10/PROMOTION_DISPOSITION.md
  promotion_disposition_sha256: 0e84191149c87e8e3cde68c253497098cc8a76ce48ee1722f12bd495777344dc
  promotion_addendum_seal_sha256: 569f5389061c71903961092eea1832c7ddd7cf7cb7a286e092d5f5f2239d05d2
  main_verification_epoch: 1789033798.9805026
  main_unique_pins: 8865
  main_verified_bytes: 1527337103
  main_pin_errors: 0
  main_semantic_review: Read all six faithful program/scalar links and selected full native paths; author-reviewed all 34 available finals.
followup_counterfactual96:
  report: ../analyses/root-counterfactual-card-signatures-live-2026-09-10/REPORT.md
  report_sha256: 5a5cdfcb0809bdf81e0fb47f2af51012f011853b1a9c7aa2dead2d84ea832351
  final_sha256: fbea77327442bffeef973e3305b245905d969901e9051e67662e661b48be0ade
  cells: [original_unguided, original_guided, changed_unguided, changed_guided]
  planned_per_cell: 24
  strict_correct: [5, 5, 1, 2]
  native_available: [19, 14, 18, 10]
  faithfully_requested_computations: [0, 3, 0, 2]
  faithful_and_correct: [0, 3, 0, 2]
  guided_changed_contexts_with_faithful_computation: 1
  full_practical_gate_met: false
  gate_failures: [availability_loss, fewer_than_four_additional_faithful_cases, fewer_than_three_supporting_contexts]
  physical_attempts: 1166
  native_completions: 1149
  unknown_usage_attempts: 17
  main_unique_pins: 12302
  main_pin_errors: 0
next_comparison: Evaluate a fixed question-sensitive demonstration curriculum without the guide; do not extend the guide as an established accuracy improvement.
---

# A short guide elicited procedures that the model had not been using

## The changed-parameter follow-up did not establish a practical improvement

The follow-up retained original questions and added changed weights and
parameters that distinguish the requested answer from four named shortcuts.
It used eight exposed contexts, fresh paired seeds and the same guide. The
challenge was deliberately selected using known answers, not randomly sampled.

On original questions, guided and unguided runs each scored 5/24. On changed
questions, the scores were 2/24 and 1/24, but only 10 guided final answers were
available versus 18 unguided. Five guided programs were faithful and correct
across both panels; only two were changed cases, both in one context. All three
parts of the practical continuation criterion failed. The extra one correct
answer is not a reliable net gain. The larger follow-up therefore preserves
limited evidence that instructions can elicit a procedure, but does not promote
the guide into an effective method. The original smaller result remains below.

## Original 48-run diagnostic

We kept the model, questions and records fixed. In one condition we appended
the same short guide explaining three calculations: the largest per-user total,
the number of users whose total exceeds a threshold, and a total restricted to
users selected by another category. It supplied neither record labels nor answers.

With the guide, six available programs executed the requested calculation and
scope. Four gave correct answers; two correctly calculated from incorrect child
predictions. Without the guide, none of the 18 available answers executed the
requested procedure. All three procedure families appeared among the six guided
executions, spread across five context groups.

For example, one guided program formed per-user totals of 7, 7, 0 and 6, then
counted the three totals greater than 5. Another guided program counted one
qualifying user, while its paired unguided run summed weights to 9 from the same
complete child-prediction map. These examples locate a difference in calculation,
not merely answer formatting or having access to evidence.

The complete practical improvement criterion was not met. Strict scores were
7/24 with the guide and 3/24 without it, but only 16 guided final answers were
available versus 18 unguided. Missing-outcome bounds overlap. Three guided
successes and all three unguided successes used a wrong calculation or scope
that happened to give the correct number. A better score alone would conceal this.

This is instructional headroom on eight already-exposed contexts, not a learned
skill, unseen generalization, reliable task decomposition or a publication-ready
method. The guide also costs tokens and may induce extra calls. One unguided
path genuinely accumulated two batches before applying the wrong operation;
we must not generalize the earlier absence of completed accumulation to every run.

The next diagnostic changes weights and question parameters so four named
shortcut calculations disagree with the requested answer. It retains original
and changed tasks in both guide conditions. Selection uses known answers and is
explicitly a targeted challenge, not a random benchmark sample. A surviving
effect would justify a question-sensitive training curriculum; it would not by
itself prove that a general algorithm has been learned.
