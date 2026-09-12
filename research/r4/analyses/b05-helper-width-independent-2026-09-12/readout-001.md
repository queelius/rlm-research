# B05 helper-width native audit

Status: COMPLETE; 126/126 calls available. Nine stage cases, two repeats; no learned fan-out.

| helpers | strict exact /18 | unordered exact /18 (post hoc) | strict invalid / unavailable | input / output tokens | length stops |
|---|---:|---:|---:|---:|---:|
| 1 | 0 | 2 | 11 / 0 | 70930 / 2959 | 0 |
| 2 | 0 | 0 | 15 / 0 | 80802 / 2733 | 0 |
| 4 | 2 | 2 | 8 / 0 | 100546 / 2848 | 0 |

Strict primary retains the frozen sorted-list contract. Post-hoc unordered scoring ignores order only for unique, in-scope IDs; it never inserts, drops, or eligibility-filters claims. Invalid syntax/scope and unavailable calls remain separate. Costs are physical observed subtotals; unknown-usage counts are in JSON.

Full owner elapsed: 144.651433467865 seconds. Phase costs: `{"cleanup_seconds": 1.0265545845031738, "science_elapsed_seconds": 101.32618737220764, "service_startup_seconds": 42.2694411277771}`.

strict, k2 versus k1: 0 wins/0 losses among 18/18 available pairs; per-case and per-width details retained in JSON.
strict, k4 versus k1: 2 wins/0 losses among 18/18 available pairs; per-case and per-width details retained in JSON.
unordered, k2 versus k1: 0 wins/2 losses among 18/18 available pairs; per-case and per-width details retained in JSON.
unordered, k4 versus k1: 2 wins/2 losses among 18/18 available pairs; per-case and per-width details retained in JSON.

Interpretation: assess whether smaller public scope reduces omission/invalid claims enough to justify duplicated inputs/calls. Three cases per width are descriptive; do not select the best k as a confirmed learned policy. Any new follow-up needs a separate frozen decision. No further optimizer or model calls are authorized by this audit.
