# BA18 dose10: paired raw readout

COMPLETE: 72/72 available; nine material cases per split, two repeats.

| split/model | strict exact /18 | semantic exact /18 | semantic valid / available | mean BA (valid only) | TP / FP / FN / TN |
|---|---:|---:|---:|---:|---:|
| train/base | 0 | 2 | 17 / 18 | 0.6296459259694553 | 120 / 45 / 21 / 22 |
| train/cp1 | 0 | 1 | 18 / 18 | 0.5649426191092858 | 105 / 44 / 49 / 30 |
| held/base | 0 | 0 | 18 / 18 | 0.6301473988973989 | 117 / 54 / 31 / 26 |
| held/cp1 | 0 | 0 | 18 / 18 | 0.6582049894549894 | 100 / 43 / 48 / 37 |

train: semantic 1 wins/2 losses; 15 changed sets and 0 order-only changes. Paired BA delta -0.05603505971153031 over 17/18 valid pairs. Width/context detail and all outcomes are in JSON.

held: semantic 0 wins/0 losses; 16 changed sets and 2 order-only changes. Paired BA delta 0.028057590557590557 over 18/18 valid pairs. Width/context detail and all outcomes are in JSON.

Owner 99.74106955528259s; phases {"cleanup_seconds": 1.4367954730987549, "science_seconds": 54.94290518760681, "startup_seconds": 43.202216148376465}. Physical tokens: 284332 input, 10618 output; unknown-usage counts retained. Runtime differs from the old width study, so old totals are not pooled.

Changed-set candidate records include true eligibility, revision/check summaries and rejection reasons. These explain the scoring consequences, not the model’s hidden reasoning. Strict order failures are not hallucinated IDs. Train is in-sample fit; held is a small generated-family test, not learned recursion or broad generalization.

## Descriptive dose contrast

The LR1e-4 and LR1e-3 models each retain their own fresh paired base. Both trained from the exact same original zero-B tensors/actions; training math is trusted through qualified receipts. Separate service/cache histories mean cross-run comparisons remain descriptive. Held nine cases are research-exposed, not a fresh confirmation.

train: base tokens changed on 2/18 coordinates; base sets changed on 2. The difference between within-run BA effects is -0.09668632021573198 over 17/18 common-valid quadruples. All original/current validity denominators and cases are in JSON.
held: base tokens changed on 0/18 coordinates; base sets changed on 0. The difference between within-run BA effects is 0.03317053317053317 over 18/18 common-valid quadruples. All original/current validity denominators and cases are in JSON.

This closes the accepted bounded dose comparison. Separate stronger local fit, held transfer, validity and precision/recall tradeoffs; exact-null does not mean no selection movement. Preserve any signal as exploratory evidence, not a selected-dose claim. No further training, model calls, or automatic experiment preparation follows this audit.
