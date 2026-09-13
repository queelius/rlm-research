# Singleton176 independent saved-native readout

Status: COMPLETE_RAW_AUDIT; 176/176 native calls available; six context units, two repeats each.

| Arm | Exact / 12 | Semantic valid | Unknown | TP / FP / FN / TN | Input / output tokens |
|---|---:|---:|---:|---|---|
| list | 4 | 10 | 0 | 66 / 18 / 2 / 26 | 27446 / 1927 |
| vector | 4 | 11 | 0 | 76 / 7 / 5 / 44 | 27850 / 376 |
| singleton | 10 | 12 | 0 | 92 / 2 / 0 / 58 | 103002 / 912 |

list_vs_vector: {'both_exact': 4, 'both_wrong': 8}.
list_vs_singleton: {'both_exact': 4, 'both_wrong': 2, 'win': 6}.
vector_vs_singleton: {'both_exact': 4, 'both_wrong': 2, 'win': 6}.

Owner elapsed 100.610s. Full raw bytes, native token/model/prefix/seed/usage and complete scalar unions were checked; 0 audit issues.

Invalid arrays/scalars and missing calls remain separate; confusion totals require matched-valid denominators. Every scalar is required for a full stage answer. No eligibility repair, output filtering or learned routing. Natural physical cost is not matched compute; six contexts are not176 independent samples.
