# Same fixed-k2 confidence rule does not show a routing advantage on the replica

The unchanged rule ranks parent-vector decisions by lowest saved chosen-native-token log-probability, with public-index tie breaking, and substitutes exactly two cached singleton answers. All24 attempts across12 fresh contexts remain in the denominator. One malformed parent has no mapped queries and remains a failure;23 parents are rankable. MAIN already knew the replica's aggregate singleton22/24 result before this analysis. This is **post-hoc offline policy analysis**, not prospectively preregistered routing.

| Cached policy / diagnostic | Exact /24 | Corrected candidate decisions | Regressed decisions |
|---|---:|---:|---:|
| Parent vector unchanged | 10 | 0 | 0 |
| Two lowest chosen-token log-probabilities | 12 | 4 | 0 |
| First two public positions | 13 | 5 | 0 |
| Uniform random two, analytical expectation | 12.064 | 2.9 | 0 |

There are15 available singleton corrections among the284 decisions in valid parents. Confidence captures4/15. The two exact gains, with no losses, are both repeats of **one** width12 context (`root_39669eb3e130ae`): its one erroneous decision ranks first. A second width12 context (`root_f396ecb6aae718`) gets one of its two errors corrected in each repeat, but the other ranks seventh and prevents exact success. No other context improves under the two-query confidence rule. All12 context records, histories/check-revision counts and both repeats are retained in [CONFIDENCE_SUMMARY.json](CONFIDENCE_SUMMARY.json).

The major limitation repeats:263/284 chosen-token log-probabilities are exactly zero, and19/23 units have a tie at the second/third rank boundary. Some recoverable errors rank3rd,6th,15th or17th, driven largely by public order among ties. These are selected-token probabilities that can include inseparable comma/space, not calibrated Boolean confidence. The rule does not outperform the simple first-position control or random expected exactness here. The earlier six-context signal therefore does **not** provide replicated support for this particular confidence heuristic. This does not overturn the independently audited fixed-singleton improvement or exclude other routing signals.

Cached cost is46 selected helpers (31,259 input+276 output tokens), plus all24 parents (56,925 total tokens):70 calls and88,460 summed tokens. Full parent+all-singleton acquisition used328 calls/265,753 tokens. These are observed cached quantities, not measured runtime savings for a new policy. Random expectation uses the same two-query count for valid parents, not exact input-token matching. No query is issued for the malformed parent in this counterfactual; the original all-helper22/24 result remains separate and unchanged.

No ranking rule, threshold, budget, tie rule, prompt or model was changed; no sweep, new runner, GPU call or training was prepared. Keep the old six-context and this12-context result separate; repeated seeds are not independent contexts.

Evidence: [CONFIDENCE.json](../../../../../ARTIFACTS.md) SHA256 `b1d92255dc7e1ca33a6192bdfa9212b7f1037572880dc785421f51a4f9d911b4`; [CONFIDENCE_SUMMARY.json](CONFIDENCE_SUMMARY.json) SHA256 `39ed8a6b29df0e230c58bc70819bfb5f851577f6e3204a041c3ca9da6c02e7ae`; source native audit `f969d2d649721d38a1c0c280dadbe43c0b9672d2fb1a7d32e96b2079f915c6f9`. Reproduction: `../confidence_binding.py`, which hash-pins and reuses the original rule with only dataset/metadata bindings plus the requested descriptive summary. Saved source and consumed native-record hashes are preserved in the JSON files.
