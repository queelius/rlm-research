---
status: complete_native_audit
date: 2026-09-10
study: root-supplied-plan-selective-recheck-v1
promotion_gate_passed: false
native_calls: 24
valid_arm_episodes: 16
---

# Selective recheck: native audit

Confidence selection strongly targeted and repaired leaf errors relative to the hash-uniform budget,
but it did not clear the frozen downstream promotion gate. All 24 second-pass calls were native-valid,
giving 16/16 valid arm-episodes and no NULL or authenticated-invalid results. Confidence captured
107/151 baseline errors (70.9%) versus uniform's 34/151 (22.5%). After unconditional overwrite,
confidence made 71 repairs and 31 regressions, net **+40** correct labels; uniform made 19 repairs and
28 regressions, net **-9**. Confidence's net correction exceeded uniform in 7/8 paired episodes and
was positive in aggregate at both sizes (+6 versus 0 at size 64; +34 versus -9 at size 256).

The leaf advantage did not reliably become exact J1 answers. All eight unchanged baselines were J1
wrong. Confidence repaired one to exact (cluster 3, size 64); uniform repaired none. Thus the paired
J1 exact net is only **+1**, short of the prespecified +2 requirement. Neither arm could regress a
baseline-correct answer because none existed. The full gate therefore fails only its downstream +2
clause; there is no reroll and this result alone does not promote a larger fresh-context run.

| Arm | Selected initial errors | Repairs | Regressions | Net leaf | Exact J1 |
|---|---:|---:|---:|---:|---:|
| confidence | 107/320 | 71 | 31 | +40 | 1/8 |
| uniform | 34/320 | 19 | 28 | -9 | 0/8 |

## Paired episode results

| Cluster/size | Confidence leaf net | Uniform leaf net | Advantage | Confidence J1 | Uniform J1 | Gold |
|---|---:|---:|---:|---:|---:|---:|
| 0/64 | +2 | 0 | +2 | 78 | 93 | 82 |
| 0/256 | +9 | -4 | +13 | 251 | 238 | 254 |
| 1/64 | 0 | +1 | -1 | 51 | 47 | 54 |
| 1/256 | +10 | -2 | +12 | 180 | 182 | 196 |
| 2/64 | +3 | 0 | +3 | 54 | 54 | 48 |
| 2/256 | +10 | -5 | +15 | 156 | 160 | 148 |
| 3/64 | +1 | -1 | +2 | **15** | 0 | 15 |
| 3/256 | +5 | +2 | +3 | 147 | 155 | 106 |

The unchanged baseline J1 values, in the same order, were 81, 238, 47, 174, 54, 156, 0, and 148.
Detailed selection recall, qualifying-user differences, contribution errors, native call pins, and
per-episode availability are retained in `AUDIT.json`.

## Availability and physical cost

The 40 frozen first-pass ceiling calls are shared evidence and are counted once: 71,426 input,
24,629 output, and 37,520 cached tokens. The 24 incremental rechecks used 38,781 input, 12,395
output, and 17,840 cached tokens. Their union is 64 physical calls, 110,207 input, 37,024 output,
and 55,360 cached tokens, with zero unknown-usage calls. All 24 provider request IDs were unique.
Second-pass confidence versus uniform input-plus-output token ratio was 1.016, inside the frozen
0.8--1.25 balance range. Elapsed owner time was 83.217 seconds (parent 83.750 seconds); clean service
release and empty post-exit GPU process inventory were authenticated by the exact relayed OWNER and
EXIT hashes.

## Interpretation limits

These are eight nested observations from four correlated clusters, not independent contexts. The
clusters and model are research/optimizer exposed. Structured JSON generation conditions each
second-pass result on the selected subset and repacking, so the study supports error ranking and
leaf-repair usefulness, not probability calibration. It also does not show that requerying improves
new-context J1 performance: the sharp leaf gain translated into only one exact-answer repair.

Replay with `python audit.py --output /tmp/recheck-audit`; this reads producer artifacts but writes
only to the requested analysis directory.
