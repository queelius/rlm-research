---
schema: rlm-living-claim-card-v1
id: "claim:operator-exact-dose-acquisition"
question_id: "rq:controller"
updated_utc: "2026-09-10T06:12:00Z"
status: promising_local_gain_with_verified_transfer_limit
publication_readiness: not_publication_ready
novelty_claim: none_established
statement: More updates on the same demonstrations increased actual child acquisition and correct answers on this local panel.
intervention:
  root: Qwen3-4B-Instruct-2507 LoRA
  checkpoints: [6, 24]
  corpus_trajectories: 72
  additional_updates: 18
  additional_masked_target_exposures: 411246
  child_policy_changed: false
  interface_changed: false
  checkpoint_selection: fixed_before_readout
evaluation:
  planned_per_policy: 48
  context_clusters: 12
  paired_samples_per_question: 1
  serial_order: [sft6, sft24]
  strict_correct: {sft6: 5, sft24: 29}
  native_available: {sft6: 31, sft24: 38}
  nonzero_correct: {sft6: 2, sft24: 28}
  child_acquisition_endpoints: {sft6: 1, sft24: 48}
  physical_child_calls: {sft6: 2, sft24: 75}
  conservative_correct_bounds: {sft6: [5, 22], sft24: [29, 39]}
  jointly_available_pairs: {sft24_wins: 19, sft6_wins: 1, both_correct: 3, both_wrong: 4}
  pairs_with_missing_final: 21
  sft24_correct_with_observed_map_scalar_and_displayed_integer_agreement: 29
  sft24_wrong_with_observed_map_scalar_agreement: 5
  sft24_correct_with_verified_requested_live_label_computation: 26
  sft24_correct_wrong_scope_coincidences: 2
  sft24_correct_literal_id_recovery: 1
  sft24_wrong_with_verified_requested_computation_and_relevant_child_error: 5
  relevant_child_error_context_clusters: 2
  requested_operator_scope_and_actual_state_use: retrospective_exact_code_and_observation_review_complete
  source_exposure: Four root-new-under-named-inventory contexts and eight exposed contexts; all child-training exposure disclosed.
evidence:
  report: ../analyses/root-operator-dose-continuation-live-2026-09-10/REPORT.md
  report_sha256: c67c2b7430b69a890d9a51f0be14d3084fc45439210284fca1454708b84a749e
  final_manifest_sha256: 0cf15b28dcede96e06e79ec87b1880411e337168f2b3dbcb14b46723bc1b1616
  accounting_erratum: ../analyses/root-operator-dose-continuation-live-2026-09-10/ACCOUNTING_ERRATUM.md
  erratum_sha256: 949d6c5b74c6eb5286dff38b2155200ec825b3b51fb43a07b371b77506083090
  erratum_manifest_sha256: e771a2325c3c1ee849eb9047e7a27b23719c66d18054b1101a06d5436d09edb9
  availability_erratum: ../analyses/root-operator-dose-continuation-live-2026-09-10/AVAILABILITY_ERRATUM.md
  availability_erratum_manifest_sha256: cf600a76205dcb7b03e1f88fd7751c36d5f6daa42b32bf97e7e9081c1e71ee97
  mechanism_qualification: ../operations/2026-09-09-allocation-5780/operator-dose-mechanism-qualification.md
  semantic_retrospective: ../analyses/root-operator-dose-semantic-retrospective-2026-09-10/REPORT.md
  semantic_report_sha256: 61a9742c38adb10a219f1358c3a4a749b5a6664ee262557fa3694d900d6f08fd
  semantic_final_sha256: 891c073261527297bb6609d13e81554f13e3de7acf4dc1a5987a88eea2bf541b
  transfer_limit: operator-composition-transfer-limit.md
  plot: ../analyses/root-operator-dose-continuation-live-2026-09-10/operator-dose-fit-vs-behavior.svg
audit_timing:
  training_method: Postlaunch, knew checkpoint7 existed, before its contents.
  readout_method: Prelaunch.
  detailed_dataflow_parser: Post-outcome and aggregate-aware; diagnostic, not primary scoring.
  semantic_retrospective: Outcome-aware exact-code review by implementation author independent of the prior dataflow analysis; not independent experiment authorship.
next_comparisons:
  - ../ideas/2026-09-10-operator-dose-fresh-composition96.md
  - ../ideas/2026-09-10-operator-dose-intermediate-readout-design.md
  - ../ideas/2026-09-10-after-operator-sft-rlvr-options.md
---

# More fitting increased acquisitions and correct answers

After six updates, the model usually did not acquire labels from a child model.
After24, it did so in every task, and correct answers rose from5 to29. The
overall gain survives conservative treatment of missing finals. Exact program
and observation review verifies26 requested computations on actual child-label
state, including25 nonzero successes. Two other correct answers use the wrong
user scope but happen to give the right number; one uses a literal record ID
after repeatedly overwriting the child map. The earlier claim that all29 used
the correct live-label computation is corrected, without changing any scores.

This is a local training result, not proof of general decomposition. Most
successful tasks used one child request. The model has not yet demonstrated
reliable accumulation across several batches. Five wrong answers are verified
as requested computations over wrong child predictions, but four share one
source error and the fifth comes from another context: two error clusters, not
five independent failures. There are
only12 context groups and one paired sample per question; serial evaluation and
exposure limit generalization claims.

The accounting erratum changes only the word “unrun”: all nine episodes lacking
RESULT files were attempted and failed without an authenticated final. Their
calls are included in the ledger, and no scores or missing-outcome bounds change.
The second arithmetic erratum corrects27 model-specific NULL slots, not23.

The completed new-context transfer test substantially narrows the claim:
fixed24 gives9/48 strict answers versus6/48 for fixed6, with only two faithful
primitive successes and no faithful composed success. Missing-final bounds
overlap. This is a learned local routine, not demonstrated general decomposition.
Intermediate checkpoints can locate a candidate behavioral transition, but
cannot establish an abrupt threshold or select a winning checkpoint afterward.
