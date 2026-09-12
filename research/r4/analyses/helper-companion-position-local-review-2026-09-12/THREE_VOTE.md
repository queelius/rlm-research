# Fixed three-vote offline baseline

[BatchPrompt §§2–3](https://arxiv.org/html/2309.00384v2#S2) already uses permutation majority voting and confidence-based early stopping. Its later unresolved sets can be smaller. Grouping/order sensitivity or ensembling is not a new-method claim here. This baseline votes over original and two available companion regroupings, with an all-distinct tie returning original; it is not an exact BPE/SEAS reproduction.

| Dataset | Original16 | Three-vote | Three-vote tokens | All-distinct ties |
|---|---:|---:|---:|---:|
| trec | 117/128 | 119/128 | 36794 | 0 |
| ag_news | 115/128 | 113/128 | 51124 | 0 |

| Dataset / singleton rule | Correct | Wins/losses vs three-vote | Token ratio vs three-vote |
|---|---:|---:|---:|
| trec: neighbor_A+neighbor_B | 119/128 | 1/1 | 0.983 |
| trec: original+neighbor_A | 121/128 | 2/0 | 0.870 |
| trec: original+neighbor_B | 119/128 | 1/1 | 0.960 |
| ag_news: neighbor_A+neighbor_B | 110/128 | 1/4 | 0.928 |
| ag_news: original+neighbor_A | 112/128 | 0/1 | 0.821 |
| ag_news: original+neighbor_B | 111/128 | 1/3 | 0.867 |

All comparisons remain offline and use 256 unique exposed records. Singleton outcomes come from a different service/cache history; costs are replayed physical input+output sums, without transferable cache/latency claims. Every predeclared rule is shown; none is confirmed best. The fresh question is whether selective smaller requests add useful accuracy/cost beyond a fixed contextual ensemble—not whether batched order effects exist.
