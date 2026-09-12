# Offline disagreement-to-singleton replay

This is not a live adaptive evaluation. Three fixed nongold rules use saved group-label agreement, escalating only disagreements to saved singleton predictions. The two source runs have different service/cache histories and seed namespaces; no model calls or training were added.

| Dataset / rule | Replay correct | Escalations | Common wrong consensus | Calls | Replay tokens |
|---|---:|---:|---:|---:|---:|
| trec: original+neighbor_A | 121/128 | 9 | 6 | 25 | 32019 |
| trec: original+neighbor_B | 119/128 | 13 | 6 | 29 | 35333 |
| trec: neighbor_A+neighbor_B | 119/128 | 14 | 5 | 30 | 36180 |
| ag_news: original+neighbor_A | 112/128 | 10 | 8 | 26 | 41961 |
| ag_news: original+neighbor_B | 111/128 | 13 | 9 | 29 | 44300 |
| ag_news: neighbor_A+neighbor_B | 110/128 | 17 | 8 | 33 | 47449 |

Baselines: TREC original16 117/128 and saved always-singleton 120/128; news original16 115/128 and saved always-singleton 109/128.

The replay gives a TREC-specific lead, not a general rule: original+neighbor_A gains four correct answers without a recorded loss versus original16, but costs 2.61× its physical tokens. It uses about 30% of always-singleton tokens. The other two TREC variants score 119/128, below always-singleton. All three news variants lose accuracy versus original16, despite spending more tokens. These differences must not be used to declare a confirmed best rule on this exposed panel.


## Paired changes and tradeoffs

- trec, original+neighbor_A: 4 wins/0 losses versus original16; 1 wins/0 losses versus saved always1. Replay tokens are 2.61× original16 and 0.30× always1.
- trec, original+neighbor_B: 3 wins/1 losses versus original16; 0 wins/1 losses versus saved always1. Replay tokens are 2.88× original16 and 0.33× always1.
- trec, neighbor_A+neighbor_B: 4 wins/2 losses versus original16; 0 wins/1 losses versus saved always1. Replay tokens are 2.95× original16 and 0.34× always1.
- ag_news, original+neighbor_A: 0 wins/3 losses versus original16; 5 wins/2 losses versus saved always1. Replay tokens are 2.46× original16 and 0.41× always1.
- ag_news, original+neighbor_B: 1 wins/5 losses versus original16; 3 wins/1 losses versus saved always1. Replay tokens are 2.60× original16 and 0.44× always1.
- ag_news, neighbor_A+neighbor_B: 1 wins/6 losses versus original16; 2 wins/1 losses versus saved always1. Replay tokens are 2.78× original16 and 0.47× always1.

The selector never reads gold; gold is used only for this scoring. Agreement can preserve common wrong answers, whose IDs are listed alongside every escalated ID in DIAGNOSTIC.json. All three predeclared rules remain visible; no rule is promoted as a confirmed best.

Costs always include both full16 passes before selected singleton calls. Physical input lengths are known, but output tokens are replayed from different service histories. These are optimistic, no-retry token estimates—not actual live adaptive cost or latency. DIAGNOSTIC.json also reports input plus every scheduled request's output cap; those large ceilings are bounds, not predictions. No cache savings are transferred or subtracted.

A promising pattern could motivate a fresh adaptive run on a new panel. It does not establish a novel algorithm, learned selector, stable decomposition improvement or general recursion gain.
