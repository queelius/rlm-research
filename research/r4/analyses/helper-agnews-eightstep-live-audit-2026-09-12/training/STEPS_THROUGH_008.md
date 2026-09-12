# RL training-only diagnostics

Each step uses different fixed128 training rows. No heldout or checkpoint selection.

| Step | Correct/512 | Mixed/32 | ESS/128 | Max IS weight | Delta L2 | Owner s |
|---|---|---|---|---|---|---|
| 1 | 434/512 | 7 | 110.518 | 0.04048 | 0.04021 | 260.86 |
| 2 | 398/512 | 4 | 126.151 | 0.01247 | 0.02931 | 250.62 |
| 3 | 434/512 | 4 | 122.281 | 0.01980 | 0.02565 | 250.65 |
| 4 | 421/512 | 6 | 123.275 | 0.01838 | 0.02309 | 249.91 |
| 5 | 432/512 | 7 | 124.958 | 0.01774 | 0.02298 | 250.26 |
| 6 | 459/512 | 3 | 127.537 | 0.00947 | 0.02153 | 250.78 |
| 7 | 428/512 | 4 | 126.169 | 0.01312 | 0.02095 | 252.06 |
| 8 | 444/512 | 8 | 126.502 | 0.01088 | 0.02009 | 250.21 |

Listed steps passed the sealed per-step source/action/mask/IS/replay/Adam audit.
Token costs are recorded per step in JSON; training is separate from final512 evaluation.
