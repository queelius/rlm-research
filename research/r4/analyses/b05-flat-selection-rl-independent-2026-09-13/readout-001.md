# BA18 selection RL: paired raw readout

COMPLETE: 72/72 available; nine material cases per split, two repeats.

| split/model | strict exact /18 | semantic exact /18 | semantic valid / available | mean BA (valid only) | TP / FP / FN / TN |
|---|---:|---:|---:|---:|---:|
| train/base | 0 | 2 | 17 / 18 | 0.6250240772299596 | 120 / 46 / 21 / 21 |
| train/cp1 | 0 | 2 | 17 / 18 | 0.6656753377341613 | 120 / 41 / 21 / 26 |
| held/base | 0 | 0 | 18 / 18 | 0.6301473988973989 | 117 / 54 / 31 / 26 |
| held/cp1 | 0 | 0 | 18 / 18 | 0.6250344562844563 | 116 / 54 / 32 / 26 |

train: semantic 0 wins/0 losses; 5 changed sets and 0 order-only changes. Paired BA delta 0.040651260504201675 over 17/18 valid pairs. Width/context detail and all outcomes are in JSON.

held: semantic 0 wins/0 losses; 2 changed sets and 0 order-only changes. Paired BA delta -0.005112942612942613 over 18/18 valid pairs. Width/context detail and all outcomes are in JSON.

Owner 101.41363096237183s; phases {"cleanup_seconds": 1.0405690670013428, "science_seconds": 57.399330615997314, "startup_seconds": 42.81378173828125}. Physical tokens: 284332 input, 11480 output; unknown-usage counts retained. Runtime differs from the old width study, so old totals are not pooled.

Changed-set candidate records include true eligibility, revision/check summaries and rejection reasons. These explain the scoring consequences, not the model’s hidden reasoning. Strict order failures are not hallucinated IDs. Train is in-sample fit; held is a small generated-family test, not learned recursion or broad generalization.

Conditional decision: valid held semantic/BA gains beyond ordering warrant one fixed-seed replication on new held stage cases. Train-only gains warrant a small fresh-item same-dose comparison before dose escalation. No semantic change suggests checking probability/selected-ID shifts on saved actions, not another blind optimizer step. Harmful precision/recall or validity tradeoffs retire this exact recipe pending an explicit cause. No further model calls or training authorized by this audit.
