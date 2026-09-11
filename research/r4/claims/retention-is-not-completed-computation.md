---
schema: rlm-living-claim-card-v1
id: "claim:retention-is-not-completed-computation"
question_id: "rq:sufficient-interface"
updated_utc: "2026-09-10T09:40:00Z"
status: exploratory_mechanism_lead
publication_readiness: not_publication_ready
novelty_claim: none_established
statement: A harness retained actual answers across subtask calls, but the controller still did not complete a calculation using that accumulated evidence.
evaluation:
  fixed_root: operator_sft24
  fixed_child: c32
  parent_clusters: 4
  planned_per_arm: 16
  arms: [batch_local, cumulative]
  strict_correct: [1, 0]
  native_available: [5, 4]
  primary_NULL: [11, 12]
  cumulative_growing_returns: 6
  parents_with_cumulative_growing_returns: 4
  executed_requested_multibatch_reductions: [0, 0]
  faithful_single_complete_map_reductions: [4, 2]
  faithful_but_wrong_child_label_answers: 5
  strict_success_has_offsetting_child_label_errors: true
  missing_result_overlength_requests: {root: 10, child: 3}
  malformed_native_tool_envelope_without_final: 10
  source_exposure: All large-panel records and context groups previously exposed; adaptive diagnostic, not protected generalization.
cost:
  physical_attempts: 640
  root_attempts: 462
  child_attempts: 178
  returned_native_completions: 627
  known_input_tokens: 2170666
  known_output_tokens: 90217
  known_cached_input_tokens: 1987520
  unknown_usage_attempts: 13
  outer_wall_seconds: 951.101362627
evidence:
  report: ../analyses/root-acquired-evidence-accumulation-live-2026-09-10/REPORT.md
  report_sha256: 9192c4c4276a5002969b631d8b4c5ed22af54ff21df1aacacb79d5e507e893b0
  final_seal_sha256: aa5a3a41bed06795d130ad74322d2180edf4dd47c9ac5995d18554bb37b33549
  main_combined_verification_epoch: 1789033203.7574017
  main_combined_unique_pins: 8847
  main_combined_verified_bytes: 1584081794
  main_pin_errors: 0
  verification_scope: Accumulation source/output/analysis closure plus the separate task-file semantic addendum.
next_comparison: Batch versus cumulative return crossed with unchanged versus bounded root-visible tool output, preserving full Python state and raw audit logs.
---

# Keeping answers is not the same as using them

The measurements below describe the accumulation-only test. A later crossed
view-budget experiment did produce two genuine 256-record calculations with
cumulative returns and a shorter printed view. Neither answer was correct,
because child labels were wrong. This narrows the earlier limitation without
rewriting it. [Follow-up evidence](shorter-view-enables-retained-computation.md).

The earlier scale test showed the model overwriting old subtask answers. We
changed the decoder so it returned all answers decoded so far, not just the
latest batch. This supplied no new labels or calculation instructions.

That mechanism did operate: six cumulative-arm tasks across all four context
groups returned growing collections of genuine child predictions. But none
finished the requested calculation over multiple batches. The ordinary and
cumulative versions produced1 and0 correct answers out of16, with only5 and4
available final answers. This does not establish an accuracy improvement.

There are several distinct obstacles. Growing printed maps consume the root's
context, while retained Python state itself does not require printing every
entry again. Ten missing-result paths ended in oversized root requests, and
three others in oversized child requests. Ten retained episode graphs instead
ended with an invalid tool envelope and no final answer. These failures are
kept separate, including calls made by tasks with no final result.

Even completion would not solve every problem. Six of the nine available
answers correctly calculated from one complete child-prediction map, but five
were wrong because those predictions were wrong. The lone correct result had
offsetting label errors. Three other answers used the wrong user scope.

The next small test preserves Python state and the complete raw research log,
but limits the text shown back to the root after a tool call. It compares both
batch-local and cumulative interfaces at both output budgets. That separates
retention from the cost of displaying retained evidence. It neither repairs
child requests nor injects a task-aware summary or a preferred algorithm.

This is a four-context, already-exposed exploratory panel. The return-scope
change also requires truthful instruction wording, and model-induced failures
are not random missing data. Six observed growing returns are not six completed
reasoning successes. A future positive result must show actual reduction and
stopping, not merely a larger map or more child calls.
