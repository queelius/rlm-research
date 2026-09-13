# Mechanical normalization helps recall, but does not solve eligibility

The independent [native audit](REPORT.json) found zero issues: all 36 calls known, exact frozen model/prefix/seed matches, all 114 public candidates retained, every effective field independently reconstructed, and runtime qualified/released. Canonical response digests and raw-byte hashes were checked separately. No generated code was executed or output repaired.

Unordered exact improves **0/18 → 4/18**, four wins and no losses. These are **two of nine stage contexts**, each successful at both seeds—not four independent tasks. Both successful contexts have width 6. Strict sorted exact remains 0 in both arms: every new exact set is unsorted.

| Width | Exact raw → normalized | Mean BA raw → normalized |
|---|---:|---:|
| 6 (3 stages × 2 seeds) | 0/6 → 4/6 | .800 → .917 |
| 12 (3 × 2) | 0/6 → 0/6 | .673 → .694 |
| 20 (3 × 2) | 0/6 → 0/6 | .423 → .594 |

Across all 18 valid sets per arm, TP/FP/FN/TN change 116/53/32/27 → 138/49/10/31. Micro precision is .6864 → .7380 (116/169 → 138/187), recall .7838 → .9324 (116/148 → 138/148), and mean per-set BA .6320 → .7351. Invalid-known and unknown are both zero. Four seed pairs have lower BA despite no exact losses; improvement is not universal.

All nine cases are adjudicated against public policy in [MECHANISM_REVIEW.json](MECHANISM_REVIEW.json):

- `3b55ef23e40dea`: both wins restore one missed eligible ID; no false positive added.
- `3a96f2bcc0b496`: both wins restore one eligible ID and remove one ineligible ID.
- `5b6abad4190621`: restores the missing eligible ID but introduces a failed-schema candidate; BA falls at both seeds.
- `4d622901f2285d`: retains full recall and reduces false positives; two failed-check candidates remain.
- `33ca83880db0c7`: normalized full recall, but two below-minimum-quality candidates remain; seed 0 trades omissions for false positives.
- `81a3b6f141854a`: normalization selects all 12 candidates, restoring three eligible IDs but retaining five check failures; BA falls at both seeds.
- `cec12b35e126c3`: fewer false positives and better BA, but one eligible ID is missed at both seeds.
- `a8815208d53ada`: normalization selects all 20 candidates; full recall is accompanied by nine ineligible IDs.
- `5f8ef53952b1fa`: fewer omissions and false positives, yet four eligible IDs are missed and three check failures selected.

The remaining failures are not only bookkeeping: normalized records explicitly expose failed checks and low quality, yet the model still includes those candidates. This is observable selection behavior, not evidence of the model's hidden reasoning. Most residual false positives violate required checks; six repeat-weighted violations concern quality.

Natural cost is one call per answer in both arms, 36 physical calls total. Input tokens fall 71,236 → 41,298 (−42.0%); output tokens rise 2,781 → 3,069. Total tokens fall 74,017 → 44,367. All calls stopped normally; owner elapsed 119.8256 s. Representation and explanatory wording jointly changed, and token costs are not matched.

Next: the approved fresh 12-stage replication, preserving the exact transform/prompt and both fresh raw controls, with prospective history-depth 1/3 and width strata. It tests same-family generalization and bookkeeping load—not learned decomposition. Do not add another prompt variant from these exposed nine cases.

Evidence: REPORT SHA `9c1a82841c9eccfb2f18aa27cf8c3cf9e710dd8bbd66a1c16d84528af03b06be`; mechanism SHA `46eb9c6fc379a0a953bdf31b199125cc44956b0f364d97357bb2fe20e6ae5dbc`. Full source/call hashes are retained in those files; primary results remain unchanged.
