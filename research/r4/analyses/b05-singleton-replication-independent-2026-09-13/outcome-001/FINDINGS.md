# Singleton328 independent saved-native readout

Status: COMPLETE_RAW_AUDIT; 328/328 native calls available; twelve context units, two repeats each.

| Arm | Exact / 24 | Semantic valid | Unknown | TP / FP / FN / TN | Input / output tokens |
|---|---:|---:|---:|---|---|
| vector | 10 | 23 | 0 | 184 / 8 / 9 / 83 | 56088 / 837 |
| singleton | 22 | 24 | 0 | 206 / 2 / 0 / 96 | 207004 / 1824 |

vector_vs_singleton: {'both_exact': 10, 'win': 12, 'both_wrong': 2}.

Owner elapsed 86.137s. Full raw bytes, native token/model/prefix/seed/usage and complete scalar unions were checked; 0 audit issues.

Invalid arrays/scalars and missing calls remain separate; confusion totals require matched-valid denominators. Every scalar is required for a full stage answer. No eligibility repair, output filtering or learned routing. Natural physical cost is not matched compute; twelve contexts are not328 independent samples.
