---
schema: rlm-living-claim-card-v1
id: "claim:shorter-view-enables-retained-computation"
question_id: "rq:sufficient-interface"
updated_utc: "2026-09-10T11:51:36Z"
status: exploratory_mechanism_lead
publication_readiness: not_publication_ready
novelty_claim: none_established
statement: Retaining child answers and limiting their printed view supported two completed 256-record calculations, but incorrect child labels still prevented correct task answers.
evaluation:
  fixed_root: operator_sft24
  fixed_child: c32
  parent_context_clusters: 4
  size_blocks_per_parent: 2
  planned_per_cell: 8
  cells: [batch_20000, batch_4096, cumulative_20000, cumulative_4096]
  strict_correct: [0, 0, 0, 0]
  native_available: [2, 2, 2, 5]
  primary_NULL: [6, 6, 6, 3]
  faithful_but_wrong_from_child_labels: [1, 1, 1, 4]
  genuine_256_record_multibatch_reductions: [0, 0, 0, 2]
  parents_with_genuine_multibatch_reduction: 2
  frozen_mechanism_criterion_met: true
  task_accuracy_promotion: false
  source_exposure: Four reused large-panel parent contexts; the two witnesses were selected after observing completion.
cost:
  physical_attempts: 440
  native_completions: 427
  unknown_usage_attempts: 13
  known_input_tokens: 1178615
  known_output_tokens: 87310
  known_cached_input_tokens: 1028528
  owner_seconds: 939.381994009018
  outer_seconds: 939.87356529385
evidence:
  report: ../analyses/root-bounded-observation-view-live-2026-09-10/REPORT.md
  report_sha256: 70b43478141ac3612679065b1ed786f22d5919f5f14c27b6ce82bcfd578c8fe1
  final_sha256: 6ec5ccb96d2b9fc121dbfaad530c7c28e1cfd7c8669a3042f162a32f9562e1d3
  matched_witnesses: ../analyses/root-bounded-observation-view-live-2026-09-10/MATCHED_WITNESSES.json
  child_error_diagnostic: ../analyses/root-bounded-child-error-diagnostic-2026-09-10/REPORT.md
  child_error_report_sha256: fa1146d333b0033a51c827073feae64be9e23d93c766a6b948315502067fda55
  main_verification: ../operations/2026-09-09-allocation-5780/MAIN_VERIFICATION_1145.json
  main_unique_pins: 8080
  main_pin_errors: 0
next_comparison: Classify the same two contexts in fresh wide versus 16-record child batches, preserving IDs, order, model and native interface.
---

# A smaller printed view helped the model use retained answers

The model does not need to see every stored answer again to calculate with it.
We tested that distinction by keeping Python's stored data unchanged while
showing a shorter view of each tool result. We crossed this with either returning
only the latest batch of child answers or returning all answers collected so far.

With cumulative answers and the shorter view, two runs successfully processed
256 records in batches of 100, 100 and 56. They then calculated from all three
batches and returned a final answer. The earlier accumulation-only test had
retained growing maps but completed no such calculation. In this new comparison,
cumulative-answer availability was 5/8 with the shorter view and 2/8 with the
larger view. This is a small, already-exposed diagnostic, not a general effect.

One useful example used the same three acquisition programs in both conditions.
The larger-view run's final model request exceeded its context limit. The
shorter-view run retained the data in Python, counted from it and finished.
Its child predictions were not identical to the control's, so this is not a
perfect same-evidence causal comparison. The other witness's control chose a
different initial program before clipping could act; that difference cannot be
attributed to the view limit.

Crucially, every condition still scored zero correct task answers. The two
completed large calculations returned 151 instead of 170 and 36 instead of 40.
Their arithmetic was correct for the child labels they actually received.
The child made 26 and 32 labeling errors, respectively; the errors affecting the
requested category account for both wrong totals. There is no additional root
arithmetic error in these two cases. Correct output IDs alone did not establish
that the labels were correct.

This makes the next question more specific: would smaller child batches improve
label accuracy enough to repair those totals? That comparison uses fresh calls
in both arms, not the old failing predictions as a control. It changes batch
size, input/output length and call count together, so it tests a practical
granularity choice rather than a pure attention mechanism or equal-compute effect.

The view cap limits passive printed output, not access to the existing session
log. The 4,096-byte payload also has a small warning-marker overhead. No answers,
labels or calculation procedure were supplied by the view intervention.
