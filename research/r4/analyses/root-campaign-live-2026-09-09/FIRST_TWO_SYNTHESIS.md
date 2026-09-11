# First two fresh-generation updates: milestone analysis

Snapshot cutoff: 2026-09-09 00:47:07.929010 UTC. Requested milestone reached; CPU watcher exited normally. This is a two-update interim report, not the eight-round campaign result and not a launch/stop recommendation.

## Result and limits

Fixed-eight validation increased from 2/8 to 3/8: two newly correct, one newly wrong, one retained correct, four retained wrong. All eight first-root physical prompt hashes and sampling-object hashes match; every first-root action differs. This establishes a matched-input comparison, not deterministic replay or reliable learning from eight trajectories. The separate prior pilot's 2/8 → unchanged 4/8 → post-update 2/8 illustrates trajectory variability but uses different seeds and cannot be pooled as this campaign's control.

Training fresh-generation success changed 12/32 → 13/32 with different seeds and changed policy. It is not a paired improvement estimate. Two real optimizer steps are verified, but neither these counts nor more recursion establishes successful record coverage or general reasoning.

## Authenticated update chain

| Update | Adam step | Credited episodes / root turns / tokens | Gradient norm | Adapter delta L2 | Optimization seconds |
|---|---:|---:|---:|---:|---:|
| 1 | 1 | 28 / 63 / 23,130 | 0.12961346 | 0.14762313 | 59.732 |
| 2 | 2 | 20 / 41 / 11,091 | 0.13349472 | 0.13932442 | 30.214 |

Actual optimizer tensors have 504 parameter states in each checkpoint, with 252 then 504 nonzero first moments. The second generation binds the first checkpoint's adapter, optimizer and RNG hashes. Parameter deltas were independently recomputed from actual safetensors, not merely copied from RESULT. Root starts at converted original `857a7ce6…`; step 1 is `5c29c593…`, step 2 `5064c043…`. The fixed child remains `c32de129…`; credited child and observation tokens are zero in both exported groups and checkpoint metrics. Full identifiers and authenticated source/input/state/optimizer/RNG/correction chains are in the snapshot METRICS/AUDIT.

Both frozen inference/training distribution checks passed: mean absolute log-ratio 0.00992 / 0.00690, raw-token ESS fraction 0.99596 / 0.99787, removed IS mass fraction 0.000288 / 0. Both use fresh native action probabilities, one full-batch optimizer update per generation, and persistent Adam. These checks support fidelity of this update execution, not policy quality.

Round 1 selects seven mixed four-episode task groups; `root-credit:00:1` is all wrong and contributes no gradient. Round 2 selects five mixed groups; `00:1`, `02:0`, and `02:1` are all wrong and excluded for homogeneous reward. All 64 collection episodes are admitted completed outcomes, with no infra/null/empty-root exclusions. Homogeneous failures remain failures in reported task scores, not missing data. Validation is never selected for training.

## Validation coordinates

| Task | Seed | Before | After update 2 |
|---|---:|---:|---:|
| root-credit:04:0 | 453083576 | 0 | 1 |
| root-credit:04:0 | 616227862 | 1 | 1 |
| root-credit:04:1 | 732686622 | 0 | 0 |
| root-credit:04:1 | 1513209551 | 0 | 1 |
| root-credit:05:0 | 626579430 | 1 | 0 |
| root-credit:05:0 | 699556793 | 0 | 0 |
| root-credit:05:1 | 817681254 | 0 | 0 |
| root-credit:05:1 | 1371633301 | 0 | 0 |

## Trajectory and failure evidence

| Stage | Root / child calls | Root / child action tokens | Root / child length stops | Recursive episodes | Invalid terminals |
|---|---:|---:|---:|---:|---:|
| Validation 0 | 14 / 43 | 3,627 / 3,140 | 0 / 1 | 6/8 | 2 |
| Collection 1 | 70 / 372 | 25,261 / 51,582 | 1 / 14 | 21/32 | 13 |
| Collection 2 | 64 / 176 | 19,867 / 18,922 | 1 / 7 | 20/32 | 10 |
| Validation 2 | 16 / 86 | 4,005 / 3,909 | 0 / 1 | 8/8 | 1 |

Structured/executed tool-call totals agree at 6/6, 109/109, 32/32, and 8/8 respectively. First-root classifications are empty content / structured IPython 2/6, 10/22, 9/23, and 0/8; empty content here is a response classification, not proof of an absent root attempt or infra failure. No provider-error events or overlength-error heuristic matches were observed in these captured artifacts. Length-stopped calls above are separately retained; no truncation or parse error is silently converted into a null episode. Error absence is limited to captured evidence and is not proof that no underlying retry occurred.

Two completed wrong trajectories in collection 1 consumed 174/372 child calls and 34,356/51,582 child action tokens (66.6% of child action tokens): episode prefixes `dbb856cc…` and `704b4b7c…`, taking 373.504 and 213.951 seconds. This is a concrete tail-cost concentration, not an inferred provider retry count. Inherited nano retries are possible, but idempotent replay can occur; attributing extra inference requires request IDs/retry metadata or server replay evidence. Root-only reward cannot identify which child classification, record coverage, aggregation, or terminal-format decision caused a trajectory's reward. More child calls and valid arrays alone do not prove complete correspondence/coverage.

Most useful next evidence is the already-planned later fixed validation plus a frozen fresh-context evaluation, retaining per-coordinate outcomes and terminal validity separately. If investigating efficiency later, inspect the two identified expensive admitted failures and compare coverage/aggregation behavior before proposing a cost intervention. No additional run or source change was made by this analysis.

## Immutable evidence

Snapshot directory: `snapshots/20260909T004707.929010Z` under this analysis directory.

- METRICS.json SHA256: `4d63cae3120d9117875e8e804866e527d045c439743036f22a063ca61b24442c`
- AUDIT.json SHA256: `9c3a2ee37a9c9a33caa7b03a4dcb7603a86344004458d5d4312edb0647766ee3`
- REPORT.md SHA256: `1515762d7cec96495cd304abf60752e5692ce7760044ffa233aa54c8d3456eae`
- Audit identity: `cbe7a26b780b059127369ab4664fa9a0e5dfb625168d39ee7a9541f21c80d417`

The analyzer's three focused CPU tests passed before freezing. Watcher and this report made no GPU/network model requests and changed no experiment inputs or outputs. Separate reproduced `src/rlm` core defects are on an unused runtime path and must not be blamed for these Prime/nano results.
