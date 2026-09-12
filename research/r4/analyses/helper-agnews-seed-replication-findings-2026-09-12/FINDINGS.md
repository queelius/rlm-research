# Fixed512 training-seed replication

The positive gain repeats on this same panel under a fresh training seed; this strengthens seed-robustness evidence, not new-data confirmation.

The predeclared finalstep8 is used in both runs; no better-seed or checkpoint selection.

| Arm | Correct /512 | Available | Unavailable |
|---|---:|---:|---:|
| c32 | 422/512 | 512 | 0 |
| rl_seed2_step8 | 436/512 | 512 | 0 |
| rl_step8 | 437/512 | 512 | 0 |

| Paired contrast | Gains / losses | Net | Changed labels | Descriptive95% interval |
|---|---:|---:|---:|---|
| seed1_vs_c32 | 17 / 2 | +15 | 21 | +1.37 to +4.49 pp |
| seed2_vs_c32 | 16 / 2 | +14 | 20 | +1.17 to +4.30 pp |
| seed2_vs_seed1 | 0 / 1 | -1 | 1 | -0.59 to +0.00 pp |

The two seeds share **16 corrections** versus c32; one occurs only in seed1 and none only in seed2. They share two regressions. Seed2 has two wrong→different-wrong changes. This is not merely a similar total: **511 of512 predicted labels are identical between the trained seeds**. Exact IDs and all128 group diagnostics are in FINDINGS.json.

| Host class | c32 | Seed1 | Seed2 | Seed2 gains / losses |
|---|---:|---:|---:|---:|
| Business | 117/128 | 115/128 | 115/128 | 0 / 2 |
| Sci/Tech | 71/128 | 85/128 | 84/128 | 13 / 0 |
| Sports | 121/128 | 124/128 | 124/128 | 3 / 0 |
| World | 113/128 | 113/128 | 113/128 | 0 / 0 |

The observed class tradeoff also repeats: more Sci/Tech and Sports answers become correct, while the same two Business answers regress. The sole difference between trained seeds is one Sci/Tech correction present only in seed1. This stable error pattern strengthens reproducibility on these exact records; it does not identify a neural mechanism.

Seed2's shared B4 groups: 16 positive, 2 negative, 110 zero net; 0 incomplete.

| Cost | Seed1 | Seed2 |
|---|---:|---:|
| Training owner s | 2094.99 | 2132.90 |
| HF stage s (nested) | 614.44 | 615.04 |
| Native training prompt_tokens | 1025748 | 1025748 |
| Native training completion_tokens | 81624 | 81604 |
| Native training cached_prompt_tokens | 934016 | 934016 |

Each trainer uses1024 native maps on the SAME1024 training articles. Seed2 endpoint adds128 physical calls, owner 423.94s, 127663 prompt and 10182 completion tokens. Both saved references are reused, not re-queried or charged as new calls. Full per-phase costs and unknown-usage counts are in JSON; nested phases are not added to owner time.

Mixed groups across the eight distinct blocks were seed1 [7, 4, 4, 6, 7, 3, 4, 8] and seed2 [3, 3, 3, 6, 7, 3, 4, 7]. All eight source/raw/mask/importance/replay/Adam audits passed. Distinct-block reward scores are not a learning curve.

Limits: same now-research-exposed512, one additional training seed, and128shared request clusters—not 1024 independent test articles. Intervals are descriptive cluster bootstraps, not independent-item p-values. This is a source-to-raw audit, not an independently implemented trainer. No broad helper, recursion or planner claim follows.

Next decision: retain both seeds; assess the fixed repeated-first128 arm only if separately admitted, with retention/controller priorities unchanged. A partial-dose stop cannot answer the completed8-update mechanism contrast.

Evidence: [qualified raw paired audit](../helper-agnews-eightstep-seed2-live-audit-2026-09-12/outcomes/RAW_AUDIT.json), [full derived findings](FINDINGS.json), [derivation](analyze.py). The JSON is computed from the unchanged scorer; this Markdown includes the subsequent plain-language review.
