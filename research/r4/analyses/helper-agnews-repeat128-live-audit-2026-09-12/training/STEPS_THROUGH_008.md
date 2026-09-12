# RL training-only diagnostics

Each step reuses the SAME128 training rows with fresh sampled actions; no heldout/checkpoint selection.

| Step | Correct/512 | Mixed/32 | ESS/128 | Max IS weight | Delta L2 | Owner s |
|---|---|---|---|---|---|---|
| 1 | 434/512 | 7 | 110.518 | 0.04048 | 0.04021 | 254.27 |
| 2 | 439/512 | 5 | 127.026 | 0.01201 | 0.02897 | 249.82 |
| 3 | 438/512 | 2 | 127.308 | 0.01252 | 0.02522 | 251.96 |
| 4 | 439/512 | 4 | 127.718 | 0.00900 | 0.02256 | 250.71 |
| 5 | 443/512 | 3 | 120.698 | 0.02453 | 0.02264 | 252.00 |
| 6 | 440/512 | 3 | 126.021 | 0.01043 | 0.02134 | 253.98 |
| 7 | 442/512 | 3 | 127.056 | 0.01075 | 0.02107 | 253.10 |
| 8 | 445/512 | 4 | 124.759 | 0.01824 | 0.02092 | 253.33 |

Listed steps passed the sealed per-step source/action/mask/IS/replay/Adam audit.
Token costs are recorded per step in JSON; training is separate from final512 evaluation.
