---
schema: rlm-living-claim-card-v1
id: "claim:child-interface-compatibility"
question_id: "rq:sufficient-interface"
updated_utc: "2026-09-10T19:53:28Z"
status: exploratory_negative_interface_result
publication_readiness: requires_training_and_transfer_controls
novelty_claim: none_established
statement: A smaller output vocabulary can reduce child accuracy and erase an adapter's aggregate gain.
design:
  source_batches: 8
  distinct_official_test_questions: 128
  pairs_per_batch: 6
  policies: [base, c32]
  interfaces: [full_six_then_host_projection, direct_A_B_other]
  planned_and_native_valid_calls: 192
  optimizer_disjoint: true
  research_exposed: true
  root_calls: 0
results:
  correct_per768_base_full_base_compact_c32_full_c32_compact: [672, 605, 726, 605]
  exact_batches_per48_base_full_base_compact_c32_full_c32_compact: [4, 1, 17, 5]
  adapter_gain_full_percentage_points: 7.03125
  adapter_gain_compact_percentage_points: 0
  interaction_percentage_points: -7.03125
  interaction_batch_signs: {negative: 6, zero: 1, positive: 1}
  compact_vs_full_negative_batches_each_policy: 8
  input_tokens: 232688
  output_tokens: 51701
  cached_input_tokens: 148192
  parent_seconds: 204.64347501844168
evidence:
  report: ../analyses/leaf-trec-query-conditioned-interface-live-2026-09-10/REPORT.md
  report_sha256: d9fcb94b007b099a0d7bc8e82556d51e9a95c3a131264c55e87593f156ae0548
  corrections: ../analyses/leaf-trec-query-conditioned-interface-live-2026-09-10/ERRATUM.md
  main_adoption: ../analyses/leaf-trec-query-conditioned-interface-live-2026-09-10/MAIN_ADOPTION.json
main_verification: {pins: 614, errors: 0, exact_requests_rebuilt: 192, independent_literal_and_confusion_recounts: 192}
limits:
  - Eight correlated batches, not48 independent pair blocks or768 independent labels.
  - Compact output changes instructions, vocabulary and grammar together.
  - The adapter was trained on full labels, not the compact contract.
  - Equal compact totals hide gains on A/B and losses on other.
  - No root or end-to-end result.
next:
  - Prefer full-six predictions plus host projection in this local setting.
  - Test contract-specific training on training-only groups and a new-source readout.
  - Test root consumption separately if the projected map has operational value.
---

# Simpler output is not automatically easier for the model

We asked the child only whether each record belonged to either of two relevant
categories, with everything else called “other.” This performed worse than
requesting the familiar six categories and converting the answer in Python.

With the trained child, accuracy fell from94.5% to78.8%; with the base child it
fell from87.5% to78.8%. The compact interface was worse in every source batch.
All192 responses were valid, so this is not an output-format availability failure.

Equal compact totals do not mean the adapter did nothing: it improved the two
requested categories but became worse on “other.” Report those class-wise counts
with overall accuracy. The compact c32 arm emitted11,919 tokens versus12,816
for full labels, about7% fewer, while losing15.76 accuracy points. This is not a
billing or total-compute comparison.

This is a practical local decision and a training question, not a claim that
query-conditioned representations are generally bad. A matched training comparison
can test whether the changed contract explains the loss. Repeating host projection
would duplicate the successful comparison already performed here.
