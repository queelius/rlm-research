# One-step dose: local fit versus exposed held transfer

COMPLETE_PAIRED_AUDIT

## train

| Arm | Correct/32 | Available | Clean target | Input/output tokens | Returned/errors/start-only |
|---|---|---|---|---|---|
| cp32 | 7/32 | 32 | 24 | 69717/21111 | 66/0/0 |
| LR1e5 | 17/32 | 32 | 24 | 68270/20976 | 65/0/0 |
| LR1e4 | 24/32 | 32 | 24 | 65835/28543 | 63/0/0 |

LR1e-4 vs cp32: 17 wins/0 losses, 0 unknown pairs; 7/32 identical native paths; 17 wins preserve programs/observations and repair only edge whitespace. Contexts improved/worsened 5/0.
LR1e-4 vs LR1e5: 7 wins/0 losses, 0 unknown pairs; 17/32 identical native paths; 7 wins preserve programs/observations and repair only edge whitespace. Contexts improved/worsened 3/0.

| Context | cp32 | LR1e-5 | LR1e-4 |
|---|---|---|---|
| omrcr-next-fa62a38bf5881860a77e | 0000 | 0101 | 1111 |
| omrcr-next-83e8a79356c89d99db7f | 0100 | 1111 | 1111 |
| omrcr-next-4e5fbf922e52f33584a7 | 0000 | 0000 | 0000 |
| omrcr-next-969a7a61b93c8afa176a | 0000 | 0000 | 0000 |
| omrcr-next-3bdc3e44003cf70afba9 | 1111 | 1111 | 1111 |
| omrcr-next-64266bb0bf4dd84060f3 | 0001 | 1011 | 1111 |
| omrcr-next-0e42ccab3de2dc127f09 | 0010 | 1111 | 1111 |
| omrcr-next-ff6be6cbca8e5d4571b5 | 0000 | 0000 | 1111 |

U is unavailable, not wrong. All changed paths include actual token tails, parsed program hashes/literal slots, observation hashes/volume and terminal-copy flags in JSON; answers are not copied here.

## held

| Arm | Correct/32 | Available | Clean target | Input/output tokens | Returned/errors/start-only |
|---|---|---|---|---|---|
| cp32 | 25/32 | 32 | 30 | 70634/20739 | 64/0/0 |
| LR1e5 | 25/32 | 32 | 30 | 70634/20739 | 64/0/0 |
| LR1e4 | 28/32 | 32 | 29 | 68904/23618 | 63/0/0 |

LR1e-4 vs cp32: 5 wins/2 losses, 0 unknown pairs; 22/32 identical native paths; 4 wins preserve programs/observations and repair only edge whitespace. Contexts improved/worsened 2/1.
LR1e-4 vs LR1e5: 5 wins/2 losses, 0 unknown pairs; 22/32 identical native paths; 4 wins preserve programs/observations and repair only edge whitespace. Contexts improved/worsened 2/1.

| Context | cp32 | LR1e-5 | LR1e-4 |
|---|---|---|---|
| omrcr-0fcac135277468e96435 | 11 | 11 | 11 |
| omrcr-530d9996c900aa5d7b62 | 11 | 11 | 11 |
| omrcr-62f0a8e60638c25131ad | 11 | 11 | 11 |
| omrcr-574a80aeed5114ad4217 | 11 | 11 | 11 |
| omrcr-0661011e2430461fddc1 | 00 | 00 | 11 |
| omrcr-bcf761ed079ab9231154 | 11 | 11 | 11 |
| omrcr-f515858d24bd0388e927 | 00 | 00 | 11 |
| omrcr-8ad4bef116ef5302ddbf | 11 | 11 | 11 |
| omrcr-ef800b2a29008e4717f1 | 01 | 01 | 10 |
| omrcr-746d5e1512abdfa38878 | 00 | 00 | 00 |
| omrcr-72618dd842efffd0a22e | 11 | 11 | 11 |
| omrcr-85979118c1eb343eff52 | 11 | 11 | 11 |
| omrcr-2568744ab02d7c2786c8 | 11 | 11 | 11 |
| omrcr-85610b95bf89de2580a6 | 11 | 11 | 10 |
| omrcr-1d3d4a8e09d8c93bfbdf | 11 | 11 | 11 |
| omrcr-c277a8dfb869bd3e7819 | 11 | 11 | 11 |

U is unavailable, not wrong. All changed paths include actual token tails, parsed program hashes/literal slots, observation hashes/volume and terminal-copy flags in JSON; answers are not copied here.

Training/owner timings and physical versus mapped policy costs are separate in JSON. Errors/start-only costs are unknown, not zero. Prior controls are reused, not newly charged for each comparison.

Same original cp32 and frozen native batch, nominal LR-only one-step recipe contrast; backward arithmetic is not bitwise identical. Training is in-sample; held16x2 is research-exposed development evidence. Eight training and16 held context clusters, not independent repeats. Official scores/native decode/cost are recomputed; causal/clean-observation definitions reuse reviewed helpers. No further optimizer, threshold tuning or best-arm selection follows automatically.
