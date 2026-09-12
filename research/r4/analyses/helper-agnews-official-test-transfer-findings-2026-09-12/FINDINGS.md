---
title: Official-test AG News transfer findings
date: 2026-09-12
status: completed_exploratory_transfer_readout
---

# Official-test transfer: weaker, without a clear RL-SFT separation

The independent source-to-raw audit retained all four predeclared endpoints; no training seed or checkpoint was selected using these outcomes. All arms have 512/512 available predictions from 128/128 valid four-record calls.

## Fixed endpoints

| Arm | Correct / 512 | Accuracy | World | Sports | Business | Sci/Tech | Owner s |
|---|---:|---:|---:|---:|---:|---:|---:|
| `c32` | 422 | 82.42% | 115 | 124 | 112 | 71 | 405.96 |
| `rl_step8` | 427 | 83.40% | 111 | 125 | 110 | 81 | 433.26 |
| `sft_step8` | 426 | 83.20% | 115 | 125 | 112 | 74 | 408.15 |
| `rl_seed2_step8` | 429 | 83.79% | 113 | 125 | 110 | 81 | 398.07 |

## Paired comparisons

| Comparison | Wins / losses | Net | Changed labels | Cluster-bootstrap 95% interval |
|---|---:|---:|---:|---:|
| `c32_vs_rl_seed2_step8` | 11 / 4 | +7 | 15 | 0.00% to 2.73% |
| `c32_vs_rl_step8` | 11 / 6 | +5 | 17 | -0.39% to 2.34% |
| `c32_vs_sft_step8` | 4 / 0 | +4 | 5 | 0.20% to 1.56% |
| `rl_step8_vs_rl_seed2_step8` | 3 / 1 | +2 | 4 | -0.39% to 1.56% |
| `rl_step8_vs_sft_step8` | 6 / 7 | -1 | 14 | -1.37% to 0.98% |
| `sft_step8_vs_rl_seed2_step8` | 7 / 4 | +3 | 12 | -0.59% to 1.76% |

The two fixed RL seeds make the same prediction on 508/512 records and differ on 4; 1 favor seed 1 and 3 favor seed 2. This is seed variation, not a model-selection opportunity.

On the earlier research-exposed panel, the corresponding c32 / RL-seed1 / SFT / RL-seed2 totals were 422 / 437 / 427 / 436. The panels are not pooled, and their difference does not by itself reveal a distribution-shift mechanism.

## Cost and interpretation

- `c32` evaluation: 128 physical calls; 127682 prompt tokens (87376 cached), 10184 completion tokens; {'cached_prompt_tokens': 0, 'completion_tokens': 0, 'prompt_tokens': 0} unknown-usage ledger; 405.96s owner time.
- `rl_step8` evaluation: 128 physical calls; 127682 prompt tokens (87376 cached), 10210 completion tokens; {'cached_prompt_tokens': 0, 'completion_tokens': 0, 'prompt_tokens': 0} unknown-usage ledger; 433.26s owner time.
- `sft_step8` evaluation: 128 physical calls; 127682 prompt tokens (87376 cached), 10190 completion tokens; {'cached_prompt_tokens': 0, 'completion_tokens': 0, 'prompt_tokens': 0} unknown-usage ledger; 408.15s owner time.
- `rl_seed2_step8` evaluation: 128 physical calls; 127682 prompt tokens (87376 cached), 10208 completion tokens; {'cached_prompt_tokens': 0, 'completion_tokens': 0, 'prompt_tokens': 0} unknown-usage ledger; 398.07s owner time.

Private review of changed records is consistent with modest movement at overlapping Business/Sci-Tech and World/topic boundaries. Both RL seeds gain ten Sci/Tech answers over c32, but lose two Business and two-to-four World answers. SFT changes only five labels, gaining four correct answers without a correct-to-wrong flip. These are category-boundary movements, not evidence for a new capability, a specific learned rule, or a causal explanation for the panel difference.

The transfer signal is materially weaker than on the exposed panel. Do not claim a meaningful RL advantage over SFT: although the two RL seeds are coherent relative to c32, they exceed SFT by only one and three answers, and both descriptive RL-vs-SFT intervals span zero. A useful next decision is a prospectively frozen replication requiring both RL seeds to beat matched SFT by a preregistered margin without a compensating World/Business loss. Otherwise retire the broad RL-superiority interpretation and describe the result as modest boundary calibration.

## Limits

- Official-test examples are new local examples from AG News, not a new task or domain.
- Absence from base-model pretraining is unknown.
- The descriptive bootstrap unit is the shared four-record request, not 512 independent items.
- Different results on exposed and official-test panels do not identify distribution-shift cause.
- One favorable answer among fixed arms is not evidence that RL meaningfully beats SFT.
