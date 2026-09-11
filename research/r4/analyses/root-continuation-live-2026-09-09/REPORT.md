# Root-only RLVR continuation: final exploratory result

Finalized 2026-09-09 UTC. The continuation completed at approximately 02:44:30, within its new three-hour cap. Original V2 remains stopped and unchanged; its first three updates and already-collected round04 were inherited, not rerun. No GPU or endpoint requests were made by this analysis.

## Outcome and decision

Selected root step8 improves strict fresh-transfer success from **5/24 to 16/24** with the same frozen child: **13 paired gains, two losses and nine ties**. All48 outcomes are observable and admitted, with no transfer exclusions, integrity failures or budget censoring. Four of six context clusters improve and two tie; none declines. This is a promising exploratory root-weight result that merits replication, not a confirmatory learning claim.

The transfer consists of six new root contexts, each containing64 questions, two count queries and two seeds. Those questions are supported by the fixed child's leaf-SFT training split: this is root composition transfer, not unseen-question or cross-domain transfer. Twenty-four coordinates are not24 independent contexts.

| Context window | Original / 4 | Selected / 4 | Gains / losses |
|---|---:|---:|---:|
| 1200 | 1 | 1 | 1 / 1 |
| 1201 | 0 | 4 | 4 / 0 |
| 1202 | 1 | 4 | 3 / 0 |
| 1203 | 1 | 3 | 2 / 0 |
| 1204 | 0 | 2 | 2 / 0 |
| 1205 | 2 | 2 | 1 / 1 |

Decision: prioritize an independently seeded, counterbalanced replication with unchanged-policy replay, preserving the fixed child and initial request contract. Before a mechanism claim, a bounded follow-up can compare actual batch sizes, JSON decoding/type handling, coverage and logical/cached/output costs. More child calls and better final-format validity alone do not establish better classification or faithful aggregation. A separately observed JSON-string/character-extension failure is **not evidence of what this RLVR run fixed**.

## Matching and causal boundary

[TRANSFER_MATCHING_AND_COSTS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: TRANSFER_MATCHING_AND_COSTS.json") verifies12/12 keyed task objects, all24 coordinate contents, all six exact context texts and ordered64-question group memberships, queries, source IDs, task hashes and151 shared declared source/input hashes. Relevant actual input files were rehashed. [TRANSFER_DETAILS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: TRANSFER_DETAILS.json") verifies24/24 equal initial physical prompt-token arrays and actual provider sampling objects. Every first-root sampled action differs before any child response; downstream changes therefore cannot be attributed to child mediation alone.

The intentional intervention is the root adapter: original `857a7ce6…` versus step8 `473210b1…`. All successful audited calls use the expected depth-specific aliases and model hashes: root55→49 calls; unchanged child `c32de129…`,97→352 calls. Base, native renderer/prefill, sampling, Python/container image, maximum recursion depth1, per-episode budgets and tool/decoder contracts match. Raw root adapter configurations differ in PEFT serialization/default metadata, but the installed vLLM loader's effective rank8, alpha16, scale2 and seven-module configuration is equal.

Different `dataset_id` values are expected: they hash execution provenance, including attempt paths, actual records, specs and role bindings. Both were exactly recomputed. Coordinate-plan IDs include phase, generated run/group/pair IDs and dispatch order; the runtime then adds authenticated task hashes. Content-only paired coordinates match. Keying by task+seed resolves task-list ordering.

Qualification: original ran first, selected second, and independent dispatch permutations differ at23/24 positions with eight concurrent pairs. Their remaining shared-stage caps were1756.79s and1308.79s; neither was reached and per-episode limits were identical. Matched seeds do not eliminate serving/order variation; this campaign has no matched unchanged-policy replay.

## Learning execution and selection

