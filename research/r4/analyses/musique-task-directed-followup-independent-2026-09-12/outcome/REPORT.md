# MuSiQue task-directed follow-up: independent raw readout

The analyzer reconstructed 132/132 native returns and 48/48 scientifically available terminal endpoints across 12 fixed question contexts. Unavailable endpoints remain unknown rather than wrong.

| Arm | Correct | Wrong | Unavailable | Answer-F1 sum | Support-F1 sum |
|---|---:|---:|---:|---:|---:|
| stop | 1 | 11 | 0 | 1.227 | 5.383 |
| broad | 1 | 11 | 0 | 1.229 | 5.922 |
| targeted | 1 | 11 | 0 | 1.505 | 5.600 |
| full_source | 3 | 9 | 0 | 3.554 | 5.624 |

## Paired comparisons

- stop_to_targeted: 0 wins, 0 losses, 1 jointly correct, 11 jointly wrong, 0 unknown pairs.
- broad_to_targeted: 0 wins, 0 losses, 1 jointly correct, 11 jointly wrong, 0 unknown pairs.
- full_source_to_targeted: 0 wins, 2 losses, 1 jointly correct, 9 jointly wrong, 0 unknown pairs.

Broad and targeted each spend two additional report calls beyond the identical shared report/planner acquisition. Their contrast is the main evidence about choosing useful requests rather than merely buying more information. Targeted versus stop measures the combined effect of two extra calls and the focused questions; it does not isolate targeting. Full-source is a different one-call information condition.

## Concrete mechanisms

- `q0617d8bcca5d6bb08ed0` (2-hop): gold_string_present_but_final_wrong; outcomes stop=W, broad=W, targeted=W, full_source=W. Broad/targeted extra-report gold-string flags: True/True. This is lexical, not proof of faithful use.
- `qbb5349a9b7b73dd77f26` (2-hop): gold_string_present_but_final_wrong; outcomes stop=W, broad=W, targeted=W, full_source=W. Broad/targeted extra-report gold-string flags: False/True. This is lexical, not proof of faithful use.
- `qbefa334e11dccbcdb36d` (4-hop): gold_string_present_but_final_wrong; outcomes stop=W, broad=W, targeted=W, full_source=W. Broad/targeted extra-report gold-string flags: True/True. This is lexical, not proof of faithful use.

## Provenance and limits

Accepted source READY: `c799becad8d574d6785dbd4292e00b6bb27536175adb8b6b71f1df4c469dd1c1`; frozen data manifest: `d460d9578add8831f50d86b66897c50859ec81ce372e3b0ed4199d91d5150a3c`; schedule file: `b9a02f515d403a36aa5743c4c6daabf607f58b299b2d2dbba09ce2ca0ab73274`. The additive INPUTS.json authenticates 701 saved result artifacts.

Answers and support indices were independently reconstructed from raw native token IDs and scored with an independent implementation of the published MuSiQue normalization and support-set formulas. The analyzer executed no generated code, made no model calls, and never put host gold into model-visible prompts. Twelve contexts—not 48 IID items—are the unit of interpretation. Endpoint gains demonstrate neither learned routing nor autonomous decomposition.

## Cost

```json
{
  "authenticated_returned": 132,
  "cached_tokens_observed_subtotal": 0,
  "cached_tokens_unknown_calls": 0,
  "completion_tokens_observed_subtotal": 24284,
  "completion_tokens_unknown_calls": 0,
  "not_started": 0,
  "physical_started": 132,
  "planned_boundaries": 132,
  "prompt_tokens_observed_subtotal": 241189,
  "prompt_tokens_unknown_calls": 0,
  "status_counts": {
    "returned_valid": 132
  },
  "sum_call_seconds_not_concurrent_wall": 791.8621842861176,
  "unknown_usage_is_not_zero": true
}
```

Token subtotals exclude calls with missing usage; their counts are explicit. Summed request times overlap under four-question concurrency and are not wall time.

