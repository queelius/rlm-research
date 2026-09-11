---
schema: rlm-living-claim-card-v1
id: claim:output-addresses-help-and-interfere
question_id: rq:correspondence
updated_utc: "2026-09-10T20:45:03Z"
status: exploratory_matched_ordinal_package_replicated_on_new_contexts
publication_readiness: promising_requires_mechanism_and_full_system_controls
novelty_claim: none_established
statement: Output identifiers can help maintain correspondence, but identifiers naming another visible record can pull answers toward that record.
field_order_pilot:
  context_clusters: 8
  planned_calls: 48
  available_valid_calls: 48
  misleading_correct_tag_first_label_first: [152, 182]
  aligned_correct_tag_first_label_first: [317, 302]
  denominator_per_cell: 384
  selective_gain_percentage_points: 11.71875
  positive_context_interactions: 6
field_order_fresh_context_replication:
  context_clusters: 16
  planned_and_native_valid_calls: 96
  misleading_correct_tag_first_label_first: [302, 369]
  aligned_correct_tag_first_label_first: [639, 631]
  unrelated_correct_tag_first_label_first: [646, 607]
  denominator_per_cell: 768
  selective_gain_percentage_points: 9.765625
  context_interaction_signs: {positive: 14, negative: 1, zero: 1}
  frozen_gate_passed: false
  gate_miss_reason: observed75_labels_below77_needed_for10percentage_points
  claim: directional_replication_not_formally_promoted
host_join_pilot:
  context_clusters: 8
  planned_calls: 48
  available_valid_calls: 48
  misleading_correct_tag_first_labels_only: [148, 202]
  unrelated_correct_tag_first_labels_only: [316, 190]
  aligned_correct_tag_first_labels_only: [318, 186]
  denominator_per_cell: 384
  misleading_gain_percentage_points: 14.0625
  aligned_gain_percentage_points: -34.375
  selective_gain_percentage_points: 48.4375
  positive_context_interactions: 8
  universal_improvement: false
posthoc_position_diagnostic:
  split_chosen_after_outcome_inspection: true
  labels_only_first16_correct_per128_wrong_alien_aligned: [107, 102, 98]
  labels_only_remaining32_correct_per256_wrong_alien_aligned: [95, 88, 88]
  aligned_tag_first_first16_correct_per128: 106
  aligned_tag_first_remaining32_correct_per256: 212
  all_labels_only_contexts_decline: true
ordinal_factorial_pilot:
  context_clusters: 8
  prior_research_exposed: true
  planned_and_native_valid_calls: 96
  total_correct_absent_labels_absent_row_present_labels_present_row: [583, 572, 590, 933]
  total_denominator_per_cell: 1152
  late_correct_absent_labels_absent_row_present_labels_present_row: [277, 293, 292, 620]
  late_denominator_per_cell: 768
  original_output_only_late_gain_percentage_points: 2.0833333333333335
  original_output_only_gate_passed: false
  matched_package_total_gain_percentage_points: 29.774305555555557
  matched_package_late_gain_percentage_points: 42.708333333333336
  late_input_output_interaction_percentage_points: 40.625
  present_row_total_gains_wrong_alien_aligned_per384: [119, 112, 112]
  main_adoption: 341_pins_96_native_request_rerenders_96_literal_contract_recounts_zero_errors
ordinal_fresh_context_replication:
  context_clusters: 16
  planned_and_native_valid_calls: 192
  inventory_excluded_from_named_prior_panels: true
  late_interaction_correct: 657
  late_interaction_denominator: 1536
  late_interaction_percentage_points: 42.7734375
  positive_contexts: 16
  frozen_gate_passed: true
  present_row_output_late_gains_wrong_alien_aligned: [235, 242, 237]
  late_denominator_per_relation_cell: 512
  early_denominator_per_relation_cell: 256
  output_only_late_gain: 57
  output_only_late_denominator: 1536
  main_adoption: 192_exact_request_rerenders_and_literal_outputs_576_capture_pins_byte_identical_replay
  report_denominator_typo_corrected_additively: true