Eight actual Adam updates are authenticated, including exact inherited step3 adapter/optimizer/RNG → new4→5→6→7→8. New checkpoints retain predecessor hashes, optimizer options and parameter order; all504 saved Adam states advance to the expected step, and loaded adapter values match. Across inherited and new updates: **158 mixed-group episodes,362 root turns,108,461 credited root-action tokens**; child and observation credit are zero. All recorded distribution/gradient guards pass. This is saved-state/load/step verification, not a fresh full arithmetic re-derivation of every update.

| Fixed validation step | 0 | 2 | 4 | 6 | 8 |
|---|---:|---:|---:|---:|---:|
| Strict / 8 | 2 | 3 | 3 | 2 | 4 |

Every validation admits all eight outcomes. The unchanged earliest-maximum rule uniquely selects8, so selected and final coincide in this run. Step8 is SHA256 `473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd`. Initial→8 has three gains/one loss. Selection searched five checkpoints on only two contexts; it is not independent validation evidence. Fresh collection totals12,13,12,12,14,16,22,21 correct of32 use new trajectories and are **not a paired learning curve**. An earlier separate pilot's2/8→unchanged4/8→post2/8 illustrates relevant variability, not a matched control here.

## Admission censoring

Across256 training collections, endpoint outcomes are122 correct,132 wrong and two unobservable; admission outcomes are122 correct,129 wrong and five null. Three completed wrong trajectories remain excluded for fully authenticated unsampled child HTTP400 context overflow; two other trajectories remain unobservable. Four rejected requests exceed the8192-token limit. Their36,008 requested input tokens are not measured executed GPU usage.

The amendment keeps round04's original29 admitted rows, distinguishes its completed wrong endpoint from two unobservable nulls, and trains on19 mixed episodes without a reroll or new admission. New exclusions in rounds05/06 satisfy the same narrow criterion. Unknown failures still stop. [TRAIN_ADMISSION_CENSORING.json](../../../../ARTIFACTS.md#unpublished-files "Not published: TRAIN_ADMISSION_CENSORING.json") records the residual policy-induced censoring: training on authenticated recovered-root negatives is a separate future intervention, potentially changing group membership and normalized advantages—not a silent append to this run.

## Cost and timing

| Transfer metric | Original | Selected |
|---|---:|---:|
| Logical input tokens | 214,103 | 366,845 |
| Completion tokens | 49,457 | 28,964 |
| Model calls / recursive-subcall metric | 152 / 93 | 401 / 335 |
| Executed Python calls | 35 | 42 |
| Final-format-valid episodes | 11 / 24 | 22 / 24 |
| Length-stopped calls / affected episodes | 13 / 5 | 4 / 2 |
| Rollout elapsed seconds | 389.39 | 210.42 |
| Episode wall median / p90 / maximum seconds | 46.14 / 138.15 / 364.11 | 52.82 / 66.64 / 161.44 |

Selected has shorter observed tail/output cost but more calls and logical input; this is **not a uniform cost win**. Maximum episode model calls rise19→83. Recursive-subcall metrics and successful child provider calls are distinct counters. NativeTrain supplies no cache measurements, so physical cached work is unknown, not zero. Shared parallel wall time is not FLOPs or summed episode time.

Across inherited/new collections, fixed validations and transfer, counted once:4,507,763 logical input tokens,543,763 completion tokens and4,282 model calls. Optimization alone totals297.32s. Historical and new run envelopes are2074.01s and3410.33s; the intervening stopped gap is excluded. Service startup is171.13s historical plus295.97s new, while service occupancy is1823.74s plus2984.62s and overlaps startup/rollouts—do not add them twice. Trainer import/authentication/load intervals are retained separately; pure model-load time was not instrumented.

## Evidence

[METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") consolidates final metrics, matching and source references. The immutable full final snapshot is [FINAL-20260909T024859.654308Z.json](../../../../ARTIFACTS.md#unpublished-files "Not published: FINAL-20260909T024859.654308Z.json"); prior timestamped snapshots, step audits and decision notes remain unchanged. [SEAL.json](SEAL.json) pins this report, analysis sources and evidence artifacts. No downstream child-label correctness or program-semantics claim is made.
