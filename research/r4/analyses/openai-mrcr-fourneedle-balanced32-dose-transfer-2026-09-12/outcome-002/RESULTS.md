# Balanced four-needle dose-transfer audit

COMPLETE_RAW_NATIVE_AUDIT

Exact: cp32 24/32; LR1e-4 27/32. Available 32/32; paired wins/losses 5/2; unknown 0; identical native paths 22/32.

| Requested ordinal | cp32 | LR1e-4 | wins | losses | unknown |
|---|---:|---:|---:|---:|---:|
| 1 | 6/8 | 8/8 | 2 | 0 | 0 |
| 2 | 4/8 | 6/8 | 2 | 0 | 0 |
| 3 | 7/8 | 6/8 | 0 | 1 | 0 |
| 4 | 7/8 | 7/8 | 1 | 1 | 0 |

cp32: 64 returned, 0 errors, 0 start-only; 67556 prompt + 17583 completion tokens; 0 unknown-cost calls; copy {'exact': 24, 'edge_whitespace_difference': 5, 'no_clean_target_evidence': 3}; mechanisms {'exact_after_clean_target': 24, 'clean_target_copy_failure': 5, 'no_clean_target_and_wrong_final': 3}.
LR1e-4: 63 returned, 0 errors, 0 start-only; 66095 prompt + 21302 completion tokens; 0 unknown-cost calls; copy {'edge_whitespace_difference': 2, 'exact': 27, 'no_clean_target_evidence': 2, 'invalid_or_no_final_text': 1}; mechanisms {'clean_target_copy_failure': 2, 'exact_after_clean_target': 27, 'no_clean_target_and_wrong_final': 3}.

Changed-path trace/program/observation hashes and bounded inert program text are in JSON; no generated code was executed. Unavailable is never counted wrong.

Prospectively frozen 8-per-ordinal same-task panel. LR1e-4 was selected using exposed development contexts. Native path differences are observed, not proof of improved retrieval; clean stdout is evidence available to the policy, not internal faithfulness. Base pretraining exposure is unknown.
