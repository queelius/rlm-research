# Repeat128 checkpoint on the frozen official-test panel

All five endpoints are fixed; the four saved reference arms were not regenerated.

| Arm | Correct / 512 | Available |
|---|---:|---:|
| `c32` | 422 | 512 |
| `rl_step8` | 427 | 512 |
| `sft_step8` | 426 | 512 |
| `rl_seed2_step8` | 429 | 512 |
| `rl_repeat128_step8` | 425 | 512 |

| Comparison (reference → repeat128) | Wins | Losses | Net | Changed |
|---|---:|---:|---:|---:|
| `c32_vs_rl_repeat128_step8` | 5 | 2 | +3 | 8 |
| `rl_step8_vs_rl_repeat128_step8` | 9 | 11 | -2 | 21 |
| `sft_step8_vs_rl_repeat128_step8` | 3 | 4 | -1 | 7 |
| `rl_seed2_step8_vs_rl_repeat128_step8` | 7 | 11 | -4 | 19 |

Interpretation is bounded: persistence of the broader-versus-repeat contrast supports a breadth hypothesis, while disappearance revises it toward panel-specific boundary shifts. Neither outcome identifies breadth causally from one run.

## Limits

- Same AG News task; not domain transfer or absence from base pretraining.
- The repeated checkpoint was already scored on the research-exposed panel.
- This fixed official-panel readout adds no checkpoint selection but is one training run.
- Accuracy pairs share four-record request clusters; item-level independence is not assumed.
