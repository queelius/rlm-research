# Independent fresh adaptive-helper result

Raw audit decoded 152/152 native token responses over 128 fresh IDs; release clean: **True**; interpretation eligible: **True**.

## Policy results

| Dataset | Policy | Correct / 64 | Wrong | Unavailable | Logical calls | Observed tokens |
|---|---|---:|---:|---:|---:|---:|
| trec | original16 | 62 / 64 | 2 | 0 | 4 | 6135 |
| trec | three_vote | 61 / 64 | 3 | 0 | 12 | 18401 |
| trec | selective_singleton | 61 / 64 | 3 | 0 | 12 | 15598 |
| trec | always_singleton | 60 / 64 | 4 | 0 | 64 | 53233 |
| ag_news | original16 | 55 / 64 | 9 | 0 | 4 | 8383 |
| ag_news | three_vote | 54 / 64 | 10 | 0 | 12 | 25138 |
| ag_news | selective_singleton | 56 / 64 | 8 | 0 | 16 | 23025 |
| ag_news | always_singleton | 55 / 64 | 9 | 0 | 64 | 50435 |

## Decision

- **trec:** selective-vs-three-vote promotion screen = **True** (accuracy at least as high: True; fewer observed tokens: True; complete: True).
- **ag_news:** selective-vs-three-vote promotion screen = **True** (accuracy at least as high: True; fewer observed tokens: True; complete: True).

The single shared physical collection made 152/152 calls and reported 147207 tokens. Logical policy costs reuse those calls; they are not independent runs and imply no counterfactual wall time.

Paired record changes are descriptive only. No item-level p-value is reported because records share batched calls and routed components. TREC has five observed gold classes and no abbreviation examples, so it is reported separately and is not pooled with the older 128-example panel. Fresh means excluded from verified local helper optimization and prior panels, not unseen in base-model pretraining.
