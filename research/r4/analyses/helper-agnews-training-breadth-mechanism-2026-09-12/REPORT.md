# What differs between repeated-first128 and broader-data RL?

The 20-answer exposed-panel gap cannot be explained by category balance: every one of the eight source blocks is exactly balanced at 32 World, 32 Sports, 32 Business and 32 Sci/Tech. Both regimes contain 1,024 record memberships and 4,096 sampled label decisions, but repeat128 uses 128 unique articles eight times while broader RL uses 1,024 disjoint articles once.

The first collection is genuinely matched: all 128 sampled maps, predictions, seeds, action tokens and old log-probabilities are equal. It yields 434/512 correct sampled labels and seven mixed G4 groups in both arms. The saved post-update adapter files are nevertheless not byte-equal, so the full experiment is not an exact deterministic counterfactual beyond the matched samples.

| Step | Repeat sampled correct / 512 | Repeat mixed G4 | Broad sampled correct / 512 | Broad mixed G4 |
|---:|---:|---:|---:|---:|
| 1 | 434 | 7 | 434 | 7 |
| 2 | 439 | 5 | 398 | 4 |
| 3 | 438 | 2 | 434 | 4 |
| 4 | 439 | 4 | 421 | 6 |
| 5 | 443 | 3 | 432 | 7 |
| 6 | 440 | 3 | 459 | 3 |
| 7 | 442 | 3 | 428 | 4 |
| 8 | 445 | 4 | 444 | 8 |

Across eight updates, repeat128 exposes 31 mixed-reward groups versus 43 for broader RL. The broader blocks also span materially different class-specific error profiles, especially for Sci/Tech, even though their class counts and coarse lengths are balanced. This makes a diversity/difficulty explanation plausible; a simple class-mixture explanation is not.

The correct conclusion is narrower than ‘breadth caused 20 gains.’ There is one run per regime, the policy changes before each on-policy collection, and the first post-update adapter bytes differ despite matched sampled data. The frozen official-test readout is therefore a useful transfer check, not a causal estimator of unique-example count.
