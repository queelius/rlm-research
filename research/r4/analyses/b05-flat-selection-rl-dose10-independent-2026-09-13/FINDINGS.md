# Dose10 changes selection, but does not strengthen complete-set recovery

The saved-native audit is COMPLETE:72/72 calls available, all raw requests/responses, model aliases, prefixes/seeds, decoded tokens, gold and runtime checks pass. All72 finish with stop; no length truncation or unknown usage. Readout JSON SHA: `6536e9e7d284caf0971d3f132ddb3018512aa8f8b5fb767cb28a72ed078898eb`.

| Matched semantic-valid comparison | Train:17 pairs | Held:18 pairs |
|---|---:|---:|
| Mean balanced accuracy, base→dose10 | .629646→.573611 | .630147→.658205 |
| True positives |120→96|117→100|
| False positives |45→38|54→43|
| False negatives |21→45|31→48|
| Number of claimed IDs |165→134|171→143|

Train exact-set success is2→1/18, with one win and two losses. The two losses are both repeats of the same width6 context: the model drops two genuinely eligible implementations from previously complete answers. The one win correctly excludes an implementation whose latest schema and security checks fail. This is not stronger local fit: paired BA falls5.60 percentage points, and mean F1 falls.796786→.715778. All three train widths have negative mean paired BA effects.

The train base has17 semantic-valid answers; dose10 has18. The formerly out-of-shard coordinate (`root_f98f12f66497c2`, repeat0) is now a valid but wrong set, with9TP/6FP/4FN and BA.417582. The table deliberately excludes it from BOTH arms rather than comparing mismatched denominators. The full dose10 train mean over18 is.564943, separately retained in JSON. Transport availability remains18/18 for both models.

Held BA genuinely improves2.81 points, but exact remains0→0/18 and mean F1 falls.758460→.731623; mean Jaccard falls.619347→.587222. Precision rises slightly (.684211→.699301), while recall falls sharply (.790541→.675676). The reward therefore improves through a different false-positive/false-negative tradeoff, not better recovery of complete eligible sets. Width6/12 BA effects are positive; width20 is negative. Six held repeats improve BA, seven worsen, five tie; paired repeats are not independent cases.

Every changed set was inspected against the original public records. On held cases the model removes13 ineligible IDs but also22 eligible IDs, while adding2 ineligible and5 eligible IDs: net11 fewer false positives at the cost of17 true positives. Beneficial removals often reject failed latest security/schema checks. Harmful omissions include implementations with no rejection reason; the large width20 errors drop multiple eligible records. These are reference-derived scoring consequences, not evidence of the model's hidden reasoning. The shift toward fewer claims is observable; attributing it specifically to the list-termination gradient would require evidence not supplied by this readout.

Strict sorted-list validity declines: train6→5/18 and held7→4/18. All13 train and14 held strict-invalid dose10 answers are nevertheless unique in-scope semantic lists, invalid only in ordering. There are15 changed semantic train sets among17 valid pairs; on held there are16 changed sets and two order-only changes. No held base/dose10 native token path is identical.

Compared descriptively with LR1e-4, held BASE tokens are identical on all18 coordinates, while train BASE changes on two coordinates. On the17 common-valid train quadruples, the within-run BA effect moves from+4.065 to−5.604 points; on held it moves from−.511 to+2.806 points. Use each dose's own fresh base; do not silently pool controls or label different validity populations a dose effect.

The separate [ID-renaming audit](../b05-selection-id-renaming-audit-2026-09-13/REPORT.md) reports that the lower-dose advantage disappears on the17 common-valid renamed coordinates and no mapped selected set is identical to the original. That is evidence of strong ID/tokenization sensitivity, not proof of memorization. Together these results do not support robust predicate learning or learned delegation/depth.

Cost:99.741s owner,43.202s startup,54.943s collection,1.437s cleanup;284,332 input and10,618 output tokens. Dose10 produces4,850 output tokens versus5,768 for its fresh base, consistent with shorter claimed sets. No missing usage. Training used the identical original zero-B initialization and one fixed10×LR step; its mathematics is trusted through the qualified checkpoint receipt, not independently rerun here.

Decision: close this bounded dose comparison. The larger step overshoots local fit and improves held BA only with a substantial recall/complete-set cost. Do not promote a general selection gain, select a winning dose post hoc, or launch further training automatically. Preserve the full outcomes and finish the accepted reporting checkpoint. Nine material cases per split, exposed held data, one seed and name sensitivity remain material limitations.
