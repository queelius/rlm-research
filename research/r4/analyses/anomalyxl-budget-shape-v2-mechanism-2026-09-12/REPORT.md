---
title: AnomalyXL V2 Python-arm failure mechanism audit
date_utc: 2026-09-12
status: complete
decision: retire_current_free_form_python_variant
claim_boundary: posthoc trace diagnosis on the same ten exposed mini-panel cases; no RL, recursion, or generalization claim
source_result: /project/alex_phd/runs/rlm-research-r4/sidecars/anomalyxl-native-budget-shape-v2/outputs/attempt-001/RESULT.json
source_result_sha256: b8d93af9a51207de2b6feefb807420ffb683b889d3359707c5af12efb7e2c49d
source_study_sha256: 278c2d7c65c6e80262187dc7d7b559da7e23c5d6d487c7d8e6dd085d33c2b6b8
official_scorer_sha256: c46e12d3e0675acd7e22d618b729ff53feabbf06a3f388d93af9ef3a34fcab76
---

# Finding

The Python arms did not score zero because of a scorer or answer-schema mismatch. The official scorer parsed all eight available Python finals as strict JSON. Their values were wrong: two wrong anomaly kinds, four zero-IoU localization answers, and two empty multi-channel predictions. The remaining 12/20 Python episodes never produced a final, so they provide engineering-failure evidence rather than answer-quality evidence.

The traces separate two problems:

1. **The analysis procedure was inadequate in every scored Python trace.** Generated programs confused channel and time axes, computed an endpoint incorrectly, used a rolling mean as a rolling standard deviation, or responded to an execution exception with an unsupported empty/no-anomaly answer.
2. **The turn allocation was not operationally viable.** Eight of ten `repair3` episodes truncated their first 512-token cell before its closing fence. Two `wide1` cells also truncated at 1,536 tokens; two more used quadratic split scans and hit the eight-second execution limit.

# Trace evidence

| Trace class | Count | What physically happened | Why official primary was zero |
|---|---:|---|---|
| `wide1`, classification | 2 | The program formed a `(1, L)` array, then iterated to `len(array) - window`; with `len(array)=1`, every detector loop was empty. It printed `No Anomaly`. | Both gold rows contained anomalies with non-`No Anomaly` kinds, so `kind_correct=0` and `kind_x_iou=0`. |
| `wide1`, single-channel localization | 2 | The program found threshold crossings but computed the right edge as `argmax(mask[::-1]) + 1`, a distance from the end rather than an original index. It then raised while JSON-encoding NumPy integers. The final copied the diagnostic numbers anyway. | Returned intervals were reversed (`start > end`), hence IoU zero. |
| `repair3`, single-channel localization | 2 | The first cell indexed a `(1, L)` array as though axis 0 were time and raised at index 64. Later cells treated `len(values)==1` as fewer than two samples, printed `present:false`, and repeated that conclusion. | Both gold rows had a real late-series anomaly, so presence was wrong. |
| `wide1`, all-channel localization | 2 | The program assigned the rolling mean to both mean and “std,” padded an even-window convolution from length 32,705 to 32,769, then failed against the 32,768-sample signal. The final nevertheless returned an empty list. | Gold contained one or two channel-localized events; recall and F1 were zero. |

Concrete anonymized examples:

- On one single-channel row whose gold event was near samples 12.9k–13.0k, the program printed `[178, 28)`. This is not a scorer convention issue: it is a reversed interval created by the reverse-index formula, followed by a NumPy JSON serialization exception.
- On one 16-channel row with two gold events, the physical observation was a broadcast error between shapes `(32768,)` and `(32769,)`; the final answer was still `{"anomalies":[]}`.
- In both classification rows, parsing `context.json` succeeded, but a one-channel array's channel count was mistaken for its time length. No detection loop executed.

# Missing finals

- `repair3`: 8/10 first inspection calls ended `finish_reason=length`; the incomplete fenced cell was correctly rejected by the controller.
- `wide1`: 2/10 inspection calls ended `length` and were similarly rejected.
- `wide1`: 2/10 magnitude programs exceeded the eight-second execution limit. They repeatedly recomputed prefix/postfix statistics inside an `O(L^2)` split loop.

These failures are not wrong answers and should not be used to infer anomaly quality. Conversely, the eight parsed finals are not evidence that Python execution helped: the physical observations include the exact exceptions above, and the model either repeated the flawed result or asserted an empty result.

# Interpretation and decision

The environment demonstrated basic competence: it supplied the documented `{"series": ...}` object, executed NumPy code, captured stdout/exceptions, enforced the one-cell protocol and timeout, and the scorer consumed valid finals. The evidence instead points to inadequate free-form analysis and error recovery under these budgets. `repair3` did not repair: on its two surviving cases it repeated the same axis confusion, while its smaller per-turn cap prevented eight other cases from beginning.

Retire this free-form AnomalyXL variant for the current RL/decomposition agenda. Increasing turns or token caps would conflate a larger compute budget with a new method and would not address the observed algorithmic errors.

If AnomalyXL is revisited, the smallest meaningful next step is CPU-only: establish an axis-correct, host-authored diagnostic baseline on training-only rows using the official scorer, covering all five task families. Only if the rounded arrays support useful recovery should a later frozen-panel comparison expose a small vetted set of generic summary/change-point primitives to the model. That would test tool selection and interpretation, not spontaneous invention of anomaly algorithms. It is lower priority than the MRCR procedure calibration because it does not yet exercise learned recursion.

# Limitations

- This is posthoc analysis of ten already exposed cases, with gold used only to classify observed errors.
- No Python final existed for lead/lag or magnitude, so nothing here measures model quality on those families.
- Correcting the identified code defects would not establish that the chosen detectors are statistically adequate.
- The direct mean of 0.0916 and Python means of zero are descriptive; failed coverage prevents a valid arm-quality comparison.
- No generated code was executed during this audit; only saved code, execution receipts, answers, and scorer outputs were inspected.