evidence:
  ordinal_replication: ../analyses/leaf-mnli-positional-anchor-new-context-live-2026-09-10/REPORT.md
  ordinal_replication_report_sha256: 2e0599eb47f2e8bbb73e8ddf7c504763798d089b5e2f507a35696ad1bf9684e5
  ordinal_replication_erratum: ../analyses/leaf-mnli-positional-anchor-new-context-live-2026-09-10/ERRATUM.md
  field_order: ../analyses/leaf-mnli-output-field-order-live-2026-09-10/REPORT.md
  field_order_replication: ../analyses/leaf-mnli-field-order-replication-live-2026-09-10/REPORT.md
  field_order_replication_report_sha256: cbf87050634f4bba1e248d3a5abbe3e7fed2f69a15dc7974b11214012200a5f3
  host_join: ../analyses/leaf-mnli-host-identifier-join-live-2026-09-10/REPORT.md
  position: ../analyses/leaf-mnli-host-identifier-join-live-2026-09-10/POSITION_DIAGNOSTIC.json
  ordinal_factorial: ../analyses/leaf-mnli-positional-anchor-binding-live-2026-09-10/REPORT.md
  ordinal_factorial_report_sha256: c3452e74f115ed0c484713b00da77ad4ea3a7ca8a1c4a2b9ee5c8568603796a1
  main_adoption: MAIN_ADOPTION.json_in_each_report_directory
limits:
  - Eight previously research-exposed contexts and one seed per context in each pilot.
  - Format, instructions and generated-token burden change together.
  - Repeated premise groups and dependent labels; no independent-item significance claim.
  - Deterministic host attachment cannot fix wrong labels; its identifier fidelity is not model evidence.
  - Post-hoc position pattern is a hypothesis generator, not a confirmed mechanism.
  - Ordinal factorial method preceded outcome access, but recovery binding was retrospective after availability disclosure; same author produced and audited the run.
  - Matching row numbers changed input fields, instructions, guided grammar and generated tokens together; not an isolated attention mechanism.
next_comparisons:
  - Sixteen-new-context field-order replication supports direction but misses frozen magnitude gate.
  - Matched input/output numbering factorial is audited; original output-only gate failed while package interaction is promising.
  - Sixteen-new-context 192-call full-factorial replication passed its frozen interaction gate.
  - Test full-RLM consumption and distinguish positional numbering from other one-to-one cues.
---

# An address can be a useful cue or a misleading one

We asked a small model to classify batches of text pairs and attach a required
identifier to each answer. Earlier controls showed a large accuracy loss when
an identifier named a different visible record, even though every output was
well formed. Changing the order of the label and identifier reduced that loss
in a small pilot, but did not remove it.

A replication on 16 new context clusters points in the same direction. Writing
the answer first improved misleading-reference accuracy by 8.72 percentage
points, while aligned-reference accuracy fell by 1.04 points. The selective
effect was positive in 14 of 16 contexts. Its 9.77-point average narrowly misses
our predeclared 10-point threshold, so we retain it as directional support,
not a formally promoted result. All 96 responses were available and valid.

Letting Python attach identifiers had a more complicated effect. It improved
the misleading cases by 14 percentage points, but reduced aligned-case accuracy
by 34 points. The large interaction is not a generally better system.

A position diagnostic may explain part of this tradeoff: labels-only answers start
reasonably well but become much less accurate later in the batch. Aligned
identifier-bearing answers stay more consistent. The subsequent full factorial
found that matching numbers on both input and output helped substantially:
accuracy rose from 51.2% to 81.0% overall and from 38.0% to 80.7% on later records.
Output numbering without input numbers barely helped the later records (+2.08
points), failing the original ten-point gate. Benefits occurred under all three
reference conditions, not only misleading references. The matched package is
the follow-up lead. A subsequent16-new-context replication now supports it:
the later-record input/output interaction is+42.77 points, positive in all16
contexts, and the matched package improves later accuracy by46.48 points across
the three reference conditions. All192 responses are valid. Output-only numbering
again helps much less (+3.71 points). This is replication across named-inventory-
excluded contexts, not independent-model or independent-training replication.

Numbering itself is not novel; the research question is when a
cheap positional cue preserves correspondence without causing wrong-record
interference, and whether any benefit survives full-RLM use.
